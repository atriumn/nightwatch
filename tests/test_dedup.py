"""Tests for post-audit finding deduplication."""

from __future__ import annotations

from unittest.mock import patch


from noxaudit.config import DedupConfig
from noxaudit.dedup import (
    _apply_groups,
    _build_dedup_payload,
    _recompute_finding_id,
    deduplicate_findings,
)
from noxaudit.models import Finding, Severity


def _make_finding(
    id: str = "abc123",
    title: str = "Test finding",
    file: str = "app.py",
    line: int = 10,
    focus: str = "security",
    severity: Severity = Severity.MEDIUM,
) -> Finding:
    return Finding(
        id=id,
        severity=severity,
        file=file,
        line=line,
        title=title,
        description="Some description",
        suggestion="Fix it",
        focus=focus,
    )


class TestBuildPayload:
    def test_serializes_findings(self):
        findings = [_make_finding(id="a1", title="SQL injection")]
        payload = _build_dedup_payload(findings)
        assert '"id": "a1"' in payload
        assert '"title": "SQL injection"' in payload

    def test_truncates_long_descriptions(self):
        f = _make_finding(id="a1")
        f = Finding(
            id=f.id,
            severity=f.severity,
            file=f.file,
            line=f.line,
            title=f.title,
            description="x" * 500,
            focus=f.focus,
        )
        payload = _build_dedup_payload([f])
        # Description should be truncated to 200 chars in payload
        import json

        items = json.loads(payload)
        assert len(items[0]["description"]) == 200


class TestRecomputeFindingId:
    def test_same_metadata_same_id(self):
        f1 = _make_finding(title="SQL injection", file="app.py", line=10, focus="security")
        f2 = _make_finding(title="SQL injection", file="app.py", line=10, focus="security")
        assert _recompute_finding_id(f1) == _recompute_finding_id(f2)

    def test_different_title_different_id(self):
        f1 = _make_finding(title="SQL injection")
        f2 = _make_finding(title="Command injection")
        assert _recompute_finding_id(f1) != _recompute_finding_id(f2)


class TestApplyGroups:
    def test_applies_canonical_title(self):
        f1 = _make_finding(id="a1", title="SQL injection in auth.py")
        f2 = _make_finding(id="b2", title="Unsanitized SQL query in auth.py")
        groups = [
            {
                "canonical_title": "SQL injection vulnerability",
                "finding_ids": ["a1", "b2"],
            }
        ]
        result = _apply_groups([f1, f2], groups)
        # Both get canonical title, but same file+title+line means dedup to 1
        assert len(result) == 1
        assert result[0].title == "SQL injection vulnerability"

    def test_different_files_not_collapsed(self):
        f1 = _make_finding(id="a1", title="SQL injection", file="auth.py")
        f2 = _make_finding(id="b2", title="SQL injection", file="api.py")
        groups = [
            {"canonical_title": "SQL injection", "finding_ids": ["a1"]},
            {"canonical_title": "SQL injection", "finding_ids": ["b2"]},
        ]
        result = _apply_groups([f1, f2], groups)
        assert len(result) == 2

    def test_singletons_preserved(self):
        f1 = _make_finding(id="a1", title="Unique issue")
        groups = [{"canonical_title": "Unique issue", "finding_ids": ["a1"]}]
        result = _apply_groups([f1], groups)
        assert len(result) == 1
        assert result[0].title == "Unique issue"

    def test_empty_groups_returns_originals(self):
        f1 = _make_finding(id="a1")
        result = _apply_groups([f1], [])
        assert len(result) == 1


class TestDeduplicateFindings:
    def test_disabled_returns_originals(self):
        config = DedupConfig(enabled=False)
        findings = [_make_finding()]
        result = deduplicate_findings(findings, config)
        assert result is findings

    def test_single_finding_returns_as_is(self):
        config = DedupConfig(enabled=True)
        findings = [_make_finding()]
        result = deduplicate_findings(findings, config)
        assert result is findings

    def test_empty_returns_empty(self):
        config = DedupConfig(enabled=True)
        result = deduplicate_findings([], config)
        assert result == []

    def test_unknown_provider_returns_originals(self):
        config = DedupConfig(enabled=True, provider="unknown")
        findings = [_make_finding(id="a1"), _make_finding(id="b2", title="Other")]
        result = deduplicate_findings(findings, config)
        # Falls back gracefully on ValueError from _call_provider
        assert len(result) == 2

    @patch("noxaudit.dedup._call_provider")
    def test_successful_dedup(self, mock_call):
        mock_call.return_value = {
            "groups": [
                {
                    "canonical_title": "SQL injection vulnerability",
                    "finding_ids": ["a1", "b2"],
                }
            ]
        }
        config = DedupConfig(enabled=True, provider="gemini", model="gemini-2.0-flash")
        f1 = _make_finding(id="a1", title="SQL injection in auth")
        f2 = _make_finding(id="b2", title="Unsanitized SQL in auth")
        result = deduplicate_findings([f1, f2], config)
        assert len(result) == 1
        assert result[0].title == "SQL injection vulnerability"
        mock_call.assert_called_once()

    @patch("noxaudit.dedup._call_provider")
    def test_llm_error_returns_originals(self, mock_call):
        mock_call.side_effect = RuntimeError("API down")
        config = DedupConfig(enabled=True, provider="gemini")
        findings = [_make_finding(id="a1"), _make_finding(id="b2", title="Other")]
        result = deduplicate_findings(findings, config)
        assert len(result) == 2
        assert result[0].id == "a1"

    @patch("noxaudit.dedup._call_provider")
    def test_empty_response_returns_originals(self, mock_call):
        mock_call.return_value = {}
        config = DedupConfig(enabled=True, provider="gemini")
        findings = [_make_finding(id="a1"), _make_finding(id="b2", title="Other")]
        result = deduplicate_findings(findings, config)
        assert len(result) == 2
