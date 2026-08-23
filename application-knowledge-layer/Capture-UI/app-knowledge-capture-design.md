# Web Application Knowledge Capture — Design

## Goal

Walk the application page by page and produce a durable, machine-readable knowledge base of pages, selectors, navigation edges, visual state, and user journeys — consumable by GitHub Copilot agents for three things: (1) answering arbitrary questions about any page or journey, (2) generating accurate, assertion-level test steps, and (3) feeding the [[application-knowledge-layer]] effort.

This is a **capture pipeline**, not a one-off doc. Treat it that way: schema first, then tooling, then execution.

**Revision note:** v1 covered structure and navigation well but had three gaps — no visual artifacts, no retrieval mechanism for ad-hoc questions, and no assertion-level detail for test generation. This revision adds all three.

---

## 1. Data model (define before touching the browser)

Seven artifact types, kept separate so each can be updated independently:

| Artifact | Contains | File |
|---|---|---|
| **Page record** | route, purpose, elements/selectors, state variants, auth prerequisites | `pages/<page-id>.yaml` |
| **Visual capture** | screenshots per state/viewport + element bounding-box map | `pages/<page-id>/visuals/*.png` + `visual-map.yaml` |
| **Nav edge** | from-page → to-page, trigger, action type | `navigation/edges.yaml` (append-only log, aggregated) |
| **Journey** | named ordered sequence of (page, action) steps | `journeys/<journey-id>.yaml` |
| **Test step set** | assertion-level Given/When/Then steps, derived from a journey | `test-steps/<journey-id>.yaml` |
| **Component record** | shared UI (header, nav, modal) captured once, referenced by many pages | `components/<component-id>.yaml` |
| **Site map** | derived index of all pages + edges (generated, not hand-written) | `sitemap.generated.yaml` |

**Page record schema (example):**
```yaml
id: checkout-shipping
route: /checkout/shipping
title: "Shipping Address"
purpose: "Collect and validate shipping address before payment step"
auth_required: true
last_verified: 2026-08-20
shared_components: [global-header, footer]
states:
  - name: empty
    description: "First visit, no data entered"
  - name: validation-error
    description: "Submitted with missing/invalid zip"
  - name: populated
    description: "Fields pre-filled from saved address"
elements:
  - name: shipping-form
    role: form
    selector: "[data-testid='shipping-form']"
    strategy: testid
  - name: continue-button
    role: button
    accessible_name: "Continue to Payment"
    selector: "role=button[name='Continue to Payment']"
    strategy: role
validation_rules:
  - "zip code required if country = US"
navigation:
  enters_from: [cart-review]
  exits_to: [checkout-payment, cart-review]
test_data_dependencies:
  - "user must be authenticated"
  - "cart must contain >= 1 item"
```

**Selector priority** (matches Playwright best practice, keeps the base stable when CSS/DOM changes): `data-testid` → ARIA role+accessible-name → stable CSS → xpath as last resort. Encode `strategy` explicitly so Copilot never has to guess which selector is "the real one."

**Visual map schema (example)** — links screenshots to elements so "what does X look like" is answerable directly, and so bounding boxes can be used for visual regression later:
```yaml
page_id: checkout-shipping
state: populated
viewport: desktop
screenshot: visuals/checkout-shipping--populated--desktop.png
elements:
  - name: continue-button
    bbox: [420, 680, 560, 720]
```

**Component record** — captured once, referenced everywhere, so a question like "where is the search bar used" returns one canonical answer plus a list of pages, instead of N fragmented duplicates:
```yaml
id: global-header
elements: [...]
used_on: [checkout-shipping, cart-review, product-detail]
```

---

## 2. Capture workflow (per page, using Copilot's integrated browser)

1. **Navigate** — Copilot agent mode drives the integrated browser to the target route (or you drive it manually and hand control back).
2. **Check shared components** — before capturing page elements, check whether the page includes any already-captured component (header, nav, modal). Reference it instead of re-capturing it.
3. **Extract candidates** — agent inspects the DOM/accessibility tree for interactive elements, proposes selectors ranked by the priority above.
4. **Capture visual states** — for each meaningful state (empty, error, populated, loading — defined per page, not every page needs all four), screenshot at the required viewport(s) and record element bounding boxes into the visual map.
5. **Annotate semantics** — you (human) supply `purpose`, `validation_rules`, `test_data_dependencies`, and journey context; the agent can't infer business intent or expected outcomes from DOM/pixels alone — this is the step that keeps the knowledge base from being a dumb sitemap.
6. **Write records** — agent fills the page-record and visual-map templates and writes the files.
7. **Log edges** — every navigation action taken during capture (click, submit, redirect) gets appended to `navigation/edges.yaml` automatically — don't hand-maintain this.
8. **Validate** — schema check (JSON Schema or a small script) runs before commit: required fields present, selector strategy declared, no duplicate page IDs, every screenshot has a matching visual-map entry.
9. **PR + review** — fits the repo/PR workflow you already chose for the AKL, so page records get the same review discipline as code.

Package steps 1–6 as a single reusable Copilot skill (e.g. `.github/skills/capture-page.md`) so each page follows an identical prompt/procedure instead of drifting in format page to page.

---

## 2a. Answering arbitrary questions — retrieval strategy

