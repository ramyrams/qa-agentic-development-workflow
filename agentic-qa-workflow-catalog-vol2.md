# Agentic QA Workflow Catalog — Volume 2: Business-Outcome Expansion
### 30 additional AI-in-Quality-Engineering workflows, organized by the business result they drive

**Relationship to Volume 1:** Volume 1 (26 workflows) covered the test-lifecycle core — design, creation, exploration, triage, healing, data, process. Volume 2 adds what the industry is doing **beyond the lifecycle**: production-signal quality (shift-right), developer-quality partnership, test *strength* engineering, risk & compliance, and — strategically for your organization — **quality engineering for AI systems themselves**. Together they form the complete ideation pool; your management shortlist should draw from both.

**Industry context (why these, why now):** the 2026 consensus across vendor and analyst material is consistent — testing is becoming a continuous discipline with quality signals collected from production as much as pre-release; risk-based prioritization and self-maintaining suites are mainstream; and validating AI-generated code and AI-powered features is the fastest-growing new mandate. Treat vendor ROI figures ("10x productivity", "95% maintenance reduction") as marketing until reproduced on your own eval harness — your measurement layer exists precisely so the initiative reports *your* numbers.

**Ratings:** V(alue)/E(ffort)/R(isk), H/M/L, same scale as Volume 1.

---

## Theme A — Production-Signal Quality (Shift-Right)
**Business output: protect revenue and customer experience by testing what users actually do and catching what pre-release testing structurally cannot.**

### A1. Production Telemetry → Test Coverage Alignment — V:H E:M R:L
Agent ingests analytics/RUM data (top user journeys, device/browser mix, feature usage frequency) and diffs it against your test suite: journeys users hit daily with thin coverage, and heavily-tested paths nobody uses. Output: a coverage-reallocation proposal. This is the single strongest "business alignment" story in the catalog — testing effort provably follows customer behavior.

### A2. Synthetic Journey Monitoring Agent — V:H E:M R:M
Scheduled agent runs the 5–10 revenue-critical journeys against production (safe accounts, no destructive actions) and raises a plain-language alert with trajectory evidence when a journey degrades. Bridges QE and ops; catches the "deploy broke checkout" class before customers report it. Guardrails: production-safe data contract, read-mostly actions, strict rate limits.

### A3. Session-Replay & Error-Log Mining — V:M E:M R:M
Agent mines frontend error logs / session-replay rage-click and abandonment signals, clusters them by signature (your ledger technique applied to production), and converts confirmed clusters into bug reports and regression-test candidates. Privacy gate: only anonymized/aggregate signals — a governance checklist item before build.

### A4. Voice-of-Customer Test Mining — V:H E:L R:L
Agent mines support tickets, app-store reviews, and NPS verbatims for recurring functional complaints, maps them to features and existing coverage, and proposes test scenarios for the gaps. Cheap (text in, analysis out), and it gives management the line they most want to hear: "our test suite now covers the top ten things customers actually complain about."

### A5. Canary / Release-Health Analysis Assistant — V:M E:M R:M
During staged rollouts, agent watches error rates, key transactions, and log anomalies for the canary cohort and drafts the promote/rollback recommendation with evidence. Human makes the call; the agent compresses the evidence-gathering from hours to minutes.

### A6. Log Anomaly Detection in Staging — V:M E:M R:L
Agent baselines "normal" staging/test-env log patterns per run and flags novel error signatures after each deploy — defects surface from logs before any test asserts on them. Feeds new signatures into the failure ledger.

---

## Theme B — Developer-Quality Partnership (Shift-Left Beyond QA)
**Business output: defects prevented cost ~10x less than defects found; QE expands influence upstream without expanding headcount.**

### B1. Unit-Test Generation Service for Developers — V:H E:M R:M
QE curates the skills/prompts (coverage standards, assertion-strength rules, mutation-resistance patterns) that developers use to generate unit tests — QE as the *standard-setter* for AI-generated tests rather than the author. Guardrail: generated tests are validated for strength (see C1), not just existence — AI happily generates tests that assert nothing.

