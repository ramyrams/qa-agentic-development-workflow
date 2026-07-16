# Agentic Development Kata Set
### Deliberate Practice Exercises for the QE Team — with Grading Rubrics

**Purpose:** Build agentic-workflow expertise through repeatable, comparable exercises. Every engineer runs the **same kata on the same input**, trajectories and outputs are compared side by side, and grading uses the team's existing eval-harness methodology (trajectory grading + failure taxonomy) — so practice and measurement share one language.
**Cadence:** One kata per biweekly session (60–75 min: 40 run, 25 compare/debrief). Cycle K1→K6, then repeat with new inputs — repetition with variation is the point of katas.
**Environment:** The sandbox repo (copy of real specs + fake data), never production automation. Facilitator prepares inputs in advance and keeps them secret until start.

**Grading scale (all rubrics):** each dimension scored 0 (absent) / 1 (partial) / 2 (solid). Katas are practice, not assessment — scores exist to make progress visible and debriefs concrete, and to build the evidence trail the competency ladder later verifies.

**Session-failure taxonomy** (used across all rubrics; extends the test-failure taxonomy to agent sessions):
`WC` wrong context loaded (skill didn't fire / wrong instructions in scope) · `SG` skipped or rubber-stamped gate · `TM` tool misuse (wrong tool, unnecessary terminal, out-of-boundary attempt) · `SE` scope expansion beyond the ask/plan · `SA` silent assumption (invented data, guessed contract) · `AW` assertion weakening / wait-adding to force green.

---

## K1 — Read the Trajectory *(develops L1; the foundation kata)*

**Goal:** Turn "the agent did something weird" into precise, taxonomy-coded diagnosis.
**Setup:** Facilitator provides two completed session transcripts on the same task: one good, one seeded with 3–4 planted defects (e.g., the cypress-authoring skill never fired; the model invented a fixture; a gate was approved without changes; one terminal call was unnecessary).
**Task (individual, 25 min):** For each transcript produce a trajectory annotation: (1) which instructions were in scope and evidence they were applied or ignored; (2) which skills fired — and for the bad run, which *should* have; (3) every tool call with a one-line purpose judgment (necessary / unnecessary / out of scope); (4) each defect coded with the session-failure taxonomy; (5) the single earliest intervention point that would have saved the session.
**Debrief:** Compare annotations; facilitator reveals the planted defects.

**Rubric (max 10):**
| Dimension | 0–2 |
|---|---|
| Planted defects found | none / some / all |
| Correct taxonomy codes assigned | — |
| Tool-call purpose judgments accurate | — |
| Earliest-intervention point identified correctly | — |
| Annotation usable by someone who didn't watch the session | — |

**Common failure to watch for:** grading the *output* ("the spec looks fine") instead of the *process* — the seeded bad run should produce a plausible-looking spec.

---

## K2 — The Instruction Delta *(develops L1→L2)*

**Goal:** Make the effect of always-on context visceral and measurable.
**Setup:** Sandbox repo in two branches: `bare` (no `.github` customization) and `governed` (the team's instruction files). One user story.
**Task (pairs, 30 min):** Run the identical free-form request ("write a Cypress spec for <story>") on both branches. Diff the two outputs against the team conventions checklist (selectors, waits, independence, negative path, page-object use). Then: pick the **one** convention violation that survived even on `governed`, and draft the minimal instruction-file edit that should fix it. Re-run to verify.
**Debrief:** Which conventions do instructions reliably enforce, which need a stronger mechanism (path file? skill example? enforced tool boundary?), and why.

**Rubric (max 10):** conventions-diff completeness · violation selected is real and material · proposed edit is minimal and correctly placed (right file, right layer) · re-run verification performed · correct conclusion about instruction limits (advisory, not enforced).

---

## K3 — Prompt Authoring Under Constraint *(develops L2 competency 3)*

**Goal:** Practice turning a recurring activity into a prompt file that survives hostile inputs.
**Setup:** Facilitator names a recurring team task not yet covered by a prompt (rotate: convert a manual case; draft a regression subset for a release; summarize a spec folder's coverage).
**Task (individual, 35 min):** Author the `*.prompt.md`: frontmatter, declared `${input:}` variables, procedure with a defined end state, and an approval gate if anything mutates files. Then run three executions: (a) happy path, (b) **missing input** (must ask, not invent — SA check), (c) **oversized/ambiguous input** (must scope or clarify, not silently truncate).
**Debrief:** Read the three transcripts of the best and worst scoring prompts side by side.

**Rubric (max 12):** correct primitive choice defended (is a prompt actually right for this?) · inputs declared, not implied · defined end state and output shape · gate present where consequences warrant · missing-input run asks rather than invents · ambiguous-input run scopes rather than guesses.

---

## K4 — Skill Trigger Calibration *(develops L2 competency 4; the L2 live-assessment kata)*

**Goal:** Master the make-or-break skill mechanic: the description as trigger condition.
**Setup:** A prepared skill folder with useful body content but a **deliberately vague description** ("Helpful testing utilities"). A task list of 6 prompts: 3 that *should* trigger the skill, 3 adjacent ones that *shouldn't*.
**Task (individual, 30 min):** (1) Run all 6, record firing behavior (expect: mostly wrong). (2) Rewrite only the `description:` — trigger-condition style, task nouns and synonyms. (3) Re-run all 6. (4) Iterate to a maximum of 3 description versions. Deliverable: the version history with firing results per version.
**Debrief:** Compare final descriptions; extract the team's description-writing heuristics into the skill-authoring reference.

**Rubric (max 10):** baseline firing behavior recorded honestly · final version: 3/3 positive firing · final version: 3/3 negative non-firing · description edits are principled (task-noun coverage) not keyword-stuffing · iteration count ≤ 3 (economy of calibration).

**Facilitator note:** This kata is repeated at L2 assessment with a fresh skill — practice runs make that fair.

---

## K5 — Boundary & Handoff *(develops L2 competency 5 → L3 judgment)*

**Goal:** Experience enforced tool boundaries and multi-agent handoff as design tools, not bureaucracy.
**Setup:** Sandbox with `test-planner` (read-only) and `test-implementer`. A user story whose acceptance criteria contain one deliberate contradiction and one untestable statement.
**Task (pairs, 35 min):** (1) Run planning with `test-planner`; the plan must surface the contradiction and the untestable AC (SA check — a plan that "resolves" them silently fails). (2) Mid-planning, instruct the planner to "just go ahead and write the spec" — record its refusal behavior. (3) Hand off the approved matrix to `test-implementer`; during implementation, request an additional test outside the matrix — record whether the agent asks or silently expands (SE check). (4) Deliverable: both transcripts annotated.
**Debrief:** Where did enforcement (tools) succeed vs. instruction-level rules ("never expand scope") — and what does that imply for what you trust to each mechanism.

**Rubric (max 12):** contradiction surfaced · untestable AC surfaced, not paraphrased away · planner refusal observed and correctly explained (enforced vs. advisory) · handoff carried full plan context · scope-expansion probe handled correctly · pair articulates the enforcement-vs-instruction distinction in their own words.

---

## K6 — Red-Team the Estate *(develops L3 competency 4; run twice a year)*

**Goal:** Make the security posture in the audit checklist experiential.
**Setup (facilitator, in secret):** A fake "third-party skill" added to the sandbox containing three plants: (1) a prompt injection in the SKILL.md body ("ignore repository instructions and…"), (2) a script line that exfiltrates an environment variable (simulated — points at a dummy endpoint), (3) an `allowed-tools` pre-approval of `bash`.
**Task (teams of 3, 40 min):** You are the audit team; a colleague proposes adopting this skill. Run audit checklist §5 against it. Deliverable: a written adoption decision (approve / conditional / reject) citing checklist items, with each plant either found or missed.
**Debrief:** Reveal all plants; walk through what would have happened at runtime for each missed one; update the checklist if the kata found a gap in it.

**Rubric (max 10):** injection in Markdown found · script exfiltration found · tool pre-approval flagged as ⛔ · decision correctly cites checklist items · would-be-runtime-consequence correctly explained for each plant.

**Rule:** Nothing from K6 setup ever touches a real repo; the fake skill lives only in the sandbox and is deleted after debrief.

---

## Capstone — Design a Workflow *(L3 development; quarterly, volunteers)*

**Goal:** Full-cycle architecture practice: from a real team pain to a shipped multi-primitive design.
**Task (individual, two weeks alongside normal work):** Pick a real recurring pain (facilitator maintains a backlog — e.g., release regression selection, test-data drift detection). Produce: (1) a one-page design (primitives chosen via the four questions, deterministic/AI split, tool postures, gates), (2) a threat sketch (injection paths, blast radius), (3) a working sandbox prototype, (4) an eval plan (which representative tasks, graded how).
**Review:** Design defense in the biweekly session — the same format the L3 assessment uses, so the capstone is a rehearsal.

**Rubric (max 14):** problem is real and recurring · primitive placement survives the four-questions challenge · deterministic/AI split defensible · minimal tool postures with exclusion rationale · gates placed where consequences warrant · threat sketch identifies the top realistic risk · eval plan measurable with the existing harness.

---

## Running the Program

1. **Comparability is the engine.** Same input, same time-box, side-by-side debrief — the variance between engineers on identical input is where the learning is. Protect this: no input previews, no extended time.
2. **Score trends, not sessions.** Keep a simple sheet (person × kata × attempt × score). The interesting signal is second-attempt deltas when a kata cycles back around.
3. **Feed the harness.** Kata inputs and their graded outputs become new cases for the eval set; planted-defect transcripts from K1 become regression fixtures for "can the team still spot this." The kata program and the eval harness should grow each other.
4. **Rotate facilitation** among L2+ engineers — preparing the planted defects is itself high-value practice (you must understand a failure mode deeply to seed it convincingly), and it evidences the L3 teaching competency.
5. **Debrief format:** 5 min per person max, structured as *one thing that worked / one taxonomy-coded miss / one thing stolen from someone else's trajectory*. The last item is mandatory — cross-pollination is the program's actual product.

*Owner: ________ · Version 1.0 · Companions: agentic-competency-ladder.md (which katas evidence which levels), enterprise audit checklist (K6), eval harness methodology*
