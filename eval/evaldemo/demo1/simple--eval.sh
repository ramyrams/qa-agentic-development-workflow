#!/usr/bin/env bash
# eval.sh — the eval for cypress-todo-finder
# Two labeled fixtures, known-correct answers, no CI, run by hand.
set -uo pipefail
SCRIPT="scripts/find-todos.sh"
PASS=true

echo "--- Case 1: fixture WITH todos (fixtures/has-todos.cy.js) ---"
RESULT=$(bash "$SCRIPT" fixtures/has-todos.cy.js)
COUNT=$(echo "$RESULT" | wc -l)
if [ "$COUNT" -eq 2 ]; then echo "PASS: found exactly 2 items"; else echo "FAIL: expected 2 items, got $COUNT"; PASS=false; fi
bash "$SCRIPT" fixtures/has-todos.cy.js > /dev/null 2>&1
if [ $? -eq 1 ]; then echo "PASS: exit code 1"; else echo "FAIL: expected exit code 1"; PASS=false; fi

echo ""
echo "--- Case 2: clean fixture (fixtures/no-todos.cy.js) ---"
RESULT=$(bash "$SCRIPT" fixtures/no-todos.cy.js)
if [ -z "$RESULT" ]; then echo "PASS: zero items found"; else echo "FAIL: expected zero items"; PASS=false; fi
bash "$SCRIPT" fixtures/no-todos.cy.js > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "PASS: exit code 0"; else echo "FAIL: expected exit code 0"; PASS=false; fi

echo ""
echo "--- Case 3 (NEW): fixture with a HACK comment (fixtures/has-hack.cy.js) ---"
RESULT=$(bash "$SCRIPT" fixtures/has-hack.cy.js)
COUNT=$(echo "$RESULT" | wc -l)
if [ "$COUNT" -eq 1 ]; then echo "PASS: found exactly 1 item"; else echo "FAIL: expected 1 item, got $COUNT"; PASS=false; fi
bash "$SCRIPT" fixtures/has-hack.cy.js > /dev/null 2>&1
if [ $? -eq 1 ]; then echo "PASS: exit code 1"; else echo "FAIL: expected exit code 1"; PASS=false; fi

echo ""
if [ "$PASS" = true ]; then echo "===== EVAL RESULT: ALL CASES PASSED ====="; exit 0
else echo "===== EVAL RESULT: FAILURES PRESENT ====="; exit 1; fi
