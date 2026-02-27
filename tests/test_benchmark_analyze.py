"""Tests for the benchmark analysis script (scripts/benchmark_analyze.py)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Add scripts/ to import path so we can import benchmark_analyze
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from benchmark_analyze import (  # noqa: E402
    compute_cross_model_unique,
    compute_run_metrics,
    generate_scorecard_markdown,
    jaccard_similarity,
    load_results,
)


# ─── jaccard_similarity ───────────────────────────────────────────────────────


class TestJaccardSimilarity:
    def test_identical_sets(self):
        ids = {"abc", "def", "ghi"}
        assert jaccard_similarity(ids, ids) == 1.0

    def test_disjoint_sets(self):
        a = {"abc", "def"}
        b = {"ghi", "jkl"}
        assert jaccard_similarity(a, b) == 0.0

    def test_partial_overlap(self):
        a = {"abc", "def", "ghi"}
        b = {"def", "ghi", "xyz"}
        # Intersection: {def, ghi} = 2, Union: {abc, def, ghi, xyz} = 4
        assert jaccard_similarity(a, b) == pytest.approx(2 / 4)

    def test_both_empty(self):
        # Two runs with no findings → perfectly consistent
        assert jaccard_similarity(set(), set()) == 1.0

    def test_one_empty(self):
        a = {"abc"}
        assert jaccard_similarity(a, set()) == 0.0
        assert jaccard_similarity(set(), a) == 0.0

    def test_single_element_match(self):
        assert jaccard_similarity({"abc"}, {"abc"}) == 1.0

    def test_single_element_no_match(self):
        assert jaccard_similarity({"abc"}, {"def"}) == 0.0


# ─── load_results ─────────────────────────────────────────────────────────────


class TestLoadResults:
    def test_loads_json_files(self, tmp_path):
        result = {
            "repo": "requests",
            "repo_tag": "small-clean",
            "provider": "anthropic",
            "model": "claude-haiku-4-5",
            "focus": "security",
            "run_number": 1,
            "timestamp": "2026-02-27T10:00:00Z",
            "duration_seconds": 30.0,
            "exit_code": 0,
            "dry_run": False,
            "findings_count": 5,
            "high_severity_count": 2,
            "medium_severity_count": 2,
            "low_severity_count": 1,
            "input_tokens": 10000,
            "output_tokens": 500,
            "cache_read_tokens": 0,
            "cost_usd": 0.005,
            "findings": [
                {
                    "id": "aaa111",
                    "severity": "high",
                    "file": "auth.py",
                    "line": 10,
                    "title": "SQL injection",
                    "description": "desc",
                },
                {
                    "id": "bbb222",
                    "severity": "medium",
                    "file": "api.py",
                    "line": 5,
                    "title": "Missing rate limit",
                    "description": "desc",
                },
            ],
        }
        (tmp_path / "run1.json").write_text(json.dumps(result))

        results = load_results(tmp_path)
        assert len(results) == 1
        assert results[0]["repo"] == "requests"
        assert results[0]["findings_count"] == 5

    def test_skips_invalid_json(self, tmp_path):
        (tmp_path / "bad.json").write_text("{invalid json{{")
        results = load_results(tmp_path)
        assert results == []

    def test_recurses_into_subdirs(self, tmp_path):
        subdir = tmp_path / "requests"
        subdir.mkdir()
        data = {
            "repo": "requests",
            "findings_count": 3,
            "provider": "gemini",
            "model": "gemini-2.0-flash",
            "focus": "security",
            "run_number": 1,
            "high_severity_count": 0,
            "medium_severity_count": 2,
            "low_severity_count": 1,
            "cost_usd": 0.001,
            "findings": [],
            "dry_run": False,
        }
        (subdir / "result.json").write_text(json.dumps(data))
        results = load_results(tmp_path)
        assert len(results) == 1

    def test_empty_dir(self, tmp_path):
        results = load_results(tmp_path)
        assert results == []


# ─── compute_run_metrics ──────────────────────────────────────────────────────


def _make_result(
    repo="requests",
    provider="anthropic",
    model="claude-haiku-4-5",
    focus="security",
    run_number=1,
    findings=None,
    cost_usd=0.01,
    duration_seconds=30.0,
):
    findings = findings or []
    return {
        "repo": repo,
        "repo_tag": "small-clean",
        "provider": provider,
        "model": model,
        "focus": focus,
        "run_number": run_number,
        "timestamp": "2026-02-27T10:00:00Z",
        "duration_seconds": duration_seconds,
        "exit_code": 0,
        "dry_run": False,
        "findings_count": len(findings),
        "high_severity_count": sum(1 for f in findings if f.get("severity") == "high"),
        "medium_severity_count": sum(1 for f in findings if f.get("severity") == "medium"),
        "low_severity_count": sum(1 for f in findings if f.get("severity") == "low"),
        "input_tokens": 10000,
        "output_tokens": 500,
        "cache_read_tokens": 0,
        "cost_usd": cost_usd,
        "findings": findings,
    }


class TestComputeRunMetrics:
    def test_single_run(self):
        findings = [
            {
                "id": "aaa",
                "severity": "high",
                "file": "f.py",
                "line": 1,
                "title": "T",
                "description": "D",
            },
        ]
        results = [_make_result(findings=findings)]
        metrics = compute_run_metrics(results)

        key = ("anthropic", "claude-haiku-4-5", "requests", "security")
        assert key in metrics
        m = metrics[key]
        assert m["avg_findings"] == 1.0
        assert m["avg_high_severity_rate"] == 1.0
        assert m["consistency_jaccard"] is None  # Only 1 run
        assert m["avg_cost_usd"] == pytest.approx(0.01)

    def test_two_identical_runs(self):
        findings = [
            {
                "id": "aaa",
                "severity": "high",
                "file": "f.py",
                "line": 1,
                "title": "T",
                "description": "D",
            },
            {
                "id": "bbb",
                "severity": "low",
                "file": "g.py",
                "line": 2,
                "title": "T2",
                "description": "D",
            },
        ]
        results = [
            _make_result(findings=findings, run_number=1),
            _make_result(findings=findings, run_number=2),
        ]
        metrics = compute_run_metrics(results)
        key = ("anthropic", "claude-haiku-4-5", "requests", "security")
        m = metrics[key]
        assert m["consistency_jaccard"] == pytest.approx(1.0)
        assert m["avg_findings"] == pytest.approx(2.0)

    def test_two_disjoint_runs(self):
        findings_1 = [
            {
                "id": "aaa",
                "severity": "high",
                "file": "f.py",
                "line": 1,
                "title": "T",
                "description": "D",
            },
        ]
        findings_2 = [
            {
                "id": "bbb",
                "severity": "high",
                "file": "g.py",
                "line": 2,
                "title": "T2",
                "description": "D",
            },
        ]
        results = [
            _make_result(findings=findings_1, run_number=1),
            _make_result(findings=findings_2, run_number=2),
        ]
        metrics = compute_run_metrics(results)
        key = ("anthropic", "claude-haiku-4-5", "requests", "security")
        m = metrics[key]
        assert m["consistency_jaccard"] == pytest.approx(0.0)

    def test_high_severity_rate_computed(self):
        findings = [
            {
                "id": "aaa",
                "severity": "high",
                "file": "f.py",
                "line": 1,
                "title": "T",
                "description": "D",
            },
            {
                "id": "bbb",
                "severity": "high",
                "file": "g.py",
                "line": 2,
                "title": "T2",
                "description": "D",
            },
            {
                "id": "ccc",
                "severity": "low",
                "file": "h.py",
                "line": 3,
                "title": "T3",
                "description": "D",
            },
        ]
        results = [_make_result(findings=findings)]
        metrics = compute_run_metrics(results)
        key = ("anthropic", "claude-haiku-4-5", "requests", "security")
        m = metrics[key]
        assert m["avg_high_severity_rate"] == pytest.approx(2 / 3)

    def test_cost_per_finding_computed(self):
        findings = [
            {
                "id": "aaa",
                "severity": "high",
                "file": "f.py",
                "line": 1,
                "title": "T",
                "description": "D",
            },
            {
                "id": "bbb",
                "severity": "low",
                "file": "g.py",
                "line": 2,
                "title": "T2",
                "description": "D",
            },
        ]
        results = [_make_result(findings=findings, cost_usd=0.10)]
        metrics = compute_run_metrics(results)
        key = ("anthropic", "claude-haiku-4-5", "requests", "security")
        m = metrics[key]
        assert m["cost_per_finding_usd"] == pytest.approx(0.05)

    def test_cost_per_finding_none_when_no_findings(self):
        results = [_make_result(findings=[], cost_usd=0.01)]
        metrics = compute_run_metrics(results)
        key = ("anthropic", "claude-haiku-4-5", "requests", "security")
        m = metrics[key]
        assert m["cost_per_finding_usd"] is None

    def test_groups_by_model_repo_focus(self):
        results = [
            _make_result(model="claude-haiku-4-5", repo="requests", focus="security", run_number=1),
            _make_result(
                model="gemini-2.0-flash",
                provider="gemini",
                repo="requests",
                focus="security",
                run_number=1,
            ),
            _make_result(model="claude-haiku-4-5", repo="flask", focus="security", run_number=1),
        ]
        metrics = compute_run_metrics(results)
        assert len(metrics) == 3

    def test_batch_cost_is_half_sync(self):
        results = [_make_result(cost_usd=0.10)]
        metrics = compute_run_metrics(results)
        key = ("anthropic", "claude-haiku-4-5", "requests", "security")
        m = metrics[key]
        assert m["avg_batch_cost_usd"] == pytest.approx(0.05)

    def test_zero_cost_run(self):
        results = [_make_result(cost_usd=0.0, findings=[])]
        metrics = compute_run_metrics(results)
        key = ("anthropic", "claude-haiku-4-5", "requests", "security")
        m = metrics[key]
        assert m["avg_cost_usd"] == pytest.approx(0.0)
        assert m["avg_batch_cost_usd"] == pytest.approx(0.0)


# ─── compute_cross_model_unique ──────────────────────────────────────────────


class TestComputeCrossModelUnique:
    def test_no_overlap(self):
        results = [
            _make_result(
                model="claude-haiku-4-5",
                findings=[
                    {
                        "id": "aaa",
                        "severity": "high",
                        "file": "f.py",
                        "line": 1,
                        "title": "T",
                        "description": "D",
                    }
                ],
            ),
            _make_result(
                model="gemini-2.0-flash",
                provider="gemini",
                findings=[
                    {
                        "id": "bbb",
                        "severity": "low",
                        "file": "g.py",
                        "line": 2,
                        "title": "T2",
                        "description": "D",
                    }
                ],
            ),
        ]
        unique = compute_cross_model_unique(results)
        assert "aaa" in unique["claude-haiku-4-5"]
        assert "bbb" in unique["gemini-2.0-flash"]

    def test_shared_finding_not_unique(self):
        shared_finding = {
            "id": "shared",
            "severity": "high",
            "file": "f.py",
            "line": 1,
            "title": "T",
            "description": "D",
        }
        unique_a = {
            "id": "only-a",
            "severity": "low",
            "file": "g.py",
            "line": 2,
            "title": "T2",
            "description": "D",
        }
        results = [
            _make_result(model="claude-haiku-4-5", findings=[shared_finding, unique_a]),
            _make_result(model="gemini-2.0-flash", provider="gemini", findings=[shared_finding]),
        ]
        unique = compute_cross_model_unique(results)
        assert "shared" not in unique.get("claude-haiku-4-5", set())
        assert "only-a" in unique.get("claude-haiku-4-5", set())

    def test_empty_results(self):
        unique = compute_cross_model_unique([])
        assert unique == {}


# ─── generate_scorecard_markdown ─────────────────────────────────────────────


class TestGenerateScorecardMarkdown:
    def test_generates_markdown_with_headers(self):
        results = [_make_result()]
        metrics = compute_run_metrics(results)
        unique = compute_cross_model_unique(results)
        md = generate_scorecard_markdown(metrics, unique, results)
        assert "# Noxaudit Provider Quality Scorecard" in md
        assert "## Benchmark Corpus" in md
        assert "## Models Tested" in md
        assert "## Recommendations" in md
        assert "## Methodology Notes" in md

    def test_contains_all_focus_tier_sections(self):
        results = [_make_result()]
        metrics = compute_run_metrics(results)
        unique = compute_cross_model_unique(results)
        md = generate_scorecard_markdown(metrics, unique, results)
        assert "Security (single focus)" in md
        assert "Does It Work?" in md
        assert "Full Sweep" in md

    def test_contains_model_names(self):
        results = [_make_result()]
        metrics = compute_run_metrics(results)
        unique = compute_cross_model_unique(results)
        md = generate_scorecard_markdown(metrics, unique, results)
        assert "gemini-2.0-flash" in md
        assert "claude-haiku-4-5" in md
        assert "gpt-5-mini" in md

    def test_empty_results_still_generates(self):
        md = generate_scorecard_markdown({}, {}, [])
        assert "# Noxaudit Provider Quality Scorecard" in md
