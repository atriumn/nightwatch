# Phase 2: Product-Market Fit

## What success looks like

Noxaudit stops being a tool people try and starts being a tool people rely on. The shift: from "interesting, I'll check the report" to "noxaudit opened 4 PRs this week and I merged 3 of them without editing." Users measure the time it saves them. Teams add it to their workflow docs. Removing it would feel like losing a team member.

Specifically:

- Auto-fix handles routine cleanup — dead code, stale docs, simple security fixes — and produces PRs that pass CI and get merged without modification >60% of the time
- Teams can define their own audit rules in plain English, not just use the built-in 7
- Prompts understand the difference between a Django app and a Go microservice, producing findings that reference framework-specific patterns
- Findings appear where developers already work — PR comments, Slack, IDE — not just in markdown reports

## What exists today

- AI produces a `suggestion` field per finding — natural language advice, not executable patches
- 7 hardcoded focus areas with generic prompts
- No language or framework awareness beyond file extension matching in glob patterns
- Telegram is the only notification channel
- GitHub issues are created but not as PR review comments
- MCP server is read-only (query findings, can't act on them)

## What needs to exist

### Auto-fix engine

The single highest-leverage feature. Transform findings from "here's what's wrong" to "here's a PR that fixes it."

**Outcome**: A nightly audit finds 6 issues. 4 are auto-fixable (2 dead imports, 1 stale docstring, 1 missing type annotation). Noxaudit generates patches, applies them to a branch, runs the repo's test suite, and opens a PR for the 3 that pass tests. The developer reviews and merges in the morning. The 1 that failed tests is reported as "fix attempted, tests failed" with the error output.

**Two operating modes**:

1. **Interactive** (`noxaudit fix --finding FINDING_ID`) — Generates a fix for a single finding, applies it locally, user reviews. Low risk, good for building trust.

2. **Batch** (`noxaudit fix --auto`) — Fixes all auto-fixable findings from the latest audit, opens a PR. This is the "set it and forget it" mode that makes noxaudit indispensable.

**Fix confidence model**:

Not all fixes are equal. The engine needs a confidence signal:

- **High confidence** (dead code removal, unused imports, typos in docs) — auto-merge candidate
- **Medium confidence** (refactoring suggestions, dependency updates) — PR with review requested
- **Low confidence** (security fixes, architectural changes) — finding reported with suggested diff, not auto-applied

**Test verification loop**:

A fix that breaks the build is worse than no fix. Every auto-fix must:
1. Apply the patch to a clean branch
2. Run the repo's test command (auto-detected or configured)
3. If tests pass → commit and include in PR
4. If tests fail → revert, report failure, include test output in the finding for human review

**Considerations**:
- Batch API won't work for fixes — fix generation is iterative (generate, apply, test, maybe regenerate). Use the standard API.
- Cost per fix is higher than cost per finding (more tokens for diff generation + test output analysis). Track and report this separately.
- Fixes should be atomic — one commit per finding, so reviewers can accept/reject individually within a PR
- Branch naming: `noxaudit/fix/{date}` or `noxaudit/fix/{focus}` — predictable, won't collide

### Auto-fix scope by focus area

| Focus Area | Auto-fix tier | What gets fixed |
|---|---|---|
| **hygiene** | High confidence | Dead code, unused imports, orphaned files, stale config entries |
| **docs** | High confidence | Outdated docstrings, README sections that contradict code, missing parameter docs |
| **dependencies** | Medium confidence | Version bumps for patch/minor versions, known CVE remediations with published fixes |
| **patterns** | Medium confidence | Naming convention violations, inconsistent patterns with clear project precedent |
| **testing** | Medium confidence | Generate missing test stubs, add edge case tests for uncovered branches |
| **security** | Low-Medium | Hardcoded secrets → env vars, missing input validation, CORS misconfig |
| **performance** | Low | Most perf fixes involve tradeoffs — suggest, don't auto-apply |

### Custom focus areas

Teams have rules that no generic tool covers: "all API endpoints must have rate limiting," "database migrations must be reversible," "every public function needs an integration test." Let teams express these in their own words.

**Outcome**: A team adds a `custom_focus` block to their config with a plain-English prompt file. The next audit runs their custom checks alongside the built-in ones. Findings from custom focus areas work identically to built-in ones — same decision memory, same auto-fix pipeline, same reports.

```yaml
custom_focus:
  - name: api-contracts
    description: "Verify API responses match our OpenAPI spec"
    file_patterns: ["**/routes/**", "**/schemas/**", "openapi.yaml"]
    prompt: .noxaudit/prompts/api-contracts.md
    severity_default: medium

  - name: error-handling
    description: "Ensure errors are handled consistently per our style guide"
    file_patterns: ["**/src/**/*.py"]
    prompt: .noxaudit/prompts/error-handling.md
```

**Considerations**:
- Provide a prompt template/guide so users write effective audit prompts — most people will write vague ones that produce vague findings
- Custom focus areas should be shareable — a team should be able to publish their focus area as a standalone YAML+prompt package
- Built-in focus areas should use the exact same mechanism internally (eat your own dog food)

### Language and framework-aware prompts

The difference between "this code might have a SQL injection" and "this Django ORM `.extra()` call on line 47 is vulnerable to SQL injection — use `.annotate()` instead" is the difference between a finding people ignore and one they fix immediately.

**Outcome**: Noxaudit detects the language and framework of each repo (or accepts explicit config) and selects prompt variants that reference framework-specific patterns, common vulnerabilities, and idiomatic solutions.

**Language detection strategy**:
- Primary: explicit config (`language: python`, `framework: django`)
- Fallback: file extension analysis + marker file detection (presence of `manage.py` → Django, `go.mod` → Go, `package.json` + `next.config.js` → Next.js)
- The detection doesn't need to be perfect — it's selecting a prompt variant, not compiling code

**What changes per language/framework**:
- Security focus: Python/Django SQL injection patterns vs. Go template injection vs. React XSS vectors
- Pattern focus: Pythonic idioms vs. Go conventions vs. React component patterns
- Testing focus: pytest patterns vs. Go table tests vs. Jest/RTL patterns
- Dependency focus: PyPI advisories vs. npm audit vs. Go vulnerability database

**Considerations**:
- Start with 3-4 languages (Python, TypeScript/JavaScript, Go, Rust) — cover the most likely early adopters
- Framework variants within a language (Django vs. FastAPI, React vs. Vue) are a separate axis — start with language-level, add framework-level based on demand
- Prompt variants should be community-contributable — this is where OSS contributions will naturally flow

### PR review comments

Findings that appear as inline comments on pull requests are 10x more actionable than findings in a separate report. The developer sees the issue exactly where it is, in the context of the change they're making.

**Outcome**: When noxaudit runs in diff-aware mode on a PR, findings are posted as review comments on the specific lines of the PR diff. The review is submitted as a single GitHub review (not individual comments) with an overall summary.

**Considerations**:
- Use GitHub's pull request review API, not individual comments — this groups findings into a coherent review
- Only comment on lines that are part of the PR diff — don't flag pre-existing issues in unchanged code (that's what nightly audits are for)
- Include a "noxaudit" label or bot identity so comments are clearly automated
- Support "request changes" vs. "comment" review types based on severity — critical security findings request changes, style suggestions are just comments
- Rate limit: don't post 50 comments on a PR. Summarize if findings exceed a threshold (e.g., top 10 findings + "and 12 more")

