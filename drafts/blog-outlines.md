# Blog Post Outlines

## Post 1: "We Ran the Same AI Audit 12 Times. Here's What Happened."

The hook — people assume AI is deterministic. We prove it isn't.

- We ran 4 models x 3 runs on the same unchanged codebase
- Best model (Opus): only 35% overlap between runs
- Worst (GPT-5.4): 14% overlap despite finding the most issues
- The output budget ceiling: models find ~50 of ~92 issues and stop. Which 50? Different every time.
- What this means for anyone building AI-powered code analysis
- Charts: Jaccard heatmaps, finding count distributions, the "92 issues" discovery

Audience: AI engineers, devtools builders, skeptics of AI code review

## Post 2: "Why We Stopped Trying to Make AI Consistent"

The narrative pivot — we spent weeks chasing consistency and it was the wrong goal.

- Started with dedup (normalize titles) — helped, but 49% overlap is still a coin flip
- Tried chunking (split files into small batches) — found 8x more issues but even noisier
- The realization: two runs finding different things isn't a bug, it's sampling
- The architecture shift: stop demanding identical runs, start building a pipeline that embraces variance
- Audit -> Validate -> Dedup -> Accumulate
- Each run adds to a growing knowledge base instead of replacing the last one
- Consistency emerges over time, not within a single run

Audience: product engineers building with LLMs, anyone who's hit the "LLMs aren't deterministic" wall

## Post 3: "The Three-Stage Pipeline That Made AI Code Audits Actually Useful"

The technical deep dive on the architecture.

- Stage 1 (Audit): cheap model, chunked, intentionally broad. Find everything, worry about noise later.
- Stage 2 (Validate): each finding sent back with source code. "Is this real?" — verification is easier than generation
- Stage 3 (Dedup): persistent vocabulary normalizes titles across runs. Same issue = same ID forever.
- The accumulation layer: findings build up over nightly runs. Seen 5 times = high confidence. Seen once = flag it.
- Cost breakdown: full pipeline on 100 files = ~$0.04
- Open source (CLI) vs SaaS: CLI gets single-pipeline quality, SaaS adds cross-model validation and confidence scoring over time

Audience: technical, devtools/AI infra people who want to build something similar

## Post 4: "What 10 AI Models Think Is Wrong With Your Code"

The Phase 1 benchmarking results, framed for developers not AI researchers.

- We pointed 10 models at 2 real repos (noxaudit + python-dotenv)
- The hallucination canary: python-dotenv is well-maintained, so findings should be minimal and real
- Model-by-model breakdown: who finds the most? Who hallucinates? Who's cheapest per real finding?
- The consensus view: 6 issues that 8+ models agree on vs findings only one model sees
- What this means for choosing a model for your own tooling
- Cost table: $0.008 (gpt-5-nano) to $0.65 (Opus) per audit

Audience: developers evaluating AI code review tools, broad HN/Reddit appeal
