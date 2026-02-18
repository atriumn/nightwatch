# Phase 5: Enterprise

## What success looks like

A security or engineering director at a regulated company can adopt noxaudit, pass it through procurement, satisfy their auditors, and get a single-pane view of codebase health across 50+ repositories. The tool doesn't just find issues — it proves to external auditors that issues are being found and resolved systematically.

Specifically:

- A SOC 2 auditor asks "how do you ensure code quality and security?" and the team hands them a noxaudit compliance report that maps directly to control objectives
- A CISO can enforce organization-wide policies ("no hardcoded secrets, no dependencies older than 180 days") and verify compliance across every repo
- An engineering VP sees a single dashboard showing health trends across all teams, identifying which repos need attention
- The tool passes enterprise security review: SSO, audit trails, data residency, access controls

## What exists today

- Single-user CLI tool with no access controls
- Decision history in a local JSONL file with a `by` field but no real attribution
- No compliance framework awareness
- No policy enforcement mechanism
- No organization-level concepts
- No self-hosted deployment option

## What needs to exist

### Compliance framework mapping

The most direct path to enterprise budgets. Map noxaudit findings to the frameworks enterprises are already audited against.

**Outcome**: Every finding includes references to relevant compliance controls. Reports can be filtered and exported by framework. An auditor sees: "NoxAudit ran 365 security audits this year, identified 847 findings, 812 were resolved within SLA, here's the mapping to SOC 2 CC6/CC7/CC8."

**Frameworks to support** (in priority order):

1. **SOC 2** — Most common for SaaS companies. Map to Trust Service Criteria:
   - CC6 (Logical and Physical Access Controls) ← security focus findings
   - CC7 (System Operations) ← hygiene, performance findings
   - CC8 (Change Management) ← patterns, testing findings

2. **OWASP Top 10 / OWASP API Security Top 10** — Universal for web applications:
   - Direct mapping from security focus findings to specific OWASP categories
   - A01:2021 Broken Access Control, A03:2021 Injection, etc.

3. **PCI DSS** — Required for payment processing:
   - Requirement 6 (Develop and Maintain Secure Systems) ← security, dependencies
   - Requirement 11 (Regularly Test Security) ← testing focus

4. **ISO 27001** — International standard for InfoSec:
   - Annex A controls map to various focus areas

5. **HIPAA** — Healthcare:
   - Technical safeguards map to security and access control findings

**How the mapping works**:
- Each finding type (not each individual finding) maps to one or more framework controls
- The AI doesn't need to know about frameworks — the mapping layer sits between findings and reports
- Mapping metadata lives in a structured file (YAML or JSON) that can be community-contributed and auditor-reviewed
- Custom mappings for internal frameworks ("our security policy section 4.2")

**Considerations**:
- Compliance mapping must be reviewed by someone with compliance expertise — an incorrect mapping is worse than no mapping
- Mappings should be versioned alongside framework versions (SOC 2 criteria update periodically)
- Export formats: PDF for auditors, CSV for GRC tools, JSON for programmatic access

### Policy-as-code

Organizations need to go beyond "find and report" to "find and enforce." Policy-as-code lets teams define rules that gate deployments, not just generate reports.

**Outcome**: An organization defines policies in a YAML file that lives in their repo (or at the org level). Audits evaluate against these policies. CI fails if a policy is violated above a configured severity. Teams can't merge PRs that introduce policy violations.

```yaml
# .noxaudit/policies.yml
policies:
  no-hardcoded-secrets:
    focus: security
    action: block          # block CI, warn, or report
    severity_minimum: high
    message: "Hardcoded secrets are not permitted. Use environment variables."

  dependency-freshness:
    focus: dependencies
    action: warn
    rule: "No dependency older than 180 days without an explicit waiver"

  test-coverage:
    focus: testing
    action: block
    rule: "All public API endpoints must have integration tests"

  doc-freshness:
    focus: docs
    action: report
    rule: "README must be updated within 30 days of any public API change"

  custom-api-standards:
    focus: api-contracts      # custom focus area
    action: block
    rule: "All endpoints must match the OpenAPI spec"
```

