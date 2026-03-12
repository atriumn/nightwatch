"""Post-audit finding validation via LLM reasoning pass.

For each finding, sends the finding + actual source code to an LLM
and asks: "Is this real?" Drops false positives, tags the rest with
a confidence level.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from noxaudit.config import DedupConfig
from noxaudit.dedup import DEFAULT_DEDUP_MODELS, _call_provider
from noxaudit.models import Finding


VALIDATE_SYSTEM_PROMPT = """\
You are a code audit validator. You are given a finding from an automated \
audit and the actual source code of the file. Your job is to determine if \
the finding is real and useful.

Evaluate the finding against the actual code and classify it:
- "high": The finding is clearly correct and actionable. The code has this problem.
- "medium": The finding is plausible but may be minor or debatable.
- "low": The finding is technically true but not worth acting on (nitpick, style-only).
- "false_positive": The finding is wrong. The code does not have this problem, \
or the finding misunderstands the code.

Return JSON with this exact schema:
{
  "finding_id": "the finding's id",
  "confidence": "high|medium|low|false_positive",
  "reason": "one sentence explaining your verdict"
}"""


@dataclass
class ValidatedFinding:
    """A finding with a validation confidence level."""

    finding: Finding
    confidence: str  # high, medium, low, false_positive
    reason: str


def _build_validate_payload(finding: Finding, source_code: str) -> str:
    """Build the user message for validating a single finding."""
    finding_json = json.dumps(
        {
            "id": finding.id,
            "file": finding.file,
            "line": finding.line,
            "focus": finding.focus,
            "severity": finding.severity.value if finding.severity else None,
            "title": finding.title,
            "description": finding.description,
            "suggestion": finding.suggestion,
        },
        indent=2,
    )

    parts = [
        f"FINDING:\n{finding_json}",
        f"SOURCE CODE ({finding.file}):\n```\n{source_code}\n```",
    ]
    return "\n\n".join(parts)


def _read_source_file(file_path: str, repo_path: str) -> str | None:
    """Read source code for a finding's file."""
    full_path = Path(repo_path) / file_path
    if not full_path.exists() or not full_path.is_file():
        return None
    try:
        return full_path.read_text(errors="replace")
    except (PermissionError, OSError):
        return None


def validate_finding(
    finding: Finding,
    source_code: str,
    provider: str,
    model: str,
) -> ValidatedFinding:
    """Validate a single finding against its source code.

    Returns a ValidatedFinding with confidence and reason.
    On error, returns medium confidence (benefit of the doubt).
    """
    payload = _build_validate_payload(finding, source_code)

    try:
        response = _call_provider(provider, model, VALIDATE_SYSTEM_PROMPT, payload)
    except Exception as exc:
        print(f"[validate] LLM call failed for {finding.id} ({exc})", file=sys.stderr)
        return ValidatedFinding(finding=finding, confidence="medium", reason="validation failed")

    # _call_provider may return a list (batch of results) — take first dict
    if isinstance(response, list):
        response = response[0] if response and isinstance(response[0], dict) else {}

    if not isinstance(response, dict):
        return ValidatedFinding(
            finding=finding, confidence="medium", reason="unexpected response format"
        )

    confidence = response.get("confidence", "medium")
    if confidence not in ("high", "medium", "low", "false_positive"):
        confidence = "medium"

    reason = response.get("reason", "")
    return ValidatedFinding(finding=finding, confidence=confidence, reason=reason)


def validate_findings(
    findings: list[Finding],
    config: DedupConfig,
    repo_path: str = ".",
    drop_false_positives: bool = True,
    min_confidence: str | None = None,
) -> list[Finding]:
    """Validate all findings against their source code.

    Args:
        findings: Raw findings from the audit.
        config: Provider/model config (reuses DedupConfig for now).
        repo_path: Path to the repository root for reading source files.
        drop_false_positives: Remove findings classified as false positives.
        min_confidence: Minimum confidence to keep. None = keep all except
            false positives. "medium" = drop low. "high" = drop low + medium.

    Returns:
        Filtered list of findings that passed validation.
    """
    if not findings:
        return findings

    model = config.model or DEFAULT_DEDUP_MODELS.get(config.provider, "")
    if not model:
        print(f"[validate] No model for {config.provider}, skipping", file=sys.stderr)
        return findings

    confidence_rank = {"false_positive": 0, "low": 1, "medium": 2, "high": 3}
    min_rank = confidence_rank.get(min_confidence or "false_positive", 0)
    if drop_false_positives:
        min_rank = max(min_rank, 1)

    validated: list[Finding] = []
    dropped = 0

    # Group findings by file to avoid re-reading the same file
    by_file: dict[str, list[Finding]] = {}
    for f in findings:
        by_file.setdefault(f.file, []).append(f)

    for file_path, file_findings in by_file.items():
        source = _read_source_file(file_path, repo_path)
        if source is None:
            # Can't validate without source — keep the findings
            validated.extend(file_findings)
            continue

        for finding in file_findings:
            result = validate_finding(finding, source, config.provider, model)
            rank = confidence_rank.get(result.confidence, 2)

            if rank >= min_rank:
                validated.append(finding)
            else:
                dropped += 1
                print(
                    f"[validate] Dropped: {finding.file}:{finding.title} "
                    f"({result.confidence}: {result.reason})",
                    file=sys.stderr,
                )

    if dropped:
        print(
            f"[validate] {len(findings)} findings → {len(validated)} ({dropped} dropped)",
            file=sys.stderr,
        )

    return validated
