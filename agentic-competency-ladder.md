# Agentic Development Competency Ladder
### QE Team — Copilot Agentic Workflow Expertise Levels, Criteria & Assessment

**Purpose:** Define what "good" looks like at each level of agentic-workflow expertise, with **observable, evidence-based** criteria — so progression is assessed on demonstrated work, not tenure or enthusiasm.
**Design rule:** Every criterion is something an assessor can watch, read, or verify in git. No criterion is "understands X" — understanding is demonstrated or it doesn't count.
**Scope:** Applies to both automation and functional QE engineers; L1 is expected of everyone, L2/L3 are role-and-interest driven.

---

## The Ladder at a Glance

| Level | Title | One-line definition | Expected coverage |
|---|---|---|---|
| **L1** | **User** | Operates the agentic workflow correctly and can read what happened | 100% of the team within a quarter |
| **L2** | **Author** | Builds and maintains customization assets that pass the audit checklist | ~half the team, all automation engineers |
| **L3** | **Architect** | Designs multi-agent workflows, owns measurement, sets standards | 1–2 per team |

Levels are cumulative — L2 requires demonstrated L1, L3 requires demonstrated L2. A level is **held**, not just earned: each has maintenance criteria, because this ecosystem moves monthly and stale expertise is a real failure mode.

---

## L1 — User

**Definition:** Uses the team's agents, prompts, and skills correctly in daily work; can inspect an agent session and explain what happened; knows when *not* to trust an output.

### Observable competencies

1. **Correct primitive selection in use.** Picks the right entry point for a task (invokes `/generate-e2e-test` rather than free-prompting a spec; selects `test-planner` for planning rather than asking the implementer). *Evidence: observed over normal work, or in the kata.*
2. **Trajectory reading.** Given a completed agent session, can walk an assessor through it: which instructions were in scope, which skill(s) fired and why, each tool call and its purpose, and the point where the session succeeded or went wrong. *Evidence: live walkthrough of one of their own sessions (Kata K1).*
3. **Approval-gate discipline.** At plan/approval gates, meaningfully reviews rather than reflex-approves — can name at least one thing they changed or challenged at a gate in the last month. *Evidence: session transcript showing a rejected/amended plan.*
4. **Output verification habit.** Never merges agent-generated tests without running them and checking assertion strength ("would this fail if the feature broke?"). *Evidence: their PRs; spot-check three.*
5. **Failure vocabulary.** Describes agent misbehavior using the session-failure taxonomy (wrong context loaded / skipped gate / tool misuse / scope expansion / silent assumption) rather than "it did something weird". *Evidence: their reports in the escalation channel or biweekly review.*
6. **Escalation path.** Knows what to do when the agent misbehaves: capture the trajectory, classify, route to the estate owner — not silently retry until something plausible appears. *Evidence: one properly-filed session report.*

### Assessment method
- **Format:** 45-minute practical review with an L2+ assessor: (a) trajectory walkthrough of a real session from the candidate's last two weeks, (b) Kata K1 performed live, (c) three of the candidate's agent-assisted PRs spot-checked against competency 4.
- **Pass bar:** All six competencies evidenced. No written test — the walkthrough *is* the test.

### Maintenance
- Participates in the biweekly prompt review at least monthly; files at least one classified session report per quarter (good or bad — the habit is the point).

---

## L2 — Author

**Definition:** Creates, tests, and maintains customization assets (instructions, prompts, skills, agents) that pass the enterprise audit checklist; improves assets based on evidence rather than intuition.

### Observable competencies

