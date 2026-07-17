# Agentic QA Workflow Catalog — Volume 5: The Functional Tester's Edition
### 18 new workflows for the manual/functional QA team — zero repeats from Volumes 1–4

**Scope check:** Volumes 1–4 already covered the functional team's session scribe, environment setup, data concierge, case healing, retest prep, smoke/regression planning, domain Q&A, UAT kit, localization, bug bash, duplicate pre-check, coverage reconciliation, and exploratory agents. Volume 5 goes after what remains — and what remains is the *craft* of functional testing: how testers think up cases, how they run cycles under pressure, and how they fight for their defects. These are the workflows that make a functional tester *better at testing*, not just faster at paperwork.

**Ratings:** V/E/R as before · 🔧 = strong first-build candidate.

---

## Theme N — Test-Thinking Amplifiers
**Business output: the depth and creativity of test design — historically capped by individual experience — becomes a team-wide capability. A two-year tester starts finding what only the ten-year tester used to find.**

### N1. 🔧 Screenshot → Test Ideas ("point at the screen") — V:H E:L R:L
The lowest-friction test-design tool possible: tester screenshots any screen (or pastes a mockup) and the agent returns a structured probe list for *that* screen — field boundaries, state combinations, sequence attacks, what should be disabled when, what the error paths must be. No setup, no formalism; it meets testers exactly where they work. Doubles as a training tool: juniors see *how* an experienced mind interrogates a screen, every time they use it.

### N2. Business Rules → Decision Table Builder — V:H E:M R:L
Functional logic hides in prose: requirements, ticket comments, email threads, SME folklore. Agent extracts the rules into explicit decision tables (conditions × actions), flags **conflicts and gaps between sources** ("the FSD says X, ticket 4521's resolution implies Y"), and derives the minimal covering test set from the table. The conflict-detection output regularly matters more than the tests — it finds requirement bugs before they become code bugs.

### N3. Abuse & Misuse Case Generator — V:M E:L R:L
Beyond standard negative paths: what would a *confused* user do (double-submit, back-button mid-payment, stale tab), a *creative* user (unexpected-but-legal sequences), a *hostile* user (parameter tampering at the functional level, workflow-order bypasses)? Agent generates the misuse catalog per feature, each with the expected safe behavior to verify. Functional testers rarely get security training; this puts the attacker's-mindset checklist in every session.

### N4. Persona-Driven Test Tours — V:M E:L R:L
Agent maintains a persona library (novice, power user, impatient user on mobile data, screen-reader user, non-native speaker) and generates persona-specific walkthroughs of a feature: what *this* user would do, struggle with, and expect. Converts abstract "think about the user" advice into concrete, executable tours — and quietly folds accessibility and i18n empathy into everyday functional passes.

### N5. Form & Field Validation Matrix Builder — V:H E:L R:L
Forms are the functional tester's daily bread and the most combinatorially tedious thing they verify. Agent inventories a form (element-exploration machinery), enumerates fields × validation rules × expected messages × interaction effects (field A disables field B) into a verification matrix, and tracks which cells the tester has covered. Nothing about this needs AI creativity — which is exactly why an agent should own the tedium.

