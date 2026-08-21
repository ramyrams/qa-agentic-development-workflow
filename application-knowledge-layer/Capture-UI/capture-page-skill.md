# Skills Needed

Four skills cover the pipeline end to end. Build in this order — each depends on the schema from the design doc being stable first.

| Skill | Purpose | Built in |
|---|---|---|
| **capture-page** | Drive the integrated browser to a page, extract selectors, capture visual states, write the page record | Phase 1 |
| **query-knowledge-base** | Answer arbitrary questions by reading/combining page, journey, and component records | Phase 7 |
| **generate-test-steps** | Turn a journey + its page records into an assertion-level test-step set | Phase 6 |
| **audit-capture-quality** *(optional, meta)* | Check a page record for missing purpose/validation/test-data fields before it's PR'd — mirrors the audit-skill-quality pattern from [[appdev-copilot-skills-expertise]] | After Phase 1 pilot |

Below is the first one, `capture-page`, since it's the Phase 1 dependency everything else builds on.

---

# Skill: capture-page

**File:** `.github/skills/capture-page.md`

**Trigger:** Invoked per page during the walkthrough — either standalone or after the automated crawl has produced a skeleton record you're now enriching.

## Skill definition

```markdown
---
name: capture-page
description: >
  Navigate to a given page of the application using the integrated browser,
  extract element selectors and navigation behavior, capture visual states,
  and write a complete page record following the knowledge-base schema.
inputs:
  - page_id: string        # e.g. checkout-shipping
  - route: string           # e.g. /checkout/shipping
  - states_to_capture: list # e.g. [empty, validation-error, populated]
  - existing_skeleton: path # optional, if crawl already produced one
outputs:
  - pages/<page_id>.yaml
  - pages/<page_id>/visuals/*.png
  - visual-map entries for each screenshot
---

## Procedure

1. If `existing_skeleton` is provided, load it as the starting record instead
   of starting blank.
2. Navigate the integrated browser to `route`.
3. Check `components/*.yaml` for any shared component (header, nav, footer,
   modal) present on this page. If found, add its id to `shared_components`
   and do NOT re-extract its elements individually.
4. Inspect the DOM/accessibility tree. For every interactive element not
   already covered by a shared component, propose a selector using this
   priority order: data-testid > ARIA role+accessible-name > stable CSS >
   xpath. Record the `strategy` used.
5. For each entry in `states_to_capture`, put the page into that state
   (e.g. submit invalid data for validation-error), take a screenshot, and
   record element bounding boxes for elements visible in that state.
6. STOP and ask the human operator to supply (do not guess):
   - `purpose` — one sentence, why this page exists
   - `validation_rules` — any business rules enforced on this page
   - `test_data_dependencies` — preconditions needed to reach this page in a
     valid state (auth, cart contents, feature flags, etc.)
   - confirmation of `enters_from` / `exits_to` if not obvious from the
     browsing session
7. Write `pages/<page_id>.yaml` conforming to the page-record schema.
8. Write one visual-map entry per screenshot, linking bounding boxes to
   element names from step 4.
9. Append any navigation actions taken during this session to
   `navigation/edges.yaml` (from_page, to_page, trigger, action).
10. Run the schema validator. Do not report the page as captured if
    validation fails — report the specific missing/invalid field instead.
```

## Prompt to run in VS Code (Copilot Chat, agent mode, integrated browser enabled)

```
You are running the capture-page skill on the application at
{base_url}{route}, page_id = "{page_id}".

1. Open the integrated browser and navigate to this page. If it requires
   authentication or specific app state, tell me what's needed before you
   proceed — don't guess and don't fabricate a logged-in state.

2. Check components/ in this repo for any already-captured shared
   component (header, nav, footer, modal) present on this page. Reference
   it by id instead of re-extracting it.

3. Inspect the page's DOM and accessibility tree. List every interactive
   element (buttons, inputs, links, form controls) with a proposed
   selector, using this priority: data-testid > role+accessible-name >
   stable CSS > xpath. Tell me which strategy you used for each.

4. Capture these states as screenshots, and for each one list the
   element name + bounding box for elements visible in that state:
   {states_to_capture, e.g. "empty, validation-error, populated"}

5. Before writing anything, ask me for: purpose (one sentence), any
   validation rules you observed but can't confirm are complete, and
   test data dependencies needed to reach this page validly. Wait for my
   answers — don't infer business intent from the DOM.

6. Write pages/{page_id}.yaml matching the schema in
   [link to schema/design doc], plus the visual-map entries and any new
   rows in navigation/edges.yaml for navigation you triggered getting here.

7. Run the validator and tell me the result. If anything fails, show me
   exactly what's missing rather than silently working around it.

Do not capture pages other than {page_id} in this session, and do not
modify any existing page record except to add navigation edges pointing
into or out of {page_id}.
```

## Why the prompt is written this way

- **Step 6 forces a stop, not a guess** — purpose/validation/test-data are the fields that make test-step generation accurate later; letting the agent infer them from the DOM is exactly the failure mode the gap review flagged.
- **Scoped to one page_id** — keeps each PR small and reviewable, consistent with the repo/PR workflow already chosen for the AKL.
- **Component check comes before element extraction** — prevents the header/nav from being re-captured on every page, which is what causes fragmented answers to "where is X used" questions later.
