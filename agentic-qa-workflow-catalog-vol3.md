# Agentic QA Workflow Catalog — Volume 3: The Deep Cut
### 28 further workflows across dimensions Volumes 1–2 didn't touch — plus the master index and a shortlisting scorecard for your management finalization

**What Volume 3 adds:** Vol 1 covered the test lifecycle; Vol 2 covered business-outcome themes and AI-system QE. Vol 3 mines four spaces that remain: **(G)** quality dimensions of the *application* that almost no team tests today, **(H)** the *self-improving* QE organization — workflows that make your estate and team learn automatically, **(I)** transition & platform plays, and **(J)** the *business of quality* — workflows that speak money. These tend to be the most differentiating ideas precisely because nobody's doing them yet.

**Ratings:** V/E/R as before. Items marked 💎 are, in my judgment, the highest insight-per-effort picks in this volume.

---

## Theme G — Untested Quality Dimensions of the Application
**Business output: entire defect classes currently invisible to your suite become testable — mostly with agents doing tedium no human team was ever going to staff.**

### G1. 💎 Analytics Instrumentation Testing — V:H E:L R:L
Marketing and product decisions run on tracking events — and tracking is among the least-tested code in any web app. Agent tours key journeys (Playwright MCP), captures the analytics beacons (network layer), and validates against the tracking plan: events fire, properties populated, no duplicates, consent state respected. **The pitch writes itself:** "the data your product decisions are based on is now tested." A broken funnel event costs real money invisibly for months.

### G2. Privacy, Consent & Cookie Compliance Testing — V:H E:M R:L
Agent verifies the compliance *behavior*, not the banner's existence: no tracking beacons before consent; rejection actually suppresses them; data-subject flows (export/delete) work end-to-end; cookie inventory matches the declared policy. Regulatory exposure made testable — and squarely in your governance lane. Pairs with G1 (same beacon-capture machinery).

### G3. Time, Timezone & DST Behavior Testing — V:M E:L R:L
The bug class every enterprise app has and almost none tests systematically. Agent designs and scaffolds clock-manipulation tests (`cy.clock` / container TZ): month-end, year-end, DST transitions, cross-timezone rendering of the same record, expiry boundaries. A classic "agent removes the tedium that made us skip it" play.

### G4. Financial Calculation Reconciliation Testing — V:H E:M R:M
Wherever your app computes money (totals, tax, discounts, proration): agent derives an independent reference implementation from the business rules, generates high-volume randomized inputs, and reconciles app output vs. reference (property-based testing, C2, specialized to currency). Rounding and order-of-operations bugs are business-visible defects; this is their systematic hunter.

### G5. Notification & Webhook Delivery Testing — V:M E:M R:L
Email/SMS/push/webhook side-effects, chronically asserted-around rather than asserted-on. Agent-designed harness: capture endpoints (mail-trap, webhook sink), delivery assertions, content validation against templates (extends C10), retry/failure-path behavior.

### G6. Concurrency & Race-Condition Probing — V:M E:M R:M
Agent designs targeted concurrency probes for state-mutating flows: double-submit, parallel edits to one record, rapid navigation during in-flight requests — the "two tabs" bug class. Deterministic harness executes; model designs the probe matrix from the app's state model (see H5).

### G7. Degraded-Network & Offline Behavior Testing — V:M E:L R:L
Agent tours journeys under throttled/intermittent/offline network profiles: graceful errors vs. silent data loss, retry behavior, state recovery. Users live on bad networks; test environments never do.

### G8. Search & Relevance Testing — V:M E:M R:M
If the app has search: golden-query sets with graded expected results, tolerance-based relevance assertions, regression detection when the index or ranking changes. LLM-as-judge assists relevance grading with human calibration — the E-theme machinery pointed at a classic feature.

### G9. Backward Compatibility & API Versioning Sentinel — V:M E:M R:L
Agent replays the previous release's contract tests against the new build and diffs API surfaces (breaking-change detection on params, responses, defaults). Catches the "we didn't think anyone used that field" incident class before partners do.

### G10. Database Migration Testing Agent — V:M E:M R:M
For releases containing schema migrations: agent generates pre/post validation (row counts, integrity, spot reconciliation on representative data), plus rollback-path verification. Migrations are the highest-blast-radius change type most suites ignore entirely.

### G11. Usability Heuristic Evaluation Tour — V:L→M E:L R:L
Agent tours new UI against classic heuristics (visibility of state, error prevention, consistency) and drafts a findings report for human UX review. Not a UX-researcher replacement — a cheap first-pass filter that catches the obvious before humans spend time.

---

## Theme H — The Self-Improving QE Organization
**Business output: the estate, the suite, and the team get better automatically from their own exhaust — this is where compounding lives, and it's the most "meaningful" theme in all three volumes.**

