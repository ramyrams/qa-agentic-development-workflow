#!/usr/bin/env bash
# find-todos.sh — the "hello world" of this skill package.
# Finds leftover TODO/FIXME comments in a Cypress/JS test file.
# Usage: find-todos.sh <file>
# Output: JSON Lines, one per finding. Exit 0 = none found, 1 = at least one found.
set -uo pipefail

TARGET="${1:?Usage: find-todos.sh <file>}"
FOUND=0

grep -noE "(TODO|FIXME|HACK)[^\"'\`]*" "$TARGET" 2>/dev/null | while IFS=: read -r line text; do
  text=$(printf '%s' "$text" | sed 's/"/\\"/g' | tr -d '\r')
  printf '{"line":%s,"text":"%s"}\n' "$line" "$text"
done

MATCHES=$(grep -cE "(TODO|FIXME|HACK)" "$TARGET" 2>/dev/null || true)
[ "$MATCHES" -eq 0 ] && exit 0 || exit 1
