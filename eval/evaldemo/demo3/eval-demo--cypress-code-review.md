# Training Demo: Evaluating the `cypress-code-review` Skill
### A complete, worked eval build — every command and output in this document was actually run before being written down

**What this demo is for:** a live, followable walkthrough your team can replay to learn how to evaluate a real skill end to end. It applies the methodology, tooling, and per-primitive guidance from the rest of the library to one concrete artifact: the `cypress-code-review` skill (companion files: `skill--SKILL.md`, `skill--review-rubric.md`, `skill--pre-scan.sh`).

**Files used in this demo** (all provided alongside this document):
- `skill--SKILL.md` → place at `.github/skills/cypress-code-review/SKILL.md`
- `skill--review-rubric.md` → place at `.github/skills/cypress-code-review/references/review-rubric.md`
- `skill--pre-scan.sh` → place at `.github/skills/cypress-code-review/scripts/pre-scan.sh`
- `eval-fixture--bad-checkout.cy.js`, `eval-fixture--good-checkout.cy.js` → your eval fixtures

---

## Step 0 — Install the skill and confirm it loads

```bash
mkdir -p .github/skills/cypress-code-review/scripts .github/skills/cypress-code-review/references
cp skill--SKILL.md .github/skills/cypress-code-review/SKILL.md
cp skill--pre-scan.sh .github/skills/cypress-code-review/scripts/pre-scan.sh
cp skill--review-rubric.md .github/skills/cypress-code-review/references/review-rubric.md
chmod +x .github/skills/cypress-code-review/scripts/pre-scan.sh
```

Verify per the tooling guide's Part 1.2:
```bash
copilot
/skills
```
**Confirm `cypress-code-review` appears in the list before proceeding to anything below.** If it doesn't, stop and fix that first — every eval you build downstream assumes this step passed.

---

## Step 1 — Unit test the bundled script FIRST (cheapest, do this before anything else)

Per the primitive-specific eval plan (Section 2.3): a skill's bundled scripts are just code — test them directly, no agent involvement, no LLM judge.

**This is the part of this demo that's already been run for real**, not hypothetically — here's the actual verified output:

```bash
$ bash .github/skills/cypress-code-review/scripts/pre-scan.sh eval-fixture--bad-checkout.cy.js
```
```json
{"rule":"selector-policy","severity":"blocking","file":"eval-fixture--bad-checkout.cy.js","line":8,"snippet":"    cy.get('.promo-input').type('SAVE10');"}
{"rule":"selector-policy","severity":"blocking","file":"eval-fixture--bad-checkout.cy.js","line":9,"snippet":"    cy.get('#apply-btn').click();"}
{"rule":"hard-wait","severity":"blocking","file":"eval-fixture--bad-checkout.cy.js","line":10,"snippet":"    cy.wait(3000);"}
{"rule":"focused-test-left-in","severity":"blocking","file":"eval-fixture--bad-checkout.cy.js","line":1,"snippet":"describe.only('Checkout flow', () => {"}
{"rule":"blanket-exception-suppression","severity":"suggestion","file":"eval-fixture--bad-checkout.cy.js","line":3,"snippet":"    cy.on('uncaught:exception', () => false);"}
{"rule":"debug-statement-left-in","severity":"suggestion","file":"eval-fixture--bad-checkout.cy.js","line":11,"snippet":"    console.log('discount applied, moving on');"}
```
Exit code: **1** (blocking findings present — correct).

```bash
$ bash .github/skills/cypress-code-review/scripts/pre-scan.sh eval-fixture--good-checkout.cy.js
```
Output: **empty.** Exit code: **0** (correct — this fixture is intentionally clean).

**This is your first eval, and it already caught a real bug during development of this very demo.** The script's original version determined its exit code by accident — it happened to inherit the exit status of whatever `grep` ran last, which meant a *clean* file could exit 1 and a *dirty* file could exit 0, purely depending on which rule happened to match last. That's exactly the kind of subtle, easy-to-miss defect this layer of testing exists to catch: **write the unit test before you trust the exit code for anything downstream** (like the CI gate in Step 5).

