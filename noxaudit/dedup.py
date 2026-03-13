"""Post-audit finding deduplication via LLM reasoning pass.

Uses a persistent vocabulary of canonical finding titles. On first run,
findings establish the vocabulary. On subsequent runs, findings are mapped
to existing canonical entries for stable IDs across runs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from noxaudit.config import DedupConfig
from noxaudit.models import Finding
from noxaudit.providers.base import BaseProvider

DEFAULT_DEDUP_MODELS: dict[str, str] = {
    "gemini": "gemini-3-flash-preview",
    "openai": "gpt-5-mini",
    "anthropic": "claude-haiku-3-5-20241022",
}

VOCAB_FILE = ".noxaudit/dedup-vocab.json"

DEDUP_SYSTEM_PROMPT = """\
You are a deduplication engine for code audit findings. You have a vocabulary \
of known canonical finding titles from previous runs. Your job is to map new \
findings to existing canonical entries where they describe the same issue.

A new finding matches an existing canonical entry if:
- Same file AND same underlying problem (even if worded differently)
- Same logical concern in nearby lines of the same file and focus area

A new finding does NOT match if:
- Different file (even if similar problem type)
- Same file but genuinely different problem

For each new finding, either:
1. Map it to an existing canonical entry by returning that entry's key
2. Mark it as "new" if no existing entry matches

Also group new findings among themselves if they describe the same issue, \
and pick a canonical title for each new group.

Return JSON with this exact schema:
{
  "mappings": [
    {
      "finding_id": "id of the new finding",
      "vocab_key": "key of the matching canonical entry, or null if new",
      "canonical_title": "title to use (existing vocab title if matched, new title if new)"
    }
  ]
}

Every input finding ID must appear exactly once. Do not invent findings or drop any."""


def _load_vocab(vocab_path: str = VOCAB_FILE) -> dict[str, dict]:
    """Load the canonical vocabulary from disk.

    Returns dict keyed by vocab_key (deterministic hash) with entries:
    {"file": str, "focus": str, "title": str}
    """
    path = Path(vocab_path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_vocab(vocab: dict[str, dict], vocab_path: str = VOCAB_FILE) -> None:
    """Persist the canonical vocabulary to disk."""
    path = Path(vocab_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(vocab, indent=2))


def _vocab_key(file: str, focus: str | None, title: str) -> str:
    """Generate a deterministic key for a vocab entry."""
    raw = {"file": file, "title": title, "line": "", "focus": focus}
    return BaseProvider.make_finding_id(raw)


def _build_dedup_payload(findings: list[Finding], vocab: dict[str, dict]) -> str:
    """Build the user message with vocabulary context and new findings."""
    parts = []

    if vocab:
        vocab_items = [
            {"key": k, "file": v["file"], "focus": v["focus"], "title": v["title"]}
            for k, v in vocab.items()
        ]
        parts.append(
            f"EXISTING VOCABULARY ({len(vocab_items)} entries):\n"
            + json.dumps(vocab_items, indent=None)
        )

    finding_items = [
        {
            "id": f.id,
            "file": f.file,
            "line": f.line,
            "focus": f.focus,
            "title": f.title,
            "description": f.description[:200],
        }
        for f in findings
    ]
    parts.append(
        f"NEW FINDINGS ({len(finding_items)} to classify):\n"
        + json.dumps(finding_items, indent=None)
    )

    return "\n\n".join(parts)


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


def _apply_mappings(
    findings: list[Finding],
    mappings: list[dict],
    vocab: dict[str, dict],
) -> tuple[list[Finding], dict[str, dict]]:
    """Apply canonical title mappings and update vocabulary.

    Returns (deduplicated_findings, updated_vocab).
    """
    findings_by_id = {f.id: f for f in findings}

    # Build mapping: finding_id -> canonical_title
    title_map: dict[str, str] = {}
    for m in mappings:
        fid = m.get("finding_id", "")
        title = m.get("canonical_title", "")
        if fid in findings_by_id and title:
            title_map[fid] = title

    # Apply canonical titles, recompute IDs, deduplicate
    result: list[Finding] = []
    seen_ids: set[str] = set()
    updated_vocab = dict(vocab)

    for f in findings:
        canonical_title = title_map.get(f.id, f.title)
        new_finding = Finding(
            id=f.id,
            severity=f.severity,
            file=f.file,
            line=f.line,
            title=canonical_title,
            description=f.description,
            suggestion=f.suggestion,
            focus=f.focus,
        )
        new_id = _recompute_finding_id(new_finding)
        if new_id in seen_ids:
            continue
        seen_ids.add(new_id)
        new_finding = Finding(
            id=new_id,
            severity=new_finding.severity,
            file=new_finding.file,
            line=new_finding.line,
            title=new_finding.title,
            description=new_finding.description,
            suggestion=new_finding.suggestion,
            focus=new_finding.focus,
        )
        result.append(new_finding)

        # Add to vocabulary if not already present
        vkey = _vocab_key(new_finding.file, new_finding.focus, canonical_title)
        if vkey not in updated_vocab:
            updated_vocab[vkey] = {
                "file": new_finding.file,
                "focus": new_finding.focus or "",
                "title": canonical_title,
            }

    return result, updated_vocab


def deduplicate_findings(
    findings: list[Finding],
    config: DedupConfig,
    vocab_path: str = VOCAB_FILE,
) -> list[Finding]:
    """Deduplicate findings using an LLM reasoning pass with persistent vocabulary.

    On first run, findings establish the vocabulary. On subsequent runs,
    findings are mapped to existing canonical entries for stable IDs.

    Falls back to returning original findings on any error.
    """
    if not config.enabled or len(findings) <= 1:
        return findings

    model = config.model or DEFAULT_DEDUP_MODELS.get(config.provider, "")
    if not model:
        print(f"[dedup] No model configured for {config.provider}, skipping", file=sys.stderr)
        return findings

    vocab = _load_vocab(vocab_path)
    payload = _build_dedup_payload(findings, vocab)

    try:
        response = _call_provider(config.provider, model, DEDUP_SYSTEM_PROMPT, payload)
    except Exception as exc:
        print(f"[dedup] LLM call failed ({exc}), returning original findings", file=sys.stderr)
        return findings

    # _call_provider may return a list — take first dict
    if isinstance(response, list):
        response = response[0] if response and isinstance(response[0], dict) else {}
    if not isinstance(response, dict):
        return findings

    mappings = response.get("mappings", [])
    if not mappings:
        return findings

    result, updated_vocab = _apply_mappings(findings, mappings, vocab)
    _save_vocab(updated_vocab, vocab_path)

    return result