1. **Primitive placement judgment.** Given a real need, chooses the correct primitive and defends the choice using the framework's four questions — including recognizing when the answer is "don't build it" (the curation rule). *Evidence: design note attached to a shipped asset.*
2. **Instruction authoring.** Has authored or materially revised an instructions file that (a) passed audit §2, (b) produced a measurable before/after difference on the eval set. *Evidence: the PR + eval delta.*
3. **Prompt authoring with gates.** Has shipped a prompt file with declared inputs, a defined end state, and a human approval gate where consequences warrant one; the prompt survives the missing-input spot-check (asks, doesn't invent). *Evidence: the file + a recorded end-to-end run.*
4. **Skill authoring & trigger calibration.** Has shipped a skill with bundled resources and — the differentiating skill — **calibrated its description**: demonstrated positive and negative trigger tests, iterating the description until firing is reliable. *Evidence: recorded trigger tests (audit §5.1).*
5. **Tool-posture reasoning.** Can specify the minimal tool allow-list for a proposed agent role and articulate what each exclusion prevents; has negatively tested a boundary. *Evidence: agent file + recorded negative test.*
6. **Evidence-driven iteration.** When an asset underperforms, diagnoses via trajectories and eval results, fixes the *asset* (description, taxonomy reference, template) — not the individual output. *Evidence: one improvement PR whose description cites trajectory/eval evidence.*
7. **Audit fluency.** Can run the per-type sections of the audit checklist on a peer's asset and produce findings an L3 endorses. *Evidence: one completed peer audit.*

### Assessment method
- **Format:** Portfolio review + one live kata. Portfolio: minimum one shipped asset of **three different primitive types**, each meeting the evidence requirements above. Live: Kata K4 (skill trigger calibration) performed with the assessor observing.
- **Pass bar:** Portfolio complete, K4 passed, and one peer audit accepted. Assessed by an L3 (or the estate owner while the first L3s are being grown).

### Maintenance
- Owns at least one production asset (named in CODEOWNERS) and keeps its last-reviewed date current; presents at least two improvements per year at the biweekly review.

---

## L3 — Architect

**Definition:** Designs multi-agent workflows end to end; owns the measurement layer; sets and evolves the team's standards; is accountable for the customization estate's audit posture.

### Observable competencies

1. **Workflow design.** Has designed a multi-component workflow (agents + skills + prompts + instructions composing together, with handoffs and enforced boundaries) that shipped and survived contact with real use — e.g., the Allure analysis pipeline. *Evidence: the design doc + the running system + shadow-mode comparison results.*
2. **Deterministic/AI split.** Demonstrates the architecture judgment of placing deterministic work in scripts and judgment work in the model, and can defend each placement in a shipped design. *Evidence: design review of their system.*
3. **Measurement ownership.** Owns the eval set: representative tasks defined, failure taxonomy maintained, before/after grading run on material `.github/` changes, baselines recorded and trended. *Evidence: the eval records themselves.*
4. **Risk architecture.** Can threat-model a proposed workflow (injection paths, tool pre-approval consequences, blast radius of a compromised asset) and specify compensating controls; leads the red-team kata (K6). *Evidence: a written threat assessment for one shipped workflow.*
5. **Standards stewardship.** Authors/evolves the framework docs, runs the quarterly audit, and adjudicates intake decisions using the standing rule (activity served / why no other primitive / who maintains). *Evidence: audit reports + intake decisions with rationale.*
6. **Teaching.** Has taken at least two engineers from L1 to L2 (as assessor/mentor); their biweekly-review sessions demonstrably transfer technique (attendees ship improvements based on them). *Evidence: mentee progressions.*
7. **Ecosystem tracking.** Maintains the tooling-change watch: verifies framework docs against product changes on major releases, and has caught at least one behavior change before it bit the team. *Evidence: changelog of doc updates with product-change citations.*

### Assessment method
- **Format:** Design defense. Candidate presents one shipped workflow to a panel (governance lead + an external-to-team architect if available): design rationale, measurement evidence, threat model, and what they'd change. Plus verification of the mentorship and stewardship evidence.
- **Pass bar:** All seven competencies evidenced; the design defense withstands challenge on trade-offs (why these boundaries, why this split, why not simpler).

### Maintenance
- Runs the quarterly audit; keeps eval baselines current; L3 lapses if the audit or eval cadence lapses two consecutive quarters — the role *is* the cadence.

---

## Operating the Ladder

1. **Assessment cadence:** L1 assessments monthly (rolling, as people are ready); L2 quarterly; L3 on demand. Keep sessions short and practical — the evidence should already exist in git and transcripts; assessment is verification, not examination.
2. **Records:** One row per person in a simple register (level, date, assessor, evidence links). Levels are visible to the team — the ladder motivates only if progression is acknowledged.
3. **Anti-gaming rules:** Portfolio assets must be in production use (invocations/trigger-firings in the last quarter), not built for the assessment. Trajectory walkthroughs use sessions the assessor picks from the candidate's recent history, not a rehearsed one.
4. **Connection to the kata program:** Katas K1–K3 develop and evidence L1; K4–K5 develop L2; K6 and the capstone develop L3 judgment. Run katas as practice long before anyone is assessed — the ladder measures what the katas build.
5. **Review the ladder itself** annually or on major tooling shifts: criteria reference today's product behavior (trigger mechanics, tool allow-lists) and must track reality, per the ecosystem-watch role.

*Owner: ________ · Version 1.0 · Companion: agentic-kata-set.md, enterprise audit checklist, framework guide*
