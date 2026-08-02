#!/usr/bin/env bash
# pre-scan.sh — deterministic mechanical checks for Cypress/JS spec files
# Usage: pre-scan.sh <file>
# Output: JSON Lines, one finding per line
set -uo pipefail

TARGET="${1:?Usage: pre-scan.sh <file>}"

emit() {
  local rule="$1" severity="$2" file="$3" line="$4" snippet="$5"
  snippet=$(printf '%s' "$snippet" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n')
  printf '{"rule":"%s","severity":"%s","file":"%s","line":%s,"snippet":"%s"}\n' \
    "$rule" "$severity" "$file" "$line" "$snippet"
}

FINDINGS_FILE=$(mktemp)
trap 'rm -f "$FINDINGS_FILE"' EXIT

scan_file() {
  local f="$1"

  grep -nE "cy\.get\((\"|')(\.[A-Za-z0-9_-]+|#[A-Za-z0-9_-]+)(\"|')" "$f" 2>/dev/null | \
    while IFS=: read -r line content; do
      emit "selector-policy" "blocking" "$f" "$line" "$content"
    done >> "$FINDINGS_FILE"

  grep -nE "cy\.wait\([0-9]+\)" "$f" 2>/dev/null | while IFS=: read -r line content; do
    emit "hard-wait" "blocking" "$f" "$line" "$content"
  done >> "$FINDINGS_FILE"

  grep -nE "(describe|it|context)\.only\(" "$f" 2>/dev/null | while IFS=: read -r line content; do
    emit "focused-test-left-in" "blocking" "$f" "$line" "$content"
  done >> "$FINDINGS_FILE"

  grep -nE "cy\.on\((\"|')uncaught:exception(\"|')" "$f" 2>/dev/null | while IFS=: read -r line content; do
    emit "blanket-exception-suppression" "suggestion" "$f" "$line" "$content"
  done >> "$FINDINGS_FILE"

  grep -nE "console\.(log|debug)\(" "$f" 2>/dev/null | while IFS=: read -r line content; do
    emit "debug-statement-left-in" "suggestion" "$f" "$line" "$content"
  done >> "$FINDINGS_FILE"
}

scan_file "$TARGET"
cat "$FINDINGS_FILE"

# Deliberate, documented exit-code contract for grader/CI use:
#   0 = no BLOCKING findings (suggestions don't fail the scan)
#   1 = at least one BLOCKING finding
BLOCKING_COUNT=$(grep -c '"severity":"blocking"' "$FINDINGS_FILE" || true)
[ "$BLOCKING_COUNT" -eq 0 ] && exit 0 || exit 1
