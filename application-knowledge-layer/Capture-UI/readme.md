
app-knowledge-capture-design.md — the core design doc: data model (7 artifact types), capture workflow, retrieval strategy, journeys/test-steps split, versioning, phased sequencing, and open decisions.
capture-page-skill.md — the capture-page skill definition + ready-to-run VS Code Copilot prompt for capturing a single page.
capture-journey-session-prompt.md — the multi-page session prompt that chains captures across a real user path (home → login → main-page → catalog-page → create-catalog) in one continuous, human-confirmed session.
audit-capture-quality-skill.md — the sufficiency-audit skill and prompt, for checking whether a captured page record is actually complete, not just schema-valid.
web-app-knowledge-capture.docx — the consolidated Word document with everything above plus the discussion content (gap review, validation approach, status summary) in one 14-page file.


This fits well alongside your application knowledge layer work — same repo/PR pattern, same consumers.

Key design points:

1. **Separate the four artifact types** — page records, nav edges, journeys, and a generated sitemap — so each updates independently and edges don't have to be hand-maintained.
2. **Selector priority is explicit** in the schema (`data-testid` → role+name → CSS → xpath) so Copilot never guesses which selector is authoritative.
3. **Capture is a repeatable skill, not a one-off prompt** — package navigate → extract → annotate → write → validate as a single `.github/skills/capture-page.md` so every page follows the same procedure.
4. **The real trade-off**: automated crawl gets you fast structural coverage but zero business-intent metadata; a guided Copilot walkthrough gets you the semantics but doesn't scale. Recommended hybrid — crawl first for skeletons, then walk through with Copilot to fill in purpose/validation/journey context.

Straight answer: no — the original design covers structure and navigation well, but it's missing the pieces that actually matter for your three new requirements (visual capture, answering arbitrary questions, generating accurate test steps). Here's the gap review, grouped by requirement.

**A. Visual capture — mostly absent**
1. No screenshot/visual artifact at all. The schema captures DOM/selectors, not what the page *looks like*. "Complete visual capture" needs an actual image artifact per page.
2. No state variants. A page has multiple visual states — empty, loading, error, populated, hover/focus, logged-in vs logged-out. The design assumes one snapshot; test steps often hinge on the state, not just the route.
3. No viewport/breakpoint variants (desktop/tablet/mobile) if the app is responsive.
4. No link between screenshot regions and selectors — so "what does the Continue button look like" can't be answered without that mapping (bounding box → element).

**B. Answering arbitrary questions — no retrieval layer**
5. The design has files, not a query mechanism. Flat YAML scales fine for structured lookups ("show me checkout-shipping") but "ask anything" needs either an index (embeddings/RAG) or a Copilot skill that knows how to search/aggregate across pages, journeys, and edges on demand. Right now nothing defines *how* a question gets answered.
6. No shared-component handling. Header, nav, modals repeat on every page. Without dedup, "where's the search bar used" returns fragmented, redundant answers instead of one canonical record with a list of pages that include it.

**C. Accurate test-step generation — the biggest gap**
7. No expected-outcome/assertion field. The page record has selectors and purpose but not the actual unit a test step needs: *action → expected result*. This is the single most important missing piece for "very accurate detailed test steps."
8. No test-data/fixture dependencies. Reaching `checkout-shipping` in a real state (cart populated, user logged in) requires setup data that isn't captured anywhere.
9. No explicit test-step schema separate from the journey. A journey today is just an ordered list of pages/actions — not granular enough to emit Given/When/Then-level steps.

**D. Cross-cutting**
10. No versioning or staleness detection — selectors and screenshots drift as the UI changes, nothing flags when a page record is out of date.
11. No coverage tracking against the actual page inventory, so you can't tell what's captured vs. missing at a glance.

None of this invalidates the original structure — it's the right skeleton (schema-first, phased, PR-reviewed). It just needs a visual layer, a retrieval strategy, and an assertion-level test-step schema added on top.

Four skills total, built in dependency order: `capture-page` (Phase 1), `query-knowledge-base` (Phase 7), `generate-test-steps` (Phase 6), and an optional `audit-capture-quality` meta-skill to catch incomplete records befo
re they're PR'd.

