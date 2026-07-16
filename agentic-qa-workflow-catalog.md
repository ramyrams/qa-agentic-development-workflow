# Agentic QA Workflow Catalog — AI Initiative Ideation
### Every workflow worth considering, organized by lifecycle, rated, and prioritized

**How to read this:** 26 workflows across 7 lifecycle stages. Your five seed ideas are expanded first (marked ★). Each entry: what it is → why it pays → how it's built (primitives + tooling) → **V**alue / **E**ffort / **R**isk rating (H/M/L). Section 8 turns the catalog into a Now / Next / Later roadmap — do not attempt all of these; the catalog exists so you can choose deliberately.

**Stack context:** Cypress today; several workflows use **Playwright MCP** as an *exploration and healing engine alongside Cypress* — Playwright now ships first-party test agents (planner, generator, healer) that run on its MCP server and work inside VS Code agent mode / Copilot, driving a real browser through the accessibility tree rather than screenshots. You can adopt that engine for discovery/healing without migrating your suite.

---

## 1. Requirements & Test Design Stage

### ★ 1.1 KT / Meeting Video → Test Cases (your idea #1) — V:H E:M R:M
Knowledge-transfer sessions contain behavior details that never make it into written requirements — currently lost.
**Design:** Deterministic first: pull the **transcript** (Teams/Zoom auto-transcripts; or Whisper-class speech-to-text on the video file) — never feed video to the model. Then a `kt-to-testcases` skill: pass 1 extracts features, behaviors, edge cases, and open questions from the transcript with timestamps; pass 2 feeds them into your existing `/design-test-cases` prompt (formal techniques applied); output lands in `qa/test-cases/` formatted by your instructions file, with each case traced to a transcript timestamp so reviewers can verify.
**Guardrails:** Recording/consent policy check (governance item — your lane); everything extracted is marked "derived from KT — confirm with SME" until a human accepts it; the open-questions list is often the most valuable output.

### 1.2 AC / Requirements Ambiguity Linter — V:H E:L R:L
An agent pass over every new user story before sprint start: untestable adverbs, missing actors, undefined states, contradictions — powered by your existing `requirements-analysis` skill. Cheapest high-value item in this catalog; output is questions for the BA, not rewrites.

### 1.3 Requirements-Change Impact Analysis — V:M E:M R:L
When a story/AC changes, an agent maps the delta to affected test cases and specs (traceability IDs + code search) and proposes the update list. Kills the "requirement changed, tests silently stale" failure mode.

### 1.4 Test Case Deduplication & Suite Rationalization — V:M E:M R:L
Periodic agent pass over `qa/test-cases/` + spec titles: near-duplicate detection, overlap clusters, orphaned cases with no traceability. Output: a rationalization proposal PR — human decides.

---

## 2. Test Creation & Authoring Stage

### ★ 2.1 Live Element Exploration for Script Development (your idea #3) — V:H E:L R:L
**Design:** Playwright MCP in VS Code gives the agent a live browser it drives via the accessibility tree — the agent navigates your app, snapshots each page, and emits: the element inventory, role/label-based locator suggestions, and — for your conventions — a **`data-cy` gap report** (elements a test would need that lack your required attribute → a dev ticket, generated). Feed the inventory straight into page-object generation: "explore /checkout, then scaffold the page object per our conventions."
**Why this is the best on-ramp:** near-zero build (install the MCP server, add one prompt file `/explore-page`), immediate speed-up on every new feature, read-only against the app.
**Guardrails:** point it at test environments only; the selector map it produces becomes a reference in your `cypress-authoring` skill so it compounds.

### ★ 2.2 Self-Exploring API Testing (your idea #4) — V:H E:M R:M
**Design:** Two modes. *Spec-driven:* agent reads your OpenAPI contracts (already in your `api-contract-testing` skill), generates the full case checklist per endpoint (happy/authz matrix/per-field validation/boundaries/idempotency), probes the sandbox to verify actual vs. documented behavior, and reports **contract drift** — often more valuable than the tests themselves. *Discovery-driven:* for undocumented services, agent explores from a seed endpoint + HAR captures and drafts the missing contract for human confirmation.
**Guardrails:** sandbox environments only, enforced by the test-data-setup skill's deny-list; rate-limited probing; destructive verbs (DELETE) require the approval gate.

### 2.3 Manual Test Case → Automation Conversion Pipeline — V:H E:L R:L
Your functional team's case library is a scripted backlog. `/convert-manual-case` (already in your catalog) run as a batch program: agent triages which cases are automatable (and at which level — API beats UI), converts in priority order via the plan-gate flow. Bridges your two teams; the triage judgment ("this one stays manual, here's why") is the interesting output.

### 2.4 HAR / Session Recording → Test Draft — V:M E:M R:L
Engineer performs the flow once with recording on; agent converts the HAR + DOM snapshots into a spec draft with real request/response shapes for intercepts. Good for complex flows where writing intercepts by hand is the slow part.

