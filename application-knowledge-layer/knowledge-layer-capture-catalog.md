# Application Knowledge Layer — What to Capture, Per Layer

## Purpose of this document

A reference catalog, not a workflow — for each layer of the application, what technical details are worth capturing and why they pay off later (test generation, Q&A, governance, onboarding, impact analysis). Use this to scope what "complete" means for each layer before capturing it, rather than discovering gaps after the fact.

You've already designed capture for UI, API, and DB (Sections 1–3 below are the fullest). Business rules, security, integration, and configuration (4–7) are the layers worth adding next — scope them, don't necessarily build all of them at once.

---

## 1. UI / Presentation Layer

| Detail | Why it matters later |
|---|---|
| Route, title, purpose | Basic identity — what a page is, answerable directly in Q&A |
| Elements + multi-strategy selectors (testid/role/CSS/xpath) | Test-step generation, resilient to DOM changes |
| States (empty, error, loading, populated) | Test coverage for non-happy-path scenarios |
| Visual capture — screenshots per state/viewport + bounding boxes | Visual Q&A ("what does X look like"), visual regression later |
| Client-side validation rules | Test-step assertions; also flags where client-only validation might be bypassable (see Business Rules layer) |
| Navigation edges (entry/exit, trigger) | Journey construction, nav-graph Q&A |
| **Site map (derived, aggregate)** — all pages + edges as one navigable graph | Answers "what's the full path to X," orphan-page detection, coverage-at-a-glance |
| **User journeys / workflow paths (named sequences of pages+actions)** | The actual unit test-step generation consumes; also the clearest artifact for "how does a user get from A to B" Q&A |
| Shared components + usage list | Avoids fragmented answers to "where is X used"; dedup |
| Auth/access requirement to reach the page | Test preconditions, security review input |
| Feature flags affecting visibility | Avoids false "this page doesn't exist" gaps across environments |

---

## 2. API Layer

| Detail | Why it matters later |
|---|---|
| Method, path, version | Endpoint identity |
| Auth requirement (token type, scopes) | Test preconditions, security review |
| Request schema (fields, types, required/optional) | Test-step generation for valid/invalid payloads |
| Response schema (success + error shapes) | Assertions in generated test steps |
| Status codes and error semantics | Negative-path test coverage |
| Backing handler / service location (when code-reachable) | Enables DB linkage, impact analysis when code changes |
| Tables touched + confidence tag | The UI→API→DB trace payoff |
| Source tag (spec / observed / code-traced / reconciled) | Keeps stale-spec drift visible instead of silently trusted |
| Deprecation / versioning status | Prevents generating test steps against a dying endpoint |
| **API map (derived, aggregate)** — endpoints grouped by domain/service, plus which endpoints call which other internal services | Blast-radius Q&A ("what else uses this endpoint"), and surfaces cross-service call chains a single endpoint record can't show alone |

---

## 3. Database / Data Layer

| Detail | Why it matters later |
|---|---|
| Table, column, type, keys, constraints (from DDL) | Test data setup, schema Q&A |
| Relationships (FK, cardinality) | Understanding cascade effects, test data dependencies |
| Sensitive-data flags (PII, financial, etc. columns) | Feeds directly into your governance work — data classification matters more than schema shape alone |
| Table ownership (which service/team owns writes) | Impact analysis — who to loop in before a schema change |
| Source (DDL export, migration, introspection) + refresh date | Staleness tracking, since your export is a point-in-time snapshot, not live |
| **Schema-wide ERD (derived, aggregate)** — all tables + relationships as one graph, not just per-table FK lists | "What tables are connected to X" Q&A, cascade-impact analysis when a table changes |

---

## 4. Business Rules / Workflow Layer *(not yet designed — natural next addition)*

| Detail | Why it matters later |
|---|---|
| Rule statement in plain language | The thing test-step generation actually needs — "zip required if country=US" is more useful than inferring it from a regex |
| Where enforced — client only, server only, or both | Security/governance-relevant: client-only enforcement is bypassable and worth flagging as a risk, not just a fact |
| Conditions and exceptions | Captures edge cases a single validation_rules line misses |
| Rule source/owner (BA doc, SME, code comment) | Traceability when a rule is questioned or changes |
| **Enforced-at link(s)** — specific page_id/element and/or endpoint_id where the rule is actually applied | Without this, a rule is just a floating statement — this is what lets you ask "is this rule enforced everywhere it should be" and get a real answer |
| Multi-step business workflows spanning multiple pages/services | Distinct from a UI journey — a business workflow (e.g. "order fulfillment") may span systems a page-by-page walkthrough never touches directly |
| **Rules index (derived, aggregate)** — all rules grouped by domain/page, plus a decision table where multiple rules interact on the same field | Surfaces conflicting or overlapping rules across pages that a single page's validation_rules list can't show; the aggregate view is what a governance review would actually read |

This layer is what turns "the form has a zip field" into "the business requires X, and here's whether the system actually enforces it everywhere it should" — closer to what your governance-intake and Governance Gate work already cares about.

---

## 5. Security / Auth Layer *(recommend scoping next after business rules)*

