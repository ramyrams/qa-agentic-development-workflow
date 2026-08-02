# Full End-to-End Eval Demo — Following agentskills.io's Methodology
### Applied to the real `cypress-code-review` skill, with every file provided

**Source methodology:** https://agentskills.io/skill-creation/evaluating-skills — this demo follows that structure exactly (test cases in `evals/evals.json`, with-skill/without-skill comparison, an `iteration-N/` workspace, script + LLM grading, `benchmark.json` aggregation, human review, and the improvement loop), applied to a skill you already have rather than the source's own CSV-analyzer example.

**Read this before anything else — what's real and what isn't:** this sandbox has no network access, so I cannot invoke a live Copilot CLI session to actually generate `with_skill`/`without_skill` outputs — that step requires *your* environment. Everything that doesn't need a live agent call was actually built and run before being written into this document: `evals.json` is real and validated, `check-assertions.sh` is real and was tested against both fixtures with genuine output shown below (including a real bug it caught along the way). Everything that *does* need a live agent call — the actual review text, `grading.json`'s LLM-judged rows, `benchmark.json`'s real numbers — is clearly marked `EXAMPLE` in the provided files, showing you the correct shape so you recognize a good result when your own run produces one.

**Files provided:** `agentskills--evals.json`, `agentskills--check-assertions.sh`, `agentskills--timing-example.json`, `agentskills--grading-example.json`, `agentskills--benchmark-example.json`, `agentskills--feedback-example.json`. Reused from earlier in this conversation: `skill--SKILL.md`, `skill--pre-scan.sh`, `skill--review-rubric.md` (the skill itself), `eval-fixture--bad-checkout.cy.js`, `eval-fixture--good-checkout.cy.js` (the two input files).

---

## Step 1 — Install the skill

```bash
mkdir -p cypress-code-review/scripts
cp skill--SKILL.md cypress-code-review/SKILL.md
cp skill--pre-scan.sh cypress-code-review/scripts/pre-scan.sh
chmod +x cypress-code-review/scripts/pre-scan.sh
```
(`skill--review-rubric.md` goes at `cypress-code-review/references/review-rubric.md` if you want the full judgment-based review, not just the mechanical scan — optional for this demo, since the eval below focuses on the mechanically-checkable assertions.)

## Step 2 — Design test cases

Two test cases, each with a realistic prompt (not "review this file" — a real phrasing someone would actually type), a plain-language description of success, and the input file:

```bash
mkdir -p cypress-code-review/evals/files
cp eval-fixture--bad-checkout.cy.js cypress-code-review/evals/files/bad-checkout.cy.js
cp eval-fixture--good-checkout.cy.js cypress-code-review/evals/files/good-checkout.cy.js
cp agentskills--evals.json cypress-code-review/evals/evals.json
```

**One honest deviation from the source's recommended order, worth calling out explicitly:** the source guidance says don't write assertions until *after* you've seen a first round of real output — you often don't know exactly what "good" looks like until the skill has actually run. Because this sandbox can't run a live agent session, I wrote the assertions in `evals.json` up front, grounded in what the deterministic pre-scan script is already known to find (verified in Step 1 of the earlier code-review demo). **When you use this pattern on a skill of your own, do it in the proper order**: write just the `prompt` and `expected_output` first, run the eval once, look at what actually comes back, and only then add the `assertions` array — you'll write better assertions after seeing a real result than you would guessing in advance.

## Step 3 — Set up the workspace

```bash
mkdir -p cypress-code-review-workspace/iteration-1/eval-review-checkout-bad/with_skill/outputs
mkdir -p cypress-code-review-workspace/iteration-1/eval-review-checkout-bad/without_skill/outputs
mkdir -p cypress-code-review-workspace/iteration-1/eval-review-checkout-clean/with_skill/outputs
mkdir -p cypress-code-review-workspace/iteration-1/eval-review-checkout-clean/without_skill/outputs
```
This structure — one folder per eval case, each split into a `with_skill` and `without_skill` side — is what makes the comparison in Step 7 possible. Skipping the `without_skill` half is the single most common shortcut people take, and it's the one that matters most: without it you only know the skill *produces* something, never whether it's actually better than nothing.

## Step 4 — Spawn the runs (this is the part you run yourself)

Each run starts from a clean session — no leftover context from writing the skill itself, so the agent follows only what `SKILL.md` says. Using the headless Copilot CLI pattern from the tooling guide:

**With skill, eval case 1:**
```bash
copilot -p "Can you review cypress/e2e/checkout/pay.cy.js before I open the PR? Just tell me if there's anything blocking." \
  --agent cypress-code-review \
  -s --no-ask-user \
  > cypress-code-review-workspace/iteration-1/eval-review-checkout-bad/with_skill/outputs/review.md
```

**Without skill (baseline), same prompt — disable the skill first:**
```bash
mv cypress-code-review/SKILL.md cypress-code-review/SKILL.md.disabled
copilot -p "Can you review cypress/e2e/checkout/pay.cy.js before I open the PR? Just tell me if there's anything blocking." \
  -s --no-ask-user \
  > cypress-code-review-workspace/iteration-1/eval-review-checkout-bad/without_skill/outputs/review.md
mv cypress-code-review/SKILL.md.disabled cypress-code-review/SKILL.md
```

