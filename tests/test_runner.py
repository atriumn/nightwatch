"""Tests for the runner module (no API calls)."""

from __future__ import annotations

import pytest

from noxaudit.config import NoxauditConfig, PrepassConfig, normalize_focus
from noxaudit.models import FileContent, Finding, Severity
from noxaudit.runner import (
    _chunk_files,
    _focus_label,
    _maybe_prepass,
    _merge_findings,
    _resolve_focus_names,
    estimate_tokens,
)


class TestFocusLabel:
    def test_single(self):
        assert _focus_label(["security"]) == "security"

    def test_multiple(self):
        assert _focus_label(["security", "performance"]) == "security+performance"

    def test_all(self):
        label = _focus_label(normalize_focus("all"))
        assert "+" in label
        assert "security" in label


class TestResolveFocusNames:
    def test_override_single(self):
        config = NoxauditConfig()
        names = _resolve_focus_names("security", config)
        assert names == ["security"]

    def test_override_comma_separated(self):
        config = NoxauditConfig()
        names = _resolve_focus_names("security,docs", config)
        assert names == ["security", "docs"]

    def test_override_all(self):
        config = NoxauditConfig()
        names = _resolve_focus_names("all", config)
        assert len(names) == 7

    def test_no_override_defaults_to_all(self):
        config = NoxauditConfig()
        names = _resolve_focus_names(None, config)
        assert len(names) == 7

    def test_off_returns_empty(self):
        config = NoxauditConfig()
        names = _resolve_focus_names("off", config)
        assert names == []

    def test_unknown_focus_raises(self):
        config = NoxauditConfig()
        with pytest.raises(ValueError, match="Unknown focus area"):
            _resolve_focus_names("nonexistent", config)

    def test_unknown_in_list_raises(self):
        config = NoxauditConfig()
        with pytest.raises(ValueError, match="Unknown focus area"):
            _resolve_focus_names("security,bogus", config)


class TestEstimateTokens:
    def test_empty_files(self):
        files = []
        assert estimate_tokens(files) == 0

    def test_single_file(self):
        files = [FileContent(path="test.py", content="a" * 4000)]
        assert estimate_tokens(files) == 1000

    def test_multiple_files(self):
        files = [
            FileContent(path="test.py", content="a" * 4000),
            FileContent(path="main.py", content="b" * 4000),
        ]
        assert estimate_tokens(files) == 2000


def _make_finding(id: str, title: str = "test") -> Finding:
    return Finding(
        id=id,
        severity=Severity.MEDIUM,
        file="test.py",
        line=1,
        title=title,
        description="desc",
        suggestion="fix",
        focus="security",
    )


class TestChunkFiles:
    def test_no_chunking_when_zero(self):
        files = [FileContent(path=f"f{i}.py", content="x") for i in range(10)]
        chunks = _chunk_files(files, 0)
        assert len(chunks) == 1
        assert len(chunks[0]) == 10

    def test_no_chunking_when_fewer_than_chunk_size(self):
        files = [FileContent(path=f"f{i}.py", content="x") for i in range(5)]
        chunks = _chunk_files(files, 10)
        assert len(chunks) == 1

    def test_even_split(self):
        files = [FileContent(path=f"f{i}.py", content="x") for i in range(20)]
        chunks = _chunk_files(files, 10)
        assert len(chunks) == 2
        assert len(chunks[0]) == 10
        assert len(chunks[1]) == 10

    def test_uneven_split(self):
        files = [FileContent(path=f"f{i}.py", content="x") for i in range(15)]
        chunks = _chunk_files(files, 10)
        assert len(chunks) == 2
        assert len(chunks[0]) == 10
        assert len(chunks[1]) == 5

    def test_all_files_preserved(self):
        files = [FileContent(path=f"f{i}.py", content="x") for i in range(23)]
        chunks = _chunk_files(files, 7)
        all_paths = [f.path for chunk in chunks for f in chunk]
        assert len(all_paths) == 23
        assert len(set(all_paths)) == 23


