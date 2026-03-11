"""Post-audit finding deduplication via LLM reasoning pass.

Sends findings to a cheap model to group semantically equivalent findings
and assign canonical titles, making finding IDs stable across runs.
"""

from __future__ import annotations

import json
import sys

from noxaudit.config import DedupConfig
from noxaudit.models import Finding
from noxaudit.providers.base import BaseProvider

DEFAULT_DEDUP_MODELS: dict[str, str] = {
    "gemini": "gemini-2.0-flash",
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-haiku-3-5-20241022",
}

DEDUP_SYSTEM_PROMPT = """\
You are a deduplication engine for code audit findings. Your job is to group \
findings that describe the same underlying issue.

Two findings are the same issue if they:
- Refer to the same file AND the same problem (even if described with different words)
- Point to the same logical concern in nearby lines of the same file

Two findings are NOT the same issue if they:
- Refer to different files (even if the problem type is similar)
- Refer to the same file but genuinely different problems

For each group, pick the most precise and descriptive title as the canonical title.

Return JSON with this exact schema:
{
  "groups": [
    {
      "canonical_title": "The best title for this issue",
      "finding_ids": ["id1", "id2"]
    }
  ]
}

Every input finding ID must appear in exactly one group. Singletons get a group \
with one ID. Do not invent new findings or drop any."""


def _build_dedup_payload(findings: list[Finding]) -> str:
    """Serialize findings to a compact JSON payload for the dedup prompt."""
    items = []
    for f in findings:
        items.append(
            {
                "id": f.id,
                "file": f.file,
                "line": f.line,
                "focus": f.focus,
                "title": f.title,
                "description": f.description[:200],  # Truncate for cost
            }
        )
    return json.dumps(items, indent=None)


def _call_gemini(model: str, system_prompt: str, user_msg: str) -> dict:
    """Call Gemini via direct (non-batch) API."""
    from google import genai

    client = genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=user_msg,
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
        },
    )
    return BaseProvider._safe_json_loads(response.text)


def _call_anthropic(model: str, system_prompt: str, user_msg: str) -> dict:
    """Call Anthropic via direct (non-batch) API."""
    import anthropic

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = message.content[0].text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return BaseProvider._safe_json_loads(text.strip())


def _call_openai(model: str, system_prompt: str, user_msg: str) -> dict:
    """Call OpenAI via direct (non-batch) API."""
    import openai

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
    )
    text = response.choices[0].message.content
    return BaseProvider._safe_json_loads(text)


_CALLERS = {
    "gemini": _call_gemini,
    "anthropic": _call_anthropic,
    "openai": _call_openai,
}


def _call_provider(provider: str, model: str, system_prompt: str, user_msg: str) -> dict:
    """Dispatch to the appropriate provider caller."""
    caller = _CALLERS.get(provider)
    if not caller:
        raise ValueError(f"Unknown dedup provider: {provider}")
    return caller(model, system_prompt, user_msg)


def _recompute_finding_id(finding: Finding) -> str:
    """Recompute a finding's ID from its current metadata."""
    raw = {
        "file": finding.file,
        "title": finding.title,
        "line": finding.line,
        "focus": finding.focus,
    }
    return BaseProvider.make_finding_id(raw)


def _apply_groups(findings: list[Finding], groups: list[dict]) -> list[Finding]:
    """Apply canonical titles from dedup groups and collapse duplicates."""
    findings_by_id = {f.id: f for f in findings}

    # Build mapping: old_id -> canonical_title
    canonical_map: dict[str, str] = {}
    for group in groups:
        title = group.get("canonical_title", "")
        for fid in group.get("finding_ids", []):
            if fid in findings_by_id and title:
                canonical_map[fid] = title

    # Apply canonical titles and recompute IDs
    result: list[Finding] = []
    seen_ids: set[str] = set()

    for f in findings:
        canonical_title = canonical_map.get(f.id)
        if canonical_title:
            f = Finding(
                id=f.id,
                severity=f.severity,
                file=f.file,
                line=f.line,
                title=canonical_title,
                description=f.description,
                suggestion=f.suggestion,
                focus=f.focus,
            )
        new_id = _recompute_finding_id(f)
        if new_id in seen_ids:
            continue  # Duplicate after title normalization
        seen_ids.add(new_id)
        f = Finding(
            id=new_id,
            severity=f.severity,
            file=f.file,
            line=f.line,
            title=f.title,
            description=f.description,
            suggestion=f.suggestion,
            focus=f.focus,
        )
        result.append(f)

    return result


def deduplicate_findings(
    findings: list[Finding],
    config: DedupConfig,
) -> list[Finding]:
    """Deduplicate findings using an LLM reasoning pass.

    Sends finding metadata to a cheap model which groups semantically
    equivalent findings and assigns canonical titles. Returns findings
    with stable titles and recomputed IDs.

    Falls back to returning original findings on any error.
    """
    if not config.enabled or len(findings) <= 1:
        return findings

    model = config.model or DEFAULT_DEDUP_MODELS.get(config.provider, "")
    if not model:
        print(f"[dedup] No model configured for {config.provider}, skipping", file=sys.stderr)
        return findings

    payload = _build_dedup_payload(findings)
    user_msg = f"Group these {len(findings)} audit findings by semantic equivalence:\n\n{payload}"

    try:
        response = _call_provider(config.provider, model, DEDUP_SYSTEM_PROMPT, user_msg)
    except Exception as exc:
        print(f"[dedup] LLM call failed ({exc}), returning original findings", file=sys.stderr)
        return findings

    groups = response.get("groups", [])
    if not groups:
        return findings

    return _apply_groups(findings, groups)