### N6. Component Heuristics Library ("how do we test a ___?") — V:M E:L R:L
A living skill of house test heuristics per component type — date picker, file upload, data grid, search box, payment form, wizard — each with its known-treacherous cases (DST for dates, size/type/interrupt for uploads, sort-stability for grids). Tester invokes it per component; every heuristic learned by anyone (fed from H1's escape analysis) becomes everyone's checklist next week. This is how a team's testing wisdom stops living in individual heads.

### N7. SME Elicitation Interviewer — V:M E:L R:L
Before testing an unfamiliar or under-documented feature: agent generates the interview script for the SME/BA — the "what happens when…?" questions ranked by risk, informed by the ambiguity linter's findings and the decision-table gaps (N2). Testers usually discover these questions *during* testing, at the most expensive moment; this front-loads them into a thirty-minute conversation.

### N8. Error-State Audit Tour — V:M E:L R:L
A dedicated pass over the application's *error personality*: agent helps enumerate reachable error states, and the tester evaluates each message for clarity, actionability, consistency, and tone against house standards the agent checks mechanically (terminology drift, blame-the-user phrasing, dead-end errors with no next step). Error UX is a quality dimension nobody owns — the functional team claiming it is cheap and visible.

---

## Theme O — Cycle Operations Under Pressure
**Business output: test cycles stop being managed by gut feel — leads see progress, risk, and conflicts as data while there's still time to act.**

### O1. 🔧 Cycle Progress Forecaster — V:H E:M R:L
Mid-cycle, from execution records: current velocity vs. remaining cases, defect arrival and retest load, blocked time — projected completion date and the at-risk areas *if nothing changes*. The test lead's daily question ("will we make it?") answered with a trend line instead of a hallway estimate, early enough to descope or reinforce deliberately rather than discover the miss in the final week.

### O2. Shift & Handover Composer — V:M E:L R:L
For distributed/offshore-onshore cycles: agent composes the handover from the day's execution records and environment state — what was tested, what's blocked and why, data conditions left in place, exact next actions — instead of the hand-written summary that omits the one detail the next shift needed. Continuity stops depending on the discipline of the most tired person in the room.

### O3. Journey/State Coverage Heatmap for Manual Testing — V:M E:M R:L
The manual-testing sibling of model-based testing (Vol 3 H5), without the formalism: agent maintains a lightweight map of the app's areas/journeys and shades what this cycle has touched, at what depth, by whom — so "are we done?" becomes a picture, and untouched high-risk zones are visible *during* the cycle. Session scribe (K2) and execution records feed it automatically.

### O4. Before/After Behavior Differ ("did anything else change?") — V:H E:M R:M
For a release or hotfix: agent walks the same journeys on the previous and candidate builds (MCP, side by side) and reports *behavioral deltas* — changed copy, moved elements, different validation responses, altered flows — for the tester to judge as intended vs. regression. This is what manual regression testing is actually trying to do with human eyes and memory; the agent does the diffing, the human does the judging.

### O5. Environment & Data Conflict Coordinator — V:M E:L R:L
The silent cycle-killer: two testers on one environment, one reseeds the data mid-someone-else's-test. Agent tracks who is testing what, where, with which datasets (declared via the concierge, K5), warns on collisions before they happen, and brokers the "can I reset stage-2 at 3pm?" negotiation. Boring, and worth hours a week in un-lost work.

### O6. Evidence Privacy Spot-Checker — V:M E:L R:L
Before evidence attaches to tickets or reports: agent scans screenshots and logs for real-looking personal data (names, emails, card fragments that shouldn't be in a test env at all) and flags for masking — plus the meta-finding that production-like data leaked into the environment. Protects the team from the embarrassing-screenshot-in-Jira incident, and it's a governance control you can name in an audit.

---

## Theme P — Defect Craft
**Business output: the functional team's findings survive triage — defects get fixed instead of deflected, and their business weight is understood the first time.**

### P1. 🔧 Defect Advocacy Assistant — V:H E:L R:L
When a bug comes back "works as designed" or "won't fix": agent builds the case — citing the requirement or AC it violates, the decision-table rule (N2), precedent defects, and the user expectation argument — *or tells the tester honestly that the rejection is sound* and why. Defect advocacy is a senior-tester skill juniors lack; this levels it. The both-directions honesty is the design point: an advocacy tool that always argues becomes noise nobody reads.

### P2. Business-Impact Narrative Generator — V:H E:L R:L
Translates a defect from tester language ("validation bypassed on step 3") into triage language: which user segments hit it, on which journeys, with what frequency signals (analytics/telemetry where available, A1 machinery), and the plausible cost framing. Severity debates shorten because the impact arrives quantified instead of asserted — and the functional team stops losing priority fights to whoever argues loudest.

### P3. Non-QA Reporter Interviewer — V:M E:L R:L
Bugs arriving from support, sales, or executives are vague by nature ("customer says checkout is broken"). Agent interviews the reporter conversationally — environment, account, steps, timing — and produces a QA-grade preliminary report before a tester spends an hour on archaeology. The functional team stops being the translation layer for the whole company's bug reports.

### P4. Triage Meeting Scribe & Actioner — V:M E:L R:L
Defect triage meetings produce decisions that die in people's notebooks. Agent (from the meeting transcript) extracts every decision — severity changes, ownership, defer rationale — drafts the tracker updates for one-click application, and maintains the "deferred with rationale" register that answers next quarter's "why didn't we fix this?" A meeting's worth of tracker hygiene in two minutes, and an audit trail for deferral decisions.

---

## Rollout Note for Volume 5

Openers (all E:L, felt within a week): **N1** screenshot→ideas, **N5** validation matrix, **P1** defect advocacy — one per theme, each demonstrating a different kind of value (thinking, tedium, influence). Month two: **O1** forecaster and **N2** decision tables, which need execution-record and requirements plumbing respectively. **O4** (behavior differ) is the sleeper flagship — build it after the element-exploration machinery (Vol 1 §2.1) is routine, because it reuses that engine wholesale.

As with Volume 4: build these as L2 ladder portfolio work, measure in minutes-saved and *defects-that-survived-triage*, and route everything through the intake rule. Theme N items in particular should feed the component-heuristics library (N6) so every workflow makes the next tester smarter.

---

**Catalog status: 5 volumes · 134 workflows.** Volume 5 closes the functional-team gap: Volumes 1–4 made testers faster; Volume 5 makes them sharper and harder to overrule.
