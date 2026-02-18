# Phase 3: noxaudit.com & Web Presence

## What success looks like

Someone hears about noxaudit, Googles it, and lands on a site that makes the value obvious in 10 seconds. They can read docs without digging through a GitHub README. They can see a live demo of what an audit produces. If they're ready to pay, they can sign up. If they're not, they walk away knowing exactly what the tool does and how to install it.

The site is both the front door (marketing, docs, demo) and eventually the product surface (dashboard, settings, billing). Phase 3 builds the front door. Phase 4 builds the product behind it.

Specifically:

- noxaudit.com ranks on the first page for "AI code audit," "automated code review," and "nightly code analysis"
- A visitor understands what noxaudit does, who it's for, and how to start in under 30 seconds
- Documentation is searchable, versioned, and not a wall of markdown on GitHub
- The site communicates credibility — open source roots, real examples, not vaporware

## What exists today

- GitHub README with installation, usage, and configuration docs
- CONTRIBUTING.md and CHANGELOG.md
- No website, no domain (assumed), no landing page
- No documentation site
- No visual identity or brand assets beyond the name

## What needs to exist

### Brand identity

Before building anything, noxaudit needs a visual language. Not a full brand book — a minimal, consistent identity that works across the site, README, GitHub social preview, and future dashboard.

**Outcome**: A cohesive visual identity that communicates "serious tool, not a toy" without feeling corporate. Developers trust tools that look intentional.

**Elements**:
- **Logo**: Minimal mark + wordmark. The "nox" (night) theme suggests dark palette, possibly an owl or moon motif — but avoid being cute. A clean typographic mark may be stronger.
- **Color palette**: Dark primary (the tool runs at night), one accent color for CTAs and severity highlights. Must work on both light and dark backgrounds (developers use dark mode).
- **Typography**: Monospace for code, clean sans-serif for body. Nothing trendy.
- **Social preview image**: The 1280x640 image that appears when the GitHub repo or website is shared on Twitter/LinkedIn/Slack. This is disproportionately important for first impressions.

**Considerations**:
- The identity should feel like a developer tool, not a SaaS marketing site. Think Tailwind, Astro, or Ruff — not Salesforce.
- Keep it simple enough that a single developer can maintain consistency without a designer on call.

### Landing page (noxaudit.com)

The marketing site. One page initially, expanding as needed.

**Outcome**: A single-page site that converts visitors into either installers (OSS) or signups (paid, when available).

**Structure (top to bottom)**:

1. **Hero section**
   - One sentence: what noxaudit does and for whom
   - `pip install noxaudit` front and center
   - Animated or static terminal demo showing an audit running and producing findings
   - No signup gate — the OSS tool is the top CTA

2. **Problem statement**
   - 3–4 pain points: docs drift, security issues creep in, patterns diverge, dead code accumulates
   - Brief — developers don't read marketing copy. Show, don't tell.

3. **How it works**
   - Visual: config → schedule → AI audit → findings → auto-fix → PR
   - Show the weekly rotation concept (Mon: security, Tue: patterns, etc.)
   - Emphasize the decision memory — "it remembers what you've already reviewed"

4. **Sample output**
   - Real (or realistic) audit report snippet
   - Real (or realistic) auto-fix PR screenshot
   - This is the "proof it actually works" section

5. **Focus areas**
   - Visual grid of the 7 (and counting) focus areas with one-line descriptions
   - Click-to-expand with example findings per area

6. **Integrations**
   - GitHub Actions, MCP, Slack, Telegram, SARIF → GitHub Security
   - Logo grid with brief descriptions

7. **Pricing** (when Phase 4 is ready)
   - Placeholder until then: "Free and open source. Pro features coming soon."

8. **Open source callout**
   - GitHub stars badge, license, link to repo
   - "Built in public" credibility signal
   - Contributor count, recent commits — signs of life

9. **Footer**
   - GitHub, docs, changelog, contributing guide
   - "Made by [you/your org]"

**Considerations**:
- Static site — no backend needed for Phase 3. Astro, Next.js static export, or even plain HTML. Choose based on what you want the eventual dashboard to be built in (if Next.js dashboard, use Next.js now).
- Host on Vercel or Cloudflare Pages — free tier is fine, global CDN, automatic HTTPS.
- The terminal demo is the most important element. A short asciinema recording or a custom animated terminal component. Don't use a video — too heavy, doesn't feel native.
- Mobile-responsive but desktop-optimized. Developers primarily browse on desktop.

### Documentation site

GitHub READMEs work for getting started. They don't work for reference docs, guides, or searchable content.

**Outcome**: docs.noxaudit.com (or noxaudit.com/docs) with structured, searchable documentation that a user can navigate without reading top-to-bottom.

**Structure**:

