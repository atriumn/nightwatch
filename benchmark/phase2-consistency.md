# Benchmark Phase 2 — Consistency Analysis

**Date**: 2026-03-11
**Design**: Top 4 models from Phase 1 × noxaudit × all 7 focus areas × 3 runs = 12 runs
**Cost**: ~$1.81 (new runs only; run1 reused from Phase 1)

## Methodology

Finding IDs are non-deterministic (generated hashes), so consistency is measured
by fuzzy-matching findings on **file path + title similarity** (SequenceMatcher ≥ 0.55).
Jaccard similarity = |intersection| / |union| where intersection is the set of
matched finding pairs. Higher = more consistent.

## Overall Consistency

| Model | Provider | Run 1 | Run 2 | Run 3 | Mean Jaccard | Range |
|-------|----------|-------|-------|-------|-------------|-------|
| claude-opus-4-6 | anthropic | 51 | 49 | 54 | **0.351** | 49–54 |
| claude-sonnet-4-6 | anthropic | 48 | 39 | 42 | **0.188** | 39–48 |
| gpt-5.4 | openai | 52 | 84 | 71 | **0.137** | 52–84 |
| gpt-5-mini | openai | 24 | 20 | 20 | **0.135** | 20–24 |

## Per-Focus Consistency

| Model | security | docs | patterns | testing | hygiene | dependencies | performance |
|-------|---------|---------|---------|---------|---------|---------|---------|
| claude-opus-4-6 | 0.18 | 0.47 | 0.33 | 0.13 | 0.61 | 0.36 | 0.04 |
| claude-sonnet-4-6 | 0.34 | 0.20 | 0.15 | 0.13 | 0.00 | 0.07 | 0.25 |
| gpt-5.4 | 0.02 | 0.15 | 0.06 | 0.07 | 0.06 | 0.00 | 0.17 |
| gpt-5-mini | 0.07 | 0.17 | 0.00 | 0.33 | 0.00 | 0.24 | 0.00 |

## Per-Focus Finding Counts

| Model | Run | security | docs | patterns | testing | hygiene | dependencies | performance | Total |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-------|
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

## Noisy Focus Areas (Jaccard < 0.3)

| Model | Focus Area | Jaccard | Counts per run |
|-------|-----------|---------|---------------|
| claude-sonnet-4-6 | hygiene | 0.000 | [5, 3, 4] |
| gpt-5.4 | dependencies | 0.000 | [1, 5, 4] |
| gpt-5-mini | patterns | 0.000 | [3, 3, 2] |
| gpt-5-mini | hygiene | 0.000 | [7, 2, 4] |
| gpt-5-mini | performance | 0.000 | [1, 2, 0] |
| gpt-5.4 | security | 0.022 | [3, 12, 4] |
| claude-opus-4-6 | performance | 0.042 | [3, 6, 4] |
| gpt-5.4 | patterns | 0.061 | [14, 10, 12] |
| gpt-5.4 | hygiene | 0.064 | [5, 14, 11] |
| claude-sonnet-4-6 | dependencies | 0.067 | [4, 4, 2] |
| gpt-5.4 | testing | 0.067 | [5, 11, 7] |
| gpt-5-mini | security | 0.067 | [3, 6, 3] |
| claude-opus-4-6 | testing | 0.127 | [7, 6, 5] |
| claude-sonnet-4-6 | testing | 0.135 | [7, 5, 6] |
| gpt-5.4 | docs | 0.152 | [22, 26, 32] |
| claude-sonnet-4-6 | patterns | 0.153 | [7, 5, 7] |
| gpt-5.4 | performance | 0.167 | [2, 6, 1] |
| gpt-5-mini | docs | 0.169 | [5, 4, 8] |
| claude-opus-4-6 | security | 0.185 | [4, 4, 5] |
| claude-sonnet-4-6 | docs | 0.202 | [10, 8, 9] |
| gpt-5-mini | dependencies | 0.244 | [4, 2, 2] |
| claude-sonnet-4-6 | performance | 0.248 | [5, 3, 3] |

## Key Insight

All models show low run-to-run consistency. The finding **counts** are relatively
stable (Opus: 49–54, Sonnet: 39–48, gpt-5-mini: 20–24), but the **specific findings**
differ substantially between runs. Models identify the same *classes* of issues
(e.g., "old project name in docs") but phrase them differently and pick different
specific instances each time.

This has product implications:

1. **Decision memory keyed on finding ID will not work for deduplication** — IDs are
   non-deterministic and titles vary too much for exact matching.
2. **Multi-run consensus is valuable** — running 2-3 times and intersecting findings
   would surface the most reliable issues.
3. **Finding count is a better stability metric than finding identity** for evaluating
   model reliability.
4. **Prompt improvements could help** — more structured output format, deterministic
   finding ID generation (e.g., hash of file + line + category), or explicitly
   asking for canonical issue names.

## Verdict

- **claude-opus-4-6** (anthropic): Jaccard 0.351, 49–54 findings/run (10% count variance)
- **claude-sonnet-4-6** (anthropic): Jaccard 0.188, 39–48 findings/run (21% count variance)
- **gpt-5.4** (openai): Jaccard 0.137, 52–84 findings/run (46% count variance)
- **gpt-5-mini** (openai): Jaccard 0.135, 20–24 findings/run (19% count variance)

**Best consistency**: claude-opus-4-6 (Jaccard 0.35, tightest count range)

**Best count stability**: gpt-5-mini (20–24, ±9% variance) and claude-opus-4-6 (49–54, ±10%)

**Most variable**: gpt-5.4 (52–84, ±46% count variance, Jaccard 0.14)