### Slack integration

Telegram works for solo developers. Teams use Slack.

**Outcome**: Noxaudit posts audit summaries to a Slack channel with the same information density as Telegram but using Slack's Block Kit for formatting — collapsible sections, severity color coding, action buttons for "view report" and "triage findings."

**Considerations**:
- Slack webhook (incoming webhook URL) for simplest setup — no OAuth app needed initially
- Slack app (with OAuth) later for interactive features (triage from Slack, thread replies)
- Message formatting should degrade gracefully — Block Kit for Slack, plain markdown for Telegram, both readable

### Interactive MCP tools

The current MCP server is read-only. Making it interactive turns every AI coding assistant into a noxaudit triage interface.

**Outcome**: A developer using Claude Code or Cursor can say "show me the latest security findings, dismiss the false positives, and fix the real ones" — and the MCP tools handle the entire workflow without leaving the editor.

**New MCP tools**:
- `decide(finding_id, action, reason)` — record a decision
- `fix(finding_id)` — generate and apply a fix
- `explain(finding_id)` — detailed explanation with context
- `reaudit(file_path)` — re-run audit on a specific file after changes
- `get_trends(repo, days)` — finding trends over time

## Dependencies & sequencing

```
Auto-fix engine ───────────────────────── (core capability, start first)
  ├── needs: test verification loop
  ├── needs: fix confidence model
  └── benefits from: diff-aware audits (Phase 1)

Custom focus areas ────────────────────── (independent, parallelize)
  └── benefits from: language-aware prompts (richer custom prompts)

Language-aware prompts ────────────────── (independent, parallelize)
  └── benefits from: community contributions (more languages)

PR review comments ────────────────────── (needs diff-aware from Phase 1)
  └── depends on: diff-aware audits

Slack integration ─────────────────────── (independent, low dependency)

Interactive MCP ───────────────────────── (benefits from auto-fix engine)
  └── depends on: auto-fix engine for fix() tool
```

Auto-fix is the critical path. Custom focus areas and language-aware prompts can progress in parallel. PR comments depend on Phase 1's diff-aware audits. Slack is independent and can ship anytime.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Auto-fixes break builds despite test verification | Users lose trust, disable auto-fix | Conservative confidence defaults; "suggest" mode before "auto" mode; require 2+ successful fix cycles before enabling batch auto-fix |
| Fix quality varies wildly by language/repo | Inconsistent experience | Start with high-confidence fix types only (hygiene, docs); expand as quality data accumulates |
| Custom focus prompts are hard to write well | Feature exists but produces bad findings | Ship prompt writing guide, examples, and a `noxaudit validate-prompt` command that tests a prompt against sample code |
| PR comments are noisy / low signal | Teams disable the integration | Default to conservative thresholds; never comment on style in PRs (save that for nightly); respect configured severity minimums |
| Too many features dilute focus | Phase 2 takes forever | Auto-fix is the priority. Everything else is valuable but secondary. If forced to ship one thing, ship auto-fix. |

## How we'll know it's working

- **Fix merge rate**: >60% of auto-generated PRs are merged without human edits
- **Fix adoption**: >40% of active users enable auto-fix within 30 days of it being available
- **Custom focus adoption**: >20% of teams with >3 months of usage create at least one custom focus area
- **Time saved**: Users report (via survey or GitHub discussions) measurable time savings — target "saves me 2+ hours per week"
- **Retention shift**: Weekly active usage (not just installed, actually running audits) exceeds 70% of installs
- **PR comment engagement**: Developers respond to or resolve >50% of PR comments within 24 hours (vs. being ignored)
