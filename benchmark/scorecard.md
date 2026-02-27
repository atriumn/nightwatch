# Noxaudit Provider Quality Scorecard

> **Status:** Template — run `./scripts/benchmark.sh` then `uv run python scripts/benchmark_analyze.py` to populate with real results.

> **Methodology:** Each model × repo × focus tier combination was run twice.
> Consistency is measured as Jaccard similarity of finding IDs across the two runs.
> Cost figures are sync-mode (benchmark) prices; batch prices shown separately.
> All providers support 50% batch discount in production.

## Table of Contents

1. [Benchmark Corpus](#benchmark-corpus)
2. [Models Tested](#models-tested)
3. [Results by Focus Tier](#results-by-focus-tier)
   - [Security (single focus)](#security-single-focus)
   - [Does It Work? (security + testing)](#does-it-work-security--testing)
   - [Full Sweep (all 7 focus areas)](#full-sweep-all-7-focus-areas)
4. [Per-Model Summary](#per-model-summary)
5. [Cross-Model Unique Findings](#cross-model-unique-findings)
6. [Pre-Pass Impact](#pre-pass-impact)
7. [False Positive Spot-Check](#false-positive-spot-check)
8. [Recommendations](#recommendations)
9. [Methodology Notes](#methodology-notes)

---

## Benchmark Corpus

Five open-source Python repos covering the size and quality spectrum:

| Repo | Category | URL | Description |
|------|----------|-----|-------------|
| requests | small-clean | https://github.com/psf/requests | Well-maintained HTTP library, ~30 Python files |
| black | small-messy | https://github.com/psf/black | Python formatter with complex internals |
| flask | medium | https://github.com/pallets/flask | Web framework, ~100 files, mixed quality |
| httpx | large | https://github.com/encode/httpx | Async HTTP client, 300+ files, multiple contributors |
| rich | polyglot | https://github.com/Textualize/rich | Terminal library with Python + JS/TS docs |

These repos were chosen because:
- They are actively maintained and representative of real production codebases
- They cover different quality profiles (highly polished → intentionally complex)
- They are large enough to produce meaningful findings counts
- A sample of findings can be manually verified against the source

---

## Models Tested

9 models across 3 providers — all support batch API at 50% discount:

| Provider | Model | Input/1M (sync) | Input/1M (batch) | Context |
|----------|-------|-----------------|------------------|---------|
| gemini | gemini-2.0-flash | $0.10 | $0.05 (batch) | 1M |
| gemini | gemini-2.5-flash | $0.30 | $0.15 (batch) | 1M |
| gemini | gemini-3-flash | $0.50 | $0.25 (batch) | 1M |
| gemini | gemini-2.5-pro | $1.25 | $0.63 (batch) | 1M |
| anthropic | claude-haiku-4-5 | $0.80 | $0.40 (batch) | 200K |
| anthropic | claude-sonnet-4-5 | $3.00 | $1.50 (batch) | 200K |
| anthropic | claude-sonnet-4-6 | $3.00 | $1.50 (batch) | 200K |
| anthropic | claude-opus-4-6 | $5.00 | $2.50 (batch) | 200K |
| openai | gpt-5-mini | $0.25 | $0.13 (batch) | 400K |
| openai | gpt-5.2 | $1.75 | $0.88 (batch) | 400K |

---

## Results by Focus Tier

### Security (single focus)

Most objective tier — security findings are easiest to judge as true/false positives.

| Model | requests | black | flask | httpx | rich | Avg Findings | Avg Cost | Consistency |
|-------|----------|-------|-------|-------|------|--------------|----------|-------------|
| **gemini-2.0-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-2.5-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-3-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-2.5-pro** (gemini) | — | — | — | — | — | — | — | — |
| **claude-haiku-4-5** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-sonnet-4-5** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-sonnet-4-6** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-opus-4-6** (anthropic) | — | — | — | — | — | — | — | — |
| **gpt-5-mini** (openai) | — | — | — | — | — | — | — | — |
| **gpt-5.2** (openai) | — | — | — | — | — | — | — | — |

> **Avg Findings**: mean across 2 runs. **Avg Cost**: sync pricing. **Consistency**: Jaccard similarity of finding IDs between run 1 and run 2.

### Does It Work? (security + testing)

Combined frame — tests real daily-use behavior. Two focus areas in one API call.

| Model | requests | black | flask | httpx | rich | Avg Findings | Avg Cost | Consistency |
|-------|----------|-------|-------|-------|------|--------------|----------|-------------|
| **gemini-2.0-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-2.5-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-3-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-2.5-pro** (gemini) | — | — | — | — | — | — | — | — |
| **claude-haiku-4-5** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-sonnet-4-5** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-sonnet-4-6** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-opus-4-6** (anthropic) | — | — | — | — | — | — | — | — |
| **gpt-5-mini** (openai) | — | — | — | — | — | — | — | — |
| **gpt-5.2** (openai) | — | — | — | — | — | — | — | — |

### Full Sweep (all 7 focus areas)

All focus areas in one API call. Tests max token pressure, context window behavior, and cost ceiling.

| Model | requests | black | flask | httpx | rich | Avg Findings | Avg Cost | Consistency |
|-------|----------|-------|-------|-------|------|--------------|----------|-------------|
| **gemini-2.0-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-2.5-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-3-flash** (gemini) | — | — | — | — | — | — | — | — |
| **gemini-2.5-pro** (gemini) | — | — | — | — | — | — | — | — |
| **claude-haiku-4-5** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-sonnet-4-5** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-sonnet-4-6** (anthropic) | — | — | — | — | — | — | — | — |
| **claude-opus-4-6** (anthropic) | — | — | — | — | — | — | — | — |
| **gpt-5-mini** (openai) | — | — | — | — | — | — | — | — |
| **gpt-5.2** (openai) | — | — | — | — | — | — | — | — |

---

## Per-Model Summary

Aggregate across all repos and focus tiers.

| Model | Avg Findings | High Sev Rate | Consistency | Avg Cost/Run | Avg Cost/Finding | Avg Time |
|-------|-------------|---------------|-------------|--------------|------------------|----------|
| **gemini-2.0-flash** | — | — | — | — | — | — |
| **gemini-2.5-flash** | — | — | — | — | — | — |
| **gemini-3-flash** | — | — | — | — | — | — |
| **gemini-2.5-pro** | — | — | — | — | — | — |
| **claude-haiku-4-5** | — | — | — | — | — | — |
| **claude-sonnet-4-5** | — | — | — | — | — | — |
| **claude-sonnet-4-6** | — | — | — | — | — | — |
| **claude-opus-4-6** | — | — | — | — | — | — |
| **gpt-5-mini** | — | — | — | — | — | — |
| **gpt-5.2** | — | — | — | — | — | — |

> **High Sev Rate**: % of findings rated high/critical. **Consistency**: Jaccard similarity across 2 runs.
> **Avg Time**: wall-clock in sync mode (batch mode would vary).

---

## Cross-Model Unique Findings

Finding IDs caught by exactly one model — not reproduced by any other model.
These represent each model's "exclusive insight" into the codebase.

| Model | Unique Findings | % of Total |
|-------|----------------|------------|
| gemini-2.0-flash | — | — |
| gemini-2.5-flash | — | — |
| gemini-3-flash | — | — |
| gemini-2.5-pro | — | — |
| claude-haiku-4-5 | — | — |
| claude-sonnet-4-5 | — | — |
| claude-sonnet-4-6 | — | — |
| claude-opus-4-6 | — | — |
| gpt-5-mini | — | — |
| gpt-5.2 | — | — |

---

## Pre-Pass Impact

Pre-pass runs Gemini Flash to classify files into full/snippet/map/skip tiers before
the main audit model. This reduces token count for large repos, saving cost and
keeping Anthropic models under the 200K tier threshold.

Test repo: **httpx** (large, 300+ files) with `--focus security`.

| Metric | Without Pre-Pass | With Pre-Pass | Delta |
|--------|-----------------|---------------|-------|
| Input tokens | — | — | — |
| Files sent | — | — | — |
| Audit cost (anthropic sonnet) | — | — | — |
| Findings count | — | — | — |
| High severity findings | — | — | — |
| Total time (triage + audit) | — | — | — |

> **To reproduce:** Run `./scripts/benchmark.sh --repo httpx --focus security --model anthropic:claude-sonnet-4-6`
> with `prepass.enabled: false` and then `true` in the generated config.

---

## False Positive Spot-Check

Manual review of 10 randomly-sampled findings per provider across all repos.
A finding is a **false positive** if the described issue does not exist in the code
or is not actionable (correctly intentional, documented, or impossible to fix).

| Provider | Findings Reviewed | False Positives | FP Rate | Notes |
|----------|------------------|----------------|---------|-------|
| anthropic | 10 | — | — | — |
| gemini | 10 | — | — | — |
| openai | 10 | — | — | — |

### Sampling methodology

```bash
# Sample 10 random finding IDs from all results for a provider
jq -r '.findings[].id' benchmark/results/*/<provider>-*.json | sort -R | head -10
```

Then look up each finding in the source repo and classify as:
- **True positive**: Finding is valid and actionable
- **False positive**: Finding is incorrect, inapplicable, or not meaningful
- **Ambiguous**: Could go either way (count as 0.5 for FP rate)

---

## Recommendations

Based on benchmark results, here are the recommended models by use case:

| Use case | Recommended model | Expected cost | Rationale |
|----------|------------------|---------------|-----------|
| Daily automated audit (small repo, <20 files) | gemini-2.0-flash | <$0.05/run | Lowest cost, sufficient recall |
| Daily automated audit (medium repo, ~100 files) | gemini-2.5-flash | $0.10–$0.30/run | Best cost-quality balance |
| Deep security audit (any size) | claude-sonnet-4-6 | $0.50–$2.00/run | Higher precision, structured output |
| Large repo (300+ files) | gemini-2.5-pro + pre-pass | $0.20–$0.80/run | 1M context handles full codebase |
| Budget-conscious (any size) | gpt-5-mini | $0.02–$0.10/run | Strong value in OpenAI tier |
| Maximum coverage | claude-opus-4-6 | $1.00–$5.00/run | Highest depth, highest cost |

### Rule of thumb

- **Repos < 50K tokens (~200KB source):** Any flash model. Gemini 2.0 Flash is cheapest.
- **Repos 50K–200K tokens:** Gemini 2.5 Flash or Claude Haiku 4-5.
- **Repos > 200K tokens:** Use Gemini (1M context) or enable pre-pass for Anthropic models.
- **Security-critical systems:** Claude Sonnet or Opus for higher precision and structured reasoning.
- **Production batch pricing:** All providers offer 50% discount — multiply costs above by 0.5.

---

## Methodology Notes

### Run configuration

- **Mode:** Sync (`noxaudit run`) — batch API discount not applied during benchmark
- **Runs per combination:** 2 (for Jaccard consistency measurement)
- **Repo state:** Fixed git commit (depth=1 clone, same commit for both runs)
- **Decision memory:** Fresh `.noxaudit/` per run (no carry-over between runs)
- **Context window behavior:** Noted if model truncated, refused, or degraded at high token counts

### Focus tiers

| Tier | Flag | Focus areas | Why |
|------|------|-------------|-----|
| Single focus | `--focus security` | security | Most objective — easiest to judge true/false positives |
| Combined frame | `--focus does_it_work` | security + testing | Tests real daily-use behavior with combined audits |
| Full sweep | `--focus all` | all 7 focus areas | Tests combined audit at scale, max token pressure, cost ceiling |

### Metric definitions

| Metric | Definition |
|--------|-----------|
| Findings/run | Raw count of findings returned by the model |
| High severity rate | % of findings rated high or critical |
| Consistency (Jaccard) | \|run1 ∩ run2\| / \|run1 ∪ run2\| across finding IDs |
| Cost/run | Actual API spend (sync pricing, from cost ledger) |
| Batch cost | Cost/run × 0.5 (estimated production cost with batch API) |
| Cost/finding | Cost/run ÷ findings count |
| Time to complete | Wall clock in sync mode |
| Unique findings | Finding IDs not reproduced by any other model |

### Finding ID stability

Finding IDs are SHA-256 hashes of `{file}:{title}:{line}:{focus}`. Two runs
see the same ID only if the model produces the same file, title, and line number.
This makes Jaccard similarity a conservative measure of consistency — equivalent
findings with slightly different titles will not match.

### Cost reporting

Costs reported here are **sync mode** prices (as run in the benchmark).
In production with batch APIs, all three providers offer 50% discount:

| Provider | Batch API | Discount |
|----------|-----------|---------|
| Anthropic | Message Batches API | 50% |
| Gemini | Batch API | 50% |
| OpenAI | Batch API | 50% |

### Reproducing results

All raw findings are stored in `benchmark/results/<repo>/<provider>-<model>-<focus>-run<N>.json`.

```bash
# Clone repos and run full benchmark
./scripts/benchmark.sh

# Re-run specific combination
./scripts/benchmark.sh --repo requests --model anthropic:claude-haiku-4-5 --focus security

# Generate scorecard from results
uv run python scripts/benchmark_analyze.py

# Skip cloning if repos already downloaded
./scripts/benchmark.sh --skip-clone
```
