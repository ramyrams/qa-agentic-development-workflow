# Knowledge Layer — Role-Based Use Cases

## How this document was built

For each role, I worked through realistic scenarios of how they'd actually query or rely on this knowledge base. Where a scenario couldn't be answered by the schema as designed so far, that's flagged as a gap and a fix is proposed inline, then consolidated in Section 9. This surfaced five real gaps that weren't visible when the layers were reviewed in isolation — cross-layer "reverse" links and cross-cutting groupings tend to only show up once you ask "how would a specific person actually use this."

Coverage claim: this covers the roles and query patterns that come up repeatedly in application development — not a literal statistical 90%, but the scenarios that would account for the large majority of real usage. Edge-case or org-specific workflows will still surface gaps over time; treat this as the core set, not the final word.

---

## 1. Developer (feature work / maintenance)

| Scenario | Draws from | Status |
|---|---|---|
| "Before I change this table, what breaks?" | DB → API → UI trace, walked backward | Supported |
| "Is there already a pattern for this kind of form validation elsewhere in the app?" | Business Rules index, grouped by domain | Supported |
| "What selector convention does this page already use, so my new element is consistent?" | Page record, elements list | Supported |
| "I'm deprecating this endpoint — who else calls it?" | **API contract record needs a reverse `used_by_pages` link** | **Gap — see §9.1** |
| "What test coverage exists for the thing I'm about to touch?" | Test-step sets, but no way to tell if they're actually automated/passing | **Gap — see §9.2** |

## 2. QA / Test Engineer

| Scenario | Draws from | Status |
|---|---|---|
| "Generate test steps for this journey, including edge cases." | Journey + page records' validation_rules/states/test_data_dependencies | Supported |
| "Which pages have known validation error states I should regression-test after a UI change?" | Page states field | Supported |
| "Has this scenario already been automated, or do I need to write it fresh?" | Test-step set | **Gap — no automation status field — see §9.2** |
| "What test data do I need to reach this page in a valid state?" | test_data_dependencies | Supported |
| "This bug report mentions an error message — what page/endpoint does it map to?" | API response error shapes, but nothing indexes error text/code back to source | **Gap — see §9.4** |

## 3. Business Analyst

