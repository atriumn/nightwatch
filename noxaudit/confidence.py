"""Confidence scoring based on cross-run finding frequency.

Reads findings-history.jsonl and scores each finding by how often it has
appeared across previous runs. Findings seen consistently are high
confidence; one-off findings are low confidence.
"""

from __future__ import annotations

import json
from pathlib import Path

from noxaudit.models import Finding

HISTORY_FILE = ".noxaudit/findings-history.jsonl"

# Thresholds: what fraction of recent runs must contain a finding
HIGH_THRESHOLD = 0.6  # Seen in 60%+ of runs
MEDIUM_THRESHOLD = 0.3  # Seen in 30%+ of runs
# Below MEDIUM_THRESHOLD = low


def _finding_key(finding: Finding) -> str:
    """Stable key for matching findings across runs.

    Uses file + title (lowercased) since dedup normalizes titles.
    """
    return f"{finding.file}::{finding.title.lower()}"


def load_history(base_path: str | Path = ".", max_runs: int = 10) -> list[set[str]]:
    """Load recent finding keys from history.

    Returns a list of sets, one per run, each containing finding keys.
    Most recent runs first, up to max_runs.
    """
    path = Path(base_path) / HISTORY_FILE
    if not path.exists():
        return []

    runs: list[set[str]] = []
    try:
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            keys = set()
            for f in record.get("findings", []):
                key = f"{f.get('file', '')}::{f.get('title', '').lower()}"
                keys.add(key)
            runs.append(keys)
    except (json.JSONDecodeError, OSError):
        return []

    # Return most recent runs (last N)
    return runs[-max_runs:]


def score_findings(
    findings: list[Finding],
    base_path: str | Path = ".",
    max_runs: int = 10,
) -> list[Finding]:
    """Score findings based on how often they appear in run history.

    Only upgrades confidence — if validation already set a confidence,
    history can promote it but won't demote it.

    Args:
        findings: Current run's findings (after validate + dedup).
        base_path: Repo root where .noxaudit/ lives.
        max_runs: How many recent runs to consider.

    Returns:
        The same findings list with confidence fields updated.
    """
    history = load_history(base_path, max_runs)

    if not history:
        # No history yet — first run. Keep existing confidence from validation.
        return findings

    num_runs = len(history)

    for finding in findings:
        key = _finding_key(finding)

        # Count how many historical runs contain this finding
        appearances = sum(1 for run_keys in history if key in run_keys)
        frequency = appearances / num_runs

        if frequency >= HIGH_THRESHOLD:
            history_confidence = "high"
        elif frequency >= MEDIUM_THRESHOLD:
            history_confidence = "medium"
        else:
            history_confidence = "low"

        # Merge: if no existing confidence, use history. Otherwise take the higher.
        confidence_rank = {"low": 1, "medium": 2, "high": 3}
        current_rank = confidence_rank.get(finding.confidence, 0)
        history_rank = confidence_rank.get(history_confidence, 1)

        if finding.confidence is None or history_rank > current_rank:
            finding.confidence = history_confidence

    return findings
