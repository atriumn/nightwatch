"""Tests for confidence scoring module."""

from __future__ import annotations

import json

from noxaudit.confidence import (
    _finding_key,
    load_history,
    score_findings,
)
from noxaudit.models import Finding, Severity


def _f(title: str = "Test finding", file: str = "app.py", confidence: str | None = None):
    return Finding(
        id="test-id",
        severity=Severity.MEDIUM,
        file=file,
        line=1,
        title=title,
        description="desc",
        confidence=confidence,
    )


class TestFindingKey:
    def test_basic(self):
        f = _f(title="Missing Auth", file="auth.py")
        assert _finding_key(f) == "auth.py::missing auth"

    def test_case_insensitive(self):
        f1 = _f(title="Missing Auth")
        f2 = _f(title="missing auth")
        assert _finding_key(f1) == _finding_key(f2)


class TestLoadHistory:
    def test_no_file(self, tmp_path):
        result = load_history(tmp_path)
        assert result == []

    def test_single_run(self, tmp_path):
        history_path = tmp_path / ".noxaudit" / "findings-history.jsonl"
        history_path.parent.mkdir(parents=True)
        record = {
            "timestamp": "2026-03-13",
            "repo": "test",
            "focus": "all",
            "findings": [
                {"file": "app.py", "title": "Bug A"},
                {"file": "app.py", "title": "Bug B"},
            ],
        }
        history_path.write_text(json.dumps(record) + "\n")

        result = load_history(tmp_path)
        assert len(result) == 1
        assert "app.py::bug a" in result[0]
        assert "app.py::bug b" in result[0]

    def test_max_runs(self, tmp_path):
        history_path = tmp_path / ".noxaudit" / "findings-history.jsonl"
        history_path.parent.mkdir(parents=True)
        lines = []
        for i in range(20):
            record = {
                "findings": [{"file": "app.py", "title": f"Bug {i}"}],
            }
            lines.append(json.dumps(record))
        history_path.write_text("\n".join(lines) + "\n")

        result = load_history(tmp_path, max_runs=5)
        assert len(result) == 5
        # Should be the last 5
        assert "app.py::bug 15" in result[0]


class TestScoreFindings:
    def test_no_history_keeps_existing(self, tmp_path):
        findings = [_f(confidence="medium")]
        result = score_findings(findings, base_path=tmp_path)
        assert result[0].confidence == "medium"

    def test_no_history_no_confidence(self, tmp_path):
        findings = [_f()]
        result = score_findings(findings, base_path=tmp_path)
        assert result[0].confidence is None  # No history, no change

    def test_high_frequency_scores_high(self, tmp_path):
        history_path = tmp_path / ".noxaudit" / "findings-history.jsonl"
        history_path.parent.mkdir(parents=True)
        # Finding appears in 8 of 10 runs (80% > HIGH_THRESHOLD)
        lines = []
        for i in range(10):
            findings_data = []
            if i < 8:  # Present in first 8 runs
                findings_data.append({"file": "app.py", "title": "Bug A"})
            lines.append(json.dumps({"findings": findings_data}))
        history_path.write_text("\n".join(lines) + "\n")

        findings = [_f(title="Bug A", file="app.py")]
        result = score_findings(findings, base_path=tmp_path)
        assert result[0].confidence == "high"

    def test_medium_frequency_scores_medium(self, tmp_path):
        history_path = tmp_path / ".noxaudit" / "findings-history.jsonl"
        history_path.parent.mkdir(parents=True)
        # Finding appears in 4 of 10 runs (40% — between thresholds)
        lines = []
        for i in range(10):
            findings_data = []
            if i < 4:
                findings_data.append({"file": "app.py", "title": "Bug A"})
            lines.append(json.dumps({"findings": findings_data}))
        history_path.write_text("\n".join(lines) + "\n")

        findings = [_f(title="Bug A", file="app.py")]
        result = score_findings(findings, base_path=tmp_path)
        assert result[0].confidence == "medium"

    def test_low_frequency_scores_low(self, tmp_path):
        history_path = tmp_path / ".noxaudit" / "findings-history.jsonl"
        history_path.parent.mkdir(parents=True)
        # Finding appears in 1 of 10 runs (10% < MEDIUM_THRESHOLD)
        lines = []
        for i in range(10):
            findings_data = []
            if i == 0:
                findings_data.append({"file": "app.py", "title": "Bug A"})
            lines.append(json.dumps({"findings": findings_data}))
        history_path.write_text("\n".join(lines) + "\n")

        findings = [_f(title="Bug A", file="app.py")]
        result = score_findings(findings, base_path=tmp_path)
        assert result[0].confidence == "low"

    def test_never_seen_stays_low(self, tmp_path):
        history_path = tmp_path / ".noxaudit" / "findings-history.jsonl"
        history_path.parent.mkdir(parents=True)
        lines = []
        for _ in range(5):
            lines.append(json.dumps({"findings": [{"file": "other.py", "title": "Other"}]}))
        history_path.write_text("\n".join(lines) + "\n")

        findings = [_f(title="New Bug", file="app.py", confidence="low")]
        result = score_findings(findings, base_path=tmp_path)
        assert result[0].confidence == "low"

    def test_history_upgrades_but_never_downgrades(self, tmp_path):
        """If validation said high, history saying low shouldn't downgrade."""
        history_path = tmp_path / ".noxaudit" / "findings-history.jsonl"
        history_path.parent.mkdir(parents=True)
        # Finding appears in 1 of 10 runs — history would say "low"
        lines = []
        for i in range(10):
            findings_data = []
            if i == 0:
                findings_data.append({"file": "app.py", "title": "Bug A"})
            lines.append(json.dumps({"findings": findings_data}))
        history_path.write_text("\n".join(lines) + "\n")

        findings = [_f(title="Bug A", file="app.py", confidence="high")]
        result = score_findings(findings, base_path=tmp_path)
        assert result[0].confidence == "high"  # Not downgraded

    def test_history_upgrades_from_validation(self, tmp_path):
        """History can upgrade a medium validation to high."""
        history_path = tmp_path / ".noxaudit" / "findings-history.jsonl"
        history_path.parent.mkdir(parents=True)
        # Finding in 8/10 runs
        lines = []
        for i in range(10):
            findings_data = []
            if i < 8:
                findings_data.append({"file": "app.py", "title": "Bug A"})
            lines.append(json.dumps({"findings": findings_data}))
        history_path.write_text("\n".join(lines) + "\n")

        findings = [_f(title="Bug A", file="app.py", confidence="medium")]
        result = score_findings(findings, base_path=tmp_path)
        assert result[0].confidence == "high"  # Upgraded by history