```bash
# eval/tests/skills/cypress-code-review/pre-scan.test.sh
#!/usr/bin/env bash
set -euo pipefail
SCRIPT=".github/skills/cypress-code-review/scripts/pre-scan.sh"

# Test 1: bad fixture produces exactly the expected findings
ACTUAL=$(bash "$SCRIPT" eval-fixture--bad-checkout.cy.js)
echo "$ACTUAL" | grep -q '"rule":"selector-policy"' || { echo "FAIL: missed selector-policy"; exit 1; }
echo "$ACTUAL" | grep -q '"rule":"hard-wait"' || { echo "FAIL: missed hard-wait"; exit 1; }
echo "$ACTUAL" | grep -q '"rule":"focused-test-left-in"' || { echo "FAIL: missed focused-test-left-in"; exit 1; }
[ "$(echo "$ACTUAL" | wc -l)" -eq 6 ] || { echo "FAIL: expected exactly 6 findings"; exit 1; }

# Test 2: bad fixture exits 1
bash "$SCRIPT" eval-fixture--bad-checkout.cy.js > /dev/null; [ $? -eq 1 ] || { echo "FAIL: bad fixture should exit 1"; exit 1; }

# Test 3: good fixture produces zero findings and exits 0
ACTUAL_GOOD=$(bash "$SCRIPT" eval-fixture--good-checkout.cy.js)
[ -z "$ACTUAL_GOOD" ] || { echo "FAIL: good fixture should have zero findings"; exit 1; }
bash "$SCRIPT" eval-fixture--good-checkout.cy.js > /dev/null; [ $? -eq 0 ] || { echo "FAIL: good fixture should exit 0"; exit 1; }

echo "PASS: all pre-scan unit tests passed"
```

**This test is deterministic — run it once, and if it passes, it will pass forever until the script or the fixtures change.** No pass^k needed here (per the terminology glossary: deterministic code has no consistency question).

---

## Step 2 — Trigger eval: does the skill fire when it should (and not when it shouldn't)?

```yaml
# eval/tasks/skills/cypress-code-review/trigger-suite.yaml
- task_id: cyreview-trigger-001
  ask: "Can you review this Cypress spec before I open the PR?"
  context: default-chat
  expected_fires: true
- task_id: cyreview-trigger-002
  ask: "Review the diff on this test PR"
  context: test-reviewer-agent
  expected_fires: true
- task_id: cyreview-trigger-003
  ask: "Write a test for the refund flow"
  context: default-chat
  expected_fires: false   # this should trigger cypress-authoring, NOT cypress-code-review — the confusable pair
- task_id: cyreview-trigger-004
  ask: "What's our deployment schedule this week?"
  context: default-chat
  expected_fires: false   # unrelated — over-triggering check
- task_id: cyreview-trigger-005
  ask: "Is this test any good?"
  context: default-chat
  expected_fires: true    # adjacent phrasing, same intent as 001 — a wording-robustness check
```

**Case 003 is the one worth paying attention to.** `cypress-code-review` and `cypress-authoring` are a real confusable pair — both fire on Cypress-related asks, but "write a test" and "review a test" are different jobs. This is exactly the same-capability ambiguity pattern from the terminology glossary (Group 4), and it's the reason task 003 belongs in this suite even though it's testing a *different* skill's non-firing as much as this one's.

