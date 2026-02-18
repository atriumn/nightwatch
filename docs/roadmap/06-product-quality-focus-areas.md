# Product Quality Focus Areas

## The gap

All 7 current focus areas audit code **for engineers**: security vulnerabilities, dead code, stale docs, test gaps. These are valuable. But they miss an entire category of problems that live in the code and ship to users:

- The help section describes a feature that was renamed 3 months ago
- The onboarding flow has a dead end if the user skips step 2
- A button label says "Save" but the action is "Submit and close"
- The error message says "Something went wrong" instead of telling the user what to do
- The responsive layout breaks at 768px because someone hardcoded a pixel value
- The loading state shows a spinner forever on slow connections with no timeout or fallback
- Screen readers can't navigate the main menu

These aren't "bugs" in the traditional sense. The code works. The tests pass. But the product is broken. These issues typically get caught by QA teams, design reviews, or user complaints — all expensive, all late. An AI reviewing the actual templates, copy, styles, and routing logic can catch many of them at the code level, before they ship.

## What this changes about noxaudit

Today noxaudit's value proposition is: "keep your codebase healthy." Adding product quality focus areas shifts it to: "keep your **product** healthy." That's a larger market, a different buyer (product/design leads, not just engineering), and a stronger justification for the SaaS tier.

It also creates differentiation that's hard to replicate. Every SAST tool does security scanning. No tool does AI-powered UX copy review on a nightly schedule.

## Proposed focus areas

### 1. UX Copy & Microcopy (`ux-copy`)

**What the AI reviews**: Every piece of user-facing text in the codebase — button labels, error messages, empty states, tooltips, confirmation dialogs, placeholder text, notification content, onboarding copy.

**What it flags**:

| Severity | Example |
|---|---|
| Critical | Error message exposes internal state ("NullPointerException in UserService.java:47") |
| High | Destructive action has no confirmation ("Delete" button with no "Are you sure?") |
| High | Error message is unhelpful ("Something went wrong" with no guidance) |
| Medium | Inconsistent terminology (some buttons say "Save," others say "Submit," others say "Confirm" for equivalent actions) |
| Medium | Empty state provides no guidance (blank page with no "Get started by..." prompt) |
| Low | Placeholder text is still in the codebase ("Lorem ipsum," "TODO: write copy") |
| Low | Tone inconsistency (formal in one area, casual in another) |

**File patterns**: Templates, components with rendered text, i18n/l10n files, error handler responses, notification templates, email templates.

**Why this matters**: Bad microcopy is the #1 source of support tickets that aren't actual bugs. Users get confused, can't complete actions, and blame the product. Fixing copy is also the cheapest fix possible — high-value findings with trivial remediation. Perfect auto-fix candidate.

**Considerations**:
- Needs to understand the difference between developer-facing strings (log messages) and user-facing strings (UI text). The prompt must be explicit about this boundary.
- i18n complicates things — the AI needs to review the source language strings, not the translation keys. If the codebase uses i18n, the prompt should focus on the default locale files.
- Tone guidelines vary by product. The prompt should either detect the dominant tone or accept a configured tone profile ("professional," "casual," "technical").

---

### 2. User Flow Coherence (`user-flows`)

**What the AI reviews**: Routing definitions, navigation components, page templates, form sequences, onboarding steps, wizard/stepper implementations, redirect logic, auth guards.

**What it flags**:

| Severity | Example |
|---|---|
| Critical | Route exists in navigation but the page component is missing or returns 404 |
| Critical | Form submit handler navigates to a route that doesn't exist |
| High | Multi-step flow has no way to go back from step 3 to step 2 |
| High | Auth-protected page has no redirect to login — user sees a blank page or error |
| High | Success action navigates to a page with no context ("Payment complete!" → lands on homepage with no confirmation) |
| Medium | Navigation item is visible but the feature behind it is disabled/incomplete |
| Medium | Dead-end page — no clear next action, no navigation back |
| Medium | Inconsistent flow patterns (some forms redirect after submit, others show inline confirmation) |
| Low | Orphan routes — defined in the router but unreachable from any navigation element |

**File patterns**: Route definitions, navigation/sidebar/header components, page-level components, form handlers, middleware/guards, redirect logic.

**Why this matters**: Broken or confusing flows are invisible in unit tests and code review. They emerge from the interaction between routing, components, and state — exactly the kind of cross-file semantic analysis that AI is good at. Users who hit a dead end don't file a bug; they leave.

**Considerations**:
- This requires sending related files together — the router, the navigation component, and the page components. The focus area's file gathering needs to be smarter than simple glob patterns.
- Framework-specific knowledge matters enormously here. React Router, Next.js App Router, Vue Router, and SvelteKit all define routes differently. Language/framework-aware prompts (Phase 2) are important for this focus area.
- Dynamic routes (e.g., `/users/:id`) can't be fully validated statically. The prompt should flag suspicions but acknowledge limits.

