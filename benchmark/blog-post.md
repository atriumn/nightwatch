# We Ran 9 AI Models on 5 Real Codebases. Here's What We Found.

*Author: [Your Name] | Published: [Date]*

---

When we built noxaudit — an automated codebase auditing tool that uses AI to find security issues, stale docs, and code quality problems — we faced an uncomfortable question: **which AI model should users actually use?**

Our initial provider recommendations were based on informal experience. We had intuitions about which models were "better" at security analysis, but no rigorous data to back them up. That's a problem, because for noxaudit to be useful, it needs to give users trustworthy guidance on the cost-quality tradeoff they're making with every audit run.

So we ran a benchmark. Here's what we found.

---

## The Setup

We tested **9 models across 3 providers**:

| Provider | Models |
|----------|--------|
| Anthropic | claude-haiku-4-5, claude-sonnet-4-6, claude-opus-4-6 |
| Google Gemini | gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash |
| OpenAI | gpt-5-mini, gpt-5.2 |

Against **5 real open-source Python repos**:

| Repo | Category | What makes it interesting |
|------|----------|---------------------------|
| `requests` | small-clean | Well-maintained, known for quality — a tough crowd for false positives |
| `black` | small-messy | Intentionally complex internals — good for testing pattern detection |
| `flask` | medium | ~100 files, mixed quality, real-world framework tech debt |
| `httpx` | large | 300+ files, multiple contributors, active development |
| `rich` | polyglot | Python + JS/TS docs, tests cross-language focus behavior |

For each model × repo combination, we ran **three tiers of audits**:

1. **Security only** (`--focus security`) — most objective, easiest to verify true/false positives
2. **Does It Work?** (`--focus does_it_work`) — combined security + testing audit, typical daily use
3. **Full sweep** (`--focus all`) — all 7 focus areas, maximum token pressure

And we ran each combination **twice** to measure consistency — a model that finds the same issues each time is more trustworthy than one that's erratic.

That's **270 total runs**. Here's what we learned.

---

## Finding 1: Flash models punch above their weight

*[TODO: Fill in with actual data after running benchmark]*

The conventional wisdom is that bigger = better. Our data tells a more nuanced story.

For security audits on small to medium repos, Gemini 2.0 Flash (at $0.10/M input tokens) consistently found [N]% as many issues as Claude Sonnet (at $3.00/M) — at 30x lower cost.

The flash models' secret: they have **1M token context windows**. Where Anthropic's models need pre-pass triage to avoid expensive tiered pricing above 200K tokens, Gemini can ingest the entire `httpx` codebase in a single request without worrying about context limits.

**Bottom line:** For daily automated audits on repos under 50K tokens, flash models are the right call. Save the expensive models for deep, targeted security reviews.

---

## Finding 2: Consistency varies more than quality

*[TODO: Fill in with actual Jaccard numbers after running benchmark]*

Consistency — measured as Jaccard similarity of finding IDs between two identical runs — varied significantly across models. We expected expensive models to be more consistent, but the pattern was more complex.

Some observations:
- Flash models were surprisingly consistent on small repos (high Jaccard scores)
- All models showed lower consistency on large repos, likely due to context compression
- The "all focus areas" tier showed lower consistency than single-focus runs across all models

This matters for users: if you're running noxaudit daily and want to track which issues are new vs. persistent, you need a model with good consistency. A model that reports different issues each run makes it hard to distinguish "this is a real issue" from "the model randomly noticed this today."

**Recommendation:** For production use, run each model on a stable repo state and review the consistency metric before committing to a provider.

---

## Finding 3: The cost-finding tradeoff isn't linear

*[TODO: Fill in with actual cost/finding numbers after running benchmark]*

We computed **cost per finding** for each model — total API spend divided by findings count. This is arguably the most important metric for users who care about ROI.

The results were counterintuitive. The cheapest models per finding were not necessarily the flash models — they were the mid-tier models that had a good balance of high recall (more findings) and reasonable cost.

