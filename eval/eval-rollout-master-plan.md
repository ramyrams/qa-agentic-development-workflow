# Master Plan: Introducing Eval to the Team
### A Day-by-Day Rollout — From First Exposure to Standard Practice

**Goal:** take the team from zero eval experience to writing, running, and trusting evals as a normal part of shipping any agent, skill, prompt, or instruction — in two working weeks, using the exact files already built. **"Mastery" is defined concretely at the end of this document, not left vague** — you'll know the rollout worked because of specific, checkable things the team can do unassisted, not because everyone attended a training.

**The design principle behind the sequencing:** every day builds on real, previously-verified material — nobody is asked to trust an explanation; they're asked to run something and read the result. This mirrors the discipline used to build the demo files themselves (every script was executed and its real output captured before being written down) — the training should model the practice, not just describe it.

---

## Day 0 — Facilitator Prep (before anyone else's Day 1)

**Owner: you, or whoever is leading the rollout.**

- [ ] Confirm Copilot CLI is installable/authenticated on team machines, or that IT/procurement has cleared it — don't discover this blocker on Day 1 with the whole team watching.
- [ ] Distribute all files: the two hello-tier demos and their setups, the full code-review package and its setup, the policy document, the terminology glossary. (Full file list in the Appendix.)
- [ ] Pick who leads each day (Section "Roles" below) — don't default everything to yourself; this is also how you start building L3 teaching evidence for your competency ladder.
- [ ] Block calendar time now. A rollout that competes with sprint work every day loses to sprint work every day — treat these as scheduled, protected sessions, not "whenever there's a gap."

---

## Week 1 — Learn & Practice (individual/pair hands-on, low stakes)