Repeat both for eval case 2's prompt (`"Is cypress/e2e/checkout/pay.cy.js ready to merge?"`), saving into `eval-review-checkout-clean/with_skill/outputs/` and `.../without_skill/outputs/`.

## Step 5 — Capture timing

Immediately after each run, record token count and duration — most agent CLIs surface this in the session/task completion output and it isn't saved anywhere else automatically:

```bash
# cypress-code-review-workspace/iteration-1/eval-review-checkout-bad/with_skill/timing.json
```
See `agentskills--timing-example.json` for the exact shape — two fields, `total_tokens` and `duration_ms`. Fill in your real numbers from the run's completion output.

## Step 6 — Grade the outputs

Two grading paths, exactly per the source's split between mechanical and judgment-based checks:

**Mechanically-checkable assertions — the real, tested part:**
```bash
cd cypress-code-review
bash evals/check-assertions.sh 1 evals/files/bad-checkout.cy.js
```
This is genuinely verified — here's what actually happened when it was run in this sandbox:
```
=== Mechanically-checkable assertions for eval id=1, file=evals/files/bad-checkout.cy.js ===
PASS: selector-policy violation found for .promo-input
PASS: selector-policy violation found for #apply-btn
PASS: hard wait cy.wait(3000) flagged
PASS: describe.only flagged

Mechanical check summary: 4 passed, 0 failed
```
```bash
bash evals/check-assertions.sh 2 evals/files/good-checkout.cy.js
```
```
=== Mechanically-checkable assertions for eval id=2, file=evals/files/good-checkout.cy.js ===
PASS: zero blocking findings
PASS: no false-positive selector-policy finding

Mechanical check summary: 2 passed, 0 failed
```

**One real bug this script had, worth telling the team about:** the first version hardcoded eval case 1's four checks and ran them unconditionally — which meant running it against case 2's clean fixture produced four confident-looking `FAIL` results that meant nothing, because those assertions were never relevant to that case. The fix was making the script dispatch by eval ID, checking only the assertions that actually apply to that case. This is exactly the source guidance's point about **reviewing the assertions themselves, not just trusting the results** — a grading script checking the wrong thing produces a confident, wrong answer, and it looks identical to a real failure until you look closer.

**Judgment-based assertions** (classification present, verdict wording) — these need the actual captured `with_skill/outputs/review.md` text, graded by an LLM judge or a human reading it against the assertion. `agentskills--grading-example.json` shows the combined shape: four rows sourced from the script (real), two rows marked `EXAMPLE` for you to replace with real evidence quoted from your own captured output.

## Step 7 — Aggregate into benchmark.json

Once every run in the iteration is graded, compute pass-rate, time, and token statistics per configuration, plus the delta between them — `agentskills--benchmark-example.json` shows the shape and includes a worked explanation of what the numbers would mean if they were real. **The `delta` block is the actual point of this whole exercise**: it's the concrete answer to "is this skill worth having," expressed as a trade-off (more time and tokens spent) against a payoff (higher, more consistent pass rate) — not a vague impression.

## Step 8 — Analyze patterns, not just the aggregate

Per the source guidance, read past the summary numbers for these specific patterns:
- **An assertion that passes in both `with_skill` and `without_skill`** tells you nothing about the skill's value — the baseline agent already handles it fine. Candidate for removal from the eval, not a sign of skill quality.
- **An assertion that fails in both** means the assertion itself is broken, or the case is too hard — fix the assertion before blaming the skill.
- **An assertion that passes with the skill and fails without it** is where the skill is *proven* to add value — in this demo, expect that to be exactly the four mechanically-checked findings, since a baseline agent without the pre-scan script has to notice a bare CSS selector and a hardcoded wait purely from reading the code, which is far less reliable than a script that greps for them every time.
- **High `stddev` on a pass rate** means the same eval passes sometimes and fails other times across repeated runs — investigate whether the eval itself is flaky or the skill's instructions are ambiguous enough to produce different behavior run to run.

## Step 9 — Human review

Read the actual outputs, not just the grades — `agentskills--feedback-example.json` shows the shape: specific, actionable text per eval case, or an empty string if the output looked fine. "The suggestion was phrased as a command instead of matching the house output format" is useful feedback for the next iteration; "looks bad" is not.

## Step 10 — Iterate

Take the three signals — failed assertions, human feedback, and (if something looked confusing) the execution transcript — along with the current `SKILL.md`, and use them to propose specific improvements. Apply the changes, then repeat Steps 4–9 in a new `iteration-2/` directory. Stop when feedback is consistently empty and pass rates have stopped improving between iterations — not on a fixed schedule.

---

## What to Actually Do With This

1. Run Step 4's real commands yourself — that's the one step this document couldn't do for you.
2. Fill in the two `EXAMPLE`-marked rows in `grading.json` and the real numbers in `timing.json`/`benchmark.json` from what you actually captured.
3. Compare your real `benchmark.json` delta against the illustrative one provided — if your real pass-rate delta is much smaller than the example, that's a genuine, useful finding: it means the skill's judgment-based review content (the rubric) isn't adding as much as the mechanical script is, and Step 10's iteration should focus there first.

*Companion: `eval-demo--cypress-code-review.md` (the earlier, CI-oriented eval build for this same skill) — that document and this one are two different, complementary methodologies applied to the same real skill; comparing them is itself a useful exercise for the team.*