| Detail | Why it matters later |
|---|---|
| Auth mechanism (SSO, OAuth, roles) | Test precondition setup, security review |
| Role/permission matrix — which roles reach which pages/endpoints | Access-control test generation, governance review |
| **Matrix entries as explicit links** — role_id → list of page_ids + endpoint_ids, not just a narrative description | Makes the permission matrix queryable and diffable, not just a document someone has to read |
| Session/token behavior (expiry, refresh) | Test scenarios for session-expired states, a commonly-missed test case |

---

## 6. Integration / External Systems Layer *(lower priority — scope only if the app has significant external dependencies)*

| Detail | Why it matters later |
|---|---|
| External systems called (third-party APIs, other internal services) | Blast-radius understanding when something breaks |
| What triggers the call, data flowing out/in | Test stubbing strategy for environments without live integration access |
| **Triggered-by link** — which internal endpoint_id initiates this external call | Connects the integration layer back to the API layer instead of floating as a standalone fact |
| Auth/credential type (never the secret itself) | Test environment setup, without capturing anything sensitive |
| Failure/fallback behavior | Negative-path test coverage for degraded-dependency scenarios |

---

## 7. Configuration / Feature Flags Layer *(capture opportunistically, not as its own phase)*

| Detail | Why it matters later |
|---|---|
| Feature flags gating UI/API behavior | Prevents false "gap" flags when a page/endpoint only appears under a flag |
| Environment-specific behavior differences relevant to what was captured | Avoids confusion when captured behavior doesn't match another environment |

---

## 8. Cross-Layer Linkage — the connective tissue

This is the part that was implicit rather than explicit until now. Each layer above captures details *within* itself; the links *between* layers are separate artifacts in their own right, not something that falls out automatically from having both layers captured.

| Link | Connects | Where it's defined | Status |
|---|---|---|---|
| **UI → API → DB trace** | element → endpoint → table(s) | `traces/<trace-id>.yaml`, with rolled-up confidence | Fully designed (earlier session) |
| **Rule → enforcement point** | business rule → page/element and/or endpoint | `enforced_at` field on the rule record | Newly added above — not yet built out |
| **Role → access surface** | role → pages + endpoints it can reach | permission matrix entries as explicit id lists, not prose | Newly added above — not yet built out |
| **Integration → trigger** | external call → the internal endpoint that initiates it | `triggered_by` field on the integration record | Newly added above — not yet built out |
| **Sensitive data → exposure surface** | PII/sensitive DB column → every page/endpoint that reads or writes it | derivable by walking the UI→API→DB trace backward from a flagged column | Not yet defined as its own artifact — worth adding if governance work needs it directly, rather than making someone manually trace it |

**Without these being explicit fields, the "layers" are really just four or five separate documents that happen to describe the same application** — none of the cross-layer questions (is this rule enforced everywhere, what can this role actually touch, what's exposed if this column leaks) are answerable without walking from one file to another by hand. The links are what make it one knowledge layer instead of five.

Only the UI→API→DB trace has been fully designed with its own artifact type so far. The other three link types are real gaps the same way sitemap/ERD/rules-index were — worth building out with the same pattern (a field on the record, generated/reconciled where possible, confidence-tagged where inferred) rather than left as narrative fields someone has to read and connect mentally.

---

Site map, API map, ERD, and rules index are all **derived** from the per-item records — generated by aggregation scripts once enough per-item capture exists, not hand-authored separately. User journeys are the one exception: they're curated (someone names a sequence as a meaningful path), though the raw edges they're built from are still logged automatically during capture. Don't treat "capture the aggregate view" as a separate manual task per layer — it's a generation step that runs once the underlying records exist, same pattern as `sitemap.generated.yaml` in the UI layer design.

---

## Cross-cutting fields (apply to every layer, not layer-specific)

- **Source** — how the detail was captured (browser observation, code trace, DDL parse, spec import, manual annotation).
- **Confidence** — high/medium/low, rolled up across any chain that links layers together (a trace is only as trustworthy as its weakest link).
- **last_verified** — staleness marker; all of this drifts as the app changes.

---

## How the layers get used together, not just individually

- **Test-step generation** draws primarily from UI + API + Business Rules, with DB used for test-data setup.
- **Arbitrary Q&A** draws from whichever layers are relevant to the question — this is why consistent schema and dedup (shared components, single-source API contracts) matters across all of them, not just within one.
- **Governance/compliance work** draws primarily from Business Rules + Security + DB sensitive-data flags — this is the layer combination most directly useful to your governance-intake effort, separate from the QA/test-generation use case.
- **Onboarding** benefits from having all layers linked — a new engineer can trace a button through to the table it writes to instead of reading five separate systems.
- **Impact analysis** ("what breaks if I change this table") needs the full UI→API→DB trace plus the Integration layer if external systems also read that data.

## Recommended prioritization

You've already scoped UI, API, and DB. Business Rules is the next highest-value addition — it's the layer that makes test-step generation actually *accurate* rather than just DOM-accurate, and it feeds your governance work directly. Security/Auth after that. Integration and Configuration are worth capturing opportunistically as they come up during walkthroughs, not as dedicated phases, unless the application has unusually heavy external dependencies.