**Policy enforcement levels**:
- **block**: CI fails, PR cannot merge (enforced via check status)
- **warn**: CI passes with warning, finding created, notification sent
- **report**: Finding created, included in reports, no CI impact

**Considerations**:
- Policies need an escape hatch — waivers for specific findings with expiry dates and approval requirements
- Organization-level policies should be inheritable by repos, with repo-level overrides allowed (or not, based on org settings)
- Policy evaluation must be deterministic for CI gating — an AI finding is probabilistic, so policy enforcement needs a confidence threshold ("only block if the AI is >90% confident")

### Audit trail and tamper evidence

Enterprise customers need to prove that audit results haven't been altered, decisions were made by authorized people, and the historical record is complete.

**Outcome**: Every action in noxaudit (audit run, finding created, decision made, policy waiver granted, fix applied) is recorded in an append-only log that can be independently verified. An auditor can trace any finding from discovery through resolution with timestamps, actor identity, and justification.

**What gets logged**:
- Audit runs (who triggered, what was audited, what model, what cost)
- Findings (created, updated, resolved — with full content)
- Decisions (who, when, what action, what reason, what file state)
- Policy waivers (who approved, when, what finding, when it expires)
- Auto-fix activity (patch generated, tests run, PR created, merged/rejected)
- Configuration changes (schedule changed, policy updated, team member added)

**Tamper evidence**:
- Each log entry includes a SHA-256 hash of the previous entry (hash chain)
- Periodic checkpoints signed with a server key
- Export capability for external archival

**Considerations**:
- The audit trail must be separate from the operational data store — even admins shouldn't be able to delete audit log entries
- Retention period: configurable, default 7 years (common compliance requirement)
- Performance: audit logging must not slow down the audit workflow. Write-ahead log with async persistence.

### Organization-level dashboard

Enterprises don't have one repo. They have hundreds. The dashboard needs to roll up across all of them.

**Outcome**: A VP of Engineering sees a single view: 127 repos, 89 healthy, 31 need attention, 7 critical. They drill into a team, see their repos, drill into a repo, see its findings. Trends show whether the organization is getting healthier or not.

**Organization views**:

1. **Org health overview**
   - Aggregate health score across all repos
   - Heat map: repos by health score (red/yellow/green)
   - Trend: organization-wide finding count over time
   - Top issues: most common finding types across the org

2. **Team view**
   - Repos grouped by team/ownership
   - Per-team health scores and trends
   - Comparison across teams (not for blame — for resource allocation)

3. **Policy compliance**
   - Which repos comply with which policies
   - Waiver status and expiry dates
   - Compliance percentage by framework

4. **Cost center**
   - API spend by repo, team, focus area
   - Cost trends and projections
   - Budget alerts

### SSO and access controls

Enterprise auth requirements.

**Outcome**: Users authenticate via their company's identity provider. Admins manage who can see which repos, who can make decisions, and who can configure policies. Noxaudit doesn't become another set of credentials to manage.

**Requirements**:
- SAML 2.0 SSO (required for most enterprise procurement)
- SCIM provisioning (auto-create/deactivate users based on IdP state)
- Role-based access control:
  - **Viewer**: see findings and reports
  - **Triager**: make decisions, assign findings
  - **Admin**: manage repos, configure policies, manage team members
  - **Org admin**: manage billing, SSO config, organization policies
- Repo-level permissions (a team can only see their repos)

**Considerations**:
- SSO is often a hard procurement gate — no SSO, no deal. Prioritize it early in Phase 5.
- SCIM is a nice-to-have initially but becomes necessary at scale (offboarding users)
- Start with SAML via a provider like WorkOS or Clerk Enterprise — don't build SAML yourself

### Self-hosted deployment

Some enterprises won't send code to a third-party service. They need to run noxaudit in their own infrastructure.

**Outcome**: An enterprise customer deploys noxaudit's backend (API, dashboard, database) in their own cloud (AWS, GCP, Azure) or on-premises. Code never leaves their network. They manage their own LLM API keys. They get the same dashboard and features as the hosted version.

**Deployment model**:
- Helm chart for Kubernetes (covers most enterprise infrastructure)
- Docker Compose for simpler setups
- Infrastructure requirements documented: Postgres, S3-compatible storage, outbound HTTPS to LLM API

