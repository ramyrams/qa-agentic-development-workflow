# Skill: audit-capture-quality

**File:** `.github/skills/audit-capture-quality.md`

**Trigger:** Run after `capture-page` produces a draft record, before it's PR'd. Distinct from schema validation — this checks whether the content is *sufficient*, not just structurally valid.

## Skill definition

```markdown
---
name: audit-capture-quality
description: >
  Audit a captured page record for completeness against the live page,
  not just schema conformance. Flags thin/rubber-stamped fields, missing
  states, orphaned navigation actions, and elements present in the DOM
  but absent from the record.
inputs:
  - page_id: string
  - page_record_path: path   # pages/<page_id>.yaml
  - live_route: string       # to re-inspect the DOM for comparison
outputs:
  - audit report: pass/fail per check, with specifics for any failure
---

## Procedure

1. Load the page record at `page_record_path`.
2. Re-navigate to `live_route` in the integrated browser and inspect the
   current DOM/accessibility tree.
3. Element coverage: compare live interactive elements against the
   record's `elements` list. Report any live element with no matching
   entry, by name/selector. Compute coverage %.
4. Orphan actions: for every element with role=button or role=link in
   the record, confirm a nav edge exists with that element as the
   trigger. Report any that don't.
5. Purpose check: if `purpose` is under 6 words, identical to the page
   `title`, or a generic phrase ("this page", "the page"), flag as thin
   — do not accept as sufficient.
6. Validation rules check: if the record contains a `form` role element
   but `validation_rules` is empty, flag as incomplete.
7. States check: if `validation_rules` is non-empty (i.e. the page has
   rules to violate) but `states` doesn't include anything error-like,
   flag as incomplete.
8. Test data check: if `auth_required: true` or the page has an
   `enters_from` dependency, but `test_data_dependencies` is empty,
   flag as incomplete.
9. Dangling edges: confirm every `enters_from`/`exits_to` id resolves to
   an existing page record file. Report any that don't.
10. Output a pass/fail report per check above, with specifics — never
    just "incomplete," always name the missing element/field/state.
```

## Prompt to run in VS Code (after a capture-page session, before PR)

```
Run the audit-capture-quality skill on pages/{page_id}.yaml against the
live page at {route}.

1. Re-inspect the live DOM at this route and compare every interactive
   element you find against the elements already listed in the page
   record. List anything present live but missing from the record.

2. For every button/link element in the record, confirm there's a
   matching row in navigation/edges.yaml with it as the trigger. List
   any that don't have one.

3. Check the "purpose" field — if it's generic, too short, or just
   restates the title, tell me it needs to be rewritten and why.

4. If the record includes a form element, confirm validation_rules is
   non-empty. If it's empty, flag it.

5. If validation_rules is non-empty, confirm "states" includes at least
   one error/invalid state. If not, flag it.

6. If auth_required is true, confirm test_data_dependencies is
   non-empty. If not, flag it.

7. Confirm every enters_from/exits_to id in this record points to a
   page record file that actually exists in pages/.

Give me a pass/fail list, one line per check, with the specific
element/field name for any failure — not just "incomplete."
```

## Why this is a separate skill from schema validation

Schema validation is cheap and mechanical — it runs in CI on every PR and catches malformed YAML or missing required keys in milliseconds. Sufficiency auditing requires re-inspecting the live DOM and judgment calls (is this purpose sentence actually specific?) — it's slower and belongs as a pre-PR step you run deliberately, not a CI gate that blocks on every commit. Keeping them separate means CI stays fast while sufficiency checking stays thorough.