I built out `capture-page` fully since it's the one everything else depends on — both the `.github/skills/capture-page.md` definition and a ready-to-run prompt for VS Code Copilot agent mode with the integrated browser.

Two things worth calling out:

- The prompt has a hard stop at step 6 that forces Copilot to ask you for purpose/validation/test-data rather than guess — that's the field set the gap review flagged as most load-bearing for accurate test steps, so it can't be left to inference.
- It's scoped to one `page_id` per run, which keeps each PR small and matches your existing repo/PR review pattern.


Here's the pilot-ready prompt. Fill in the three placeholders and paste into VS Code Copilot Chat with agent mode + integrated browser enabled — after you've logged in manually in that browser session.

```
You are running the capture-page skill on the application at
{route/URL of the page — e.g. https://app.internal.com/admin/dashboard},
page_id = "{short id — e.g. admin-dashboard}".

I am already logged in on the integrated browser. Do not attempt to log
in or navigate away from this session — work within the current
authenticated state.

1. Navigate to the target page within this browser session.

2. Check components/ in this repo for any already-captured shared
   component (header, nav, footer, modal) present on this page. Reference
   it by id instead of re-extracting it. If components/ doesn't exist yet,
   tell me and proceed without it.

3. Inspect the page's DOM and accessibility tree. List every interactive
   element (buttons, inputs, links, form controls) with a proposed
   selector, using this priority: data-testid > role+accessible-name >
   stable CSS > xpath. Tell me which strategy you used for each.

4. Capture these two states only for this pilot run — screenshot each,
   and for each one list the element name + bounding box for elements
   visible in that state:
   - empty (or default/initial load state)
   - {second state — e.g. "loading" or a validation/error state, your call}

5. Before writing anything, ask me for: purpose (one sentence), any
   validation rules you observed but can't confirm are complete, and
   test data dependencies needed to reach this page validly. Wait for my
   answers — don't infer business intent from the DOM.

6. Write pages/{page_id}.yaml matching the page-record schema below,
   plus visual-map entries and any navigation/edges.yaml rows for
   navigation you triggered getting here.

7. Run the validator if one exists; otherwise just show me the finished
   YAML so I can check it against the schema myself for this pilot.

Do not capture pages other than {page_id} in this session.

--- schema reference ---
[paste the page-record example from the design doc here]
```

A few things to watch for when you run it, since this is the first real test:

- **Whether it actually stops at step 5** instead of fabricating a purpose — that's the behavior most worth checking, since it's what the rest of the pipeline depends on.
- **Whether the selector priority holds** — if the app has weak `data-testid` coverage, you'll see it fall back to CSS/xpath a lot, which tells you something about selector strategy investment before you scale to more pages.
- **How messy step 4 gets with two states** — if this is already awkward, the "states_to_capture" design assumption needs revisiting before you commit to a page-by-page rollout.

Good question — this is exactly the operational detail the design was missing: how single-page captures chain into a walked sequence. Here's how to run it and validate it.

## How to operate it

**1. Keep one continuous browser session for the whole walk, not one session per page.**
Run `capture-page` for `home`, but instead of ending the session, stay in the same integrated browser and let it flow into the next page. This matters because the *trigger* for each navigation (which link/button was clicked) is only known while you're still on the previous page — if you reset sessions per page, you lose that information and have to reconstruct it later.

**2. Every route change, log it as a nav edge — every modal/tab-switch without a route change, capture it as a state instead.**
This is the fork you'll hit at "create catalog": if clicking it opens a form on a new URL, it's a new page record and a new edge (`catalog-page → create-catalog-page`). If it opens a modal on the same URL, it's a `state` on the catalog page record (or its own component, if the modal is reused elsewhere), not a separate page.

**3. Walk order for your example, concretely:**