```
Docs
├── Getting Started
│   ├── Installation
│   ├── Quick Start (first audit in 5 minutes)
│   ├── Configuration reference
│   └── GitHub Actions setup
├── Concepts
│   ├── How audits work
│   ├── Focus areas explained
│   ├── Decision memory
│   ├── Batch API and cost model
│   └── Combined audits and token savings
├── Guides
│   ├── Writing custom focus areas
│   ├── Setting up auto-fix
│   ├── PR integration
│   ├── Notification channels
│   ├── MCP server for AI assistants
│   └── SARIF and GitHub Security integration
├── Reference
│   ├── CLI commands
│   ├── Configuration YAML schema
│   ├── Environment variables
│   ├── MCP tools
│   └── API (Python library usage)
├── Providers
│   ├── Anthropic (setup, models, cost)
│   ├── OpenAI
│   └── Google Gemini
└── Changelog
```

**Considerations**:
- Use a docs framework that supports versioning, search, and dark mode out of the box. Starlight (Astro-based), Nextra (Next.js-based), or Mintlify are strong options.
- Docs should live in the repo (`docs/` directory) so they're updated alongside code changes. The docs site builds from the repo.
- Every CLI command should have a dedicated reference page with examples, not just `--help` output.
- Search is non-negotiable. Algolia DocSearch (free for OSS) or built-in framework search.

### SEO and discoverability

Noxaudit needs to be findable by people who don't know it exists yet.

**Outcome**: Organic search traffic from developers looking for AI-powered code analysis, automated code review, or nightly audit tools.

**Content strategy**:
- The docs site itself is the primary SEO asset — structured content with clear headings ranks well
- Blog (lightweight, in /blog) for announcements, case studies, and "how we built X" posts
- Each focus area should have a standalone page explaining what it checks and why — these are long-tail SEO targets ("automated security audit for Python," "AI documentation freshness checker")

**Considerations**:
- Don't over-invest in content marketing early. The docs and focus area pages are the content. A blog with 2 posts that get stale is worse than no blog.
- GitHub README should link to the site (not the other way around for docs). The site is the canonical home.
- Social proof matters: if any notable repos adopt noxaudit, feature them (with permission).

### Open source community infrastructure

The website drives people to the repo. The repo needs to support the traffic.

**Outcome**: A contributor can go from "I want to add a Rust language variant for the security focus" to an open PR in under an hour. Issues are triaged, discussions are active, and the project feels alive.

**What this means**:
- Issue templates (bug report, feature request, new focus area, new language variant)
- Discussion board enabled for questions and ideas
- Good first issue labels maintained — these are the on-ramp
- CONTRIBUTING.md updated with architecture overview so contributors understand where code goes
- PR template with checklist (tests, docs, changelog)

## Technical decisions

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| **Site framework** | Next.js (App Router, static export) | Same stack as eventual dashboard; large ecosystem; Vercel deployment is trivial |
| **Docs framework** | Nextra or Fumadocs (Next.js-based) | Lives in same repo/deployment as the main site; avoids a second framework |
| **Hosting** | Vercel (free tier) | Zero-config for Next.js, global CDN, preview deploys for PRs |
| **Domain** | noxaudit.com | Check availability; alternatives: noxaudit.dev, getnoxaudit.com |
| **Analytics** | Plausible or Fathom | Privacy-respecting, no cookie banner needed, developers won't block it as aggressively |
| **Terminal demo** | Custom React component or asciinema embed | More polished than a GIF, lighter than a video |

## Dependencies & sequencing

```
Brand identity ─────────────────────────── (start first, unblocks everything visual)
  │
  ├── Landing page ─────────────────────── (needs brand identity)
  │     └── deploys to noxaudit.com
  │
  ├── Documentation site ───────────────── (needs brand identity, can parallelize with landing page)
  │     └── deploys to noxaudit.com/docs
  │
  └── Social preview / GitHub assets ──── (needs brand identity)

SEO / content ──────────────────────────── (needs docs site live first)
Community infrastructure ───────────────── (independent, can start anytime)
```

Brand identity is the gating item for all visual work. Landing page and docs can be built in parallel once identity is established. Community infrastructure is independent.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Site looks like vaporware (promises without substance) | Developers disengage; hurts credibility | Only show features that exist in the current release; mark roadmap items clearly as "coming soon" |
| Over-investing in site before product-market fit | Time wasted on polish instead of product | Keep it minimal — one page, one docs site. No custom illustrations, no animations beyond the terminal demo |
| Docs drift from code | Users follow outdated instructions, get frustrated | Docs live in the repo, CI checks for broken links, version docs alongside releases |
| Domain unavailable | Naming friction | Secure domain early; have fallback options ready |
| SEO takes months to build | No traffic from search in the short term | Supplement with dev community posts (Reddit, HN, dev.to) at launch; SEO is the long game |

## How we'll know it's working

- **Traffic**: noxaudit.com receives >1,000 unique visitors/month within 3 months of launch
- **Conversion**: >10% of site visitors click through to GitHub repo or run `pip install`
- **Docs engagement**: Average session duration on docs >2 minutes (people are reading, not bouncing)
- **Search ranking**: First page for "noxaudit" (table stakes) and top 3 pages for "AI code audit tool" within 6 months
- **Referral source**: The site becomes the #1 referral source for GitHub repo traffic (surpassing direct GitHub discovery)