### Day 1 — Orientation: Why This Exists, and the Vocabulary
**Format:** 90 minutes, whole team, discussion-led, minimal screens.
**Materials:** `ai-eval-terminology-glossary.md` (pre-read the night before — assign it, don't read it live), `copilot-customization-framework-qa.md` for anyone who needs the primitive refresher.
**Activities:**
1. Open with the "why" in plain terms: an unverified agent ships on trust; this changes that.
2. Walk the five "if you only remember" points from the glossary out loud — don't re-teach the whole document, hit the load-bearing ideas: grade outcomes not narration, pass@k vs pass^k, never self-grade, pair positive with negative tests, instructions/skills need effect-based eval.
3. Run the self-check questions from the glossary as a group discussion, not a quiz — the goal is comfort with the vocabulary, not a score.
**Exit gate:** everyone can explain, in their own words, the difference between pass@k and pass^k. If that one concept isn't landing, don't move to Day 2 yet — it's the concept the rest of the week depends on.

### Day 2 — Hands-On: The Simple Loop (no CI, no infrastructure)
**Format:** Half day, everyone runs it individually on their own machine.
**Materials:** `simple-eval-loop-demo.md`, `setup-simple-eval-loop-demo.md`, plus `hello--find-todos.sh`, both hello fixtures, `simple--find-todos-v2.sh`, `simple-fixture--has-hack.cy.js`, `simple--eval.sh`.
**Activities:**
1. Each person runs Steps 1–10 from the setup runbook individually — this is deliberately solo, so everyone builds their own muscle memory rather than watching one person drive.
2. Whoever's leading does the **optional regression-break demonstration** live for the whole room once everyone's finished their own run — this is the one moment worth doing as a group: watching a real red result land.
3. Close with a 10-minute discussion: "what did Cases 1–2 passing again actually prove, versus Case 3 passing?"
**Exit gate:** every person has personally seen `===== EVAL RESULT: ALL CASES PASSED =====` on their own machine, for both the before and after versions of the skill.

### Day 3 — Hands-On: The Real Skill (Copilot CLI, actual `.github/skills/`)
**Format:** Half day, individual, with the facilitator on standby for CLI/environment issues.
**Materials:** `hello-world-eval-walkthrough.md`, `setup-hello-world-demo.md`, `hello--SKILL.md`, `hello--find-todos.sh`, both hello fixtures.
**Activities:**
1. Each person installs `cypress-todo-finder` as a real skill and confirms it with `/skills` — this is most people's first time actually seeing a skill they can inspect load into Copilot.
2. Run the unit test, trigger eval, and consistency check individually.
3. **This is the first day the `eval/` scaffold from the tooling guide gets used for real** — if it isn't set up yet, building it together at the start of this day is a reasonable use of the first 30 minutes.
**Exit gate:** everyone has a passing `find-todos.test.sh` and has personally read a `pass^5: 1` result and can say what it means.

### Day 4–5 — Hands-On: The Full Methodology (judgment, delta testing, CI, policy)
**Format:** Two half-days or one full day, pairs recommended — this is meaningfully harder than Days 2–3, and pairing catches confusion faster than solo struggle.
**Materials:** `eval-demo--cypress-code-review.md`, `howto-use-cypress-review-package.md`, all `skill--*` files, both `eval-fixture--*` files.
**Activities:**
1. **Day 4:** Steps 1–4 of the setup guide — install, verify, unit test, and the trigger suite (routing). Stop and discuss the confusable-skill-pair lesson (Step 6's case 003 equivalent) as a group before continuing.
2. **Day 5:** Steps 7–10 — the content-delta test (this is the one that proves the skill is worth having, make sure it isn't rushed), the healing-style safety-gate concept even though this particular skill isn't a healer (use the assertion-diff pattern as the teaching example of a hard gate), and finally CI wiring plus the policy's structural check.
**Exit gate:** every pair has a working CI workflow that fails when the policy-check step finds a skill with no matching eval — **prove this by testing it**: temporarily add a dummy skill folder with no eval and watch the pipeline fail, then remove it. Don't accept "the YAML looks right" as evidence.

---

## Week 2 — Apply & Institutionalize (real work, real stakes)

### Day 6 — The Policy, For Real
**Format:** 1 hour, whole team.
**Materials:** `policy--eval-gated-development.md`.
**Activities:**
1. Read the policy together, out loud if needed — this is the moment it stops being training material and becomes a rule.
2. Confirm CODEOWNERS is actually updated (Step 10 of the code-review setup guide) in your real repo, not just the demo.
3. Agree on the exception/waiver process now, before anyone needs it under deadline pressure — a policy without an agreed escape hatch gets silently ignored the first time it's inconvenient.
**Exit gate:** the CI policy-check job (Step 9's structural gate) is live against your real `.github/` folder, not just the demo repo.

### Day 7 — Everyone Picks a Real Asset and Writes Its Eval
**Format:** Full day, individual, this is the actual point of the whole two weeks.
**Materials:** `eval-must-test-checklist.md` (the minimum-viable-set of 15 cases as the starting punch list), `eval-plans-by-primitive.md` (whichever section matches what they picked).
**Activities:**
1. Each engineer picks **one skill, agent, or prompt they actually own** from your real estate — not a demo, the real thing.
2. Using the must-test checklist's ⭐ rows as the floor, they write and run a real eval suite for it.
**Exit gate:** every real asset picked today has at least a passing unit test (if it has bundled scripts) or a passing trigger/capability suite (if it doesn't) by end of day. Partial credit is fine — a started-but-incomplete real eval is still real progress; a finished demo repeated a third time is not.

### Day 8 — Peer Review
**Format:** Half day, paired cross-review.
**Materials:** `copilot-customization-audit-checklist.md` Section 5 (skills) and the relevant per-type section for whatever each person built.
**Activities:**
1. Pair people up to review each other's Day 7 eval work against the audit checklist.
2. Findings get fixed live where quick, filed as follow-ups where not.
**Exit gate:** every Day 7 eval has been read by someone other than its author.

### Day 9 — Wire It All Into CI
**Format:** Half day.
**Materials:** the CI workflow pattern from `howto-use-cypress-review-package.md` and `policy--eval-gated-development.md`.
**Activities:** each Day 7/8 eval gets added to the real CI workflow — regression suite if it's stable, capability suite (informational) if it's still new.
**Exit gate:** your real `.github/` estate now has a real, running CI eval gate covering at least as many assets as there were participants this week.

### Day 10 — Retro and Handoff to Ongoing Practice
**Format:** 90 minutes, whole team.
**Activities:**
1. Retro: what was confusing, what clicked, what needs a better example — feed this back into the demo files themselves (they're documents, not monuments; improve them).
2. **Explicitly hand off to the standing mechanisms** that keep this alive past this two-week sprint (Section below) — the rollout ends, the practice doesn't.
3. Log competency-ladder evidence now, while it's fresh: everyone who completed Day 7's real eval has a legitimate L2 portfolio entry.

---

## Roles

| Day(s) | Leads | Why |
|---|---|---|
| 1 | You or your strongest communicator | Sets the "why" — needs conviction, not just accuracy |
| 2–3 | A different person than Day 1 | Start distributing facilitation early — this is L3 teaching evidence in the making |
| 4–5 | Your eval architect (if named) or you | Hardest content, needs the deepest familiarity with the methodology docs |
| 6 | You | It's a policy — it should come from the person accountable for it |
| 7–9 | Self-directed, you float | This is real work, not a lecture — your job here is unblocking, not presenting |
| 10 | You | Retro and the ongoing-practice handoff are management functions |

---

## After Day 10: How This Stays Alive (don't skip this section)

A two-week sprint that ends with no follow-up decays back to zero within a quarter. Three mechanisms carry it forward, all of which already exist in your library:

1. **The policy is now permanent, not a training exercise.** `policy--eval-gated-development.md`'s "no eval, no merge" rule applies to every future asset, starting now.
2. **The kata cycle absorbs ongoing practice.** Run `agentic-kata-set.md`'s K4 (trigger calibration) using one of the real skills from Day 7 at your next biweekly session — the rollout's real work becomes the kata program's first real material instead of a hypothetical.
3. **The competency ladder captures what just happened.** Everyone who did Day 7's real eval work has evidence toward L2; log it in the ladder's register (`agentic-competency-ladder.md`) this week while it's traceable, not months from now when nobody remembers who did what.

If you're also running the larger technical program from `eval-program-master-plan.md` (evaluating the automation agent itself, not just individual skills), this two-week rollout is what makes that program's Phase 1–2 work achievable by the whole team instead of just your eval architect — sequence this rollout to land before or alongside that program's Phase 1.

---

## Definition of Mastery — What "Successfully Introduced" Actually Means

Not attendance. By the end of Day 10, each team member should be able to, unassisted:
1. Explain pass@k vs. pass^k and why "works every time" is a pass^k claim.
2. Write a unit test for a bundled script with a known-correct fixture, without a template in front of them.
3. Write a balanced trigger case pair (one positive, one negative) for a skill they didn't build.
4. State, correctly, why a skill's content needs a delta test and not just a trigger test.
5. Point to the specific CI check that would block their own merge if they skipped writing an eval — and explain why that's correct, not annoying.

**Run this as a real checklist against real people, not a vibe.** If someone can't do #1 or #5, the rollout isn't finished for them yet, regardless of what day the calendar says it is.

---

## Appendix — Full File Manifest by Day

| Day | Files |
|---|---|
| 1 | `ai-eval-terminology-glossary.md`, `copilot-customization-framework-qa.md` |
| 2 | `simple-eval-loop-demo.md`, `setup-simple-eval-loop-demo.md`, `hello--find-todos.sh`, `hello-fixture--has-todos.cy.js`, `hello-fixture--no-todos.cy.js`, `simple--find-todos-v2.sh`, `simple-fixture--has-hack.cy.js`, `simple--eval.sh` |
| 3 | `hello-world-eval-walkthrough.md`, `setup-hello-world-demo.md`, `hello--SKILL.md`, `hello--find-todos.sh`, both hello fixtures |
| 4–5 | `eval-demo--cypress-code-review.md`, `howto-use-cypress-review-package.md`, `skill--SKILL.md`, `skill--review-rubric.md`, `skill--pre-scan.sh`, both `eval-fixture--*.cy.js` files |
| 6 | `policy--eval-gated-development.md` |
| 7 | `eval-must-test-checklist.md`, `eval-plans-by-primitive.md` |
| 8 | `copilot-customization-audit-checklist.md` |
| 9 | `howto-use-cypress-review-package.md` (CI section), `policy--eval-gated-development.md` (CI section) |
| 10 | `agentic-kata-set.md`, `agentic-competency-ladder.md` |

*Owner: ________ · Rollout start date: ________ · Definition-of-mastery checked off for each team member by: ________*