### H1. 💎 Incident → Test Feedback Loop ("escape-driven coverage") — V:H E:L R:L
Standing rule, agent-enforced: every production incident/escaped defect triggers an agent analysis — *which test should have caught this and why didn't it exist?* — producing a coverage-gap classification (untested path / weak assertion / untested config / data case) and a draft test. Over a year, your suite provably converges on what actually escapes. The single best answer to a manager asking "is testing improving?"

### H2. 💎 Self-Improving Estate (review-mining loop) — V:H E:M R:M
Agent periodically mines the exhaust of your own agentic workflow — rejected plans, corrected outputs, PR review comments on generated tests, K1-style session failures — clusters the recurring correction patterns, and **proposes instruction/skill/prompt amendments as PRs**. The estate learns from every correction instead of waiting for a human to notice a pattern. Guardrail: proposals only, human merge, eval-verified per your audit rules — the estate must never rewrite itself unsupervised.

### H3. Session Analytics for Training Priorities — V:M E:L R:L
Aggregate (anonymized) analysis of the team's agent sessions: which failure codes (WC/SG/TM/SE/SA/AW) occur most, per prompt and per person-level cohort → directly sets the next kata cycle and ladder focus. Your competency program, steered by data instead of instinct.

### H4. Suite Architecture Refactoring Agent — V:M E:H R:M
Periodic whole-suite structural analysis: duplication across page objects, dead helpers, inconsistent patterns between older and newer specs, misplaced abstraction — with a staged refactoring plan executed via plan-gated PRs. The "we should really clean up the suite" project that never gets staffed, agent-staffed.

### H5. 💎 Model-Based Testing (the state-model play) — V:H E:H R:M
The most intellectually meaningful item in this volume: agent helps build and maintain an explicit **state model** of the application (states, transitions, invariants — derived from exploration, specs, and requirements), then *generates* test paths from the model: all-transitions coverage, shortest-path regressions, invariant checks. Tests stop being hand-picked examples and become derived artifacts of a reviewed model; when the app changes, you update the model, not fifty specs. Also becomes the probe-matrix source for G6 and the tour map for exploratory agents. High effort — pilot on one well-bounded feature domain first.

### H6. Postmortem & Retro Synthesis Agent — V:L→M E:L R:L
Agent drafts test-run retros and incident postmortem quality sections from ledger + trajectory data (what the process caught/missed, where time went), so retros start from evidence instead of memory.

---

## Theme I — Transition & Platform Plays
**Business output: strategic technology moves that are normally multi-quarter slogs become agent-assisted programs with human review gates.**

### I1. 💎 Cypress → Playwright Migration Assistant — V:H E:H R:M
You're already adopting Playwright MCP for exploration and healing; if a suite migration ever makes strategic sense, it's now an agentic program rather than a rewrite: agent converts specs in dependency order (commands → page objects → specs), maps API idioms, runs both suites in parallel per converted module, and reports parity via the ledger. Decision, not recommendation — but have the assessment: agent produces the *migration cost/benefit analysis* (idiom inventory, custom-command portability, parallel-run cost) so the decision is evidence-based. Even if the answer is "stay," the analysis is worth having on paper.

