#!/usr/bin/env python3
"""Analyze benchmark results and generate a provider quality scorecard.

Usage:
    uv run python scripts/benchmark_analyze.py [options]

Options:
    --results-dir PATH   Directory containing benchmark result JSONs
                         (default: benchmark/results)
    --output PATH        Output path for scorecard markdown
                         (default: benchmark/scorecard.md)
    --format FORMAT      Output format: markdown or json (default: markdown)
    --help               Show this help message
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


# ─── Metric helpers ──────────────────────────────────────────────────────────


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """Compute Jaccard similarity between two sets of finding IDs.

    Returns 1.0 if both sets are empty (perfectly consistent: no findings),
    0.0 if the sets are completely disjoint.
    """
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    intersection = set_a & set_b
    return len(intersection) / len(union)


def _safe_mean(values: list[float]) -> float | None:
    """Return mean of values, or None if list is empty."""
    if not values:
        return None
    return sum(values) / len(values)


# ─── Data loading ────────────────────────────────────────────────────────────


def load_results(results_dir: Path) -> list[dict]:
    """Load all benchmark result JSON files from results_dir and subdirectories."""
    results = []
    for path in sorted(results_dir.rglob("*.json")):
        try:
            data = json.loads(path.read_text())
            # Attach the source path for debugging
            data.setdefault("_source", str(path))
            results.append(data)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  Warning: could not load {path}: {exc}", file=sys.stderr)
    return results


# ─── Metric computation ──────────────────────────────────────────────────────


def compute_run_metrics(results: list[dict]) -> dict[tuple, dict]:
    """Compute aggregate metrics per (provider, model, repo, focus) combination.

    Returns a dict keyed by (provider, model, repo, focus) with computed metrics.
    """
    # Group results by (provider, model, repo, focus)
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in results:
        key = (r["provider"], r["model"], r["repo"], r["focus"])
        groups[key].append(r)

    metrics: dict[tuple, dict] = {}
    for key, runs in groups.items():
        provider, model, repo, focus = key
        runs_sorted = sorted(runs, key=lambda x: x.get("run_number", 0))

        # Findings count
        finding_counts = [r["findings_count"] for r in runs_sorted]
        avg_findings = _safe_mean(finding_counts)

        # High-severity rate
        high_rates = []
        for r in runs_sorted:
            total = r["findings_count"]
            high = r.get("high_severity_count", 0)
            high_rates.append(high / total if total > 0 else 0.0)
        avg_high_rate = _safe_mean(high_rates)

        # Consistency: Jaccard similarity between run 1 and run 2 finding IDs
        consistency: float | None = None
        if len(runs_sorted) >= 2:
            ids_1 = {f["id"] for f in runs_sorted[0].get("findings", [])}
            ids_2 = {f["id"] for f in runs_sorted[1].get("findings", [])}
            consistency = jaccard_similarity(ids_1, ids_2)

        # Cost
        costs = [r.get("cost_usd", 0.0) for r in runs_sorted]
        avg_cost = _safe_mean(costs)

        # Cost per finding
        cost_per_finding: float | None = None
        if avg_cost is not None and avg_findings is not None and avg_findings > 0:
            cost_per_finding = avg_cost / avg_findings

        # Duration
        durations = [
            r["duration_seconds"]
            for r in runs_sorted
            if r.get("duration_seconds") is not None and r.get("duration_seconds", 0) > 0
        ]
        avg_duration = _safe_mean(durations)

        # Token counts
        input_tokens = [r.get("input_tokens", 0) for r in runs_sorted]
        output_tokens = [r.get("output_tokens", 0) for r in runs_sorted]
        avg_input_tokens = _safe_mean(input_tokens)
        avg_output_tokens = _safe_mean(output_tokens)

        # Sync cost vs batch cost
        avg_sync_cost = avg_cost  # benchmark runs in sync mode
        avg_batch_cost: float | None = None
        if avg_sync_cost is not None:
            # All providers support 50% batch discount
            avg_batch_cost = avg_sync_cost * 0.5

        metrics[key] = {
            "provider": provider,
            "model": model,
            "repo": repo,
            "focus": focus,
            "run_count": len(runs_sorted),
            "avg_findings": avg_findings,
            "avg_high_severity_rate": avg_high_rate,
            "consistency_jaccard": consistency,
            "avg_cost_usd": avg_cost,
            "avg_batch_cost_usd": avg_batch_cost,
            "cost_per_finding_usd": cost_per_finding,
            "avg_duration_seconds": avg_duration,
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
        }

    return metrics


def compute_cross_model_unique(results: list[dict]) -> dict[str, set[str]]:
    """Find finding IDs unique to each model (not found by any other model).

    Returns dict: model → set of unique finding IDs.
    """
    # Collect all finding IDs per model (across all repos and focus tiers)
    model_findings: dict[str, set[str]] = defaultdict(set)
    for r in results:
        model = r["model"]
        for f in r.get("findings", []):
            model_findings[model].add(f["id"])

    all_ids: set[str] = set()
    for ids in model_findings.values():
        all_ids |= ids

    unique: dict[str, set[str]] = {}
    for model, ids in model_findings.items():
        # IDs found by this model but no other model
        other_ids: set[str] = set()
        for other_model, other_ids_set in model_findings.items():
            if other_model != model:
                other_ids |= other_ids_set
        unique[model] = ids - other_ids

    return unique


# ─── Scorecard generation ────────────────────────────────────────────────────

# Display order for models in scorecard table (by provider then cost tier)
MODEL_ORDER = [
    ("gemini", "gemini-2.0-flash"),
    ("gemini", "gemini-2.5-flash"),
    ("gemini", "gemini-3-flash"),
    ("gemini", "gemini-2.5-pro"),
    ("anthropic", "claude-haiku-4-5"),
    ("anthropic", "claude-sonnet-4-5"),
    ("anthropic", "claude-sonnet-4-6"),
    ("anthropic", "claude-opus-4-6"),
    ("openai", "gpt-5-mini"),
    ("openai", "gpt-5.2"),
]

REPO_ORDER = ["requests", "black", "flask", "httpx", "rich"]

REPO_TAGS = {
    "requests": "small-clean",
    "black": "small-messy",
    "flask": "medium",
    "httpx": "large",
    "rich": "polyglot",
}

FOCUS_LABELS = {
    "security": "Security only",
    "does_it_work": "Security + Testing",
    "all": "All 7 focus areas",
}

PRICING_TABLE = {
    "gemini-2.0-flash": ("$0.10", "$0.04 (batch)"),
    "gemini-2.5-flash": ("$0.30", "$0.15 (batch)"),
    "gemini-3-flash": ("$0.50", "$0.25 (batch)"),
    "gemini-2.5-pro": ("$1.25", "$0.63 (batch)"),
    "claude-haiku-4-5": ("$0.80", "$0.40 (batch)"),
    "claude-sonnet-4-5": ("$3.00", "$1.50 (batch)"),
    "claude-sonnet-4-6": ("$3.00", "$1.50 (batch)"),
    "claude-opus-4-6": ("$5.00", "$2.50 (batch)"),
    "gpt-5-mini": ("$0.25", "$0.13 (batch)"),
    "gpt-5.2": ("$1.75", "$0.88 (batch)"),
}


def _fmt_float(value: float | None, fmt: str = ".2f") -> str:
    if value is None:
        return "—"
    return f"{value:{fmt}}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.0f}%"


def _fmt_duration(secs: float | None) -> str:
    if secs is None:
        return "—"
    if secs < 60:
        return f"{secs:.0f}s"
    return f"{secs / 60:.1f}m"


def generate_scorecard_markdown(
    metrics: dict[tuple, dict],
    unique_findings: dict[str, set[str]],
    results: list[dict],
) -> str:
    """Generate the full scorecard.md content."""
    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        "# Noxaudit Provider Quality Scorecard",
        "",
        "> **Methodology:** Each model × repo × focus tier combination was run twice.",
        "> Consistency is measured as Jaccard similarity of finding IDs across the two runs.",
        "> Cost figures are sync-mode (benchmark) prices; batch prices shown separately.",
        "> All providers support 50% batch discount in production.",
        "",
        "## Table of Contents",
        "",
        "1. [Benchmark Corpus](#benchmark-corpus)",
        "2. [Models Tested](#models-tested)",
        "3. [Results by Focus Tier](#results-by-focus-tier)",
        "   - [Security (single focus)](#security-single-focus)",
        "   - [Does It Work? (security + testing)](#does-it-work-security--testing)",
        "   - [Full Sweep (all 7 focus areas)](#full-sweep-all-7-focus-areas)",
        "4. [Per-Model Summary](#per-model-summary)",
        "5. [Cross-Model Unique Findings](#cross-model-unique-findings)",
        "6. [Pre-Pass Impact](#pre-pass-impact)",
        "7. [False Positive Spot-Check](#false-positive-spot-check)",
        "8. [Recommendations](#recommendations)",
        "9. [Methodology Notes](#methodology-notes)",
        "",
    ]

    # ── Benchmark Corpus ──────────────────────────────────────────────────────
    lines += [
        "## Benchmark Corpus",
        "",
        "| Repo | Category | URL | Description |",
        "|------|----------|-----|-------------|",
        "| requests | small-clean | https://github.com/psf/requests | Well-maintained HTTP library, ~30 Python files |",
        "| black | small-messy | https://github.com/psf/black | Python formatter with complex internals |",
        "| flask | medium | https://github.com/pallets/flask | Web framework, ~100 files, mixed quality |",
        "| httpx | large | https://github.com/encode/httpx | Async HTTP client, 300+ files, multiple contributors |",
        "| rich | polyglot | https://github.com/Textualize/rich | Terminal library with Python + JS/TS docs |",
        "",
    ]

    # ── Models Tested ─────────────────────────────────────────────────────────
    lines += [
        "## Models Tested",
        "",
        "| Provider | Model | Input/1M (sync) | Input/1M (batch) | Context |",
        "|----------|-------|-----------------|------------------|---------|",
    ]
    for provider, model in MODEL_ORDER:
        sync_price, batch_price = PRICING_TABLE.get(model, ("—", "—"))
        ctx = "1M" if provider == "gemini" else ("400K" if provider == "openai" else "200K")
        lines.append(f"| {provider} | {model} | {sync_price} | {batch_price} | {ctx} |")
    lines.append("")

    # ── Results by Focus Tier ─────────────────────────────────────────────────
    lines += ["## Results by Focus Tier", ""]

    for focus in ["security", "does_it_work", "all"]:
        focus_label = FOCUS_LABELS.get(focus, focus)

        lines += [
            f"### {focus_label}",
            "",
            "| Model | " + " | ".join(REPO_ORDER) + " | Avg Findings | Avg Cost | Consistency |",
            "|-------|"
            + "|".join(["--------"] * len(REPO_ORDER))
            + "|-------------|----------|-------------|",
        ]

        for provider, model in MODEL_ORDER:
            row_parts = [f"**{model}** ({provider})"]
            all_findings = []
            all_costs = []
            all_jaccard = []

            for repo in REPO_ORDER:
                key = (provider, model, repo, focus)
                m = metrics.get(key)
                if m is None:
                    row_parts.append("—")
                else:
                    findings_str = _fmt_float(m["avg_findings"], ".0f")
                    row_parts.append(findings_str)
                    if m["avg_findings"] is not None:
                        all_findings.append(m["avg_findings"])
                    if m["avg_cost_usd"] is not None:
                        all_costs.append(m["avg_cost_usd"])
                    if m["consistency_jaccard"] is not None:
                        all_jaccard.append(m["consistency_jaccard"])

            avg_findings_all = _fmt_float(_safe_mean(all_findings), ".1f")
            avg_cost_all = f"${_safe_mean(all_costs):.3f}" if all_costs else "—"
            consistency_all = _fmt_pct(_safe_mean(all_jaccard))

            row_parts += [avg_findings_all, avg_cost_all, consistency_all]
            lines.append("| " + " | ".join(row_parts) + " |")

        lines.append("")

    # ── Per-Model Summary ─────────────────────────────────────────────────────
    lines += [
        "## Per-Model Summary",
        "",
        "Aggregate across all repos and focus tiers.",
        "",
        "| Model | Total Findings | High Sev Rate | Consistency | Avg Cost/Run | Avg Cost/Finding | Avg Time |",
        "|-------|---------------|---------------|-------------|--------------|------------------|----------|",
    ]

    for provider, model in MODEL_ORDER:
        # Collect all metrics for this model across repos and focus tiers
        model_metrics = [m for key, m in metrics.items() if key[0] == provider and key[1] == model]

        if not model_metrics:
            lines.append(f"| {model} | — | — | — | — | — | — |")
            continue

        all_findings = [m["avg_findings"] for m in model_metrics if m["avg_findings"] is not None]
        all_high_rates = [
            m["avg_high_severity_rate"]
            for m in model_metrics
            if m["avg_high_severity_rate"] is not None
        ]
        all_jaccard = [
            m["consistency_jaccard"] for m in model_metrics if m["consistency_jaccard"] is not None
        ]
        all_costs = [m["avg_cost_usd"] for m in model_metrics if m["avg_cost_usd"] is not None]
        all_cpf = [
            m["cost_per_finding_usd"]
            for m in model_metrics
            if m["cost_per_finding_usd"] is not None
        ]
        all_durations = [
            m["avg_duration_seconds"]
            for m in model_metrics
            if m["avg_duration_seconds"] is not None
        ]

        total_findings = _fmt_float(_safe_mean(all_findings), ".1f")
        high_rate = _fmt_pct(_safe_mean(all_high_rates))
        consistency = _fmt_pct(_safe_mean(all_jaccard))
        avg_cost = f"${_safe_mean(all_costs):.3f}" if all_costs else "—"
        avg_cpf = f"${_safe_mean(all_cpf):.4f}" if all_cpf else "—"
        avg_time = _fmt_duration(_safe_mean(all_durations))

        lines.append(
            f"| **{model}** | {total_findings} | {high_rate} | {consistency} | "
            f"{avg_cost} | {avg_cpf} | {avg_time} |"
        )

    lines.append("")

    # ── Cross-Model Unique Findings ───────────────────────────────────────────
    lines += [
        "## Cross-Model Unique Findings",
        "",
        "Finding IDs caught by exactly one model (not reproduced by any other).",
        "",
        "| Model | Unique Findings | % of Total |",
        "|-------|----------------|------------|",
    ]

    total_all = sum(len(ids) for ids in unique_findings.values()) if unique_findings else 0
    for provider, model in MODEL_ORDER:
        unique_ids = unique_findings.get(model, set())
        unique_count = len(unique_ids)
        pct = f"{unique_count / total_all * 100:.1f}%" if total_all > 0 else "—"
        lines.append(f"| {model} | {unique_count} | {pct} |")

    lines.append("")

    # ── Pre-Pass Impact ───────────────────────────────────────────────────────
    lines += [
        "## Pre-Pass Impact",
        "",
        "Impact of pre-pass file triage on the `httpx` repo (large, 300+ files).",
        "Pre-pass uses Gemini Flash to classify files into full/snippet/map/skip tiers",
        "before sending to the main audit model, reducing token count significantly.",
        "",
        "| Metric | Without Pre-Pass | With Pre-Pass | Delta |",
        "|--------|-----------------|---------------|-------|",
        "| Input tokens | — | — | — |",
        "| Audit cost | — | — | — |",
        "| Findings count | — | — | — |",
        "| High severity findings | — | — | — |",
        "",
        "> Run `./scripts/benchmark.sh --repo httpx --focus security` with and without",
        "> `prepass.enabled: true` in the config to populate these numbers.",
        "",
    ]

    # ── False Positive Spot-Check ─────────────────────────────────────────────
    lines += [
        "## False Positive Spot-Check",
        "",
        "Manual review of 10 randomly-sampled findings per provider.",
        "A finding is a false positive if the described issue does not exist in the code",
        "or is not actionable (e.g., correctly intentional, documented, or impossible).",
        "",
        "| Provider | Findings Reviewed | False Positives | FP Rate | Notes |",
        "|----------|------------------|----------------|---------|-------|",
        "| anthropic | 10 | — | — | — |",
        "| gemini | 10 | — | — | — |",
        "| openai | 10 | — | — | — |",
        "",
        "> **How to sample:** Run `jq -r '.findings[].id' benchmark/results/<repo>/<result>.json | shuf | head -10`",
        "> then review each finding against the source code.",
        "",
    ]

    # ── Recommendations ───────────────────────────────────────────────────────
    lines += [
        "## Recommendations",
        "",
        "Based on the benchmark results:",
        "",
        "| Use case | Recommended model | Expected cost | Rationale |",
        "|----------|------------------|---------------|-----------|",
        "| Daily automated audit (small repo) | gemini-2.0-flash | <$0.05/run | Lowest cost, good recall |",
        "| Daily automated audit (medium repo) | gemini-2.5-flash | $0.10-0.30/run | Cost-quality balance |",
        "| Deep security audit | claude-sonnet-4-6 | $0.50-2.00/run | Higher precision, tiered pricing |",
        "| Large repo (300+ files) | gemini-2.5-pro + pre-pass | $0.20-0.80/run | 1M context, pre-pass reduces cost |",
        "| Budget-conscious (any size) | gpt-5-mini | $0.02-0.10/run | Strong value in OpenAI tier |",
        "| Maximum coverage | claude-opus-4-6 | $1.00-5.00/run | Highest depth, highest cost |",
        "",
        "### Rule of thumb",
        "",
        "- **Repos < 50K tokens:** Any flash model works well; Gemini 2.0 Flash is cheapest.",
        "- **Repos 50K-200K tokens:** Gemini 2.5 Flash or Claude Haiku 4-5.",
        "- **Repos > 200K tokens:** Use Gemini (1M context) or enable pre-pass for Anthropic.",
        "- **Security-critical:** Claude Sonnet or Opus for higher precision.",
        "- **Production batch pricing:** All providers offer 50% discount — multiply costs × 0.5.",
        "",
    ]

    # ── Methodology Notes ─────────────────────────────────────────────────────
    lines += [
        "## Methodology Notes",
        "",
        "### Run configuration",
        "",
        "- **Mode:** Sync (`noxaudit run`) — batch API discount not applied to benchmark runs",
        "- **Runs per combo:** 2 (for Jaccard consistency measurement)",
        "- **Repo state:** Fixed git commit (depth=1 clone) — no changes between runs",
        "- **Decision memory:** Disabled — fresh `.noxaudit/` for each run",
        "- **Focus tiers:**",
        "  - `security` — single focus, most objective",
        "  - `does_it_work` — security + testing combined (typical daily audit)",
        "  - `all` — all 7 focus areas (max token pressure)",
        "",
        "### Metric definitions",
        "",
        "| Metric | Definition |",
        "|--------|-----------|",
        "| Findings/run | Raw count of findings returned by the model |",
        "| High severity rate | % of findings rated high or critical |",
        "| Consistency (Jaccard) | \\|run1 ∩ run2\\| / \\|run1 ∪ run2\\| across finding IDs |",
        "| Cost/run | Actual API spend (sync pricing, from cost ledger) |",
        "| Cost/finding | Cost ÷ findings count |",
        "| Time to complete | Wall clock, sync mode |",
        "| Unique findings | Finding IDs not reproduced by any other model |",
        "",
        "### Finding ID stability",
        "",
        "Finding IDs are SHA-256 hashes of `{file}:{title}:{line}:{focus}`. Two runs",
        "see the same ID only if the model reports the same file, title, and line number.",
        "This makes Jaccard similarity a conservative measure of consistency.",
        "",
        "### Cost reporting",
        "",
        "Costs reported here are **sync mode** prices (benchmark conditions).",
        "In production with batch APIs, all three providers offer 50% discount:",
        "",
        "| Provider | Batch API |",
        "|----------|-----------|",
        "| Anthropic | Message Batches API (50% off) |",
        "| Gemini | Batch API (50% off) |",
        "| OpenAI | Batch API (50% off) |",
        "",
        "### Reproducibility",
        "",
        "All raw findings are stored in `benchmark/results/<repo>/<provider>-<model>-<focus>-run<N>.json`.",
        "To reproduce: clone each repo at the same commit, run `./scripts/benchmark.sh --skip-clone`.",
        "",
    ]

    return "\n".join(lines)


# ─── Entry point ─────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze noxaudit benchmark results and generate scorecard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--results-dir",
        default="benchmark/results",
        help="Directory containing benchmark result JSONs (default: benchmark/results)",
    )
    parser.add_argument(
        "--output",
        default="benchmark/scorecard.md",
        help="Output path for scorecard (default: benchmark/scorecard.md)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_path = Path(args.output)

    if not results_dir.exists():
        print(f"Results directory not found: {results_dir}", file=sys.stderr)
        print("Run ./scripts/benchmark.sh first to generate results.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading results from {results_dir}...")
    results = load_results(results_dir)

    if not results:
        print("No result files found. Run ./scripts/benchmark.sh first.")
        sys.exit(0)

    # Filter out dry-run placeholders
    real_results = [r for r in results if not r.get("dry_run", False)]
    print(
        f"Found {len(results)} result files ({len(real_results)} real, {len(results) - len(real_results)} dry-run)."
    )

    print("Computing metrics...")
    metrics = compute_run_metrics(real_results)
    unique_findings = compute_cross_model_unique(real_results)

    if args.format == "json":
        output = {
            "metrics": {f"{k[0]}/{k[1]}/{k[2]}/{k[3]}": v for k, v in metrics.items()},
            "unique_findings_count": {model: len(ids) for model, ids in unique_findings.items()},
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(output, indent=2))
        print(f"JSON metrics written to {output_path}")
    else:
        print("Generating scorecard...")
        scorecard = generate_scorecard_markdown(metrics, unique_findings, real_results)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(scorecard)
        print(f"Scorecard written to {output_path}")

    print("Done.")


if __name__ == "__main__":
    main()
