"""Tests for post-audit finding deduplication."""

from __future__ import annotations

import json
from unittest.mock import patch

from noxaudit.config import DedupConfig
from noxaudit.dedup import (
    _apply_mappings,
    _build_dedup_payload,
    _load_vocab,
    _recompute_finding_id,
    _save_vocab,
    _vocab_key,
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


class TestVocab:
    def test_load_empty(self, tmp_path):
        assert _load_vocab(str(tmp_path / "missing.json")) == {}

    def test_save_and_load(self, tmp_path):
        path = str(tmp_path / "vocab.json")
        vocab = {"abc": {"file": "app.py", "focus": "security", "title": "SQL injection"}}
        _save_vocab(vocab, path)
        assert _load_vocab(path) == vocab

    def test_vocab_key_deterministic(self):
        k1 = _vocab_key("app.py", "security", "SQL injection")
        k2 = _vocab_key("app.py", "security", "SQL injection")
        assert k1 == k2

    def test_vocab_key_differs_by_file(self):
        k1 = _vocab_key("app.py", "security", "SQL injection")
        k2 = _vocab_key("api.py", "security", "SQL injection")
        assert k1 != k2


class TestBuildPayload:
    def test_includes_findings(self):
        findings = [_make_finding(id="a1", title="SQL injection")]
        payload = _build_dedup_payload(findings, {})
        assert "SQL injection" in payload
        assert "NEW FINDINGS" in payload

    def test_includes_vocab_when_present(self):
        vocab = {"k1": {"file": "app.py", "focus": "security", "title": "Known issue"}}
        payload = _build_dedup_payload([_make_finding()], vocab)
        assert "EXISTING VOCABULARY" in payload
        assert "Known issue" in payload

    def test_no_vocab_section_when_empty(self):
        payload = _build_dedup_payload([_make_finding()], {})
        assert "EXISTING VOCABULARY" not in payload


class TestRecomputeFindingId:
    def test_same_metadata_same_id(self):
        f1 = _make_finding(title="SQL injection", file="app.py", line=10, focus="security")
        f2 = _make_finding(title="SQL injection", file="app.py", line=10, focus="security")
        assert _recompute_finding_id(f1) == _recompute_finding_id(f2)

    def test_different_title_different_id(self):
        f1 = _make_finding(title="SQL injection")
        f2 = _make_finding(title="Command injection")
        assert _recompute_finding_id(f1) != _recompute_finding_id(f2)


class TestApplyMappings:
    def test_applies_canonical_title(self):
        f1 = _make_finding(id="a1", title="SQL injection in auth.py")
        f2 = _make_finding(id="b2", title="Unsanitized SQL query in auth.py")
        mappings = [
            {
                "finding_id": "a1",
                "vocab_key": None,
                "canonical_title": "SQL injection vulnerability",
            },
            {
                "finding_id": "b2",
                "vocab_key": None,
                "canonical_title": "SQL injection vulnerability",
            },
        ]
        result, vocab = _apply_mappings([f1, f2], mappings, {})
        # Same file+title+focus after normalization = collapsed to 1
        assert len(result) == 1
        assert result[0].title == "SQL injection vulnerability"

    def test_different_files_not_collapsed(self):
        f1 = _make_finding(id="a1", title="SQL injection", file="auth.py")
        f2 = _make_finding(id="b2", title="SQL injection", file="api.py")
        mappings = [
            {"finding_id": "a1", "canonical_title": "SQL injection"},
            {"finding_id": "b2", "canonical_title": "SQL injection"},
        ]
        result, _ = _apply_mappings([f1, f2], mappings, {})
        assert len(result) == 2

    def test_updates_vocab_with_new_entries(self):
        f1 = _make_finding(id="a1", title="New issue", file="app.py", focus="security")
        mappings = [{"finding_id": "a1", "canonical_title": "New issue"}]
        _, vocab = _apply_mappings([f1], mappings, {})
        assert len(vocab) == 1
        entry = list(vocab.values())[0]
        assert entry["title"] == "New issue"
        assert entry["file"] == "app.py"

    def test_preserves_existing_vocab(self):
        existing = {"k1": {"file": "old.py", "focus": "docs", "title": "Old issue"}}
        f1 = _make_finding(id="a1", title="New issue", file="app.py")
        mappings = [{"finding_id": "a1", "canonical_title": "New issue"}]
        _, vocab = _apply_mappings([f1], mappings, existing)
        assert "k1" in vocab
        assert len(vocab) >= 2

    def test_empty_mappings(self):
        f1 = _make_finding(id="a1")
        result, vocab = _apply_mappings([f1], [], {})
        # No mapping -> uses original title
        assert len(result) == 1
        assert result[0].title == f1.title


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
        assert len(result) == 2

    @patch("noxaudit.dedup._call_provider")
    def test_successful_dedup(self, mock_call, tmp_path):
        mock_call.return_value = {
            "mappings": [
                {"finding_id": "a1", "vocab_key": None, "canonical_title": "SQL injection"},
                {"finding_id": "b2", "vocab_key": None, "canonical_title": "SQL injection"},
            ]
        }
        config = DedupConfig(enabled=True, provider="openai", model="gpt-5-mini")
        f1 = _make_finding(id="a1", title="SQL injection in auth")
        f2 = _make_finding(id="b2", title="Unsanitized SQL in auth")
        vocab_path = str(tmp_path / "vocab.json")
        result = deduplicate_findings([f1, f2], config, vocab_path=vocab_path)
        assert len(result) == 1
        assert result[0].title == "SQL injection"
        mock_call.assert_called_once()
        # Vocab was persisted
        assert json.loads((tmp_path / "vocab.json").read_text())

    @patch("noxaudit.dedup._call_provider")
    def test_vocab_grows_across_calls(self, mock_call, tmp_path):
        vocab_path = str(tmp_path / "vocab.json")
        config = DedupConfig(enabled=True, provider="openai", model="gpt-5-mini")

        # First call: establishes vocab
        mock_call.return_value = {
            "mappings": [
                {"finding_id": "a1", "canonical_title": "Issue A"},
                {"finding_id": "b2", "canonical_title": "Issue B"},
            ]
        }
        f1 = _make_finding(id="a1", title="Issue A", file="a.py")
        f2 = _make_finding(id="b2", title="Issue B", file="b.py")
        deduplicate_findings([f1, f2], config, vocab_path=vocab_path)
        vocab1 = json.loads((tmp_path / "vocab.json").read_text())

        # Second call: new finding added to vocab
        mock_call.return_value = {
            "mappings": [
                {"finding_id": "c3", "canonical_title": "Issue C"},
                {"finding_id": "d4", "canonical_title": "Issue A"},  # maps to existing
            ]
        }
        f3 = _make_finding(id="c3", title="Issue C", file="c.py")
        f4 = _make_finding(id="d4", title="Variant of A", file="a.py")
        deduplicate_findings([f3, f4], config, vocab_path=vocab_path)
        vocab2 = json.loads((tmp_path / "vocab.json").read_text())

        assert len(vocab2) > len(vocab1)

    @patch("noxaudit.dedup._call_provider")
    def test_llm_error_returns_originals(self, mock_call):
        mock_call.side_effect = RuntimeError("API down")
        config = DedupConfig(enabled=True, provider="openai")
        findings = [_make_finding(id="a1"), _make_finding(id="b2", title="Other")]
        result = deduplicate_findings(findings, config)
        assert len(result) == 2
        assert result[0].id == "a1"

    @patch("noxaudit.dedup._call_provider")
    def test_empty_response_returns_originals(self, mock_call):
        mock_call.return_value = {}
        config = DedupConfig(enabled=True, provider="openai")
        findings = [_make_finding(id="a1"), _make_finding(id="b2", title="Other")]
        result = deduplicate_findings(findings, config)
        assert len(result) == 2
