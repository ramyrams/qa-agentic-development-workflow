# Setup: The Simple Eval Loop Demo — Step by Step
### No CI. Just the commands, in order, to run this yourself or live in front of the team.

**Files used:** `hello--find-todos.sh` (the script, starting version) · `hello-fixture--has-todos.cy.js` · `hello-fixture--no-todos.cy.js` (the two starting fixtures) · `simple-fixture--has-hack.cy.js` (the new fixture added partway through) · `simple--find-todos-v2.sh` (the script, ending version) · `simple--eval.sh` (the eval, ending version).

**No prerequisites beyond bash.** This doesn't need Copilot CLI, jq, or anything from the tooling guide — that's deliberate, per the "no CI, no infrastructure" version of this demo.

---

### Step 1 — Create the working directory

```bash
mkdir -p eval-demo/scripts eval-demo/fixtures
cd eval-demo
```

### Step 2 — Place the skill script (starting version)

```bash
cp ../hello--find-todos.sh scripts/find-todos.sh
chmod +x scripts/find-todos.sh
```

### Step 3 — Place the two starting fixtures

```bash
cp ../hello-fixture--has-todos.cy.js fixtures/has-todos.cy.js
cp ../hello-fixture--no-todos.cy.js fixtures/no-todos.cy.js
```

### Step 4 — Write the eval (starting version — 2 cases)

```bash
cat > eval.sh << 'EOF'
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
EOF
chmod +x eval.sh
```
*(Note `set -uo pipefail`, not `set -euo pipefail` — this is the fix for the bug described in the full walkthrough; typing it correctly here skips having to hit and fix it live, unless you want to demonstrate that too by adding `-e` first on purpose.)*

### Step 5 — Run it

```bash
bash eval.sh
```
**Expected:**
```
--- Case 1: fixture WITH todos ---
PASS: found exactly 2 items
PASS: exit code 1

--- Case 2: clean fixture ---
PASS: zero items found
PASS: exit code 0

===== EVAL RESULT: ALL CASES PASSED =====
```

### Step 6 — Review

Before moving on, look at what each case actually proved (say this part out loud if presenting live):
- Case 1: real detection, with the *correct count* — not just "didn't crash."
- Case 2: no false positives on clean input — the negative case.
- Both fixtures' expected answers were verified by a human before being trusted — that's what makes this eval's "PASS" mean something.

### Step 7 — Update the skill

```bash
cp ../simple--find-todos-v2.sh scripts/find-todos.sh
chmod +x scripts/find-todos.sh
```
This swaps in the version that also detects `HACK:` comments, not just `TODO`/`FIXME`.

### Step 8 — Add the new fixture

```bash
cp ../simple-fixture--has-hack.cy.js fixtures/has-hack.cy.js
```

### Step 9 — Update the eval

```bash
cp ../simple--eval.sh eval.sh
chmod +x eval.sh
```
This is the version with **Case 3 appended and Cases 1–2 left byte-for-byte unchanged** — that's the detail that matters, not a formality (see Step 10).

### Step 10 — Run again and validate

```bash
bash eval.sh
```
**Expected:**
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

**Read this as two claims, not one:** Cases 1–2 passing again is proof the update didn't break what already worked. Case 3 passing is proof the new capability actually works. That's the entire demo.

---

## Optional: Make the Regression Visible (if you want to show a catch, not just a pass)

To demonstrate what a *caught* regression actually looks like, before Step 7 try this instead:

```bash
# Deliberately break something during the "update"
sed -i 's/TODO|FIXME|HACK/TODO|HACK/' scripts/find-todos.sh   # accidentally drops FIXME detection
bash eval.sh
```
Case 1 will now report `FAIL: expected 2, got 1` — because the fixture's `FIXME:` line is no longer being caught. **This is the eval doing its job.** Revert (`git checkout scripts/find-todos.sh` or re-run Step 7 as written) and continue with the real walkthrough. Use this only if you want the team to see a red result at least once — it's the more memorable version of "prove it still works."

---

*This is the operational sequence for `simple-eval-loop-demo.md` — that document has the full teaching narrative behind each step; this one is just the commands.*