**Considerations**:
- Self-hosted means you lose visibility into usage — you can't easily meter or bill. Options:
  - License key with annual seat-based pricing
  - Call-home telemetry (opt-in) for feature usage, no code content
  - Air-gapped mode with periodic license renewal
- Self-hosted customers need a different support model — they're running your infrastructure, so support includes deployment issues
- Version management: customers will fall behind on updates. Provide clear upgrade paths and support N-2 versions.
- Self-hosted is expensive to support relative to revenue. Price accordingly (minimum $50k/year annual contract) and only offer it when demand justifies the support burden.

### Scheduled compliance reports

Automated, periodic reports designed for auditors and management — not developers.

**Outcome**: On the first Monday of each month, a PDF report is generated and emailed to the compliance team. It summarizes: audits run, findings by framework, resolution rates, policy compliance, open waivers, and trend data. An auditor can read it without logging into the dashboard.

**Report sections**:
1. Executive summary (one paragraph, one chart)
2. Audit activity summary (audits run, repos covered)
3. Finding summary by severity and focus area
4. Compliance framework coverage (findings mapped to controls)
5. Resolution metrics (MTTR, resolution rate, auto-fix rate)
6. Policy compliance status
7. Open waivers and pending items
8. Trend comparison vs. previous period

**Formats**: PDF (primary for auditors), HTML (for email), CSV (for GRC tool import)

## Dependencies & sequencing

```
SSO (SAML + SCIM) ─────────────────────── (start early — procurement gate)
  │
  ├── Access controls (RBAC) ──────────── (needs auth infrastructure)
  │
  └── Org-level dashboard ─────────────── (needs auth + RBAC for multi-team)

Compliance framework mapping ──────────── (independent, can start early)
  │
  └── Scheduled compliance reports ────── (needs mapping + historical data)

Policy-as-code ────────────────────────── (needs findings pipeline stable)
  │
  └── Policy compliance dashboard ─────── (needs policy engine + dashboard)

Audit trail ───────────────────────────── (independent, start early — data lost before this exists is gone forever)

Self-hosted deployment ────────────────── (needs all features stable — ship last)
```

**Critical path**: SSO and audit trail should start early — SSO because it's a procurement gate, audit trail because historical data can't be backfilled. Compliance mapping is high-value and independent. Self-hosted comes last because it requires all features to be stable.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Compliance mappings are incorrect or incomplete | Auditors reject noxaudit reports; potential legal liability | Have mappings reviewed by compliance professionals; clearly label as "guidance, not legal advice"; version and cite framework sources |
| Policy-as-code false positives block legitimate PRs | Developer frustration, teams disable policies | Confidence thresholds, easy waiver process, "warn" mode as default before "block" |
| Self-hosted support burden exceeds revenue | Unprofitable customer segment | High minimum contract value; dedicated support team; invest in deployment automation and documentation to reduce support tickets |
| Enterprise sales cycle is 6–12 months | Cash flow gap between investment and revenue | Don't hire an enterprise sales team until you have 3+ inbound enterprise inquiries; let the product-led funnel generate leads |
| Feature creep from enterprise requests | Distraction from core product | Maintain a clear boundary: enterprise features are about governance, compliance, and scale — not about changing how the core audit works |
| AI-generated compliance evidence challenged by regulators | Reputational and legal risk | Position noxaudit as a tool that assists compliance, not replaces compliance processes; always include human review checkpoints |

## How we'll know it's working

- **Enterprise pipeline**: 3+ qualified enterprise leads within 6 months of launching SSO
- **Deal size**: Average enterprise contract >$50k/year
- **Compliance adoption**: >50% of enterprise customers use compliance framework mapping in their reports
- **Policy adoption**: >30% of enterprise customers have at least one "block" policy active
- **Audit satisfaction**: Compliance teams report noxaudit reduces audit prep time by >50% (measured via customer survey)
- **Self-hosted demand**: Only build self-hosted when 5+ enterprise prospects name it as a hard requirement
- **Retention**: Enterprise annual renewal rate >90%
