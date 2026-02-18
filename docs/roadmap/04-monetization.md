# Phase 4: Monetization & SaaS

## What success looks like

Noxaudit generates sustainable revenue from teams that get measurable value from it. The free OSS tool remains the best free option and drives paid adoption — not the other way around. Paying customers get acceleration (dashboard, managed scheduling, team features) rather than gated access to core functionality.

Specifically:

- A team lead can justify the cost to their manager with concrete data: "noxaudit fixed 34 issues this month, saving ~18 developer-hours, for $99"
- Free users never feel like they're using a crippled product — the CLI is complete
- Paying users get a dashboard that shows things the CLI can't: trends over time, team activity, cross-repo health
- Revenue covers infrastructure costs and funds continued development within 6 months of launch

## What exists today

- No billing, accounts, or multi-tenant infrastructure
- No dashboard or web UI
- No historical data beyond latest-findings.json and markdown reports on disk
- No team concepts — everything is single-user, single-machine
- GitHub Actions is the only scheduler (user-managed)

## What needs to exist

### Pricing model

The pricing must reflect where the value is, not where the cost is. Users don't pay for API tokens (they already have keys). They pay for time saved and organizational visibility.

**Tiers**:

| | Free | Pro | Team | Enterprise |
|---|---|---|---|---|
| **Price** | $0 | $29/mo per repo | $99/mo (10 repos) | Custom |
| **Audits** | Unlimited (self-hosted) | Unlimited (managed) | Unlimited (managed) | Unlimited |
| **Focus areas** | All 7 built-in | All 7 + custom | All 7 + custom + shared library | Custom + dedicated |
| **Auto-fix** | Hygiene + docs only | All focus areas | All focus areas | All + custom |
| **Dashboard** | — | Single repo | Multi-repo + team | Org-wide |
| **Trends** | — | 30 days | 90 days | Unlimited |
| **Scheduling** | Self-managed (GH Actions) | Managed | Managed + on-demand | Managed + SLA |
| **Notifications** | Telegram | + Slack, email | + Slack channels per team | + PagerDuty, webhooks |
| **Integrations** | GitHub issues, SARIF | + PR comments | + Jira, Linear | + ServiceNow, custom |
| **Support** | Community (GitHub) | Email, 48h response | Priority, 12h response | Dedicated, SLA |
| **API access** | — | Read-only | Read/write | Full |

**Why these boundaries**:
- **Free has all focus areas**: The audit quality is the acquisition tool. Gating focus areas would cripple the OSS tool and kill adoption.
- **Auto-fix is the upsell**: Hygiene and docs are high-confidence, low-risk — safe to give away. Security and pattern auto-fix requires more sophistication and is worth paying for.
- **Dashboard is the retention lever**: Once a team sees their codebase health trending over time, they can't go back to reading markdown files.
- **Managed scheduling is convenience**: Users *can* run everything via GitHub Actions for free. Paying removes the setup and maintenance.

**Alternative model — per-fix pricing**:

Worth testing alongside subscriptions:
- Free: 5 auto-fixes/month
- $0.50/fix after that
- Unlimited fixes for Team+ tiers

Per-fix aligns cost with value more tightly. A repo that gets 50 fixes/month pays $25 — close to Pro pricing. A repo that gets 5 is free. The risk is unpredictable revenue; the benefit is lower barrier to entry.

### Web dashboard

The dashboard is the primary paid product surface. It shows what the CLI can't: history, trends, team activity, and cross-repo comparison.

**Outcome**: A team lead opens the dashboard Monday morning and sees: which repos were audited over the weekend, what was found, what was auto-fixed, and how the overall health trend is moving. They can triage findings, assign them to team members, and track resolution — all without touching the CLI.

**Dashboard views**:

1. **Overview / Home**
   - Health score per repo (composite of finding counts weighted by severity)
   - Week-over-week trend sparklines
   - Recent activity feed (audits run, findings opened, fixes merged)
   - Action items: findings pending triage

2. **Repo detail**
   - All findings for a repo, filterable by focus area, severity, status
   - Audit history timeline
   - Auto-fix activity (PRs opened, merged, rejected)
   - Decision log (who dismissed what, when, why)
   - Cost tracker (tokens used, spend over time)

3. **Findings triage**
   - Kanban or list view: new → triaging → fixing → resolved
   - Bulk actions: dismiss multiple, assign to team member
   - Inline diff view for auto-fix suggestions
   - Link to source file in GitHub

4. **Trends & analytics**
   - Finding count over time by severity and focus area
   - Mean time to resolution
   - Auto-fix acceptance rate
   - Cost per finding / cost per fix
   - Comparison across repos ("Repo A is improving, Repo B is declining")

5. **Settings**
   - Repo management (add, remove, configure schedule)
   - Team members and permissions
   - Notification preferences
   - API key management
   - Billing

**Considerations**:
- The dashboard reads from a central data store, not from local files. This means audits need to report results to a backend (opt-in for free users, default for paid).
- Start with a read-only dashboard that displays audit results. Add triage and management features iteratively.
- The dashboard should feel fast. Pre-compute aggregations, don't query raw findings for every page load.

### Backend infrastructure

The SaaS layer needs infrastructure the CLI doesn't have.

**Outcome**: A managed backend that receives audit results, stores them durably, serves the dashboard, handles auth, and manages billing.

**Components**:

