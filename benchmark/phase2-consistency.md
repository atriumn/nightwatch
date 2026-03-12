# Benchmark Phase 2 — Consistency Analysis

**Date**: 2026-03-11
**Design**: Top 4 models from Phase 1 × noxaudit × all 7 focus areas × 3 runs = 12 runs
**Cost**: ~$1.81 (new runs only; run1 reused from Phase 1)

## Methodology

Finding IDs are deterministic hashes of `focus:file:title:line`, but models produce
different title phrasings across runs for the same underlying issue. Raw ID overlap
is near-zero.

We measure consistency two ways:
- **Fuzzy Jaccard**: title similarity matching (SequenceMatcher ≥ 0.55) — measures
  whether models find the same issues regardless of how they phrase titles
- **Exact Jaccard**: finding ID match — measures whether IDs are stable enough to
  track findings across runs

## Baseline Consistency (Before Dedup)

| Model | Provider | Findings/run | Fuzzy Jaccard | Exact Jaccard |
|-------|----------|-------------|---------------|---------------|
| claude-opus-4-6 | anthropic | 49–54 | **0.357** | 0.003 |
| claude-sonnet-4-6 | anthropic | 39–48 | **0.204** | ~0 |
| gpt-5.4 | openai | 52–84 | **0.140** | ~0 |
| gpt-5-mini | openai | 20–24 | **0.125** | ~0 |

All models have near-zero exact Jaccard because title variation produces different hashes.

## After Dedup (Persistent Vocabulary)

Post-audit dedup normalizes titles to canonical forms via LLM reasoning (gpt-5-mini).
Vocabulary persists across runs so titles stabilize over time.

| Model | Before (fuzzy) | After (fuzzy) | After (exact) | Avg findings |
|-------|---------------|---------------|---------------|-------------|
| claude-opus-4-6 | 0.357 | **0.491** (+38%) | 0.134 | 51 |
| claude-sonnet-4-6 | 0.204 | **0.356** (+74%) | 0.290 | 42 |
| gpt-5.4 | 0.140 | **0.222** (+59%) | 0.038 | 68 |
| gpt-5-mini | 0.125 | **0.427** (+242%) | 0.065 | 21 |

Dedup improves consistency across all models. Sonnet has the best exact ID match
(0.290), meaning the vocabulary approach works especially well for its output style.

## Root Cause Analysis

Two independent problems reduce consistency:

1. **Title variation** — Models phrase the same finding differently across runs.
   Dedup addresses this by normalizing to canonical titles. Improvement: +38% to +242%.

2. **Output budget ceiling** — Models find ~50 of ~92 possible issues per run and
   stop. Different runs sample different subsets of the issue space. Even with perfect
   title normalization, overlap is limited by how much the subsets overlap.
   Chunked audits (splitting files into smaller batches) address this by ensuring
   each chunk gets thorough coverage.

## Per-Focus Finding Counts

| Model | Run | security | docs | patterns | testing | hygiene | deps | perf | Total |
|-------|-----|----------|------|----------|---------|---------|------|------|-------|
| claude-opus-4-6 | 1 | 4 | 14 | 15 | 7 | 4 | 4 | 3 | 51 |
| claude-opus-4-6 | 2 | 4 | 15 | 12 | 6 | 3 | 3 | 6 | 49 |
| claude-opus-4-6 | 3 | 5 | 18 | 15 | 5 | 4 | 3 | 4 | 54 |
| claude-sonnet-4-6 | 1 | 10 | 10 | 7 | 7 | 5 | 4 | 5 | 48 |
| claude-sonnet-4-6 | 2 | 11 | 8 | 5 | 5 | 3 | 4 | 3 | 39 |
| claude-sonnet-4-6 | 3 | 11 | 9 | 7 | 6 | 4 | 2 | 3 | 42 |
| gpt-5.4 | 1 | 3 | 22 | 14 | 5 | 5 | 1 | 2 | 52 |
| gpt-5.4 | 2 | 12 | 26 | 10 | 11 | 14 | 5 | 6 | 84 |
| gpt-5.4 | 3 | 4 | 32 | 12 | 7 | 11 | 4 | 1 | 71 |
| gpt-5-mini | 1 | 3 | 5 | 3 | 1 | 7 | 4 | 1 | 24 |
| gpt-5-mini | 2 | 6 | 4 | 3 | 0 | 2 | 2 | 2 | 20 |
| gpt-5-mini | 3 | 3 | 8 | 2 | 0 | 4 | 2 | 0 | 20 |

## Verdict

**Best overall**: claude-opus-4-6 — highest baseline consistency, best finding quality,
tightest count range (49–54). After dedup: 0.491 fuzzy Jaccard.

**Best value**: gpt-5-mini — cheapest model, lowest finding count but dedup brings
consistency from 0.125 to 0.427. Good for daily runs where cost matters.

**Most variable**: gpt-5.4 — highest finding count (52–84) but wildly inconsistent
even after dedup. Count variance of 46% makes it unreliable for production.

**Recommendations**:
- Use dedup (enabled by default) for all production runs
- Chunked audits available via `chunk_size` config for repos with many files
- Opus for premium/deep-dive tier, gpt-5-mini for daily tier
- GPT-5.4 not recommended despite high finding count due to instability