### I2. AI Testing Tool Evaluation Harness — V:M E:L R:L
Vendors will pitch you constantly (Vol 2's caution about "10x" claims). Standing evaluation kit: your representative task set + graded rubrics + trajectory review, applied identically to any candidate tool. Procurement decisions on your evidence, not their demo — and reusable every time.

### I3. Multi-Framework Quality Facade — V:M E:M R:M
As tools proliferate (Cypress + Playwright MCP + API runners + AI evals), agent-maintained unification at the *reporting* layer: everything normalizes into the ledger's signature/classification scheme, one manager view regardless of engine. Protects your intelligence layer from tool churn — the ledger is the asset; runners are replaceable.

### I4. Vendor-Delivered Software Acceptance Testing — V:M E:M R:L
Enterprise-specific: when vendors/SIs deliver builds, agent generates the acceptance suite from the contract/SOW requirements and produces the acceptance evidence pack (D2 machinery). Turns contractual acceptance from a checkbox ritual into executable verification — procurement will love you.

### I5. New-Codebase Quality Assessment ("due diligence mode") — V:L→M E:L R:L
For inherited/acquired/unfamiliar codebases: standardized agent assessment — test inventory and strength (mutation-lite), coverage vs. entry points, flakiness signals, convention drift — producing a quality posture report in days. Situational, but when needed it's needed urgently.

---

## Theme J — The Business of Quality
**Business output: quality gets a financial vocabulary — which is the vocabulary your final list will be judged in.**

### J1. 💎 Cost-of-Quality Accounting — V:H E:M R:L
Agent maintains a living COQ model from data you already generate: prevention (estate/training investment), appraisal (execution + review time from ledger/CI), internal failure (rework, triage hours), external failure (incident cost estimates). Every initiative item then reports in the same currency: "the ledger cut appraisal cost X hrs/week; escape-driven coverage cut external failure Y%." **This is the workflow that makes every other workflow fundable.**

### J2. SLA / SLO Verification Suite — V:M E:M R:L
Where contracts promise service levels: agent-generated verification runs (response-time distributions, availability probes on critical transactions) with breach-risk trending — before the customer's lawyers measure it for you. Extends A2/C8 machinery.

### J3. Competitive Journey Benchmarking — V:L→M E:M R:M
Agent runs the same journeys (signup, search, checkout-equivalent) on competitor products: steps, time, friction points, performance — a quarterly UX-competitiveness brief. Legal/ethical review first (public surfaces only, ToS respected); product management will fight to fund this one.

### J4. Beta / UAT Feedback Synthesis — V:M E:L R:L
Agent synthesizes beta-program and UAT feedback into clustered findings mapped against coverage (A4 machinery pointed at pre-release cohorts), closing the loop between "what testers found" and "what users-in-beta found that testers didn't" — itself a coverage-gap signal (feeds H1).

### J5. Release-Notes & Claim Verification — V:L E:L R:L
Small but embarrassing-defect-preventing: agent verifies every claim in draft release notes against actual shipped behavior (feature present, flag on, fix verified by a run). No more announcing features that didn't make the cut.

### J6. Quality Narrative for the Board — V:M E:L R:L
Composition of F1 + J1 + H1 into the twice-yearly artifact leadership actually reads: quality posture, trend, escapes prevented, cost curve, AI-initiative ROI (measured, per your own rule, on your baselines). The initiative's own report card, generated by the initiative.

---

## MASTER INDEX — all three volumes at a glance (84 workflows)

| Vol | Theme | Items | Center of gravity |
|---|---|---|---|
| 1 | Requirements & design | 4 | KT→cases ★, ambiguity linting |
| 1 | Creation & authoring | 5 | Element exploration ★, self-exploring API ★, manual→auto |
| 1 | Exploratory & autonomous | 3 | Charter-driven agentic ET ★, a11y |
| 1 | Execution & triage | 5 | Allure+ledger ✔, CI debugging, smart regression |
| 1 | Maintenance & healing | 4 | Healer ★, drift audit, coverage gaps |
| 1 | Data & environments | 3 | Data generation, env sentinel |
| 1 | Team & process | 5 | PR review ✔, onboarding, living docs |
| 2 | A: Production-signal (shift-right) | 6 | Telemetry alignment, synthetic journeys, VoC mining |
| 2 | B: Developer partnership | 6 | AI-code validation gate, bug repro, unit-test standards |
| 2 | C: Test strength | 11 | Mutation triage, property-based, contracts, visual, i18n, perf |
| 2 | D: Risk & compliance | 4 | Defect prediction, evidence automation |
| 2 | E: QE for AI systems | 6 | Evals, prompt regression, red-team, guardrails |
| 2 | F: QE operations | 4 | KPI narrator, defect mining |
| 3 | G: Untested dimensions | 11 | Analytics testing 💎, privacy, time/DST, money reconciliation |
| 3 | H: Self-improving QE | 6 | Incident→test loop 💎, self-improving estate 💎, model-based 💎 |
| 3 | I: Transition & platform | 5 | Migration assistant 💎, tool-eval harness |
| 3 | J: Business of quality | 6 | COQ accounting 💎, SLA verification, board narrative |

---

## SHORTLISTING SCORECARD — how to finalize your management list

Score every candidate 1–5 on six criteria; weightings reflect an enterprise AI initiative that must show results and survive scrutiny:

| Criterion | Weight | The question |
|---|---|---|
| Business-outcome clarity | ×3 | Can I state the payoff in one sentence a VP repeats? |
| Time-to-first-evidence | ×2 | Measurable result inside one quarter? |
| Data/asset dependency | ×2 | Do its prerequisites (ledger, contracts, telemetry access) already exist? |
| Compounding | ×2 | Does it feed other workflows or improve automatically (Theme H test)? |
| Risk & governance load | ×2 (inverse) | Human gates, injection surface, production touch — what does the audit cost? |
| Team capability fit | ×1 | Buildable at the team's current ladder level? |

**Selection rules:** (1) ≤ 8 items on the management list — one flagship per business narrative (cost, speed, revenue, compliance, AI trust) plus at most three enablers. (2) Never two H-effort items in the same quarter. (3) Every item names its metric and its owner on the slide, or it doesn't go on the slide. (4) Everything else is the governed backlog — visible, scored, intake-gated, not promised.

**If I were forced to pick the eight today** (your call, but a strawman helps): Allure+ledger ✔ (in flight, the proof point) · Element exploration ★ (fast win) · Incident→test loop H1 💎 (the "quality is improving" evidence engine) · Analytics instrumentation G1 💎 (the business-data story) · AI-code validation B2 (the board-level risk) · Prompt regression E2 (cheapest AI-trust entry) · COQ accounting J1 💎 (makes the rest fundable) · Healer ★ (the visible "wow," sequenced last per Vol 1's discipline).

*Three-volume set complete: 84 workflows, one intake rule, one measurement layer. The catalog's job is to make your shortlist defensible — every item you cut, you cut for a scored reason.*
