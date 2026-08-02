---
name: cypress-todo-finder
description: "Use when asked to find TODO or FIXME comments, list outstanding work, or check for leftover placeholder comments in a Cypress or JS test file."
---

# Cypress TODO Finder

The simplest possible skill in this estate — one job, one deterministic script, no judgment required.

## Procedure

1. Run `scripts/find-todos.sh <target-file>`.
2. Report each finding as a simple list: line number and the comment text.
3. If none are found, say so plainly — don't invent work that isn't there.

## Output Format

```
Found N outstanding item(s) in <file>:
- Line X: <comment text>
```
or, if none: `No TODO/FIXME comments found in <file>.`

## Bundled Resources

- `scripts/find-todos.sh` — greps for TODO/FIXME, outputs JSON Lines. Exits 0 if none found, 1 if at least one found.
