# Agentic QA Workflow Catalog — Volume 6: The Completion Volume
### 16 final workflows — new territory only, verified non-repeating against Volumes 1–5

**Where these come from:** After 134 items, what remains unexplored are three specific territories: **(Q)** the enterprise-assurance dimensions of an application that even mature teams rarely test — access control, audit trails, data lifecycle; **(R)** the high-stakes *moments* around releases and incidents where QE either shows up with evidence or doesn't; and **(S)** the growth of the team itself. These are real, non-padding items — and this volume is deliberately the last: the ideation well is now genuinely dry, and anything further would recycle what you have.

**Ratings:** V/E/R · 🔧 = strong first-build candidate.

---

## Theme Q — Access, Integrity & Trust Verification
**Business output: the assurance questions an enterprise auditor, security reviewer, or major customer eventually asks — "who can do what, is it logged, does exported data match, is deleted data deleted" — get standing, evidence-producing answers instead of scrambled ones.**

### Q1. 🔧 Role & Permission Matrix Testing (RBAC verification) — V:H E:M R:M
Every enterprise app has a roles × features × actions permission model; almost no team verifies it systematically, because the matrix is huge and mind-numbing — which is exactly the agent's job. Agent builds the matrix from the requirements/role definitions (or elicits it via N7 where undocumented), then probes each cell as each role — UI-level (elements hidden/disabled) *and* API-level (the request actually denied, not just the button hidden — the classic privilege-escalation gap). Output: the verified matrix with failures ranked by exposure. This is simultaneously functional testing, security assurance, and audit evidence — three budgets, one workflow.

