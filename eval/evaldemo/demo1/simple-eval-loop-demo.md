# The Simplest Possible Eval Demo — No CI, Just the Core Loop
### Create → Eval → Run → Review → Update → Re-run → Validate

**Purpose:** strip away every piece of infrastructure — no CI, no YAML task specs, no runner script, no routing/trigger testing — down to the one loop that's actually the point of evaluation: **you built something, you have evidence it works, you changed it, and you now have evidence it still works.** This is the demo to show a team who has never seen an eval before. Everything else in the library is this loop with more machinery around it.

**Continues from the same skill** used in `hello-world-eval-walkthrough.md` (`cypress-todo-finder`) — if your team already ran that demo, this picks up exactly where it left off. If not, this document is self-contained; you don't need the other one first.

**Every command and every line of output below was actually run before being written down** — nothing here is hypothetical, including the one real mistake made and fixed along the way (Step 3).

---

## Step 1 — Create the simple skill

The skill's whole job: find `TODO`/`FIXME` comments left in a Cypress spec.

```bash
mkdir -p .github/skills/cypress-todo-finder/scripts
```
`scripts/find-todos.sh` (the skill's one bundled script):
```bash
#!/usr/bin/env bash
set -uo pipefail
TARGET="${1:?Usage: find-todos.sh <file>}"

grep -noE "(TODO|FIXME)[^\"'\`]*" "$TARGET" 2>/dev/null | while IFS=: read -r line text; do
  text=$(printf '%s' "$text" | sed 's/"/\\"/g' | tr -d '\r')
  printf '{"line":%s,"text":"%s"}\n' "$line" "$text"
done

MATCHES=$(grep -cE "(TODO|FIXME)" "$TARGET" 2>/dev/null || true)
[ "$MATCHES" -eq 0 ] && exit 0 || exit 1
```
That's the entire skill for this step. No CI, no `SKILL.md` frontmatter debate needed yet — just the capability itself, because the eval loop this demo teaches applies to the script whether or not it's wrapped as a Copilot skill.

## Step 2 — Write the eval

Two fixtures with known-correct answers — this is your ground truth:

`fixtures/has-todos.cy.js` — 2 real `TODO`/`FIXME` lines. `fixtures/no-todos.cy.js` — deliberately clean, 0 lines.

`eval.sh` — one script, two cases, plain pass/fail output:
```bash
#!/usr/bin/env bash
set -uo pipefail
SCRIPT="scripts/find-todos.sh"
PASS=true

echo "--- Case 1: fixture WITH todos ---"
RESULT=$(bash "$SCRIPT" fixtures/has-todos.cy.js)
COUNT=$(echo "$RESULT" | wc -l)
if [ "$COUNT" -eq 2 ]; then echo "PASS: found exactly 2 items"; else echo "FAIL: expected 2, got $COUNT"; PASS=false; fi
bash "$SCRIPT" fixtures/has-todos.cy.js > /dev/null 2>&1
if [ $? -eq 1 ]; then echo "PASS: exit code 1"; else echo "FAIL: expected exit code 1"; PASS=false; fi

echo ""
echo "--- Case 2: clean fixture ---"
RESULT=$(bash "$SCRIPT" fixtures/no-todos.cy.js)
if [ -z "$RESULT" ]; then echo "PASS: zero items found"; else echo "FAIL: expected zero items"; PASS=false; fi
bash "$SCRIPT" fixtures/no-todos.cy.js > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "PASS: exit code 0"; else echo "FAIL: expected exit code 0"; PASS=false; fi

echo ""
if [ "$PASS" = true ]; then echo "===== EVAL RESULT: ALL CASES PASSED ====="; exit 0
else echo "===== EVAL RESULT: FAILURES PRESENT ====="; exit 1; fi
```

**One honest note worth showing your team live:** the very first version of this eval script used `set -euo pipefail`. The skill's script correctly exits with code 1 when it finds something — but under `set -e`, that non-zero exit immediately killed the *eval script itself* before it could even record the result as a pass. The fix was one word (drop `-e`, keep only `-u -o pipefail`) — but it's a real, small reminder that **the eval script is also code, and it's also worth getting right before you trust what it tells you.**

## Step 3 — Run the eval

```bash
$ bash eval.sh
```
```
--- Case 1: fixture WITH todos ---
PASS: found exactly 2 items
PASS: exit code 1

--- Case 2: clean fixture ---
PASS: zero items found
PASS: exit code 0

===== EVAL RESULT: ALL CASES PASSED =====
```

## Step 4 — Review the eval

This is a deliberate step, not a formality — before moving on, actually look at what passed and ask: **does a pass here really mean the skill works?**
- Case 1 confirms real detection *and* the correct count — not just "it ran without crashing."
- Case 2 confirms the skill doesn't invent findings on clean input — the negative case, and the one people most often skip writing.
- Both fixtures have a **known, human-verified correct answer** — the eval isn't guessing what "right" looks like, and neither should you have to when reading its result.

If either case's *expected* value were wrong (say, the clean fixture actually had a `TODO` hiding in it), the eval would be lying to you convincingly. Reviewing the eval itself, not just its output, is part of this step.

## Step 5 — Update the skill

A real, small enhancement: also detect `HACK:` comments, not just `TODO`/`FIXME`.

```diff
- grep -noE "(TODO|FIXME)[^\"'\`]*" "$TARGET" ...
+ grep -noE "(TODO|FIXME|HACK)[^\"'\`]*" "$TARGET" ...
- MATCHES=$(grep -cE "(TODO|FIXME)" "$TARGET" ...)
+ MATCHES=$(grep -cE "(TODO|FIXME|HACK)" "$TARGET" ...)
```

## Step 6 — Update the eval

Add one new case for the new capability. **Deliberately leave Case 1 and Case 2 completely untouched** — they're no longer just "the eval," they're now your regression proof for everything that existed *before* this change:

```bash
# new fixture: fixtures/has-hack.cy.js — one HACK: comment, nothing else

echo ""
echo "--- Case 3 (NEW): fixture with a HACK comment ---"
RESULT=$(bash "$SCRIPT" fixtures/has-hack.cy.js)
COUNT=$(echo "$RESULT" | wc -l)
if [ "$COUNT" -eq 1 ]; then echo "PASS: found exactly 1 item"; else echo "FAIL: expected 1, got $COUNT"; PASS=false; fi
bash "$SCRIPT" fixtures/has-hack.cy.js > /dev/null 2>&1
if [ $? -eq 1 ]; then echo "PASS: exit code 1"; else echo "FAIL: expected exit code 1"; PASS=false; fi
```
(Appended into `eval.sh`, right before the final pass/fail summary.)

## Step 7 — Run the eval again

```bash
$ bash eval.sh
```
```
--- Case 1: fixture WITH todos ---
PASS: found exactly 2 items
PASS: exit code 1

--- Case 2: clean fixture ---
PASS: zero items found
PASS: exit code 0

--- Case 3 (NEW): fixture with a HACK comment ---
PASS: found exactly 1 item
PASS: exit code 1

===== EVAL RESULT: ALL CASES PASSED =====
```

## Step 8 — Validate the result

Read this output as two separate claims, not one:

- **Cases 1 and 2 passing again, unchanged, is the proof the update didn't break anything that used to work.** This is the entire value proposition of re-running an eval after a change — without it, "I added HACK support" and "I definitely didn't also break TODO detection" would just be two separate hopes instead of one verified fact.
- **Case 3 passing is the proof the new capability actually works**, not just that it was written and looks plausible.

**If Case 1 or 2 had failed here, that would have been the eval catching a real regression** — the HACK-related change touching shared logic in a way that broke existing behavior. That didn't happen this time, but it's exactly the scenario this whole loop exists to catch, and it's worth saying out loud to the team: *this is what the eval is actually for. Not "does the new thing work," but "did I just break something I wasn't even looking at."*

---

## The Whole Loop, In One Sentence

**Create → write eval → run → review → change → update eval → run again → the old cases passing again is your regression proof, and the new case passing is your new-capability proof.** No CI, no policy, no infrastructure — just this loop, done by hand, is a complete and legitimate eval practice. Everything else in this library (routing suites, LLM judges, pass^k, CI gating) exists to make this same loop cheaper to repeat at scale — it is not a different activity.