### 2.5 Design-to-Test (Figma/mockup ingestion) — V:M E:M R:M
Agent reads design artifacts and drafts UI acceptance checks (states, validation messages, responsive breakpoints) *before* the feature is built — shifts test design genuinely left. Value depends on how disciplined your design files are.

---

## 3. Exploratory & Autonomous Testing Stage

### ★ 3.1 Charter-Driven Agentic Exploratory Testing (your idea #2) — V:H E:M R:M
**Design:** Marry your `/exploratory-charter` prompt with Playwright MCP execution: the charter (mission, scope, risks, tours, time-box) becomes the agent's instruction; the agent explores the live app through the accessibility tree, executing tours (back-button, interruption, boundary, role-switch…), logging observations, screenshots, and anomaly candidates; output is the structured debrief — bugs to confirm, questions raised, automation candidates.
**The critical framing:** the agent is a **tireless junior explorer, not a judge** — every "bug" it finds is a *candidate* a human confirms (models hallucinate defects and miss business-logic issues). Its real strengths: coverage breadth, tirelessness on tedious tours, and perfect session logging.
**Guardrails:** sandboxed environment + seeded data (test-data-setup skill); disallow destructive actions without confirmation; findings flow through `/bug-report` with a human gate.

### 3.2 Nightly Autonomous Smoke Crawl — V:M E:M R:M
A scheduled agent walks critical paths nightly (before the expensive suite runs), reporting broken flows, console errors, dead links, and a11y violations. Complements, never replaces, asserted tests — it finds "obviously broken," not "subtly wrong."

### 3.3 Accessibility Exploration Agent — V:M E:L R:L
Same MCP loop, a11y charter: keyboard-only tours, ARIA/label gaps, contrast flags. QA teams rarely have a11y bandwidth; an agent makes a baseline pass nearly free and the findings are dev tickets, not test code.

---

## 4. Execution, Triage & Reporting Stage

### 4.1 Allure Analysis & Manager Reporting — **already designed** ✔
Your flagship: parse → classify → ledger → report. (See allure-analysis-automation-design.md.)

### 4.2 Failure Ledger & Pattern Intelligence — **already designed** ✔
Signature-based recurrence, flaky candidates, chronic offenders, pattern reports.

### 4.3 CI Pipeline Failure Debugging Agent — V:H E:M R:L
Extends triage beyond test failures to *pipeline* failures: agent reads the CI log, classifies (infra / dependency / config / genuine test failure), checks against known-signature history, and posts the diagnosis to the PR. Pairs naturally with the ledger.

### 4.4 Smart Regression Selection (Test Impact Analysis) — V:H E:H R:M
Agent maps a code diff to the affected test subset (dependency graph + coverage data + ledger history) and proposes the minimal pre-merge run, with full suite nightly. Big execution-time savings; requires trust built through a shadow period where skipped-test escapes are measured. Do this only after the ledger has months of data.

### 4.5 Release Readiness Assessment — V:M E:L R:L
A prompt that composes existing assets: current ledger state + last N runs + open known-issues → a go/no-go evidence pack for the release meeting. Almost free once 4.1/4.2 exist.

---

## 5. Maintenance & Healing Stage

