---
title: Noxaudit
description: AI-powered codebase audits with rotating focus areas, multi-provider support, and decision memory.
---

## The Problem

Codebases drift. Docs go stale, security issues creep in, patterns diverge, dead code accumulates. Manual reviews are expensive and inconsistent. Linters catch syntax but miss semantics.

## The Solution

Noxaudit runs focused AI audits across 7 specialized areas — security, patterns, docs, hygiene, performance, dependencies, and testing. It remembers what you've already reviewed so it only surfaces genuinely new findings.

Each run, Noxaudit:

1. Gathers relevant files from your codebase (deduped across focus areas)
2. Sends them to an AI provider (Claude, GPT, Gemini) with focused prompts
3. Filters results against your decision history (so resolved issues don't resurface)
4. Generates a report and sends you a notification

## Key Features

- **7 Focus Areas** — Security, patterns, docs, hygiene, performance, dependencies, and testing — each with specialized prompts.
- **Decision Memory** — Record decisions about findings so they don't resurface. Decisions expire after 90 days or when the file changes.
- **Multi-Provider** — Rotate between Anthropic Claude, OpenAI GPT, and Google Gemini. Different models catch different things.
- **Cost Controls** — Budget limits, cost estimation before running, batch API discounts, and pre-pass token optimization.
- **GitHub Integration** — GitHub Actions workflow, automatic issue creation, and SARIF upload for Code Scanning alerts.
- **Notifications** — Get summaries via Telegram with severity counts and finding details.

## Quick Install

```bash
pip install noxaudit
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...
noxaudit run --focus security
```

See the full [Installation Guide](/docs/getting-started/installation) and [Quick Start](/docs/getting-started/quickstart).

## Example Output

```
🔒 Security Audit — my-app
3 new findings: 🔴 1 high, 🟡 2 medium

⚠️ SQL interpolation in query builder
   src/db/queries.ts
ℹ️ Console.log with request body
   src/middleware/auth.ts
ℹ️ Permissive CORS in production config
   src/config/cors.ts

✅ 5 previous findings still resolved
```

## License

MIT