class TestMergeFindings:
    def test_no_duplicates(self):
        chunks = [
            [_make_finding("a1"), _make_finding("a2")],
            [_make_finding("b1"), _make_finding("b2")],
        ]
        merged = _merge_findings(chunks)
        assert len(merged) == 4

    def test_deduplicates_by_id(self):
        chunks = [
            [_make_finding("a1"), _make_finding("shared")],
            [_make_finding("b1"), _make_finding("shared")],
        ]
        merged = _merge_findings(chunks)
        assert len(merged) == 3
        ids = [f.id for f in merged]
        assert ids.count("shared") == 1

    def test_empty_chunks(self):
        chunks = [[], [_make_finding("a1")], []]
        merged = _merge_findings(chunks)
        assert len(merged) == 1


class TestMaybePrepass:
    def test_explicit_enabled_with_high_tokens(self):
        """Explicit prepass.enabled=True with tokens > threshold should enable pre-pass."""
        config = NoxauditConfig(
            model="claude-opus-4-6",
            prepass=PrepassConfig(enabled=True, threshold_tokens=600_000),
        )
        files = [FileContent(path="test.py", content="a" * 2_401_000)]  # >600K tokens
        should_run, returned_files, msg = _maybe_prepass(
            files, ["security"], config, "test-repo", "anthropic"
        )
        assert should_run is True
        assert returned_files == files
        assert msg == ""

    def test_explicit_enabled_with_low_tokens(self):
        """Explicit prepass.enabled=True but tokens < threshold should NOT enable."""
        config = NoxauditConfig(
            model="claude-opus-4-6",
            prepass=PrepassConfig(enabled=True, threshold_tokens=600_000),
        )
        files = [FileContent(path="test.py", content="a" * 100_000)]  # 25K tokens
        should_run, returned_files, msg = _maybe_prepass(
            files, ["security"], config, "test-repo", "anthropic"
        )
        assert should_run is False
        assert msg == ""

    def test_anthropic_auto_enable_above_tier_threshold(self):
        """Anthropic with >200K tokens should auto-enable when auto_disable=False."""
        config = NoxauditConfig(
            model="claude-opus-4-6",
            prepass=PrepassConfig(auto_disable=False),
        )
        files = [FileContent(path="test.py", content="a" * 1_000_000)]  # 250K tokens
        should_run, returned_files, msg = _maybe_prepass(
            files, ["security"], config, "test-repo", "anthropic"
        )
        assert should_run is True
        assert "Auto-enabling pre-pass" in msg
        assert "250K tokens" in msg
        assert "tiered pricing" in msg

    def test_gemini_no_auto_enable(self):
        """Gemini with high tokens should NOT auto-enable (flat pricing, no tier_threshold)."""
        config = NoxauditConfig(
            model="gemini-2.5-flash",
            prepass=PrepassConfig(auto_disable=False),
        )
        files = [FileContent(path="test.py", content="a" * 1_000_000)]  # 250K tokens
        should_run, returned_files, msg = _maybe_prepass(
            files, ["security"], config, "test-repo", "gemini"
        )
        assert should_run is False
        assert msg == ""

    def test_anthropic_auto_disable_config(self):
        """prepass.auto_disable=True should suppress auto-enable."""
        config = NoxauditConfig(
            model="claude-opus-4-6",
            prepass=PrepassConfig(auto_disable=True),
        )
        files = [FileContent(path="test.py", content="a" * 1_000_000)]  # 250K tokens
        should_run, returned_files, msg = _maybe_prepass(
            files, ["security"], config, "test-repo", "anthropic"
        )
        assert should_run is False
        assert msg == ""

    def test_anthropic_below_tier_threshold(self):
        """Anthropic with <200K tokens should NOT auto-enable."""
        config = NoxauditConfig(
            model="claude-opus-4-6",
            prepass=PrepassConfig(auto_disable=False),
        )
        files = [FileContent(path="test.py", content="a" * 600_000)]  # 150K tokens
        should_run, returned_files, msg = _maybe_prepass(
            files, ["security"], config, "test-repo", "anthropic"
        )
        assert should_run is False
        assert msg == ""