| Step | Action | Result |
|---|---|---|
| 1 | Capture `home` (unauthenticated) | `pages/home.yaml` |
| 2 | Click login link → capture `login` | `pages/login.yaml` + edge `home→login (trigger: click login-link)` |
| 3 | Submit credentials → capture `main-page` | `pages/main-page.yaml` + edge `login→main-page (trigger: submit login-form)` |
| 4 | Click catalog nav → capture `catalog-page` | `pages/catalog-page.yaml` + edge `main-page→catalog-page (trigger: click catalog-nav)` |
| 5 | Click "create" → capture `create-catalog` (page or state, per the fork above) | new record or new state + edge/state entry |

Each step is still a `capture-page` run — same skill, same prompt template — but you tell the agent explicitly what triggered entry into that page (step 5's prompt input: "I just clicked X on the previous page"), so it can write the edge instead of guessing.

**4. After the walk, aggregate into a journey — don't hand-write it.**
Since edges got logged in order with a shared session, a short script (or a `capture-journey` wrapper skill) can turn "every edge logged in this session, in order" into a draft `journeys/<id>.yaml`. You then just name it and confirm — you're not retyping the path.

## How to validate it

Four layers, cheapest first:

1. **Schema validation** — each page record has required fields, valid selector strategy. Catches typos/omissions immediately.
2. **Referential integrity** — every edge's `from_page`/`to_page` must resolve to an existing page record id. Catches a page you captured but forgot to link, or a typo'd id.
3. **Journey replay (the real test)** — write a small Playwright script that reads the journey file and *executes* it using only the stored selectors: navigate home, click the recorded login-link selector, submit the recorded form, assert it lands on the recorded next route. If replay succeeds, your captured selectors and edges are provably accurate, not just recorded-and-hoped. This is the check that actually validates the knowledge base against the live app rather than against itself.
4. **PR review** — human reviews the diff of new page records + edges + the journey file before merge, same as any code change.

Run 1 and 2 in CI on every PR (cheap, fast). Run 3 (replay) either in CI too, or as a periodic job — it's the one that catches drift when the app's UI changes and nobody re-ran the capture.

Here's the honest status check — what's solid, what's designed but unproven, and what's still just a name on a list.

## What's actually built and ready to use
- **Schema** — 7 artifact types (page, visual, nav edge, journey, test-step set, component, sitemap) with a worked example for each.
- **`capture-page` skill** — full definition + prompt, includes the "stop and ask, don't guess" behavior for purpose/validation/test-data.
- **Multi-page session prompt** — chains captures across a walk (home→login→main→catalog→create), stays in draft mode until you confirm.

## What's designed but not yet built as skill files
- **`query-knowledge-base`** — we described the approach (a skill that knows how to combine files; embeddings only if it doesn't scale) but never wrote the actual skill file or prompt.
- **`generate-test-steps`** — same status: schema for the output exists (Given/When/Then + preconditions), but no skill file yet.
- **`audit-capture-quality`** — named as optional, never scoped at all.

## What's described but has zero tooling behind it
- Schema validator, referential-integrity check, and replay validator — all specified as *what they should do*, none written as actual scripts.
- Coverage index and staleness marker — schema fields exist (`last_verified`), but nothing generates or checks them.
- CI gate — still just a phase on the table, no config.

## The bigger gap: nothing has touched your real app yet
Everything above is unvalidated against your actual application. You haven't run the pilot capture, so we don't know yet whether:
- The selector priority actually holds up on your app's DOM
- The agent respects the "stop and ask" instruction in practice instead of drifting into guessing
- The multi-page session prompt survives five pages without losing context or getting confused at the create-catalog fork (page vs. modal)

## Open decisions still unanswered
Page ID convention, which states are mandatory per page, screenshot storage (in-repo vs. external), and who owns journey/test-step authoring — all flagged, none decided.

## My actual assessment
The design covers everything you originally asked for on paper — visual capture, arbitrary Q&A, and accurate test steps all have a schema and a plan. But two of the three newer requirements (Q&A and test-step generation) only exist as *plans for skills*, not skills — and the one skill that is fully built has never been run. Building the remaining two skills now would mean building them on assumptions the first skill hasn't tested yet.

**Recommendation:** don't build more skills next. Run the pilot walkthrough (the session prompt from last message) on the real auth-gated page you picked, bring back what it actually produces, and let that output tell us whether the schema needs adjusting before `query-knowledge-base` and `generate-test-steps` get built against it.

This is a different question than schema validation — schema checks *presence* of fields, not whether what's there is actually *sufficient*. A page record can be 100% schema-valid and still be useless for test generation if `purpose: "the page"` and `validation_rules: []` when the page clearly has required fields. This is exactly what the `audit-capture-quality` skill (named earlier, never scoped) is for — let me scope it now since it directly answers this.

## What "enough" means, concretely

| Check | Pass criteria | Catches |
|---|---|---|
| **Element coverage** | Every interactive element found in the live DOM has a corresponding entry in the page record | Elements missed during capture (common when a page has dynamic/lazy-loaded content) |
| **Orphan actions** | Every button/link that triggers navigation has a matching nav edge | Buttons captured as elements but their destination was never logged |
| **Non-trivial purpose** | `purpose` is a specific sentence about business intent, not a restatement of the title/route | Rubber-stamped fields that pass schema but say nothing |
| **Validation rules present when expected** | If the page contains a form, `validation_rules` is non-empty | Skipped annotation step on form-heavy pages |
| **States match page behavior** | If a form exists, at minimum an error state was captured, not just empty/success | Incomplete visual capture that can't support error-path test steps |
| **Test data dependencies present when expected** | If `auth_required: true` or the page needs prior app state, `test_data_dependencies` is non-empty | Missing preconditions that make replay/test generation fail silently |
| **No dangling edges** | Every edge's `from_page`/`to_page` resolves to a real page record | Broken links in the nav graph |

## Two ways to check it, cheapest first

**1. Automated coverage score** — before annotation, count interactive elements in the live DOM; after capture, count elements in the record. Report `captured / found` as a percentage. Anything under 100% (or your chosen threshold) is flagged, not silently accepted.

**2. The real proof — journey replay.** A page record can look complete and still be wrong. The only test that actually proves "enough was captured" is running the replay validator from earlier: execute a journey using *only* the recorded selectors and edges, and check it lands where the record says it should. If replay succeeds, the record is provably sufficient for navigation and test-step purposes — not just plausible-looking.

**3. Q&A dry-run** — once `query-knowledge-base` exists, sufficiency for the "ask anything" requirement can be checked by running a small fixed set of canonical questions against each new page ("what happens on invalid submit here?", "what's required to reach this page?") and treating "I don't know" as a capture gap, not an acceptable answer.

## The skill that runs thisThe key distinction to keep in mind: schema validation stays in CI (fast, mechanical, every commit), sufficiency auditing is a deliberate pre-PR step (slower, judgment-based, run once per page after capture) — and journey replay remains the strongest proof of all, since it tests the record against the live app rather than against itself.

This also means the pilot walkthrough you're about to run now has a real acceptance test attached to it — instead of just eyeballing whether the output "looks right," you can run this audit against it and get a concrete pass/fail list.


I'll compile everything — the design doc, all three skill files, the session prompt, and the discussion content (gap review, validation approach) — into one Word document.Now let me create the small YAML example snippets it references, pulling them from the earlier design content:Now let me verify it rendered correctly:14 pages. Let me spot-check a few for formatting issues.This looks clean — tables render correctly, code blocks are readable. Let me check the skills section and a table-heavy page.Good — the skill files are rendered verbatim as-is, which is appropriate since these are meant to be actual file contents. Let me check the final summary page.It all rendered correctly. The document is ready.14 pages, structured as:

1. Overview + original gap review
2. Data model (all 7 schemas with examples)
3. Capture workflow
4. Journeys and test steps
5. Versioning and coverage
6. Sequencing + trade-offs + open decisions
7. All three skill files (`capture-page`, the multi-page session prompt, `audit-capture-quality`) in full, copy-pasteable
8. Validation approach, including the sufficiency rubric from your last question
9. Status summary — what's built vs. designed vs. untested against your real app

Everything from the individual files plus the discussion content (gap review, validation reasoning, status assessment) is consolidated in one place. The skill files are included verbatim so you can still copy them straight into `.github/skills/` if useful, separate from reading the doc as a whole.





