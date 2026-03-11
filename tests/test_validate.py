"""Tests for the validate module."""

from __future__ import annotations

from unittest.mock import patch

from noxaudit.config import DedupConfig
from noxaudit.models import Finding, Severity
from noxaudit.validate import (
    _build_validate_payload,
    validate_finding,
    validate_findings,
)


def _f(id: str = "abc", title: str = "test issue", file: str = "app.py") -> Finding:
    return Finding(
        id=id,
        severity=Severity.MEDIUM,
        file=file,
        line=10,
        title=title,
        description="desc",
        suggestion="fix it",
        focus="security",
    )


class TestBuildPayload:
    def test_includes_finding_and_source(self):
        finding = _f()
        payload = _build_validate_payload(finding, "print('hello')")
        assert "FINDING:" in payload
        assert "SOURCE CODE" in payload
        assert "app.py" in payload
        assert "test issue" in payload
        assert "print('hello')" in payload


class TestValidateFinding:
    def test_high_confidence(self):
        finding = _f()
        response = {"confidence": "high", "reason": "clearly a real issue"}
        with patch("noxaudit.validate._call_provider", return_value=response):
            result = validate_finding(finding, "code", "openai", "gpt-5-mini")
        assert result.confidence == "high"
        assert result.reason == "clearly a real issue"
        assert result.finding is finding

    def test_false_positive(self):
        finding = _f()
        response = {"confidence": "false_positive", "reason": "code is fine"}
        with patch("noxaudit.validate._call_provider", return_value=response):
            result = validate_finding(finding, "code", "openai", "gpt-5-mini")
        assert result.confidence == "false_positive"

    def test_error_returns_medium(self):
        finding = _f()
        with patch("noxaudit.validate._call_provider", side_effect=RuntimeError("boom")):
            result = validate_finding(finding, "code", "openai", "gpt-5-mini")
        assert result.confidence == "medium"

    def test_invalid_confidence_defaults_medium(self):
        finding = _f()
        response = {"confidence": "yolo", "reason": "weird"}
        with patch("noxaudit.validate._call_provider", return_value=response):
            result = validate_finding(finding, "code", "openai", "gpt-5-mini")
        assert result.confidence == "medium"

    def test_list_response_extracts_first(self):
        finding = _f()
        response = [{"confidence": "high", "reason": "real"}]
        with patch("noxaudit.validate._call_provider", return_value=response):
            result = validate_finding(finding, "code", "openai", "gpt-5-mini")
        assert result.confidence == "high"

    def test_non_dict_response_defaults_medium(self):
        finding = _f()
        with patch("noxaudit.validate._call_provider", return_value="garbage"):
            result = validate_finding(finding, "code", "openai", "gpt-5-mini")
        assert result.confidence == "medium"


class TestValidateFindings:
    def test_empty_returns_empty(self):
        config = DedupConfig(enabled=True, provider="openai", model="gpt-5-mini")
        result = validate_findings([], config)
        assert result == []

    def test_drops_false_positives(self, tmp_path):
        # Create a source file
        (tmp_path / "app.py").write_text("print('hello')")

        findings = [_f(id="a1", title="real issue"), _f(id="a2", title="fake issue")]
        responses = [
            {"confidence": "high", "reason": "real"},
            {"confidence": "false_positive", "reason": "not real"},
        ]
        config = DedupConfig(enabled=True, provider="openai", model="gpt-5-mini")

        with patch("noxaudit.validate._call_provider", side_effect=responses):
            result = validate_findings(
                findings, config, repo_path=str(tmp_path), drop_false_positives=True
            )

        assert len(result) == 1
        assert result[0].id == "a1"

    def test_min_confidence_medium(self, tmp_path):
        (tmp_path / "app.py").write_text("code")

        findings = [
            _f(id="a1", title="high"),
            _f(id="a2", title="low"),
            _f(id="a3", title="med"),
        ]
        responses = [
            {"confidence": "high", "reason": "yes"},
            {"confidence": "low", "reason": "meh"},
            {"confidence": "medium", "reason": "maybe"},
        ]
        config = DedupConfig(enabled=True, provider="openai", model="gpt-5-mini")

        with patch("noxaudit.validate._call_provider", side_effect=responses):
            result = validate_findings(
                findings, config, repo_path=str(tmp_path), min_confidence="medium"
            )

        assert len(result) == 2
        ids = [f.id for f in result]
        assert "a1" in ids
        assert "a3" in ids

    def test_missing_source_keeps_findings(self):
        findings = [_f(id="a1", file="nonexistent.py")]
        config = DedupConfig(enabled=True, provider="openai", model="gpt-5-mini")

        result = validate_findings(findings, config, repo_path="/tmp/empty")
        assert len(result) == 1

    def test_no_model_skips_validation(self):
        findings = [_f()]
        config = DedupConfig(enabled=True, provider="unknown", model="")
        result = validate_findings(findings, config)
        assert len(result) == 1

    def test_groups_by_file(self, tmp_path):
        (tmp_path / "a.py").write_text("code a")
        (tmp_path / "b.py").write_text("code b")

        findings = [
            _f(id="a1", file="a.py"),
            _f(id="a2", file="a.py"),
            _f(id="b1", file="b.py"),
        ]
        responses = [
            {"confidence": "high", "reason": "yes"},
            {"confidence": "high", "reason": "yes"},
            {"confidence": "high", "reason": "yes"},
        ]
        config = DedupConfig(enabled=True, provider="openai", model="gpt-5-mini")

        with patch("noxaudit.validate._call_provider", side_effect=responses):
            result = validate_findings(findings, config, repo_path=str(tmp_path))

        assert len(result) == 3
