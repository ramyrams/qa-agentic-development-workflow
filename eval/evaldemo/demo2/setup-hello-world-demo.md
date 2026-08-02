# Setup: The Hello-World Skill Demo — Step by Step
### Same format as the simple-loop-demo setup — just the commands, in order.

**Files used:** `hello--SKILL.md` · `hello--find-todos.sh` · `hello-fixture--has-todos.cy.js` · `hello-fixture--no-todos.cy.js` — all already delivered.

**One difference from the simple-loop-demo setup, worth knowing before you start:** that one needed nothing but bash. This one is the *real* Copilot skill — installed under `.github/skills/`, verified with the actual CLI — so it needs Copilot CLI installed and authenticated (`copilot-cli-eval-tooling-setup-guide.md` Part 1) plus the `eval/` scaffold from that same guide's Part 2. If you only want the bash-only experience, use the simple-loop-demo instead; this one is intentionally one step closer to how your real skills will actually be evaluated.

**CI is deliberately left out of this runbook**, consistent with keeping this whole intro tier CI-free — the original walkthrough's Step 6 had one CI line; skip it here and wire it later using `howto-use-cypress-review-package.md`'s CI section as the template whenever you're ready to add it for this skill too.

---

### Step 1 — Install the skill

```bash
mkdir -p .github/skills/cypress-todo-finder/scripts
cp hello--SKILL.md .github/skills/cypress-todo-finder/SKILL.md
cp hello--find-todos.sh .github/skills/cypress-todo-finder/scripts/find-todos.sh
chmod +x .github/skills/cypress-todo-finder/scripts/find-todos.sh
```

### Step 2 — Verify it loads

```bash
copilot
```
Inside the session:
```
/skills
```
**Confirm `cypress-todo-finder` is listed. Stop here if it isn't — don't proceed to Step 3.**

### Step 3 — Run the script directly, then wrap it as a repeatable unit test

```bash
mkdir -p eval/fixtures eval/tests/skills/cypress-todo-finder
cp hello-fixture--has-todos.cy.js eval/fixtures/has-todos.cy.js
cp hello-fixture--no-todos.cy.js eval/fixtures/no-todos.cy.js

# run it directly first, look at the raw output
bash .github/skills/cypress-todo-finder/scripts/find-todos.sh eval/fixtures/has-todos.cy.js
bash .github/skills/cypress-todo-finder/scripts/find-todos.sh eval/fixtures/no-todos.cy.js
```

```bash
cat > eval/tests/skills/cypress-todo-finder/find-todos.test.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT=".github/skills/cypress-todo-finder/scripts/find-todos.sh"

ACTUAL=$(bash "$SCRIPT" eval/fixtures/has-todos.cy.js)
[ "$(echo "$ACTUAL" | wc -l)" -eq 2 ] || { echo "FAIL: expected exactly 2 findings"; exit 1; }
bash "$SCRIPT" eval/fixtures/has-todos.cy.js > /dev/null; [ $? -eq 1 ] || { echo "FAIL: should exit 1"; exit 1; }

CLEAN=$(bash "$SCRIPT" eval/fixtures/no-todos.cy.js)
[ -z "$CLEAN" ] || { echo "FAIL: expected zero findings on clean fixture"; exit 1; }
bash "$SCRIPT" eval/fixtures/no-todos.cy.js > /dev/null; [ $? -eq 0 ] || { echo "FAIL: should exit 0"; exit 1; }

echo "PASS: find-todos unit tests passed"
EOF
chmod +x eval/tests/skills/cypress-todo-finder/find-todos.test.sh

bash eval/tests/skills/cypress-todo-finder/find-todos.test.sh
```
**Expected:** `PASS: find-todos unit tests passed`

*(Note this test uses `set -euo pipefail` and works fine — unlike the simple-loop-demo's `eval.sh`, this script captures each exit code into `$?` on its own line rather than testing it inline in a condition, so `-e` never fires mid-check. Worth pointing out to the team as a second, different way to avoid the same class of bug.)*

### Step 4 — Trigger eval (requires the `eval/runner/` scripts from the tooling guide)

```bash
mkdir -p eval/tasks/skills/cypress-todo-finder
cat > eval/tasks/skills/cypress-todo-finder/trigger-suite.yaml << 'EOF'
- task_id: hello-trigger-001
  ask: "Are there any TODOs left in this spec file?"
  expected_fires: true
- task_id: hello-trigger-002
  ask: "Write a test for the profile page"
  expected_fires: false
EOF

bash eval/runner/run-suite.sh eval/tasks/skills/cypress-todo-finder/trigger-suite.yaml 5
bash eval/graders/routing/check-routing.sh eval/tasks/skills/cypress-todo-finder/trigger-suite.yaml eval/runs/*/tool-calls.jsonl
```
If you haven't built `eval/runner/run-suite.sh` or `eval/graders/routing/check-routing.sh` yet, that's the tooling guide's Part 4 and Part 5.2 — this step is the one place this demo depends on infrastructure beyond what's in this file.

### Step 5 — Consistency check

```bash
bash eval/runner/consistency.sh hello-trigger-001 5
```
**Expected:** `pass^5: 1`.

---

## What's Different From the Full Setup (`howto-use-cypress-review-package.md`)

| | This demo | The full code-review demo |
|---|---|---|
| Steps | 5 | 12 |
| Judgment layer (rubric, LLM judge) | None — pure deterministic script | Yes |
| Content-delta eval | Skipped | Included |
| CI | Deliberately omitted here | Included |
| Policy enforcement | N/A | Included |

Same shape, fewer layers — exactly the lesson the walkthrough itself calls out. When your team is ready to see CI added to *this* skill specifically, reuse `howto-use-cypress-review-package.md` Steps 9–10 as the template — nothing about them is specific to the code-review skill.