### ★ 5.1 Test Healing Agent (your idea #5) — V:H E:M R:**H**
**Current state of the art:** Playwright ships a first-party **healer agent** (with planner and generator, since v1.56) that re-runs failing tests and repairs broken locators and steps via accessibility-tree snapshots. For Cypress there is no first-party equivalent — you build the workflow.
**Design for your stack:** healing is a *constrained repair loop*, not magic: on failure → flaky-triage skill classifies first (this is the gate) → only **locator/timing-class** failures are healable → agent re-explores the page via Playwright MCP, finds the moved element by role/label, proposes the updated `data-cy`/page-object fix → **as a PR, never a direct commit** → reviewer approves.
**The risk that makes this R:H — and why your rules already anticipate it:** an unconstrained healer converges on exactly the anti-fix your agent rules ban (AW — weakening assertions / adding waits to force green), and worse, it can *heal away a real product bug* (the button moved because a dev broke the layout — the test was right). Hence the iron rules: classification before healing; healer may change locators and waits-discipline-compliant synchronization, **never assertions or expected values**; every heal is ledger-logged so "this test needed healing 4 times this quarter" becomes a signal (that's a design problem, not a maintenance chore).

### 5.2 Selector & Convention Drift Audit — V:M E:L R:L
Scheduled agent pass over the spec tree: selector-policy violations, `cy.wait(ms)` creep, independence violations, assertion-strength smells ("would this fail if the feature broke?"). Output: a debt report ranked by risk. Your instructions prevent new debt; this finds the old and the leaked.

### 5.3 Coverage Gap Analysis Agent — V:H E:M R:L
Cross-references: features/stories ↔ test cases ↔ specs ↔ (optionally) code coverage, and reports untested behaviors ranked by risk — turning "what are we missing?" from a quarterly anxiety into a queryable answer.

### 5.4 Dead & Redundant Test Detection — V:M E:L R:L
Ledger + git history: tests that never fail (possibly asserting nothing), tests for removed features, duplicate-coverage clusters. Proposal PR; humans decide. Suites only grow unless something argues for deletion.

---

## 6. Test Data & Environment Stage

### 6.1 Intelligent Test Data Generation — V:H E:M R:M
Agent generates boundary-rich, persona-based synthetic datasets from your schemas/contracts (never from production data — governance line), maintained as fixtures via the test-data-setup skill. Pairs with 2.2's per-field validation cases.

### 6.2 Environment Health Sentinel — V:M E:L R:L
Pre-suite agent check: services up, seed data intact, versions matched — with a plain-language "environment not test-worthy" verdict. Kills the "40 failures because the env was broken" waste, and feeds the ledger's environment classification.

### 6.3 Data Drift Detector — V:M E:M R:L
Scheduled comparison of seeded data vs. expected datasets catalog; drift report before it becomes mysterious test failures. (This was your capstone-backlog example — it's real.)

---

## 7. Team, Process & Knowledge Stage

### 7.1 Test PR Review Agent — **already designed** ✔ (`/review-test-pr` + read-only reviewer)

### 7.2 QE Onboarding Agent — V:M E:L R:L
An agent grounded in your seven framework documents + repo conventions that answers new-joiner questions with citations to the source doc. Your documentation program becomes interactive; near-zero build (a skill wrapping the docs).

### 7.3 Living Documentation Generator — V:M E:L R:L
Agent regenerates human-readable coverage documentation from specs + test cases (feature → behaviors covered → last-run status) on a schedule. Managers read this instead of asking.

### 7.4 Defect Pattern Miner (beyond test failures) — V:M E:M R:M
Extend the ledger philosophy to the bug tracker: agent mines closed defects for clusters (component, root cause, escape phase) and reports where testing investment should shift. This is the "QE intelligence" layer managers remember.

### 7.5 Sprint Test Status Narrator — V:L E:L R:L
Daily/weekly one-paragraph status from run data + board state for standups. Low value alone; nearly free once 4.1 exists — a composition, not a build.

---

## 8. Prioritized Roadmap — Now / Next / Later

**Selection logic:** maximize early wins that compound (assets feeding other assets), sequence risk after trust, and never run two H-effort builds at once.

**NOW (this quarter) — foundations + fast wins**
1. **4.1/4.2 Allure + ledger** (in flight) — the intelligence backbone; five later items feed on it.
2. **2.1 Element exploration** (★#3) — days of effort, daily payoff, and it introduces Playwright MCP safely (read-only).
3. **1.2 AC ambiguity linter** — cheapest quality shift-left; reuses an existing skill.
4. **2.3 Manual→automation pipeline** — bridges functional and automation teams; reuses an existing prompt.

**NEXT (quarter 2) — expansion on proven rails**
5. **2.2 Self-exploring API testing** (★#4) — contracts already packaged as a skill; sandbox rules already exist.
6. **3.1 Agentic exploratory testing** (★#2) — MCP now familiar from 2.1; charter prompt already exists.
7. **4.3 CI failure debugging** — natural ledger extension.
8. **5.3 Coverage gap analysis** — needs the traceability discipline items 1.2/2.3 establish.
9. **1.1 KT video → test cases** (★#1) — after the transcript pipeline and consent policy are settled.

**LATER (quarter 3+) — high-trust, high-risk items**
10. **5.1 Healing agent** (★#5) — deliberately last of your five: it needs the ledger (classification gate), the audit posture (PR-only, no-assertion-change rule), and organizational trust that the NOW/NEXT items build. A healer deployed before triage discipline exists institutionalizes assertion-weakening at machine speed.
11. **4.4 Smart regression selection** — needs months of ledger data and a measured shadow period.
12. **6.1 Test data generation**, **7.4 Defect pattern miner**, **3.2 nightly crawl** — as pull demands.

**Standing filter for anything new** (same as your intake rule): name the recurring activity it serves, the evidence it will produce, and who maintains it — or it stays an idea.

---

## 9. Three Cautions for the Whole Initiative

1. **Autonomy is earned per-workflow, not granted per-initiative.** Every workflow above starts with a human gate and sheds it only after shadow-mode evidence — the Allure pattern. The healer is the extreme case; the exploratory agent is close behind.
2. **The model explores; scripts measure; humans judge.** Workflows fail when these swap — an agent "judging" release readiness without ledger data, or a human hand-counting failures a script should parse.
3. **Everything routes through the estate.** Each adopted idea becomes audited primitives (skills/prompts/agents in `.github/`), enters the intake rule, appears in the discoverability index, and gets eval coverage — otherwise the initiative produces demos, not capability.

*Companion docs: framework guide · curated catalog · audit checklist · Allure design · competency ladder · kata set. Sources for Playwright agents/MCP state: playwright.dev release notes and current ecosystem guides — verify agent capabilities against the Playwright docs at adoption time; this area moves monthly.*