### Q2. Session & Authentication Lifecycle Testing — V:M E:L R:L
The companion to Q1, testing *when* access is valid rather than *who* has it: timeout behavior mid-form (is the user's work lost or preserved?), token refresh during long sessions, concurrent-session policy, logout completeness (back-button after logout, cached authenticated pages), remember-me boundaries. Agent generates the scenario set per auth pattern and drives the tedious clock-and-cookie mechanics; the tester judges the experience at each boundary.

### Q3. Audit Trail Verification — V:H E:M R:L
Enterprise systems promise that user actions are logged — and that promise is tested by nobody until an auditor or an incident tests it for you. Agent pairs with any test execution (manual via K4's evidence capture, automated via the suite): for each performed action, verify the corresponding audit record exists, is accurate (actor, timestamp, before/after values), and that *non*-actions didn't log. Runs as a passive verification layer on testing you're already doing — near-zero marginal execution cost, and squarely in your governance lane.

### Q4. Export ↔ Screen Reconciliation — V:M E:L R:L
Users trust that the CSV/Excel/PDF export contains what the screen showed — filtered, sorted, and permission-trimmed the same way. It frequently doesn't (exports bypassing filters or, worse, permission trims are a recurring real-world defect class). Agent captures the on-screen dataset state, triggers the export, and reconciles: rows, columns, values, ordering, and — connecting to Q1 — that role-based field masking survived into the file. Deterministic comparison, agent-orchestrated, defect class eliminated.

### Q5. Data Lifecycle & Retention Testing — V:M E:M R:M
"Deleted" and "retained per policy" are promises with regulatory weight: agent designs and drives verification that soft-deletes behave as specified, purge jobs actually purge (including from exports, search indexes, and audit views), archival preserves integrity, and retention clocks trigger — using time-manipulation techniques (Vol 5's G3 family) against seeded lifecycle datasets. Pairs with the privacy compliance work (Vol 3 G2) to make your data-handling claims *demonstrated*, not asserted.

### Q6. Deep-Link, URL & Navigation-State Testing — V:L→M E:L R:L
The forgotten front door: agent enumerates the app's route space and probes — direct entry to deep links (with/without auth, with stale IDs), bookmarkability, browser back/forward through multi-step flows, URL parameter tampering at the functional level, shared-link behavior across roles (Q1 tie-in). Users arrive through URLs constantly; test flows almost never do.

---

## Theme R — Release & Incident Moments
**Business output: at the moments of maximum organizational attention — go-lives, rollbacks, incidents, sales demos — QE arrives with evidence in minutes, which is when reputations (the team's and the product's) are actually made.**

### R1. Test Readiness Gatekeeper (entry/exit criteria as checks) — V:M E:L R:L
Cycle entry and exit criteria exist in every test strategy document and are verified by optimism. Agent turns them into executed checks: entry (environment healthy per Vol 1 §6.2, data seeded, build deployed and versioned, cases reviewed and assigned) and exit (execution coverage, open-defect thresholds by severity, retest completion) — producing the gate decision *with evidence attached*. Cycles stop starting broken, and "are we done?" gets a defensible answer.

### R2. Rollback Verification Runbook — V:M E:M R:M
Everyone tests the deploy; almost nobody tests the *undo* until the night it's needed. Agent maintains and periodically executes the rollback drill in staging: roll back, then verify prior behavior actually restored — journeys, data compatibility (especially after schema migrations, Vol 3 G10), version coherence across services. The output is the one sentence every release approver wants and rarely truly has: "rollback is tested and takes N minutes."

### R3. 🔧 Incident War-Room Context Pack — V:H E:L R:L
When production breaks, the war room burns its first hour asking what QE already knows. Agent assembles it in minutes: test coverage of the broken area (M3's reconciliation map), recent run results and any related failure signatures from the ledger, known-issues touching the component, the last time this journey was verified and by what. Distinct from root-cause correlation (Vol 2 B6, which hypothesizes causes) — this is *live evidence logistics*, and it permanently changes how engineering perceives the QE team.

### R4. Third-Party Degradation Drills — V:M E:M R:M
Your app depends on payment gateways, identity providers, shipping APIs — and their failure modes are experienced by *your* users. Agent designs and drives functional drills with dependencies stubbed into degraded states (slow, erroring, partial): does the app queue, message honestly, and recover — or corrupt and confuse? The functional-verification complement to infrastructure chaos work (Vol 2 C9): same lever, pointed at user experience rather than system survival.

### R5. Demo Environment Pre-Flight — V:L→M E:L R:L
Small, cheap, and disproportionately loved: before sales demos, exec reviews, or customer walkthroughs, agent runs the pre-flight on the demo environment — demo-script journeys green, demo data present and pretty, no debug banners, integrations alive — and alerts with time to fix. A failed customer demo costs more than most defects; this makes QE the team that quietly prevented it.

---

## Theme S — Growing the Team Itself
**Business output: the team's capability pipeline — hiring, upskilling, and institutional learning — runs on the same agentic machinery as its testing.**

### S1. Help-Content & Documentation Accuracy Testing — V:M E:L R:L
User-facing help articles, tooltips, in-app guides, and training materials silently drift from actual behavior — and stale help *generates* support tickets and UAT confusion. Agent walks documented procedures against the real app (screenshots vs. current UI, steps vs. current flow) and files the drift report. Natural co-owner: the functional team, who know both the app and the user's reading of it. (Release-notes claim-checking, Vol 3 J5, is the release-day sibling; this is the standing estate-wide version.)

### S2. Per-Epic Test Strategy Composer — V:M E:L R:L
Above sprint planning (Vol 4 M4) sits the per-epic/per-project strategy: risk profile, test-level split, environment and data needs, entry/exit criteria (feeding R1), what's explicitly out of scope and why. Agent drafts it from the epic's stories (ambiguity-linted), the affected components' history (ledger + defect mining), and house strategy patterns — the lead edits judgment, not boilerplate. Strategy documents stop being written-once-read-never.

### S3. Cross-Training Path Generator (functional → automation) — V:M E:L R:L
For each functional tester moving toward automation: agent builds a personalized path from *their own artifacts* — the manual cases they authored become their first conversion exercises (Vol 1 §2.3), sequenced against the competency ladder, with their session data (Vol 3 H3) steering weak-spot practice. Generic curricula don't stick; converting your own test case does.

### S4. QE Hiring Exercise Studio — V:L→M E:L R:L
Agent generates fresh, role-calibrated practical exercises per hiring round (a buggy sandbox spec to critique, a requirement to decompose, an agent trajectory to review — that last one now being a real job skill), plus grading rubrics aligned to the ladder's levels, and drafts the evaluation write-up from the interviewer's notes. Exercises stop leaking to interview-prep sites because they're regenerated per round, and hiring signals map directly to the competency model you actually use.

### S5. Defect Lessons Digest ("bugs of the month") — V:L→M E:L R:L
Monthly, agent curates the most instructive resolved defects — not the most severe, the most *teaching* — into a short internal digest: what it looked like, why it escaped, which heuristic now catches it (feeding N6's library), told for developers and testers alike. Institutional learning from defects currently happens by hallway anecdote; this gives it a publication. The lightweight, human-readable face of the knowledge-mining machinery (Vol 2 F2).

---

## Closing the Catalog — 150 workflows, and why this is the end

Six volumes: lifecycle core (V1) · business outcomes & AI-systems QE (V2) · deep cuts & self-improvement (V3) · practitioner workbench (V4) · functional craft (V5) · assurance dimensions, release moments & team growth (V6).

An architect's honesty, as the final entry: the catalog is now **complete in the only sense that matters — every additional idea from here would be a variation of one you already hold.** The remaining value is entirely in selection and execution:

1. **Run the Volume 3 scorecard** over your candidates (your five seeds + the 💎/🔧-marked items are the natural longlist).
2. **Commit to ≤ 8** — one flagship per business narrative, metric and owner named per item.
3. **Everything else is the governed backlog** — visible, scored, intake-gated, and drawn from as capacity earns it.

The catalog's job was to make that shortlist defensible: whatever you cut, you now cut knowingly. The next artifact worth building is the one-page initiative charter for management — and that one should be built from your picks, not mine.