Flat YAML files answer *direct* lookups fine ("show me checkout-shipping") but not open-ended questions ("everywhere the search bar appears," "what's the full path to checkout"). Two additions make that work without over-engineering it:

- **A query skill, not just a data store.** Define a `.github/skills/query-knowledge-base.md` skill that knows the file layout and how to answer common question shapes: single-page lookup → read one file; journey/path question → traverse `navigation/edges.yaml`; component usage question → read the component record's `used_on` list; visual question → resolve to the matching screenshot via the visual map. This turns "ask anything" into "the agent knows which files to combine," which is enough at the scale of one application.
- **Escalate to embeddings only if needed.** If the page count grows large enough that skimming the relevant files gets slow or unreliable, add a lightweight embedding index over page `purpose` + `elements` text as a second-stage lookup. Don't build this upfront — it's a Phase-6+ addition, not a Phase-0 dependency.

---

## 3. Journeys and test steps — two layers, not one

A journey (page/action sequence) is not detailed enough to emit a test case directly — it's missing expected outcomes and setup data. Split into two artifacts:

**Journey** (the path):
```yaml
id: guest-checkout
steps:
  - page: cart-review
    action: click continue-button
  - page: checkout-shipping
    action: submit shipping-form
  - page: checkout-payment
    action: submit payment-form
```

**Test step set** (derived from the journey, one level more detailed — this is what actually generates accurate test steps):
```yaml
journey_id: guest-checkout
preconditions:
  - "cart contains >= 1 item"
  - "user is not authenticated"
steps:
  - given: "on checkout-shipping page, state=empty"
    when: "submit shipping-form with valid US address"
    then: "navigate to checkout-payment; shipping summary shows entered address"
  - given: "on checkout-shipping page, state=empty"
    when: "submit shipping-form with missing zip"
    then: "remain on checkout-shipping; state=validation-error; error text references zip"
```

Generate the test-step set with a `.github/skills/generate-test-steps.md` skill that reads the journey plus each referenced page record (`validation_rules`, `states`, `test_data_dependencies`) — the accuracy of the output test steps depends entirely on those fields being filled in during capture, which is why they're now first-class in the page-record schema.

---

## 4. Versioning and coverage (keep the base trustworthy)

- **Staleness marker**: `last_verified` date on each page record; flag records untouched across N release cycles for re-capture. Selectors and screenshots drift as the UI changes — an unflagged stale record is worse than a missing one because it looks trustworthy.
- **Coverage index**: a generated file listing all known routes (from the crawl) against which ones have a page record, so you can see capture progress at a glance rather than guessing.

---

## 5. Sequencing (phased, matches your existing AKL structure)

| Phase | Deliverable | Depends on |
|---|---|---|
| 0 | Schema finalized (incl. visual map, test-step set), repo layout, JSON Schema validator | — |
| 1 | `capture-page` skill built and piloted on 1–2 pages, incl. visual capture | Phase 0 |
| 2 | Automated crawl for skeleton page records + coverage index across full route list | Phase 0 |
| 3 | Guided walkthrough — fill semantics (purpose, validation, states, test data) onto skeletons | Phase 1, 2 |
| 4 | Nav-edge aggregation script (edges.yaml → sitemap.generated.yaml) | Phase 3 in progress |
| 5 | Component dedup pass — extract shared header/nav/modal into component records | Phase 3 substantially complete |
| 6 | Journey authoring, then `generate-test-steps` skill | Phase 4 |
| 7 | `query-knowledge-base` skill for ad-hoc questions | Phase 3 substantially complete |
| 8 | CI validation gate on PRs (schema + dead-link + staleness check) | Phase 0 |
| 9 | Consumption — feed journeys/test steps into QA generation, other agents | Phase 6 |

Phases 4, 5, 7, and 8 can run in parallel with Phase 3 once the schema is stable — no need to wait for full page coverage.

---

## 6. Key trade-off: guided walkthrough vs. automated crawl

- **Manual/guided (Copilot-assisted) walkthrough** — higher-fidelity `purpose`, validation rules, and journey context, but slower; doesn't scale past a few dozen pages without fatigue.
- **Automated crawl** (e.g., seed with Playwright codegen or a crawler to enumerate routes/selectors first) — fast coverage of structure and can also grab default-state screenshots cheaply, but produces no business-intent metadata; purpose/validation/test-data fields come back empty.

**Recommended hybrid** (unchanged from v1, now also covers visuals): run an automated crawl first to generate skeleton page records and default-state screenshots for every discoverable page, then use the guided Copilot walkthrough to add semantics and the non-default visual states (error, populated) on top. This avoids re-deriving selectors by hand and keeps human time on the part machines can't do.

---

## 7. Open decisions to make before Phase 0

- Page ID convention (route-based vs. feature-based slugs)
- Which states are mandatory to capture per page (empty/error/populated) vs. optional
- Where journeys and test-step sets live relative to per-page records (same repo, same PR workflow as AKL — recommended for consistency)
- Who owns journey/test-step authoring — QA, BA, or whoever captured the pages
- Screenshot storage: in-repo (simple, but repo size grows) vs. external artifact store referenced by path

I can turn any of these sections (schema, the `capture-page` skill prompt, the `generate-test-steps` skill, or the CI validator) into a working artifact next — say which one.
