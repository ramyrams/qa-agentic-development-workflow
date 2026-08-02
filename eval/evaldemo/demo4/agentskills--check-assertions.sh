#!/usr/bin/env bash
# check-assertions.sh — grades the mechanically-verifiable assertions for one eval case
# by running the skill's own deterministic script against the same input file
# the agent was given, and checking that the same findings are present.
#
# This does NOT replace LLM grading of the with_skill/without_skill outputs —
# it only checks the subset of assertions that are objectively checkable without
# any model involved, per the "use a verification script for mechanical checks"
# guidance. The remaining assertions (classification present, verdict wording)
# need the actual captured agent output — see grading.json for how those are recorded.
set -uo pipefail

SCRIPT="scripts/pre-scan.sh"
EVAL_ID="$1"
INPUT_FILE="$2"
PASS=0
FAIL=0

check() {
  local desc="$1" cond="$2"
  if [ "$cond" = "true" ]; then
    echo "PASS: $desc"; PASS=$((PASS+1))
  else
    echo "FAIL: $desc"; FAIL=$((FAIL+1))
  fi
}

FINDINGS=$(bash "$SCRIPT" "$INPUT_FILE")
echo "=== Mechanically-checkable assertions for eval id=$EVAL_ID, file=$INPUT_FILE ==="

if [ "$EVAL_ID" = "1" ]; then
  echo "$FINDINGS" | grep -q "promo-input" && check "selector-policy violation found for .promo-input" "true" || check "selector-policy violation found for .promo-input" "false"
  echo "$FINDINGS" | grep -q "apply-btn" && check "selector-policy violation found for #apply-btn" "true" || check "selector-policy violation found for #apply-btn" "false"
  echo "$FINDINGS" | grep -q "hard-wait" && check "hard wait cy.wait(3000) flagged" "true" || check "hard wait cy.wait(3000) flagged" "false"
  echo "$FINDINGS" | grep -q "focused-test-left-in" && check "describe.only flagged" "true" || check "describe.only flagged" "false"

elif [ "$EVAL_ID" = "2" ]; then
  BLOCKING_COUNT=$(echo "$FINDINGS" | grep -c '"severity":"blocking"' || true)
  [ "$BLOCKING_COUNT" -eq 0 ] && check "zero blocking findings" "true" || check "zero blocking findings" "false"
  echo "$FINDINGS" | grep -q "selector-policy" && check "no false-positive selector-policy finding" "false" || check "no false-positive selector-policy finding" "true"

else
  echo "Unknown eval id: $EVAL_ID"
  exit 2
fi

echo ""
echo "Underlying script findings used for grading:"
echo "${FINDINGS:-<none>}"
echo ""
echo "Mechanical check summary: $PASS passed, $FAIL failed"