| Component | Purpose | Considerations |
|---|---|---|
| **Auth** | User accounts, team membership, repo access | GitHub OAuth is the natural choice — users already have GitHub accounts and repos. No email/password. |
| **API** | Receives audit results from CLI, serves dashboard | REST or GraphQL. The CLI already speaks HTTP (Anthropic API, Telegram). Add a `--report-to` flag that posts results to the noxaudit backend. |
| **Data store** | Findings, decisions, audit history, trends | PostgreSQL. Findings are structured, queries are relational (findings by repo by date by severity). |
| **Job scheduler** | Managed audit scheduling for paid users | Could be as simple as cron on a server, or a proper job queue (BullMQ, Celery). Managed scheduling means noxaudit runs the GitHub Action on behalf of the user, or triggers audits from its own infrastructure. |
| **Billing** | Subscription management, usage tracking | Stripe. Subscription tiers + optional metered billing for per-fix pricing. |
| **File storage** | Full audit reports, SARIF files, diffs | S3-compatible (R2, S3). Reports are immutable once generated — write once, read many. |

**Build vs. buy**:
- Auth: Use Clerk, Auth0, or NextAuth.js with GitHub provider. Don't build auth.
- Billing: Stripe. No alternatives worth considering at this stage.
- Hosting: Vercel for the frontend (already there from Phase 3), Railway or Fly.io for the API.
- Database: Neon (serverless Postgres) or Supabase. Don't run your own database.

### Managed scheduling

Free users run noxaudit via their own GitHub Actions cron. Paid users should be able to configure schedules from the dashboard without touching YAML.

**Outcome**: A paid user connects their repo, picks a schedule, and audits just run. No GitHub Actions config, no cron debugging, no "why didn't my audit run last night."

**Considerations**:
- The simplest implementation: noxaudit's backend triggers a GitHub Actions workflow dispatch on the user's repo via the GitHub API. This requires the user to install a GitHub App (not just a PAT).
- Alternative: run audits from noxaudit's own infrastructure (clone repo, run audit, report results). More control, higher infrastructure cost, more security surface.
- Start with the workflow dispatch approach — lower infrastructure cost, audits run in the user's own environment.

### Jira / Linear integration

Teams that use project management tools want findings to show up there, not just in GitHub issues.

**Outcome**: A finding above a configured severity threshold creates a ticket in Jira or Linear with the right project, labels, priority, and assignee. The ticket links back to the dashboard finding for full context.

**Considerations**:
- Jira Cloud REST API and Linear's GraphQL API are both well-documented
- Bidirectional sync (ticket closed → finding resolved) is valuable but complex — start with one-way (finding → ticket), add sync later
- Allow mapping: noxaudit severity → Jira priority, focus area → Jira component/label

### API for third-party integrations

Not every integration needs to be built-in. An API lets users build their own.

**Outcome**: A REST API that exposes findings, decisions, audit history, and trends. Third-party tools (Datadog, Grafana, custom dashboards) can consume noxaudit data.

**Endpoints**:
- `GET /repos` — list connected repos
- `GET /repos/{id}/findings` — findings with filters
- `GET /repos/{id}/audits` — audit history
- `GET /repos/{id}/trends` — pre-computed trend data
- `POST /repos/{id}/decide` — record a decision
- Webhooks for: audit completed, finding created, fix merged

**Considerations**:
- API keys for auth (simpler than OAuth for machine-to-machine)
- Rate limiting per tier (Pro: 100 req/min, Team: 1000 req/min)
- The API should be the same one the dashboard uses — no separate internal API

## Dependencies & sequencing

```
Pricing model (decision) ──────────────── (first — everything else depends on this)
  │
  ├── Stripe billing integration ──────── (needs pricing finalized)
  │
  ├── Auth (GitHub OAuth) ─────────────── (independent)
  │
  └── Backend API ─────────────────────── (needs auth, informed by pricing)
        │
        ├── Dashboard ─────────────────── (needs API)
        │     ├── Overview / Home
        │     ├── Repo detail
        │     ├── Findings triage
        │     ├── Trends (needs historical data)
        │     └── Settings / billing
        │
        ├── Managed scheduling ────────── (needs API + GitHub App)
        │
        ├── Jira / Linear ────────────── (needs API)
        │
        └── Public API + webhooks ─────── (needs API stable)
```

The pricing decision must come first — it determines what's gated, what's free, and how billing works. Auth and the backend API are next. The dashboard is the main deliverable. Integrations layer on top.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pricing too high for indie developers | Lose the long tail that drives word-of-mouth | Free tier is generous; Pro is per-repo so small teams pay little |
| Pricing too low to cover API costs | Unsustainable unit economics | Track cost per audit per repo carefully; adjust tiers based on actual usage data |
| Dashboard is table stakes, not differentiation | Users don't see enough value to pay | The dashboard must show things you genuinely can't get from the CLI — trends, team triage, cross-repo comparison. If it's just a web view of the markdown report, it's not worth paying for. |
| Self-hosted users never convert to paid | Revenue stays flat | That's fine — self-hosted users are the community. Some will convert when their team grows. Don't cripple the OSS tool to force conversions. |
| Infrastructure costs scale faster than revenue | Cash flow negative | Use serverless/managed services to keep baseline costs near zero; scale with usage |
| GitHub App permissions scare users | Drop-off during onboarding | Request minimal permissions; explain why each is needed; support PAT fallback for cautious users |

## How we'll know it's working

- **Conversion rate**: >3% of active free users convert to paid within 6 months
- **Revenue**: Covers infrastructure costs within 6 months; covers one full-time salary within 12 months
- **Dashboard DAU**: >60% of paying users log in at least once per week
- **Churn**: <5% monthly for Team tier, <8% for Pro
- **Net Promoter Score**: >40 (measured via in-app survey)
- **Time to value**: A new paid user sees their first dashboard insight within 10 minutes of signing up
