# Agentic QA Workflow Catalog — Volume 4: The Practitioner's Workbench
### 32 daily-work workflows for functional testers and automation engineers

**Why this volume exists:** Volumes 1–3 are *programs* — pipelines, intelligence layers, strategic plays. Volume 4 is the **adoption layer**: the small, daily workflows an individual tester or automation engineer feels within their first week. Initiatives win or die on this layer — people champion the AI program that removed *their* Tuesday-afternoon tedium, not the one with the best architecture diagram. Most items here are a prompt file plus a small skill (agents rarely needed), buildable in days, and ideally built by team members themselves as L2 ladder practice.

**Measurement note:** score these in **minutes saved per person per week** and feed the numbers to COQ accounting (Vol 3 J1) — aggregated, the workbench often out-earns the flagship projects.

**Ratings:** V/E/R as before. 🔧 = strong first-build candidate for an engineer's L2 portfolio.

---

## Theme K — The Functional Tester's Daily Toolkit
**Business output: manual testing capacity effectively grows without headcount — the tester's hours shift from preparation, transcription, and bookkeeping to the judgment work only a human can do.**

### K1. 🔧 Environment State Setup Agent ("get me to the interesting state") — V:H E:M R:M
The biggest hidden tax on manual testing: twenty minutes of clicking to *reach* the state worth testing — order half-shipped, user mid-onboarding, cart holding an expired promo. Tester asks in plain language; the agent performs the setup (Playwright MCP driving the UI + the test-data-setup skill's seeding scripts) and hands over the browser at the interesting state, with its setup steps logged for reproducibility. Testing time goes to testing. Guardrails: sandbox environments only; destructive setup actions confirm first.

### K2. 🔧 Exploratory Session Scribe — V:H E:L R:L
The tester explores; the agent takes the notes. Shorthand fragments as they go ("pricing wrong after coupon + currency switch, screenshot 4") become a structured debrief: observations → bug candidates (routed through `/bug-report`) → open questions → automation candidates, each tied to timestamps and evidence. Kills the worst part of exploratory testing — the hour of write-up after the interesting ninety minutes — which in practice means debriefs actually get written.

### K3. In-Session Testing Copilot — V:M E:L R:M
The scribe's active sibling: mid-session, the tester can ask "what haven't I tried on this screen?" and the agent proposes next probes from the charter's tours, the element inventory, and what the session has already covered. Kept deliberately *suggestive* — the human's instincts lead; the agent prevents tunnel vision. (Separate from K2 so teams can adopt passive note-taking without accepting active prompting.)

### K4. Evidence Capture Assistant — V:H E:M R:M
During scripted manual execution: agent pre-stages the run (data per the case's preconditions, right environment and account), then handles the bookkeeping as the tester works — screenshots per step, console/network capture on anomaly, actual-results transcribed into the house execution record from the tester's shorthand. Regulated-context bonus: evidence packs become complete and consistent by construction (feeds compliance automation, Vol 2 D2).

### K5. Test Data Concierge — V:H E:L R:L
"Find me a stage user with an expired card and an open dispute." Agent queries the seeded-datasets catalog (test-data-setup skill), returns matching records, or generates-and-seeds a compliant one if none exists. The single most-heard manual-testing complaint — "I spent an hour finding data" — answered in seconds.

### K6. 🔧 Manual Test Case Healing — V:H E:M R:L
The functional twin of the automation healer, and almost nobody builds it: when the UI changes, an agent pass flags manual cases whose steps reference vanished or renamed elements ("Step 4: click **Save Draft** — no longer exists on this screen") by checking steps against the current page inventory (element-exploration machinery, Vol 1 §2.1), and proposes step rewrites as a diff for tester approval. Case libraries rot silently; this makes the rot visible and cheap to fix.

### K7. Defect Retest Preparation — V:M E:L R:L
When a bug flips to "fixed": agent preps the verification — minimal repro restated from the ticket, exact data conditions seeded, fixing commit and build linked, and where an automated repro exists (Vol 2 B4) it pre-runs and reports. The tester walks into a prepared retest instead of an archaeology dig.

### K8. Bug-Duplicate Pre-Check — V:M E:L R:L
Before a tester files: agent checks the observation against open and recently-closed defects (signature-style matching) and either surfaces the likely duplicate — with the option to add the new evidence there — or clears the way to file. Triage meetings shrink; reporters stop being told "dupe of BUG-1234" a day later.

### K9. Release Smoke Checklist Generator — V:M E:L R:L
Per release, agent derives a *tailored* smoke checklist from the actual diff (changed components → affected journeys) rather than the same stale forty-item list every time. Smoke time drops and the checklist stops being ignorable boilerplate.

### K10. Regression Cycle Planner — V:M E:M R:L
Given release scope, the case library, and tester availability: agent drafts the manual regression assignment — cases per tester balanced by domain familiarity, priority-ordered so the riskiest coverage lands even when the cycle gets cut short (it always does). The test lead adjusts and confirms.

### K11. Domain Knowledge Q&A Agent — V:H E:L R:L
A skill wrapping the product's accumulated truth — requirements, KT transcripts (Vol 1 §1.1 output), test cases, resolved-defect discussions — so "how is proration supposed to work when a user downgrades mid-cycle?" gets a cited answer instead of an interrupt to the one person who remembers. The workflow that makes a new functional tester productive in days, and the natural companion to a living product-behavior wiki the agent keeps current from the same sources.

### K12. UAT Facilitation Kit — V:M E:L R:L
Agent translates test cases into business-language UAT scripts, then structures the returned feedback: pass/fail per scenario, verbatims clustered, defect candidates extracted through the standard pipeline. QA stops hand-holding UAT logistics; business users stop testing from developer-speak.

### K13. Localization Review Assistant — V:M E:L R:L
Side-by-side locale walkthrough support: agent captures the same screens across locales and pre-flags the mechanical issues (truncation, untranslated strings, format errors — Vol 2 C7 machinery), so the human reviews only the judgment calls: tone, meaning, cultural fit.

### K14. Bug Bash Facilitator — V:M E:L R:L
For team bug bashes: agent generates area assignments and mini-charters per participant, then acts as live intake — deduplicating findings against each other and the tracker in real time, formatting via `/bug-report`. The post-bash "which of these sixty findings are the same twelve bugs" afternoon disappears.

### K15. Cross-Browser/Device Session Orchestrator — V:L→M E:L R:L
For manual compatibility passes: agent builds the pairwise-reduced device/browser × journey matrix (Vol 2 C4 technique), tracks coverage as testers work, and flags untouched high-risk cells. Compatibility testing stops being "whatever devices were on the desk."

---

## Theme L — The Automation Engineer's Daily Toolkit
**Business output: the minutes-per-hour that leak from automation work — debugging, searching, wiring fixtures, upgrading — get compressed; this is where most automation capacity is actually lost.**

### L1. 🔧 Spec Debugging Copilot — V:H E:L R:L
A failing test locally: agent ingests the Cypress error, the DOM snapshot at failure, the screenshot/video artifact, and recent relevant commits — and returns a ranked diagnosis (selector drift vs. timing vs. app change vs. data) with the evidence line for each. The everyday inner-loop version of the flaky-triage skill: minutes per failure instead of a coffee-length stare at a stack trace.

### L2. 🔧 Intercept & Fixture Builder from Live Traffic — V:H E:L R:L
Engineer performs the flow once with capture on; agent converts the recorded traffic into `cy.intercept()` setups and fixture files matching repo conventions — realistic shapes, volatile fields normalized, aliases named per the instructions file. Hand-writing network scaffolding is the slowest part of authoring a data-heavy spec; this deletes it.

### L3. Flake Characterization Runner — V:H E:L R:L
Suspect test → deterministic runner executes it N times under varied conditions (parallel load, throttled network, order shuffling); agent characterizes the results: failure rate, correlating condition, first-divergence point. Turns "it's flaky" (a mood) into a reproduction profile (a fact) — the required input for the healer and triage workflows.

### L4. Helper Discovery ("does this already exist?") — V:M E:L R:L
Before writing any utility: agent searches custom commands, page objects, and helpers for existing coverage of the need and answers with usage examples — or confirms it's genuinely new. Duplicate-helper sprawl is how suites become unmaintainable; this makes the anti-entropy habit effortless.

### L5. Assertion Strength Advisor — V:H E:L R:L
At authoring time, given the page or response state under test: agent proposes the assertion set that would actually fail if the feature broke — state, side-effects, negative space ("and the error banner is NOT shown") — informed by the mutation-derived weakness patterns (Vol 2 C1). Attacks the deepest quality problem in generated and hand-written tests alike: green tests that verify nothing.

### L6. Selector Resilience Scorer — V:M E:L R:L
PR-time pass rating each new selector for fragility (positional, text-coupled, style-coupled vs. contract `data-cy`), compliant alternative suggested. The bridge between your instructions (advisory, at generation) and review findings (late): drift caught at authoring.

### L7. 🔧 Convention → Lint Rule Promoter — V:H E:M R:L
The most leveraged item in this theme: agent converts mechanically-checkable instruction rules ("no `cy.wait(ms)`", "no bare CSS selectors") into custom ESLint rules with tests. Every rule promoted from *advisory instruction* to *deterministic lint* is a rule neither the model nor a human can ever violate again — and always-on instruction tokens are freed for rules only judgment can check. Your "deterministic where possible" principle, applied to the estate itself.

### L8. Pre-PR Self-Review Agent — V:M E:L R:L
Before opening the PR, the engineer runs the same checklist the reviewer agent will apply (`/review-test-pr` machinery, self-serve) and fixes findings pre-submission. Review cycles shorten because the mechanical findings never reach a human reviewer.

### L9. Suite Runtime Optimizer — V:M E:M R:L
Agent analyzes CI timing artifacts: slowest specs, serial bottlenecks, redundant setup, parallelization and sharding proposals with predicted savings. Suite duration creeps monotonically unless something pushes back; this is the something.

### L10. Framework & Dependency Upgrade Assistant — V:M E:M R:M
For Cypress/plugin/Node upgrades: agent reads the changelog delta, maps breaking changes to your actual usage via code search, executes the mechanical migrations as a PR, and flags the judgment-required remainder. Upgrades stop being deferred-until-forced.

### L11. Environment Parity Debugger — V:M E:L R:L
"Passes in env A, fails in env B": agent diffs the environments across config, versions, feature flags, and seeded data, ranked by likely relevance to the failing behavior. The classic half-day hunt, compressed to minutes.

### L12. Spec Explainer & Pattern Teacher — V:M E:L R:L
For juniors and new joiners: point at any spec and get an explanation of what it verifies, which house patterns it uses and why, and what would break it — grounded in the cypress-authoring skill so the teaching matches *your* conventions, not generic Cypress. Onboarding for the automation side; pairs with K11 for the functional side.

### L13. Spec Folder Documentarian — V:L→M E:L R:L
Agent maintains a README per spec domain — behaviors covered, data dependencies, known constraints, owner — regenerated from the specs themselves so it cannot go stale. Cheap, and it makes L4 and coverage analysis smarter over time.

### L14. Backend Change Watch — V:M E:M R:M
Agent subscribes to backend repo and API-contract changes and notifies the automation team of diffs affecting their intercepts, fixtures, or contract tests — *before* the nightly run discovers it the hard way. Cross-team early warning, powered by the versioning-sentinel machinery (Vol 3 G9).

---

## Theme M — Collaboration Rituals (both teams together)
**Business output: the handoff points between functional and automation — historically where context dies — become the strongest links in the system.**

### M1. 🔧 Finding → Automation Handoff Pipeline — V:H E:L R:L
The highest-value seam between the two teams, made frictionless: any confirmed finding from exploratory sessions, bug bashes, or UAT (K2/K14/K12 outputs) flows through one pipeline — agent drafts the regression-test candidate (level recommendation: API vs. UI), attaches the session evidence and repro, and queues it into the automation backlog with traceability. Exploratory discoveries stop evaporating; the suite grows from what humans actually found.

### M2. Three-Amigos / Refinement Facilitator — V:H E:L R:L
Live in refinement: agent applies example mapping to the story under discussion — proposing rules, examples, and the questions nobody asked — and emits the agreed examples as draft acceptance criteria before the meeting ends. Test thinking enters the story at its cheapest moment, with both teams working from the same examples. (If this makes you want BDD, a Gherkin authoring assistant is the natural bolt-on — deliberately optional, since BDD is a team-process choice, not a default.)

### M3. Manual↔Automated Coverage Reconciler — V:H E:M R:L
The standing question between the teams — "is this covered manually, automatically, both, or neither?" — answered continuously: agent maintains the reconciliation map (case library ↔ specs ↔ traceability IDs), flags double-coverage worth retiring from the manual cycle and manual-only coverage worth automating (feeding Vol 1 §2.3). The workflow that operationalizes two teams as one coverage system.

### M4. Sprint Test Plan Composer — V:M E:L R:L
At sprint start: agent composes the sprint's test approach from the pieces that already exist — ambiguity-linted stories, the risk brief (Vol 2 D4), regression selection, and the manual/automation split from M3 — into the one-page plan a lead currently assembles by hand.

### M5. Case Peer-Review Buddy — V:L→M E:L R:L
Pre-review pass on new manual cases against the house checklist (observable expected results, one action per step, traceability present) so human peer review spends its time on domain correctness rather than formatting.

### M6. Pairing Session Recorder — V:L→M E:L R:L
When functional and automation pair (converting a manual case, investigating a defect), agent captures the session's decisions and rationale into the case or spec's documentation — the context that otherwise evaporates when the pairing ends.

---

## Adoption Guidance for Volume 4

1. **Pick three per persona, ship in a month.** Recommended openers — functional: K2 (session scribe), K5 (data concierge), K11 (domain Q&A). Automation: L1 (debugging copilot), L2 (intercept builder), L7 (lint promoter). All six are low-effort and felt daily. Month two, once the pattern is proven: K1, K6, M1, M3.
2. **Build them as L2 ladder work.** Every item here is a prompt+skill build sized for an engineer's Author-level portfolio — the initiative trains the team *by* building its own tooling, and the ladder gets its evidence from work people wanted anyway.
3. **The workbench funds the programs.** When management asks what the AI initiative delivered this quarter, Volumes 1–3 provide the strategy slide — Volume 4 provides the twelve teammates who volunteer that their week got better. Capture before/after minutes per adopted item from day one; that's COQ input (Vol 3 J1) and the initiative's most persuasive number.
4. **Same rules, small scale.** Every workbench item still routes through the estate: intake rule, audit checklist (light-touch for read-only prompt+skill items), discoverability index. Convenience tools that bypass governance become the shadow estate you can't audit.

---

**Catalog status: 4 volumes · 116 workflows** — lifecycle core (V1) · business outcomes & AI-systems QE (V2) · deep cuts & self-improvement (V3) · practitioner workbench (V4). The shortlisting scorecard in Volume 3 governs what graduates from catalog to commitment.