### B2. AI-Generated-Code Validation Gate — V:H E:M R:M
The fastest-growing 2026 mandate: as developers ship more AI-generated code, QE owns the validation posture for it — a review agent + checklist targeting the known failure modes of generated code (hallucinated APIs, plausible-but-wrong logic, missing edge handling, license/snippet risks). Industry surveys show large confidence gaps and real rollback rates for AI-generated code; the team that owns this gate owns a board-level risk.

### B3. Testability Review at PR Time — V:M E:L R:L
A read-only agent pass on feature PRs (not test PRs): missing `data-cy` hooks, untestable tight couplings, missing seams for intercepts, absent error states. Findings as comments. Prevents the "we can't automate this feature" conversation three sprints later.

### B4. Bug Reproduction Agent — V:H E:M R:M
Input: a bug report. Agent attempts reproduction in the sandbox via Playwright MCP (UI) or API calls, produces a minimal repro script + environment/data conditions, and attaches it to the ticket. Reproduction is often the most expensive step of a defect's life; even a 50% hit rate is a large saving.

### B5. Defect Intake Intelligence — V:M E:L R:L
Agent triages incoming defects: duplicate detection against the tracker (signature-style matching), severity/priority suggestion with rationale, component routing, missing-info requests to the reporter. Compresses triage meetings; humans confirm.

### B6. Root-Cause Correlation Agent — V:M E:M R:M
For a production or staging defect, agent correlates: recent deploys, commit diffs to the affected component, config changes, and ledger history — and drafts a ranked root-cause hypothesis list with evidence. A hypothesis generator for humans, never an authority.

---

## Theme C — Test Strength Engineering (Quality of the Quality)
**Business output: a green suite that can't catch bugs is a liability with good optics; these workflows measure and raise what the suite can actually detect.**

### C1. AI-Guided Mutation Testing — V:H E:M R:L
Mutation tools (Stryker for JS/TS) inject code faults; surviving mutants = tests that didn't notice. The classic blocker is analysis effort — thousands of mutants. The agent triages survivors, clusters them by root weakness ("no assertions on error paths in module X"), and proposes the specific assertion improvements. This is the most rigorous answer available to "how good are our tests, actually?" — a management-credible metric (mutation score) with an AI-powered remediation loop.

### C2. Property-Based & Metamorphic Test Generation — V:M E:M R:L
For pure logic (pricing, validation, calculations): agent derives *properties* ("total never negative", "sort output is ordered permutation of input") and metamorphic relations ("same cart, different currency → proportional totals") instead of example cases — then generates fast-check/property tests. Finds the edge cases example-based testing structurally misses.

### C3. Test Oracle Assistant — V:M E:L R:L
The hardest problem in test design is knowing the expected result. Agent derives expected outcomes from contracts, requirements, and historical behavior, flagging where no reliable oracle exists (those become SME questions, not guessed assertions). Directly attacks the hallucinated-assertion failure mode of AI test generation.

### C4. Combinatorial / Pairwise Configuration Testing — V:M E:L R:L
Agent models your configuration space (browsers × roles × feature flags × locales), generates the pairwise-optimal matrix, and scaffolds the parameterized runs. Classic technique, historically skipped because the modeling is tedious — exactly the tedium agents remove.

### C5. Consumer-Driven Contract Test Generation — V:H E:M R:M
Agent derives Pact-style consumer contracts from your API clients and HAR captures, generating provider verification tests. Industry direction: contract testing independently validating service interfaces reduces environment-dependency pain — most enterprise failures now originate below the UI layer, which is where this points your coverage.

### C6. Visual AI Regression Triage — V:M E:M R:M
Whether you adopt a visual-testing tool or roll screenshot diffs, the cost center is triaging diffs (anti-aliasing noise vs. real regression). Agent classifies diffs, groups by root cause ("global CSS change moved everything 2px"), and approves noise-class changes under policy. Value scales with how visual your product is.

