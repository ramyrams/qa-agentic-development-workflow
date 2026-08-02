# How to Use These Files — Step-by-Step
### Taking the `cypress-code-review` package from download to a working, policy-enforced skill in your repo

**The package (7 files):**
`skill--SKILL.md` · `skill--review-rubric.md` · `skill--pre-scan.sh` · `eval-fixture--bad-checkout.cy.js` · `eval-fixture--good-checkout.cy.js` · `eval-demo--cypress-code-review.md` (the deep walkthrough) · `policy--eval-gated-development.md` (the policy)

**This document is the operational sequence — do these steps in order.** Where a step needs more depth than fits here, it points to the file that has it rather than repeating it.

**Prerequisite:** Copilot CLI installed and authenticated, `jq` installed. If you haven't done this yet, stop here and complete `copilot-cli-eval-tooling-setup-guide.md` Part 1 first — nothing below works without it.

---

### Step 1 — Place the skill files in your repo

```bash
mkdir -p .github/skills/cypress-code-review/scripts
mkdir -p .github/skills/cypress-code-review/references

cp skill--SKILL.md .github/skills/cypress-code-review/SKILL.md
cp skill--pre-scan.sh .github/skills/cypress-code-review/scripts/pre-scan.sh
cp skill--review-rubric.md .github/skills/cypress-code-review/references/review-rubric.md
chmod +x .github/skills/cypress-code-review/scripts/pre-scan.sh
```

### Step 2 — Verify the skill actually loads

```bash
copilot
/skills
```
Confirm `cypress-code-review` is in the list. **Do not proceed past this step until it appears** — everything downstream assumes it.

### Step 3 — Set up your eval scaffold (skip if you already did this from the tooling guide)

```bash
mkdir -p eval/tasks/skills/cypress-code-review eval/tests/skills/cypress-code-review eval/hooks eval/runner eval/graders/{code,routing,judge} eval/runs eval/results
echo "eval/runs/" >> .gitignore
```
If any of this already exists from earlier setup, this is a no-op — safe to run regardless.

### Step 4 — Place the eval fixtures

```bash
mkdir -p eval/fixtures
cp eval-fixture--bad-checkout.cy.js eval/fixtures/bad-checkout.cy.js
cp eval-fixture--good-checkout.cy.js eval/fixtures/good-checkout.cy.js
```

### Step 5 — Run the bundled-script unit test (do this before anything else eval-related)

Create `eval/tests/skills/cypress-code-review/pre-scan.test.sh` using the script given in full in `eval-demo--cypress-code-review.md` Step 1, then:

```bash
bash eval/tests/skills/cypress-code-review/pre-scan.test.sh
```
**Expected output:** `PASS: all pre-scan unit tests passed`. This is deterministic — if it passes once, it passes forever until the script or fixtures change. No repeated runs needed for this one.

### Step 6 — Build and run the trigger eval

Create `eval/tasks/skills/cypress-code-review/trigger-suite.yaml` using the 5 cases given in full in `eval-demo--cypress-code-review.md` Step 2, then:

```bash
bash eval/runner/run-suite.sh eval/tasks/skills/cypress-code-review/trigger-suite.yaml 5
bash eval/graders/routing/check-routing.sh eval/tasks/skills/cypress-code-review/trigger-suite.yaml eval/runs/*/tool-calls.jsonl
```
**Read the confusion matrix, not just a pass/fail.** Pay specific attention to case `cyreview-trigger-003` — it's testing whether this skill and `cypress-authoring` stay correctly separated.

### Step 7 — Run the content-delta eval (proves the skill is worth having)

```bash
copilot -p "Review eval/fixtures/bad-checkout.cy.js for merge-readiness" -s --no-ask-user > eval/runs/with-skill.txt

mv .github/skills/cypress-code-review .github/skills/cypress-code-review.disabled
copilot -p "Review eval/fixtures/bad-checkout.cy.js for merge-readiness" -s --no-ask-user > eval/runs/without-skill.txt
mv .github/skills/cypress-code-review.disabled .github/skills/cypress-code-review
```
Compare the two output files against the 6 known findings from Step 5's fixture. The gap between them is your evidence — write it down (this is what you'll cite if anyone ever asks "is this skill actually doing anything").

