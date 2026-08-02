# Hello World: Your First Skill Eval, End to End
### Step 1 of the training sequence — do this before `eval-demo--cypress-code-review.md`

**Why this exists:** the code-review demo is the *real* methodology — trigger eval, content-delta eval, LLM-judge grading, consistency, CI policy enforcement, all of it. That's a lot to absorb in one sitting. This document strips everything down to the smallest possible skill and walks the exact same end-to-end shape — install, verify, eval, CI — with nothing to distract from the mechanics. **Do this one first.** Once it feels obvious, the code-review demo is the same shape with more layers, not a different process.

**The skill:** `cypress-todo-finder`. One job — find `TODO`/`FIXME` comments left in a test file. One script. No rubric, no LLM judgment needed, no delta test. This is deliberately as close to "hello world" as a real, useful skill gets.

**Files used:** `hello--SKILL.md`, `hello--find-todos.sh`, `hello-fixture--has-todos.cy.js`, `hello-fixture--no-todos.cy.js` — all provided, all already verified working.

---

## Step 1 — Install it

```bash
mkdir -p .github/skills/cypress-todo-finder/scripts
cp hello--SKILL.md .github/skills/cypress-todo-finder/SKILL.md
cp hello--find-todos.sh .github/skills/cypress-todo-finder/scripts/find-todos.sh
chmod +x .github/skills/cypress-todo-finder/scripts/find-todos.sh
```

Notice there's no `references/` folder this time — unlike the code-review skill. **That's a deliberate lesson, not an oversight:** a skill only needs bundled reference material when there's judgment-based content to layer on top of a script. This skill has none, so it doesn't have one. Don't add structure a skill doesn't need.

## Step 2 — Verify it loads

```bash
copilot
/skills
```
Confirm `cypress-todo-finder` appears. Stop here if it doesn't.

## Step 3 — Run the script directly first (before involving the agent at all)

This is the step people skip and shouldn't — confirm the tool works in isolation before you ever ask an agent to use it:

```bash
$ bash .github/skills/cypress-todo-finder/scripts/find-todos.sh hello-fixture--has-todos.cy.js
```
```json
{"line":3,"text":"TODO: replace with data-cy selector once the avatar component is refactored"}
{"line":11,"text":"FIXME: this assertion is too weak, check the actual saved value via API"}
```
Exit code: **1** (findings present — correct).

```bash
$ bash .github/skills/cypress-todo-finder/scripts/find-todos.sh hello-fixture--no-todos.cy.js
```
Output: **empty.** Exit code: **0** (correct).

**This already is a complete eval** — a code grader with two labeled fixtures and a known-correct answer for each. Turn it into a repeatable test:

```bash
# eval/tests/skills/cypress-todo-finder/find-todos.test.sh
#!/usr/bin/env bash
set -euo pipefail
SCRIPT=".github/skills/cypress-todo-finder/scripts/find-todos.sh"

ACTUAL=$(bash "$SCRIPT" hello-fixture--has-todos.cy.js)
[ "$(echo "$ACTUAL" | wc -l)" -eq 2 ] || { echo "FAIL: expected exactly 2 findings"; exit 1; }
bash "$SCRIPT" hello-fixture--has-todos.cy.js > /dev/null; [ $? -eq 1 ] || { echo "FAIL: should exit 1"; exit 1; }

CLEAN=$(bash "$SCRIPT" hello-fixture--no-todos.cy.js)
[ -z "$CLEAN" ] || { echo "FAIL: expected zero findings on clean fixture"; exit 1; }
bash "$SCRIPT" hello-fixture--no-todos.cy.js > /dev/null; [ $? -eq 0 ] || { echo "FAIL: should exit 0"; exit 1; }

echo "PASS: find-todos unit tests passed"
```
```bash
bash eval/tests/skills/cypress-todo-finder/find-todos.test.sh
```
**Expected: `PASS: find-todos unit tests passed`.** You just wrote and ran your first eval. Everything after this point is the same idea, repeated with more sophistication.

## Step 4 — Trigger eval (does the skill fire when it should, and not when it shouldn't)

```yaml
# eval/tasks/skills/cypress-todo-finder/trigger-suite.yaml
- task_id: hello-trigger-001
  ask: "Are there any TODOs left in this spec file?"
  expected_fires: true
- task_id: hello-trigger-002
  ask: "Write a test for the profile page"
  expected_fires: false   # a different job entirely — should NOT fire
```
```bash
bash eval/runner/run-suite.sh eval/tasks/skills/cypress-todo-finder/trigger-suite.yaml 5
bash eval/graders/routing/check-routing.sh eval/tasks/skills/cypress-todo-finder/trigger-suite.yaml eval/runs/*/tool-calls.jsonl
```
Just two cases — one positive, one negative — because that's the minimum that actually proves something (recall the balanced-pairs rule: testing only the positive direction never catches over-triggering).

## Step 5 — Consistency check

```bash
bash eval/runner/consistency.sh hello-trigger-001 5
```
Expect `pass^5: 1` — this skill's job is simple enough that instability here would be a real, worth-investigating signal, not noise.

## Step 6 — One CI line, done

```yaml
  - name: TODO-finder skill — unit test (blocking)
    run: bash eval/tests/skills/cypress-todo-finder/find-todos.test.sh
```
That's the entire regression gate for this skill. No judge model, no rubric, no delta test — because this skill doesn't need them. **Match the eval's complexity to the skill's complexity; don't build the full five-layer methodology for something this simple.**

---

## What You Just Learned (the whole point of doing this one first)

1. **Install → verify → test the deterministic part → test triggering → check consistency → wire CI.** That's the shape of every eval in this library, from this two-file skill to the healing agent in your program plan. The shape doesn't change; only how many layers you need does.
2. **Not every skill needs a rubric, an LLM judge, or a delta test.** Those exist for skills with actual judgment content. This skill has none — building them here would be overhead with no signal to show for it.
3. **The unit test is still the highest-value, first thing to build**, exactly like it was for the more complex skill — that pattern holds regardless of how simple or complex the skill is.

**Next:** `eval-demo--cypress-code-review.md`. Same shape, three more layers (rubric-based judgment, content-delta proof, full CI policy enforcement) — and now you'll recognize every step instead of encountering the methodology for the first time.