### C7. Localization & i18n Testing Agent — V:M E:L R:L
Agent tours the app per locale (MCP), checking: untranslated strings, layout breaks from text expansion, date/number/currency formats, RTL rendering. Multiplies your exploratory capability across locales no team has time to tour manually.

### C8. Performance Test Authoring & Results Interpretation — V:M E:M R:M
Two halves: agent generates k6/JMeter scripts from HAR captures + journey definitions (authoring), and — more valuable — interprets result sets against baselines in plain language ("p95 regressed 40% on /search after build 214; correlates with deploy X"). Extends the deterministic-parse/AI-interpret pattern from your Allure design.

### C9. Chaos & Resilience Scenario Design — V:L→M E:M R:M
Agent designs failure-injection scenarios from your architecture (dependency timeouts, degraded services) and drafts the expected graceful-degradation assertions. Do this only if resilience is a stated business requirement; otherwise it's engineering tourism.

### C10. Document / Email / PDF Output Validation — V:M E:L R:L
Enterprise systems emit invoices, statements, notification emails — chronically under-tested because they're annoying to assert on. Agent extracts and validates generated documents against templates and data (deterministic extraction + model comparison). Unglamorous, high defect-density territory.

### C11. ETL / Data Pipeline Validation Agent — V:M E:M R:M
If your web app sits on data pipelines: agent generates reconciliation checks (source vs. target counts, transformation rules, referential integrity) and interprets discrepancies. Data defects are business-report defects — high management visibility when caught.

---

## Theme D — Risk, Prediction & Compliance
**Business output: test effort allocated by predicted risk instead of habit; audit readiness as a by-product instead of a fire drill. (Your governance lane — these carry your signature.)**

### D1. Defect-Prediction-Driven Test Prioritization — V:H E:H R:M
Agent scores each release's change set by risk — code churn, complexity, author-history, component defect density from the ledger/tracker — and orders test execution and review depth accordingly. This is the "risk-based testing" the industry keeps promising; the ledger you're already building is the required data foundation. Sequence after two quarters of ledger data.

### D2. Compliance Evidence Automation — V:H E:M R:L
For regulated contexts: agent assembles the release evidence pack automatically — traceability matrix (requirement → case → spec → run result), sign-off records, deviation log — from artifacts that already exist in git and the ledger. Turns audit prep from days to minutes; a natural showcase for an AI-governance-led QE team.

### D3. Security-Findings Triage Assistant — V:M E:M R:M
Agent triages DAST/dependency-scan findings: deduplicates, filters known-accepted risks, drafts reproduction notes for the real ones, routes to owners. QE doesn't become the security team — it removes the noise that stops anyone from looking. Coordinate with security before building (their lane, your assist).

### D4. Quality Risk Forecast per Sprint — V:M E:L R:L
Composition play: before sprint start, agent combines story ambiguity scores (Vol 1 §1.2), component risk (D1 signals), and coverage gaps into a one-page "where quality risk concentrates this sprint" brief. Cheap once the inputs exist; makes QE proactive in planning instead of reactive in execution.

---

## Theme E — Quality Engineering FOR AI Systems (Strategic)
**Business output: your organization ships AI features (Copilot Studio agents, AI-assisted products). Someone must be able to answer "how do we know the AI works?" — the QE team that answers it becomes strategically indispensable, and industry analysis says most AI initiatives stall precisely on validation gaps.**

*(You have unfair advantages here: an eval harness methodology, trajectory grading, a failure taxonomy, and a governance mandate. This theme is your differentiation play.)*

### E1. LLM Feature Evaluation Harness — V:H E:M R:M
Extend your eval-harness discipline to AI features: golden datasets, graded rubrics (correctness, groundedness, tone, format), regression runs on every prompt/model/config change. The AI equivalent of a regression suite — and the answer to "the vendor changed the model; did our agent get worse?"

### E2. Prompt & Agent Regression Testing — V:H E:L R:L
Version-controlled prompts (which you already practice) + a pinned test set replayed on every change, diffing outputs against graded baselines. The cheapest entry into Theme E — it's your existing kata/eval mechanics pointed at a new target.