### Step 8 — Run the consistency check

```bash
bash eval/runner/run-suite.sh eval/tasks/skills/cypress-code-review/review-capability.yaml 5
bash eval/runner/consistency.sh cyreview-capability-001 5
```
Look for `pass^5: 1`. If it's lower, re-read `eval-demo--cypress-code-review.md` Step 4 for the specific known failure pattern to check first (citation of the `focused-test-left-in` finding).

### Step 9 — Graduate what's stable into the CI regression gate

Add the excerpt from `eval-demo--cypress-code-review.md` Step 5 to `.github/workflows/agent-skill-eval.yml`:
- Step 5's unit test → **regression suite, blocking, immediately** (it's deterministic and already verified).
- Steps 6–8's suites → **capability suite, informational**, until you've watched them pass consistently across a few real weeks — then move them over too.

### Step 10 — Apply the policy structurally, not just as a document

Add the `policy-check` job from `policy--eval-gated-development.md`'s CI section to the same workflow file. This is what makes "no eval, no merge" real: it fails the build if a future changed skill has no matching eval file at all, regardless of what that eval would say.

Then:
```bash
# .github/CODEOWNERS — add or confirm this line
/.github/skills/  /eval/  @your-team-eval-reviewers
```
Same reviewers on both paths, per the policy's ownership rule — someone judging a skill PR and its eval PR together is a stronger check than two separate reviewers.

### Step 11 — Use it day to day (how an engineer actually invokes this)

No special syntax needed — the skill fires automatically on a matching ask:
```
"Can you review checkout.cy.ts before I open the PR?"
```
in VS Code Copilot Chat, or headlessly:
```bash
copilot -p "Review cypress/e2e/checkout/pay.cy.ts for merge-readiness" -s --no-ask-user
```
It also composes with your existing `/review-test-pr` prompt and `test-reviewer` agent — this skill is the reusable capability either can call, not a replacement for them.

### Step 12 — What happens when someone updates this skill later

Per the policy: any edit to `SKILL.md`, `pre-scan.sh`, or `review-rubric.md` re-triggers the full suite (Steps 5–8) in CI automatically, because the workflow watches `.github/skills/**`. **Nobody needs to remember to re-run anything manually** — that's the entire point of wiring it into CI rather than leaving it as a one-time manual exercise. If the update breaks a previously-passing regression case, the PR is blocked, exactly as it would be for any other regression.

---

## The Whole Sequence, Compressed (for whoever just wants the commands)

```bash
# 1-4: install
mkdir -p .github/skills/cypress-code-review/{scripts,references} eval/fixtures
cp skill--SKILL.md .github/skills/cypress-code-review/SKILL.md
cp skill--pre-scan.sh .github/skills/cypress-code-review/scripts/pre-scan.sh
cp skill--review-rubric.md .github/skills/cypress-code-review/references/review-rubric.md
cp eval-fixture--*.cy.js eval/fixtures/
chmod +x .github/skills/cypress-code-review/scripts/pre-scan.sh

# 5: verify + unit test
copilot   # then /skills — confirm it loaded
bash eval/tests/skills/cypress-code-review/pre-scan.test.sh

# 6-8: routing, delta, consistency (build the YAML/scripts from eval-demo--cypress-code-review.md first)
bash eval/runner/run-suite.sh eval/tasks/skills/cypress-code-review/trigger-suite.yaml 5
bash eval/runner/run-suite.sh eval/tasks/skills/cypress-code-review/review-capability.yaml 5
bash eval/runner/consistency.sh cyreview-capability-001 5

# 9-10: wire CI + policy (edit .github/workflows/agent-skill-eval.yml and CODEOWNERS)
```

*If any step's expected output doesn't match what's described, stop and fix that step before moving to the next — this sequence is intentionally ordered so each step's success is a prerequisite for trusting the next one's result.*