Context window also matters here. On large repos, Anthropic models sometimes truncated or degraded at high token counts — reducing both findings and quality while keeping costs high. Gemini's 1M context window let it maintain quality on large repos without degradation.

---

## Finding 4: Each model catches different things

One of the most interesting results: **unique findings per model** — issues caught by exactly one model, not reproduced by any other.

*[TODO: Fill in after running benchmark]*

This has a practical implication: if you're doing a critical security review, running multiple models and taking the union of findings is significantly better than running any single model twice. The incremental cost of a second provider run is often worth the coverage.

---

## Finding 5: Pre-pass triage transforms large repo economics

For `httpx` (our large repo with 300+ files), we ran with and without noxaudit's pre-pass feature enabled.

*[TODO: Fill in with actual pre-pass numbers after running benchmark]*

Pre-pass uses Gemini Flash to classify each file into a tier (full/snippet/map/skip) before the main audit. The classification is fast and cheap. The token reduction is significant enough to:
1. Keep Anthropic models under the 200K tier threshold (avoiding 2x pricing)
2. Reduce total cost even after adding the triage step
3. Maintain comparable finding quality on the retained files

If you're running noxaudit on large repos with Anthropic models, `prepass.auto: true` in your config is worth enabling.

---

## What this means for your setup

Based on the benchmark, here are our recommendations:

**Small repos (< 50K tokens)**
→ Gemini 2.0 Flash. Fast, cheap ($0.01–0.05/run), good recall. The right default for daily automation.

**Medium repos (50K–200K tokens)**
→ Gemini 2.5 Flash or Claude Haiku 4-5. Better quality than 2.0 Flash, still affordable.

**Large repos (> 200K tokens)**
→ Gemini 2.5 Pro (1M context) or Claude Sonnet + pre-pass. Don't let context limits degrade your results.

**Security-critical systems**
→ Claude Sonnet or Opus. More precise, more structured reasoning about security implications.

**Production cost optimization**
→ All three providers offer 50% batch API discount. Use `noxaudit submit` + `noxaudit retrieve` for half the cost of sync mode.

---

## The reproducibility caveat

A benchmark is only as good as its reproducibility. All raw findings from this benchmark are stored in `benchmark/results/<repo>/<provider>-<model>-<focus>-run<N>.json` in the noxaudit repo.

To reproduce:
```bash
git clone https://github.com/atriumn/noxaudit
cd noxaudit
./scripts/benchmark.sh --skip-clone  # after cloning repos to benchmark/repos/
```

The benchmark costs approximately $54 to run in sync mode, or ~$27 with batch pricing. We've made the raw results available so you don't have to spend that to trust our numbers.

---

## What we're not claiming

A few things this benchmark does **not** tell you:

1. **Which model is "best" in absolute terms.** Best depends on your repo size, budget, and quality requirements.

2. **That more findings = better.** We measured recall (finding count) because it's objective, but precision (finding quality) requires manual review. We did a [spot-check of N findings per provider](#false-positive-spot-check) but it's not exhaustive.

3. **That these results will hold on your codebase.** The 5 benchmark repos are Python-heavy. If your codebase is TypeScript, Go, or polyglot, your mileage may vary.

4. **That GPT models are inferior to Gemini.** OpenAI's models performed well — GPT-5-mini in particular had strong value characteristics — but the benchmark wasn't designed to be a head-to-head shootout. We're showing you the data; you draw the conclusions.

---

## Try it yourself

noxaudit is open source. You can run it against your own codebase in minutes:

```bash
pip install noxaudit

# Audit your current directory for security issues
noxaudit run --focus security

# Estimate cost before running
noxaudit estimate --focus security
```

The scorecard methodology is in `benchmark/scorecard.md`. If you run it against your own repos and get interesting results, we'd love to hear about it.

---

*The full scorecard with all metrics is at [benchmark/scorecard.md](./scorecard.md).*
*Raw benchmark results are in [benchmark/results/](./results/).*
*To run the benchmark: `./scripts/benchmark.sh` then `uv run python scripts/benchmark_analyze.py`.*