### E3. Adversarial & Red-Team Testing for AI Features — V:H E:M R:M
Systematic hostile-input testing of the org's AI agents: prompt injection, jailbreak attempts, data-exfiltration probes, off-policy requests — scenario library + automated replay + graded outcomes. Your K6 kata is the human-practice version; this is the productized form, and it sits squarely in your governance charter.

### E4. Groundedness & Hallucination Checking — V:M E:M R:M
For RAG/knowledge-grounded features (AskHR-class agents): automated checks that responses cite and are supported by the retrieved sources, with an LLM-as-judge second pass and human calibration sampling. Reports a groundedness rate managers can track.

### E5. Agent Trajectory Testing — V:M E:M R:M
For tool-using agents: assert on the *path*, not just the answer — right tools called, right order, no unauthorized calls, gates respected. This is literally your trajectory-grading methodology applied to the org's production agents rather than your dev sessions.

### E6. AI Guardrail & Policy Conformance Suite — V:H E:M R:L
Automated verification that deployed AI features respect their declared boundaries (topics refused, data never disclosed, escalation triggers fire) — run pre-release and on schedule in production-like conditions. For an AI governance team, this converts policy documents into executable checks: governance that runs, not governance that's filed.

---

## Theme F — QE Operations & Intelligence
**Business output: the QE function itself becomes measurable, narratable, and cheaper to run.**

### F1. Quality KPI Narrator & Executive Dashboard — V:M E:L R:L
Agent maintains the small KPI set that ties QE to business outcomes (escape rate, mean-time-to-detect, coverage-vs-usage alignment from A1, flaky burden, cost per release cycle) and writes the monthly narrative — trends, causes, asks. The manager-report pattern from your Allure design, promoted to the program level.

### F2. Historical Defect Knowledge Mining — V:M E:L R:L
One-time-then-periodic agent pass over years of closed defects: where bugs cluster, which escape patterns repeat, which fixes regress. Institutional memory most teams have but can't query; informs D1 and the coverage strategy.

### F3. Test Environment Provisioning Assistant — V:M E:M R:M
Agent-assisted environment operations against your IaC/config layer: spin up a test env for branch X with dataset Y, verify health (Vol 1 §6.2), tear down on schedule. Coordinate with DevOps ownership; QE defines the verification, not the infrastructure.

### F4. Estimation & Capacity Assistant — V:L E:L R:L
Agent drafts test-effort estimates from historical actuals for similar stories (size, component, defect density). Modest value; include only if estimation is a real pain today.

---

## Consolidated Management View — both volumes, by business narrative

| Business narrative | Flagship workflows | The one-line pitch |
|---|---|---|
| **Cut cost of quality** | Vol1: Allure+ledger, healing, element exploration · Vol2: C1 mutation triage, B5 intake | "Hours of weekly analysis and maintenance become minutes of review" |
| **Ship faster, safely** | Vol1: smart regression selection · Vol2: D1 risk prioritization, A5 canary, B2 AI-code gate | "Test depth follows risk, so speed stops costing confidence" |
| **Protect revenue & customers** | Vol2: A1 telemetry alignment, A2 synthetic journeys, A4 VoC mining | "Coverage provably follows what customers do and complain about" |
| **Regulated-grade assurance** | Vol2: D2 evidence automation, E6 guardrail suite | "Audit readiness and AI policy conformance as running systems, not documents" |
| **Make AI trustworthy** (differentiator) | Vol2: Theme E entire | "We are the team that can answer: how do we know the AI works?" |

**Shortlisting advice for the management pitch:** pick **one flagship per narrative** (5 items), anchored by what's already in flight (Allure+ledger) and one Theme E item (E2 is the cheapest credible entry) — a five-line story covering cost, speed, revenue, compliance, and AI trust lands better than a 56-item catalog. Keep both volumes as the governed backlog behind it, gated by your intake rule.

*Companion: Volume 1 catalog · audit checklist (every adopted item passes it) · eval harness (every adopted item reports evidence through it). Industry claims herein reflect 2026 trend reporting; validate vendor ROI figures against your own baselines before repeating them upward.*