---

### 3. Accessibility (`a11y`)

**What the AI reviews**: HTML templates/JSX, component markup, CSS/styling, form elements, interactive elements, media elements, ARIA attributes, focus management, color values.

**What it flags**:

| Severity | Example |
|---|---|
| Critical | Form inputs with no associated label (no `<label>`, no `aria-label`, no `aria-labelledby`) |
| Critical | Interactive element not keyboard-accessible (`onClick` on a `<div>` with no `role`, `tabIndex`, or keyboard handler) |
| Critical | Image conveying information has no alt text (or `alt=""` on a meaningful image) |
| High | Color contrast below WCAG AA ratio (4.5:1 for text, 3:1 for large text) |
| High | Focus trap — modal or dialog with no way to escape via keyboard |
| High | Page has no heading hierarchy (no `<h1>`, or headings skip levels) |
| Medium | ARIA role used incorrectly (`role="button"` on an element that doesn't handle Enter/Space) |
| Medium | Touch target too small (< 44x44px for interactive elements on mobile) |
| Medium | Animation with no `prefers-reduced-motion` check |
| Low | Redundant ARIA (e.g., `role="button"` on a `<button>` element) |
| Low | Tab order doesn't follow visual order |

**File patterns**: JSX/TSX, HTML templates, Vue SFC `<template>` blocks, Svelte components, CSS/SCSS files, Tailwind class usage.

**Why this matters**: Accessibility is both a legal requirement (ADA, EAA, WCAG) and a product quality issue. Automated tools like axe-core catch some issues but miss many that require semantic understanding (is this image decorative or informational? does this div behave like a button?). AI can make judgments that rule-based tools can't. Also, a11y is increasingly a procurement requirement for enterprise sales (Phase 5 tie-in).

**Considerations**:
- This overlaps partially with rule-based linting tools (eslint-plugin-jsx-a11y, axe-core). The prompt should focus on semantic issues those tools miss, not duplicate them. Position as "catches what axe-core can't."
- Color contrast checking requires parsing actual color values from CSS/Tailwind. The AI can do this but may be unreliable — consider combining AI review with a deterministic contrast checker.
- This focus area has the strongest compliance angle. Map findings to WCAG 2.1 success criteria (1.1.1 Non-text Content, 2.1.1 Keyboard, etc.) for Phase 5 compliance framework integration.

---

### 4. Cross-Browser & Responsive (`compatibility`)

**What the AI reviews**: CSS files, Tailwind/utility classes, media queries, JavaScript using browser APIs, polyfills, viewport meta tags, responsive breakpoints, CSS features with limited browser support.

**What it flags**:

| Severity | Example |
|---|---|
| High | CSS feature used without fallback and not supported in target browsers (`container queries` without fallback, `has()` selector in a Safari-required app) |
| High | Hardcoded pixel widths on containers that should be fluid (`width: 1200px` instead of `max-width`) |
| High | `window.innerWidth` used for layout decisions instead of CSS media queries |
| Medium | Missing `viewport` meta tag or incorrect viewport settings |
| Medium | `hover`-dependent interactions with no touch alternative (dropdown menus that only open on hover) |
| Medium | Fixed positioning without accounting for mobile browser chrome (bottom nav hidden behind iOS Safari's address bar) |
| Medium | Z-index wars — arbitrary large values (`z-index: 9999`) suggesting stacking context issues |
| Low | CSS custom properties used without fallback for older browsers (if browser support matrix requires it) |
| Low | `@media` breakpoints inconsistent across the codebase (some use 768px, others 769px for "tablet") |

**File patterns**: CSS/SCSS/Less files, Tailwind config, PostCSS config, JavaScript with DOM/BOM API usage, browserslist config, polyfill imports.

**Why this matters**: "It works on my machine" is the oldest bug. Developers test on Chrome on a MacBook. Users are on Safari on an iPhone, or Firefox on a 1366x768 Windows laptop. These issues are expensive to find (require multi-device testing) and cheap to fix (CSS changes). The AI can flag likely problems by understanding browser support data and identifying patterns that typically break on specific platforms.

**Considerations**:
- Browser support is a moving target. The prompt needs to reference the project's stated browser support (browserslist, or configured). Without that, default to "last 2 versions of major browsers."
- This focus area is most valuable for web applications with consumer audiences. A developer tool or internal app may intentionally support only modern Chrome. The prompt should respect configured scope.
- False positive risk is higher here than in other focus areas — a CSS feature might be fine if the project uses a transpiler/polyfill. The prompt should check for PostCSS/Autoprefixer/Babel config before flagging.

---

### 5. Help & In-App Content Accuracy (`help-content`)

**What the AI reviews**: Help pages, FAQ content, tooltips, feature descriptions, settings labels and descriptions, changelog/release notes vs. actual features, marketing copy in the app (pricing pages, feature comparison tables), onboarding tours/walkthroughs.

**What it flags**:

| Severity | Example |
|---|---|
| Critical | Help article references a feature/button/menu that no longer exists |
| Critical | Settings page describes a behavior that doesn't match the code ("Enabling this will send a daily email" but the email feature was removed) |
| High | Feature comparison table lists capabilities that aren't implemented |
| High | Keyboard shortcut listed in help but not registered in the application |
| Medium | Tooltip describes old behavior ("Click to save draft" but the button now auto-saves) |
| Medium | Help content references UI elements by wrong name ("Click the Settings gear" but it's now labeled "Preferences") |
| Medium | Changelog entry describes a feature that was reverted or modified before release |
| Low | Help screenshots (referenced by path) point to files that don't exist |
| Low | Inconsistent feature naming between help content and actual UI |

**File patterns**: Help/FAQ page components, tooltip content, settings page components and their descriptions, feature flag definitions, keyboard shortcut registrations, changelog/release notes, marketing page components.

**Why this matters**: This is the example the user gave ("your help section doesn't reflect features correctly"), and it's one of the most common product quality failures. Help content is written once and rarely updated when features change. The AI can cross-reference help text against actual component/route/feature implementations and find the drift. This is essentially the `docs` focus area but pointed at user-facing content instead of developer-facing docs.

**Considerations**:
- This has strong overlap with the existing `docs` focus area. The distinction: `docs` reviews developer-facing documentation (README, API docs, code comments). `help-content` reviews user-facing content (help pages, tooltips, settings descriptions). The prompts must be explicit about this boundary.
- Cross-referencing requires the AI to see both the help content and the actual feature code. File gathering needs to include both help pages and the feature components they describe.
- Auto-fix is highly viable here — updating a tooltip or settings description is a low-risk text change.

---

### 6. Error & Edge State Handling (`error-states`)

**What the AI reviews**: Error boundaries, catch blocks with user-facing output, loading states, empty states, timeout handling, offline behavior, form validation messages, rate limit responses, 404/500 pages.

**What it flags**:

| Severity | Example |
|---|---|
| Critical | Unhandled promise rejection that crashes the page with no recovery |
| Critical | API error response displayed raw to the user (stack trace, internal error codes) |
| High | Loading state with no timeout — spinner shows forever if the API never responds |
| High | Form validation message is technical ("regex pattern mismatch") instead of helpful ("Please enter a valid email address") |
| High | Empty state gives no guidance (blank table with no "No items yet. Create your first..." message) |
| Medium | Network error shows generic message with no retry option |
| Medium | Partial failure not communicated (batch operation where 3/10 items fail silently) |
| Medium | Optimistic update with no rollback on failure (UI shows success, then nothing happens) |
| Low | Different error message styles across the app (some use toasts, some use inline, some use modals) |
| Low | Console.error visible in production (not user-facing but indicates unhandled cases) |

**File patterns**: Error boundary components, API call wrappers, form validation logic, loading/skeleton components, empty state components, error pages (404, 500), toast/notification systems.

**Why this matters**: The happy path always works. It's the error, loading, empty, and edge states that expose product quality. These are the states that make users trust or distrust an application. Most code reviews focus on the happy path. Most tests assert the happy path. The AI can systematically audit every error path and ask "what does the user actually see here?"

**Considerations**:
- This overlaps with `security` (error messages leaking internal state) and `patterns` (inconsistent error handling). The distinction: `security` asks "is this dangerous?", `patterns` asks "is this consistent?", `error-states` asks "is this a good user experience?"
- Framework-specific: React error boundaries, Vue error handlers, SvelteKit error pages, Next.js error.tsx — each framework has its own patterns.
- Auto-fix potential is high for the copy aspects (improving error messages) but low for structural aspects (adding error boundaries, implementing retry logic).

## How these interact with existing focus areas

```
                    Engineer-facing          User-facing
                    (existing)               (new)
                    ─────────────            ──────────────
Code quality:       patterns                 user-flows
                    hygiene                  compatibility

Documentation:      docs                     help-content
                                             ux-copy

Safety:             security                 a11y
                    testing                  error-states

Infrastructure:     dependencies
                    performance
```

The new focus areas don't replace the existing ones — they mirror them from the user's perspective. `patterns` asks "is the code consistent?" while `user-flows` asks "is the product coherent?" `docs` asks "are the READMEs accurate?" while `help-content` asks "are the tooltips accurate?" `security` asks "can an attacker exploit this?" while `a11y` asks "can a screen reader user navigate this?"

## Scheduling implications

The current weekly rotation has 7 slots for 7 focus areas. Adding 6 more means either:

**Option A: Two-week rotation**
```
Week 1:
  Mon: security         Tue: patterns      Wed: docs + hygiene
  Thu: testing          Fri: dependencies   Sat: performance

Week 2:
  Mon: a11y             Tue: user-flows    Wed: ux-copy + help-content
  Thu: error-states     Fri: compatibility  Sat: (catch-up / custom)
```

**Option B: Combined audits (recommended)**

The combined audit feature already saves ~80% tokens by deduping files. Group engineer and product focus areas that share file patterns:

```
Mon: security + a11y              (both review component markup)
Tue: patterns + user-flows        (both review routing + components)
Wed: docs + help-content + ux-copy (all review text content)
Thu: testing + error-states       (both review error handling)
Fri: dependencies + compatibility (both review config + browser targets)
Sat: hygiene + performance        (both review all source files)
```

This keeps the 6-day rotation while covering 13 focus areas. Token cost increases modestly (~20-30%) over today's 7-area schedule because file gathering is shared.

## Auto-fix suitability

| Focus Area | Auto-fix potential | Why |
|---|---|---|
| **ux-copy** | High | Text changes are low-risk, easy to verify |
| **help-content** | High | Updating descriptions and tooltips is mechanical |
| **error-states** | Medium | Improving error messages: yes. Adding error boundaries: needs review |
| **a11y** | Medium | Adding alt text, ARIA labels: yes. Restructuring heading hierarchy: needs review |
| **compatibility** | Low-Medium | Adding CSS fallbacks: yes. Restructuring layouts: needs review |
| **user-flows** | Low | Fixing dead routes is structural; can suggest but shouldn't auto-apply |

`ux-copy` and `help-content` are the strongest auto-fix candidates — they're text changes with low blast radius. This makes them excellent for the free tier auto-fix (alongside `hygiene` and `docs`), which expands the value of the free product and creates a stronger upgrade path.

## Impact on the SaaS dashboard

The dashboard (Phase 3.5) gets more interesting with product quality data:

- **Health score** can now reflect product quality, not just code quality. A repo with clean code but terrible error messages and broken help content shouldn't score 95.
- **Trends by category** (engineer-facing vs. user-facing) lets teams see if they're improving code but neglecting product, or vice versa.
- **Different audiences** care about different focus areas. An engineering manager looks at security/patterns/testing. A product manager looks at ux-copy/user-flows/error-states. A design lead looks at a11y/compatibility. The dashboard can offer role-based default views.
- **The "product health" angle** is a distinct selling point for the SaaS tier. Free users get code audits. Paid users get product audits. This is a cleaner upsell than gating auto-fix by focus area.

## Revised pricing consideration

If product quality focus areas become the paid differentiator:

| | Free | Pro | Team |
|---|---|---|---|
| **Engineer focus areas** (7) | All | All | All |
| **Product focus areas** (6) | a11y only | All 6 | All 6 + custom |
| **Auto-fix** | Hygiene + docs + a11y | + ux-copy, help-content, error-states | All |

This makes the free/paid boundary about **audience** (engineer vs. product team) rather than about **capability** (with/without auto-fix). A solo developer gets full engineering audits for free. A team that cares about product quality pays. That's a cleaner story.

## Dependencies

```
Phase 1 (OSS Foundation) must ship first
  │
  ├── Language/framework-aware prompts (Phase 2) ──── strongly benefits user-flows,
  │                                                    compatibility, a11y
  │
  ├── Custom focus areas (Phase 2) ──────────────── product focus areas should use
  │                                                  the same mechanism
  │
  └── Cross-file analysis (Phase 2) ────────────── required for user-flows,
                                                    help-content
```

Product focus areas should land **mid-Phase 2** — after the custom focus area mechanism exists (so they're built on the same foundation) and after language-aware prompts (so they can produce framework-specific findings).

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Too many focus areas overwhelm users | Confusion, config fatigue | Group into categories (engineer / product), sane defaults, don't require configuring all 13 |
| Product focus areas produce vague findings | Users dismiss them as noise | Invest in prompt quality; these prompts are harder to write than code-focused ones because "good UX" is more subjective than "has a SQL injection" |
| AI hallucinates UI issues that don't exist | Trust erosion | Higher confidence threshold for product findings; always include file/line references so users can verify immediately |
| "We already have QA for this" | Low adoption in teams with existing QA processes | Position as augmenting QA, not replacing it — catches issues before QA, reduces QA cycle time, covers things QA doesn't check every sprint |
| Accessibility findings trigger legal anxiety | Users are scared to see a list of a11y violations | Frame positively ("here's what to improve") not punitively ("you're non-compliant"). Include severity so teams can prioritize, not panic |