| Scenario | Draws from | Status |
|---|---|---|
| "Is the rule I wrote in the BRD actually enforced in the system?" | Business rule `enforced_at` link | Supported (once §8's linkage is built) |
| "Where else in the app does a similar rule already exist, so I'm consistent?" | Rules index, grouped by domain | Supported |
| "Walk me through the current guest-checkout flow as it actually behaves today." | Journey + page purposes | Supported |
| "This rule is enforced client-side only — is that a gap I should flag?" | `enforced_at` + client/server field | Supported |
| "Show me everything related to the 'returns' feature across UI, API, and rules — I'm scoping new requirements." | Nothing currently groups records by feature/epic across layers | **Gap — see §9.3** |

## 4. Architect / Tech Lead

| Scenario | Draws from | Status |
|---|---|---|
| "What's the blast radius if I change this shared component?" | Component `used_on` list | Supported |
| "What's the blast radius if I deprecate this API endpoint?" | Reverse link from endpoint to consuming pages | **Gap — see §9.1** |
| "What's the blast radius if I alter this table's schema?" | DB table `used_by` (which endpoints read/write it) | **Gap — see §9.1 (same pattern, DB side)** |
| "Which services call which other services, and where's the circular dependency risk?" | API map (aggregate) | Supported |
| "Where is validation enforced only client-side across the whole app — that's a systemic risk to prioritize." | Rules index filtered by enforcement location | Supported (once rules index exists) |

## 5. Security & Governance Reviewer

*(This is your own role — worth reading closely.)*

| Scenario | Draws from | Status |
|---|---|---|
| "List every page and endpoint that reads or writes this PII column." | Walking the UI→API→DB trace backward from a flagged column | **Gap — not yet its own artifact — see §9.5** |
| "Does the role/permission matrix match written policy?" | Role → access-surface links (§8) | Supported once built |
| "Which endpoints have no auth requirement at all?" | API contract `auth_required` field, aggregated | Supported |
| "Where is a business rule that should be a hard server-side constraint only enforced in the UI?" | Rules index filtered by enforcement location | Supported |
| "If an AI agent were given access to this knowledge base, what could it infer about sensitive data exposure just from the trace records?" | Exposure-surface index | Same artifact as row 1 — worth thinking about as a **governance-review input in its own right**, not just an incident-response tool |

## 6. Production Support / Incident Response

| Scenario | Draws from | Status |
|---|---|---|
| "A user reports an error on checkout — what page, endpoint, and table does that map to?" | Trace record, plus error catalog | **Gap — see §9.4** |
| "What auth/session behavior applies here — could this be a session-expiry issue?" | Security layer, session/token behavior | Supported |
| "Is this a known issue with a captured validation rule, or something new?" | Rules index + validation_rules | Supported |
| "What external system does this call out to, in case the failure is upstream?" | Integration record, `triggered_by` link | Supported once built |

## 7. Product Manager

| Scenario | Draws from | Status |
|---|---|---|
| "Does the product already support X, or would this be new work?" | Page/journey/rule records via Q&A | Supported |
| "What's the current user journey for this flow, so I can scope a redesign?" | Journey + site map | Supported |
| "If I ask for a new field on this form, what layers does that touch?" | UI→API→DB trace, forward direction | Supported |
| "Show me everything related to a named feature so I can review it holistically." | Same feature-grouping gap as BA scenario | **Gap — see §9.3** |

## 8. New Engineer (Onboarding)

| Scenario | Draws from | Status |
|---|---|---|
| "Explain how the checkout flow works end to end, UI to database." | Full trace, in plain language via Q&A skill | Supported |
| "What are all the pieces of the 'returns' feature I need to understand before my first ticket?" | Feature grouping | **Gap — see §9.3** |
| "What conventions does this codebase use for selectors/validation/API shape?" | Aggregate patterns across page/API records | Supported, though better with more captured pages |
| "Who do I ask if I have questions about this business rule?" | Rule `source/owner` field | Supported |

---

## 9. Gaps found during this review, and the fix for each

### 9.1 Reverse "used_by" links (Developer, Architect scenarios)
API contract records and DB table records only recorded forward references (page → endpoint, endpoint → table). Nothing let you start from an endpoint or table and ask who depends on it — the same problem shared components already solved with `used_on`. Fix: add the same pattern to both.
```yaml
# api/<endpoint-id>.yaml — add:
used_by_pages: [checkout-shipping, cart-review]

# db/<table-id>.yaml — add:
used_by_endpoints: [post-checkout-shipping, get-order-status]
```
Both are derivable automatically from the existing forward links during the linking step (§3c of the API/DB mapping design) — no new capture work, just an additional generated field.

### 9.2 Test automation status (QA, Developer scenarios)
Test-step sets recorded the steps themselves but nothing about whether they're actually automated, passing, or flaky — a QA engineer asking "do I need to write this test" had no way to get a real answer. Fix: add to the test-step set schema.
```yaml
# test-steps/<journey-id>.yaml — add:
automation_status: not-automated   # not-automated | automated | flaky | deprecated
last_run_result: null              # pass | fail | null if never run
```
This field will go stale fast unless it's synced from an actual test runner/CI result rather than hand-maintained — flag as a candidate for a connector/integration rather than manual annotation when you get to building it.

### 9.3 Feature/epic grouping (BA, PM, Onboarding scenarios)
Three different roles independently needed "show me everything related to feature X" — and nothing currently groups a page, its journey, its business rules, its endpoints, and its tables under a shared feature name. This is a cross-cutting gap, not layer-specific. Fix: add an optional `feature` tag as a cross-cutting field (alongside `source`/`confidence`/`last_verified`) on every artifact type.
```yaml
feature: returns-and-refunds
```
A generated "feature index" (same derivation pattern as the sitemap/ERD/rules-index) then becomes: everything sharing a feature tag, across all layers, in one view.

### 9.4 Error catalog (Support, QA scenarios)
API contract records capture response error shapes, but nothing maps a specific error code/message back to "which endpoint, which page, what it usually means" — exactly what an incident-response scenario needs first. Fix: a derived aggregate, generated from API contract error shapes plus any error states already captured on pages.
```yaml
# errors.generated.yaml
- error_code: "SHIPPING_INVALID_ZIP"
  endpoint_id: post-checkout-shipping
  surfaced_on_page: checkout-shipping
  meaning: "Submitted zip code failed format/country validation"
```

### 9.5 Sensitive-data exposure surface (Security/Governance scenario)
This was flagged as "not yet defined as its own artifact" in the last revision, on the theory that it's derivable on demand by walking the trace backward. Given it came up as a first-class need for your own role specifically, it's worth promoting from "derivable if asked" to a standing generated artifact rather than something reconstructed each time.
```yaml
# exposure-surface.generated.yaml
- table: users
  column: ssn
  sensitivity: pii-high
  exposed_via:
    - endpoint: get-user-profile
      page: account-settings
    - endpoint: post-checkout-shipping
      page: checkout-shipping
```
Generated the same way as the other aggregates — no new capture step, just a script that walks existing trace records filtering for `sensitivity`-flagged columns.

---

## Net effect on the design

All five fixes are **additive fields or generated aggregates** — none require re-capturing anything already designed, and none add a new manual capture step. That's a useful signal: the core schema (page, API contract, DB table, trace) was sound; what was missing was reverse-navigability and cross-layer grouping, which is exactly the kind of gap that only surfaces when you ask "how does a specific role actually use this," not when reviewing a layer in isolation.
