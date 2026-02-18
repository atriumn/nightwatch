# Phase 1: OSS Foundation

## What success looks like

A developer discovers noxaudit, installs it, runs their first audit, and decides to keep it. They configure a nightly cron, get their first useful report, and don't uninstall it after week one. The first-run experience doesn't overwhelm them with hundreds of findings they can't act on. They know what the tool costs them and can justify it.

Specifically:

- A new user goes from `pip install noxaudit` to a meaningful first report in under 10 minutes
- An existing codebase with hundreds of latent issues doesn't produce a wall of noise on first run
- Users can see exactly what they're spending on API calls and project forward
- Output integrates with the tools teams already use for security findings (GitHub Security tab, VS Code, Defect Dojo, etc.)
- The tool works with at least two LLM providers so no team is locked out by vendor policy

## What exists today

- Working CLI with 7 focus areas, decision memory, batch API, GitHub Actions, MCP server
- Anthropic as sole provider (OpenAI and Gemini declared but unimplemented)
- No baseline mechanism — first run surfaces everything, old and new
- No diff-aware mode — every audit scans the full codebase
- No cost tracking — budget config exists but doesn't measure actual spend
- Reports are markdown files and Telegram messages only
- No standard security output format (SARIF, etc.)

## What needs to exist

### Baseline command

When a team adopts noxaudit on an existing codebase, they need a way to acknowledge everything that's already there without triaging each finding individually. After baselining, only genuinely new findings appear in reports.

**Outcome**: A team with a 3-year-old codebase can adopt noxaudit and get a clean first week — reports only show findings introduced after the baseline date.

**Considerations**:
- Baseline should be reversible (undo if done accidentally)
- Baselined findings should still be visible in a separate "known issues" view — they didn't stop being issues, they're just not new
- Should work per-repo and per-focus-area (baseline security separately from docs)

### Diff-aware audits

Auditing only what changed since the last run (or since a specific commit). This enables two things: (a) dramatically cheaper nightly runs on large repos, and (b) PR-level integration where you audit a branch diff, not the whole codebase.

**Outcome**: A nightly audit on a 50k-line repo that had 3 files change costs ~10% of a full audit. A PR check runs in under 60 seconds and comments on the PR with relevant findings.

**Considerations**:
- Need to handle cross-file impacts — if file A changes, and file B depends on A, the AI might need both
- The dependency analysis doesn't need to be perfect; erring toward including more context is fine since cost savings are still significant
- PR integration needs to work with GitHub Actions (primary), GitLab CI, and ideally any CI system via the CLI

### Cost tracking and projection

Users need visibility into what noxaudit costs them. This means measuring actual token usage per audit, tracking spend over time, and projecting future costs based on repo size and schedule.

**Outcome**: A user runs `noxaudit status` and sees: last 30 days of spend, average cost per audit, projected monthly cost at current schedule. A team lead can take this to their manager and say "this tool costs us $52/month."

**Considerations**:
- Track input tokens, output tokens, and cache hits separately — Batch API pricing differs
- Store token counts per audit in a local ledger (extend the reports metadata)
- Model pricing changes over time; track tokens and let users apply current pricing, don't hardcode rates

### SARIF output

SARIF (Static Analysis Results Interchange Format) is the standard that unlocks GitHub Code Scanning, VS Code SARIF Viewer, Azure DevOps, and every enterprise security dashboard. One output format, dozens of integrations for free.

**Outcome**: Running `noxaudit run --format sarif` produces a valid SARIF 2.1.0 file. Uploading it to GitHub via `codeql-action/upload-sarif` shows noxaudit findings in the repository's Security tab alongside CodeQL, Semgrep, and other tools.

**Considerations**:
- SARIF needs stable rule IDs per finding type so findings can be tracked across runs in GitHub's UI
- Map noxaudit severity levels to SARIF severity levels (error/warning/note)
- Each focus area becomes a SARIF "tool" or "rule" depending on how granular we want GitHub to display results

### Second LLM provider

Some teams can't use Anthropic (vendor policy, data residency, budget). At minimum, OpenAI support removes the most common blocker. Google Gemini is a nice-to-have.

**Outcome**: A user sets `provider: openai` in their config, provides an OpenAI API key, and gets comparable audit quality. The prompts may need provider-specific tuning, but the experience is seamless.

**Considerations**:
- OpenAI's Batch API also offers 50% cost reduction — match the current Anthropic architecture
- Response parsing will differ; the provider abstraction in `base.py` already handles this but needs real implementation
- Finding quality may vary by provider — document which models are recommended and tested
- Don't try to make all providers produce identical results; focus on "useful findings" not "same findings"

## Dependencies & sequencing

```
Baseline ──────────────────────────────── (no dependencies, start here)
SARIF output ──────────────────────────── (no dependencies, parallelize)
Cost tracking ─────────────────────────── (no dependencies, parallelize)
Diff-aware audits ─────────────────────── (benefits from baseline existing)
Second provider ───────────────────────── (no dependency, but lower priority)
```

Baseline, SARIF, and cost tracking are fully independent — all three can progress simultaneously. Diff-aware benefits from baseline being done first (so users baseline before switching to diff-only mode). Second provider is independent but lower urgency.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Baseline mechanism is too coarse (all-or-nothing) | Users still get overwhelmed | Support per-focus, per-severity baselining |
| SARIF mapping loses nuance of AI findings | Findings look worse in GitHub than in reports | Invest in rule descriptions and markdown help text |
| Diff-aware mode misses cross-file issues | Users lose trust in findings | Default to including dependency context, let users tune |
| OpenAI provider produces noticeably worse findings | Users blame noxaudit, not the model | Test thoroughly, document model recommendations, gate behind "experimental" if needed |
| Cost tracking is inaccurate | Users distrust the tool | Use actual API response token counts, not estimates |

## How we'll know it's working

- **Retention**: >50% of users who run their first audit run a second one within 7 days
- **Baseline adoption**: >80% of users with repos older than 6 months use baseline within first 3 runs
- **Cost clarity**: Users can answer "what does noxaudit cost me?" without checking their Anthropic dashboard
- **SARIF uploads**: Repos start appearing with noxaudit findings in GitHub Security tabs (track via GitHub search for noxaudit SARIF workflow files)
- **GitHub stars and installs**: Directional signal that the tool is being discovered and tried