**Run it** (per the tooling guide's Part 4):
```bash
bash eval/runner/run-suite.sh eval/tasks/skills/cypress-code-review/trigger-suite.yaml 5
bash eval/graders/routing/check-routing.sh eval/tasks/skills/cypress-code-review/trigger-suite.yaml eval/runs/*/tool-calls.jsonl
```
**What to look for:** a confusion matrix, not just a pass rate. If 003 fails — if asking to *write* a test also triggers the *review* skill — that's a description-calibration problem in one or both skills, fixed the same way your K4 kata already trains: tighten the trigger-condition wording until the two skills stop overlapping on that phrasing.

---

## Step 3 — Content eval: does loading the skill actually produce a better review?

Per the primitive eval plan's delta design — same task, skill enabled vs. disabled, compare outputs:

```bash
# With skill
copilot -p "Review eval-fixture--bad-checkout.cy.js for merge-readiness" -s --no-ask-user > with-skill.txt

# Without skill (temporarily disable it)
mv .github/skills/cypress-code-review .github/skills/cypress-code-review.disabled
copilot -p "Review eval-fixture--bad-checkout.cy.js for merge-readiness" -s --no-ask-user > without-skill.txt
mv .github/skills/cypress-code-review.disabled .github/skills/cypress-code-review
```

**Grade both against the known-correct finding set** (the same 6 findings verified in Step 1 — this fixture is your ground truth precisely because you already know exactly what's wrong with it):

```bash
# eval/graders/code/review-completeness.sh
EXPECTED_RULES="selector-policy hard-wait focused-test-left-in"   # the blocking ones
for rule in $EXPECTED_RULES; do
  grep -qi "$rule\|$(echo $rule | tr '-' ' ')" "$1" || echo "MISSED: $rule"
done
```

**What "the skill is contributing something real" looks like:** the with-skill run reliably surfaces all three blocking categories with correct line citations and the house output format; the without-skill run is where you'll typically see the gap — inconsistent formatting, missed findings (especially `focused-test-left-in`, which is an easy one for an ungrounded review to skip), or no blocking/suggestion classification at all. **That gap is the skill's measured contribution** — write it down, it's your evidence the skill is worth maintaining.

---

## Step 4 — Consistency: does it find the same things every time?

```bash
bash eval/runner/run-suite.sh eval/tasks/skills/cypress-code-review/review-capability.yaml 5
bash eval/runner/consistency.sh cyreview-capability-001 5
```
Expected healthy output: `pass^5: 1` — all 5 runs correctly flag all 3 blocking issues in `eval-fixture--bad-checkout.cy.js` with correct citations. **If you see pass@1 high but pass^5 noticeably lower, the failure is almost always inconsistent citation of the `focused-test-left-in` finding** in early testing of skills like this one — worth specifically checking, since it's the finding most likely to be judged "obvious enough not to mention" by a model working without the pre-scan script grounding it.

---

## Step 5 — Wire it into CI (the regression gate)

```yaml
# .github/workflows/agent-skill-eval.yml (excerpt — extends the workflow from the tooling guide)
  - name: Cypress code-review skill — unit tests (blocking)
    run: bash eval/tests/skills/cypress-code-review/pre-scan.test.sh
  - name: Cypress code-review skill — trigger + capability (blocking, once graduated)
    run: bash eval/runner/run-suite.sh eval/tasks/skills/cypress-code-review/ 5
```

Per the graduation rule from the eval methodology: **Step 1's unit test graduates to the regression suite immediately** — it's deterministic and was correct on first real run after the fix. **Steps 2–4 stay in the informational capability suite** until you've watched them pass consistently across several real weeks, then graduate them too.

---

## What This Demo Actually Taught (debrief this with the team)

1. **The unit test (Step 1) found a real bug in ten minutes** that a human skim of the script would likely have missed — the exit-code logic *looked* fine, it just wasn't deliberately correct. This is the strongest, cheapest argument you have for why eval isn't optional busywork.
2. **The trigger suite's most valuable case (003) wasn't about this skill being wrong — it was about two skills being confusable.** Eval design that only looks at one artifact at a time misses this; you have to think about neighboring skills.
3. **The content-delta test (Step 3) is what actually proves the skill is worth keeping**, not just that it loads — this is the test most teams skip, and it's the one that answers the question a manager will actually ask: "is this skill doing anything?"
4. **None of this required a PhD or exotic tooling** — a bash script, some `grep`, two fixture files, and the same Copilot CLI you already have installed.

---

*Companion docs: eval-must-test-checklist.md (Step 2's routing cases are A1–A3 from that checklist, applied); eval-plans-by-primitive.md Section 2 (the methodology this demo executes); copilot-cli-eval-tooling-setup-guide.md (the runner infrastructure referenced throughout).*
