# Application Knowledge Layer — Architecture & Governance Design

**Version 2.0** · Supersedes v1.0
**Status:** Draft for team review

> **What changed from v1.0.** Five structural changes: (1) domains are now split
> into *derived*, *authored*, and *hybrid* — derived domains are generated from
> code, not hand-written; (2) governance is enforced by CI validation, not
> convention; (3) staleness is detected by code churn, not calendar dates;
> (4) an eval loop is defined so the pilot produces evidence; (5) multi-repo ID
> namespacing, security posture, and conflict arbitration are decided up front
> rather than deferred. Three domains were added: integrations, glossary, and
> decisions. Section 11 now maps every load-bearing decision to independently
> validated industry precedent. Final review added agent write-back (8.4),
> a precedence order for contradictions (8.3), context-budget constraints
> (8.5), coverage and retrieval-precision metrics (10), and cold-start
> mitigation in Phase 5. An enterprise governance review then added Section 11
> (Operating Model): named accountability, waivers, standard versioning,
> approver SLAs, audit evidence, alignment to existing AI governance, retiring
> what the layer replaces, consumption paths, enablement, indicative cost, and
> Phase 6 exit criteria.

---

## 1. Purpose

A single, versioned, git-native source of truth for everything a human or an
AI agent needs to know about a web application — business rules, workflows,
pages, elements, validation rules, non-functional requirements, DB schema,
API contracts, integrations, glossary, and decisions — structured so that:

- Every fact lives in exactly one place, owned by the team closest to it.
- Facts that already exist in machine-readable form are **generated, never
  re-typed** — eliminating the drift that kills documentation efforts.
- GitHub Copilot (and any future agent) can load the *relevant slice* of this
  knowledge automatically, based on what file the developer is touching.
- Staleness is detected mechanically and surfaced as a build signal.

---

## 2. Core Architectural Principle: Derived vs. Authored

**This is the most important decision in the design, and the one v1.0 got
wrong.**

v1.0 treated all domains as hand-authored Markdown. But DB schema and API
contracts already exist in machine-readable form — migrations, ORM models,
OpenAPI specs. Hand-writing them into Markdown creates a *second source of
truth that drifts silently*, because nothing fails when the doc is wrong.

Every domain is therefore classified:

| Type | Domains | Source of truth | How the doc is produced |
|---|---|---|---|
| **Derived** | `db-schema`, `api-contracts` | Migrations, OpenAPI spec | Generated in CI; humans add only an `## Intent` section (why a constraint exists) |
| **Hybrid** | `pages`, `elements`, `integrations` | Route config / component tree / client definitions | Inventory generated; behavior contract authored |
| **Authored** | `business-rules`, `workflows`, `validation-rules`, `non-functional`, `glossary`, `decisions` | The AKL doc itself | Fully human-authored |

### 2.1 How generation works

For derived domains, a CI job regenerates the doc body from the source
artifact on every merge to main. Human-authored content lives in a protected
block that the generator never overwrites:

```markdown
<!-- GENERATED:START — do not edit by hand -->
| Column | Type | Nullable | Constraint |
|---|---|---|---|
| id | uuid | no | PK |
| status | enum | no | refund_status |
<!-- GENERATED:END -->

## Intent
Refund rows are never hard-deleted — see [[DEC-004]]. The status enum is
deliberately narrow; adding a value requires a business-rule change first.
```

**Why this matters:** a schema change now *automatically* updates the
knowledge layer in the same PR. No review SLA, no human memory, no drift.
The `## Intent` section — the part that can't be generated and is the part
agents most need — is the only thing a human maintains.

**Trade-off:** building generators is real upfront work (est. 1–2 weeks for
both derived domains). It is the single highest-leverage investment in this
design; without it, these two domains decay within a quarter.

---

## 3. Repository Layout

```
/knowledge/
  # ---- authored ----
  /business-rules/
  /workflows/
  /validation-rules/
  /non-functional/          # NEW in v2 — perf, security, a11y, scalability
  /glossary/                # NEW in v2 — ubiquitous domain language
  /decisions/               # NEW in v2 — ADRs, linked to affected rules
  # ---- hybrid ----
  /pages/
  /elements/
  /integrations/            # NEW in v2 — third-party APIs, failure modes
  # ---- derived (generated) ----
  /db-schema/
  /api-contracts/
  # ---- governance ----
  /_governance/
    OWNERS.md               # domain -> team, fallback owner, AKL Steward
    CONTRIBUTING.md
    SECURITY.md             # what must never go in the AKL + classification map
    WAIVERS.md              # time-boxed exceptions — see Section 11.2
    VERSION                 # semver of the standard — see Section 11.3
    schema-templates/       # one worked example per domain
    review-cadence.md
    definition-of-done.md   # what "approved" means
/.github/
  CODEOWNERS
  /workflows/
    akl-validate.yml        # NEW in v2 — frontmatter, links, IDs, drafts
    akl-generate.yml        # NEW in v2 — regenerates derived domains
    akl-staleness.yml       # NEW in v2 — churn-based drift detection
  /instructions/
    *.instructions.md
  copilot-instructions.md
```

Domain-first layout, not feature-first: a single feature touches business
rules, a page, an API, and a schema table simultaneously. Organizing by domain
lets each owning team manage their slice independently, without merge
contention — which is what federated ownership requires structurally, not just
as a policy statement.

---

## 4. File Standard

```yaml
---
id: CHKOUT-BR-042             # globally unique — see Section 4.2 namespacing
domain: business-rules
title: Refund eligibility window
owner_team: ba
status: approved              # draft | approved | deprecated
sensitivity: internal         # map to corporate classification — see Section 9
last_reviewed: 2026-08-01
tracks:                       # code paths this doc describes — powers Section 7.2
  - src/services/refund/**
related:
  - CHKOUT-WF-011
  - CHKOUT-API-refunds
superseded_by: null           # set when status: deprecated
authored_by: human            # human | agent — see Section 8.4
---
```

Two fields are new in v2 and both are load-bearing:

- **`tracks:`** — the code paths this document describes. This is what makes
  churn-based staleness detection possible (Section 7.2). Without it, staleness is
  guesswork.
- **`superseded_by:`** — v1.0 had a `deprecated` status but no way to say what
  replaced it, leaving agents and humans at a dead end.
- **`authored_by:`** — distinguishes human-authored docs from agent-proposed
  drafts (Section 8.4). Agent-proposed content never reaches `approved` without human
  review.

Files stay small and single-purpose — one rule, one workflow, one endpoint,
one table. This is what makes them useful as AI context: an agent editing a
refund service pulls in exactly the refund rule and refund contract, not an
entire business-rules binder.

### 4.1 Definition of Done

v1.0 said docs move to `approved` without defining what that means. A doc is
approvable when: it has valid frontmatter; every `related:` link resolves; it
states behavior rather than implementation; it contains no credentials or
threat-model detail; and the owning team has reviewed it. This lives in
`_governance/definition-of-done.md` and is partly machine-checked (Section 6).

### 4.2 ID namespacing (multi-repo)

**Decide this before Phase 1 — it cannot be retrofitted.** `BR-042` is not
unique across four repositories, and `related:` links break the moment a
second application adopts the layer.

**Decision:** IDs are namespaced by application: `<APP>-<DOMAIN>-<NNN>` →
`CHKOUT-BR-042`. Single-app teams may alias to the short form locally, but the
canonical ID in frontmatter is always fully qualified.

**Scaling path:** shared domains (glossary, cross-cutting NFRs, shared schema)
live in a central `knowledge-core` repo consumed as a git submodule or
package; app-specific domains stay in the app repo. This keeps ownership local
while allowing genuinely shared facts to exist once.

---

## 5. Governance Model

Federated ownership: each team owns and approves changes within their domain;
the governance function sets the shared standard rather than approving every
change.

| Domain | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| business-rules, workflows | BA | BA Lead | Dev Leads | QA, Automation |
| pages, elements | Frontend Dev | Frontend Lead | BA, QA | Automation |
| db-schema, api-contracts *(derived)* | Backend Dev | Backend Lead | BA | QA, Automation |
| validation-rules | Dev + QA | Dev Lead | BA | Automation |
| non-functional | Architecture | Tech Management | Dev, Backend Leads | All teams |
| integrations | Backend Dev | Backend Lead | Architecture | QA, Automation |
| glossary | BA | BA Lead | All domain owners | All teams |
| decisions (ADRs) | Architecture | Tech Management | All domain owners | All teams |
| `_governance/` standards | BA (governance role) | Tech Management | All domain owners | All teams |

**Every domain names a fallback owner in `OWNERS.md`.** v1.0 had a single
owning team per domain, which stalls during reorgs, leave, or attrition.

### 5.1 Contribution workflow

1. Contributor opens a PR touching their domain folder.
2. `akl-validate` runs (Section 6). A PR that fails validation cannot merge.
3. CODEOWNERS requires the owning team's approval; `validation-rules` requires
   both Dev and QA.
4. On merge, `akl-generate` refreshes derived domains if the PR touched
   migrations or the OpenAPI spec.

Governance reviews only `_governance/` changes — never individual domain PRs.
That is what keeps this federated rather than centralized-with-extra-steps.

### 5.2 Conflict arbitration

v1.0 deferred this; it is a launch blocker, because dev/QA co-ownership of
`validation-rules` will deadlock in week two without it.

**Decision path:** disagreement escalates to the BA who owns the underlying
business rule — because a validation-rule dispute is nearly always a
disagreement about intended behavior, not implementation. If the business rule
itself is ambiguous, that is the actual defect: the BA clarifies the rule, and
the validation rule follows. Unresolved after that, Tech Management decides.

---

## 6. Enforcement: CI Validation

**v1.0's governance was policy without machinery.** Everything below is cheap
CI and turns stated rules into enforced ones. `akl-validate.yml` fails a PR on:

| Check | Catches |
|---|---|
| Frontmatter schema | Missing/malformed `id`, `owner_team`, `status`, `sensitivity` |
| ID uniqueness | Two docs claiming `CHKOUT-BR-042` |
| Link integrity | `related:` or `superseded_by:` pointing at a deleted or nonexistent doc |
| Draft leakage | A `status: draft` doc referenced by an `applyTo` instruction file |
| Deprecation completeness | `status: deprecated` without `superseded_by:` |
| Sensitivity scan | Credential-shaped strings, secrets, connection strings |
| Generated-block integrity | Hand-edits inside `<!-- GENERATED -->` markers |

Advisory (reported, not blocking): orphan detection — an approved API contract
with no business rule referencing it, or a business rule tracking no code
paths. These are usually signals of missing knowledge rather than errors.

Without this section the AKL degrades into the same untrustworthy state as the
wiki it replaces, just with better folder structure.

---

## 7. Freshness

### 7.1 Lifecycle

`draft` → `approved` → `deprecated` (with `superseded_by:`). Only `approved`
docs are loaded into Copilot context — enforced by the draft-leakage check in
Section 6, not by convention.

### 7.2 Churn-based staleness (replaces v1.0's calendar SLA)

Date-based review SLAs are gamed by bumping a date, and produce the wrong
signal: a doc reviewed on schedule but describing code that changed twice
since is marked "fresh."

**Primary mechanism:** `akl-staleness.yml` compares each doc's
`last_reviewed` against the commit history of the paths in its `tracks:`
field. Code changed since the doc was last reviewed → the doc is flagged and
an issue is opened against the owning team, naming the specific commits.

**Secondary mechanism:** a calendar SLA per domain remains as a floor for docs
with little code churn (NFRs, glossary), where absence of change is not
evidence of accuracy.

Derived domains need neither — they regenerate on merge and cannot drift.

---

## 8. AI Agent Integration

### 8.1 Instructions vs. skills

Instructions are passive, always-injected context ("what is true here").
Skills are active procedures an agent runs, reading the layer mid-task.

`copilot-instructions.md` at the repo root is a short, always-loaded index.
Domain-specific instruction files are scoped with `applyTo` globs:

```yaml
---
applyTo: "**/refund/**,**/services/*Refund*"
---
Before editing this code, check CHKOUT-BR-042 and CHKOUT-API-refunds for
constraints. Do not introduce logic that contradicts an approved business
rule without flagging it.
```

Scoping matters because Copilot's context budget is finite: one monolithic
instructions file either truncates or drowns out the fact relevant to the file
actually being edited.

### 8.2 Read order for skills

A skill reads domains in dependency order so contradictions surface *before*
code is generated:

1. `db-schema` — the hard constraint
2. `api-contracts` — the interface
3. `validation-rules` + `business-rules` — the logic
4. `non-functional` — the budgets it must not breach

### 8.3 Precedence and contradiction handling

"Report the contradiction" is not specific enough to implement — without a
defined precedence order, each developer gets different agent behaviour, and
the Section 10 metric "contradictions introduced" becomes unmeasurable.

Precedence, highest first:

| Rank | Source | On conflict |
|---|---|---|
| 1 | `db-schema`, `non-functional` | **Halt.** Hard constraints — a generation that breaches the schema or a stated SLA is never correct. |
| 2 | `business-rules` | **Halt.** Authoritative over contracts: if a contract permits what a rule forbids, the contract is the defect. |
| 3 | `api-contracts`, `validation-rules` | **Flag and halt** if mutually inconsistent; the owning teams resolve via Section 5.2. |
| 4 | Patterns inferred from existing code | **Warn and proceed.** Code is evidence, not authority — an `anti-patterns` entry may explain the divergence. |

Halt means: do not generate; state which two documents conflict, by ID, and
stop. Silent resolution is prohibited — an agent picking a winner hides
precisely the defect the layer exists to surface.

### 8.4 Agent write-back: closing knowledge gaps

The layer is otherwise read-only from an agent's perspective, which means an
agent encountering undocumented behaviour — constant in early adoption — leaves
no trace, and the gap stays invisible.

A `propose-knowledge-doc` skill opens a PR containing a `status: draft`
document with `authored_by: agent` in frontmatter. The owning team reviews it
through the normal Section 5.1 flow. Nothing an agent proposes reaches
`approved` without human review, and drafts are already excluded from Copilot
context (Section 6), so there is no self-reinforcement risk.

This turns every agent session into a coverage-gap detector at negligible cost,
and gives the Section 10 eval a natural source of candidate gaps.

### 8.5 Context budget

**Unverified until Phase 5, and load-bearing.** If editing one service pulls
four documents, the design works; if the `related:` graph pulls forty, the
layer truncates in practice while appearing correct on paper.

Constraints to hold:

- Measure actual token consumption for scoped retrieval on real pilot files.
- Target ceiling: **~15% of the available context budget** for AKL content.
- Cap `related:` traversal at **depth 1** by default — a skill may follow
  further only when it names the specific document it needs.
- If measurement exceeds the ceiling, the remedy is narrower `applyTo` globs
  and smaller documents, not a larger budget.

### 8.6 Instruction-file maintenance at scale

`applyTo` globs are themselves a maintenance burden — they silently stop
matching after a refactor. Two mitigations: derive globs from the `tracks:`
field rather than hand-writing them (single source, one place to update), and
treat glob drift as a validation check (a glob matching zero files fails CI).

---

## 9. Security & Compliance

**v1.0 had no position here. This is the question that will stall sponsor
approval if unanswered.** A knowledge layer describing auth flows, PII fields,
and rate limits is a useful artifact for an attacker, and it is loaded into an
AI tool's context by default.

`_governance/SECURITY.md` states:

- **Never in the AKL:** credentials, secrets, connection strings, keys,
  threat models, unpatched-vulnerability detail, security control
  implementation specifics.
- **Classification mapping:** `sensitivity` values map to the existing
  corporate data-classification scheme rather than introducing a parallel
  taxonomy. Confirm the mapping with InfoSec in Phase 0 and record it in
  `_governance/SECURITY.md`; the values used here are placeholders until
  that mapping is agreed.
- **Permitted with `sensitivity: restricted`:** PII field *identification*
  (that a column holds PII, so agents handle it correctly) without sample
  data; auth *requirements* per endpoint without implementation detail.
- **Enforcement:** the Section 6 sensitivity scan blocks credential-shaped content;
  `restricted` docs are excluded from Copilot context by default and require
  explicit opt-in per instruction file.

**Data residency:** confirm with your security team whether AKL content
leaving the tenancy via Copilot is cleared under your existing agreement, and
record the answer here. "It's just Markdown in our repo" is not an answer to
that question — the content is transmitted as model context.

---

## 10. Measuring Whether This Works

**v1.0 had no feedback loop.** The entire value proposition is that agents
produce better output when grounded in the AKL, and nothing measured it. Build
the eval before the pilot so the pilot produces evidence rather than opinion.

**Method:** a fixed set of ~20 representative development tasks in the pilot
area, run with and without AKL context loaded.

**Metrics:**

| Metric | Measures |
|---|---|
| Contradictions introduced per task | Whether grounding prevents rule violations |
| Review comments correcting factual errors | Rework avoided |
| Contract/schema mismatches caught pre-merge | Shift-left effect |
| Time-to-first-correct-implementation | Developer friction |
| Authoring hours per domain per sprint | The ongoing cost side of the ledger |
| **Coverage: % of pilot-area code matched by a `tracks:` glob** | Whether a good result reflects the design or just a well-documented corner |
| **Retrieval precision: irrelevant docs surfaced per task** | Over-retrieval degrades output as surely as under-retrieval |
| **Context consumption as % of budget** | Whether the model in Section 8.5 holds under real load |

The last three exist because output-quality metrics alone are not
interpretable. A strong result on a 20%-covered pilot area says nothing about
scale-out; and a retrieval model that surfaces the right document alongside
nine wrong ones will fail quietly as the corpus grows.

Run per phase. Phase 6 (evaluate) becomes an evidence-backed decision, and
you can answer "is this working?" with numbers rather than anecdote.

---

## 11. Operating Model

Sections 5–10 define how the layer is *designed*. This section defines how it
is *run* — the process obligations an enterprise standard needs in order to
survive contact with legacy code, reorganisations, auditors, and teams under
delivery pressure. Everything here lives in `_governance/`.

### 11.1 Named accountability

Roles do not get paged; people do. Three named individuals are required before
Phase 1:

| Role | Responsibility | Named in |
|---|---|---|
| **AKL Steward** | Owns the standard in `_governance/`; approves changes to it; arbiter of last resort below Tech Management | `OWNERS.md` |
| **Domain owner (per domain)** | Approves content PRs in their domain | `OWNERS.md` |
| **Fallback owner (per domain)** | Covers leave, reorg, attrition | `OWNERS.md` |

A domain with no named fallback fails the Phase 1 exit check.

### 11.2 Exception and waiver process

Some code cannot reasonably comply — vendor or generated code, an acquired
codebase, a module scheduled for decommission. Without a documented path,
teams either fake compliance or quietly ignore the standard, and the two become
indistinguishable.

- **Request:** the owning team raises a PR adding an entry to
  `_governance/WAIVERS.md` with scope, reason, and requested expiry.
- **Approve:** AKL Steward for scoped/technical waivers; Tech Management for
  anything spanning a whole domain or repository.
- **Expiry is mandatory.** No open-ended waivers. Maximum 2 quarters; renewal
  requires a fresh request, not an extension.
- **Visibility:** waived paths are excluded from coverage metrics (Section 10)
  and reported separately, so waivers reduce the denominator rather than
  silently inflating the score.

An unwaived, non-compliant path is a defect. A waived one is a known,
time-boxed exception. The distinction is the point.

### 11.3 Versioning the standard

`_governance/` changes affect every consuming repository at once. A frontmatter
schema change with no version policy breaks validation everywhere
simultaneously.

- The standard carries a **semantic version**, declared in
  `_governance/VERSION`.
- **Patch/minor** (new optional field, clarified wording): consuming repos pick
  it up on their next `knowledge-core` bump.
- **Major** (required field added, field removed or renamed, validation
  tightened): requires a migration note, a **one-quarter deprecation window**
  during which both forms validate, and an announced cut-over date.
- Breaking changes without a migration path are not permitted, regardless of
  how small they appear.
- Consuming repositories pin a version; `akl-validate` warns when a repo is
  more than one minor version behind and fails when it is a major behind.

### 11.4 Approver service levels

Document review cadence (Section 7) governs *content freshness*. This governs
*reviewer responsiveness* — the thing that actually kills federated models.

| Event | Target |
|---|---|
| Content PR reviewed by owning team | 2 business days |
| `validation-rules` co-review (Dev + QA) | 3 business days |
| `_governance/` standard change | 5 business days |
| Arbitration decision (Section 5.2) | 5 business days from escalation |

Breach escalates to the domain's Accountable party in Section 5. A PR blocked
purely on reviewer availability for more than 10 business days may be merged by
the AKL Steward with a follow-up review issue — because a contribution path
that stalls is worse than one that occasionally admits an imperfect document.

### 11.5 Audit evidence

The layer is positioned as an auditable AI-governance artifact (Section 12.1).
The evidence it produces must therefore be stated, not assumed:

| Question an auditor asks | Where the evidence is |
|---|---|
| Who approved this rule, and when? | Git history + PR approval record |
| What did it say at the time of the incident? | Git history at commit/tag |
| Which content is AI-proposed vs. human-authored? | `authored_by` frontmatter |
| What was excluded from AI context, and why? | `status`, `sensitivity` fields + Section 6 checks |
| Which non-compliance is known and accepted? | `_governance/WAIVERS.md` |
| Who owns this domain today? | `OWNERS.md` |

**Retention:** repository history is the record. Confirm in Phase 0 that the
retention period on the git host meets the organisation's evidentiary
requirement, and that history is not squashed in a way that destroys approval
attribution.

### 11.6 Alignment to existing AI governance

The AKL is an AI-adjacent system and is subject to the organisation's existing
AI governance process, not an alternative to it. Phase 0 must record:

- Whether the AKL itself requires governance intake, and if so, its outcome.
- Which existing gate or control it satisfies, partially satisfies, or is
  independent of — stated explicitly rather than implied.
- Whether it introduces any new control obligation (most likely around
  Section 10 data residency and `restricted` content handling).

Presenting the AKL as a governance artifact without stating its own position
relative to the existing process is the fastest way to lose a review.

### 11.7 Retiring what it replaces

If the wiki and ADO pages continue to carry the same facts, the layer has
*added* a source of truth rather than consolidated one — recreating the exact
problem it exists to solve.

For every domain seeded in the pilot, Phase 3 must record: what moves into the
AKL, what remains where it is and why, and what is archived. Superseded wiki
pages are replaced with a pointer to the governing document ID, not deleted
silently and not left in place.

### 11.8 Consumption paths by audience

Six audiences are named in Section 3 of the enterprise document; two of them —
BA and manual QA — are domain owners under Section 5 and do not work in VS Code.
If reading a business rule requires navigating repository folders, those teams
disengage regardless of governance quality, and ownership becomes nominal.

| Audience | Path | Status |
|---|---|---|
| Developers | Scoped Copilot instructions, in-editor | Defined (Section 8) |
| QA Automation | Programmatic read from the repo | Defined |
| BA, Manual QA, Tech Management | **Rendered, browsable documentation site** | **Open — decide in Phase 0** |

Options to evaluate: a static site generator publishing on merge (the
mechanism underneath Spotify TechDocs), or synchronisation into the existing
enterprise wiki as a read-only mirror. The mirror must be unambiguously
read-only; a two-way sync reintroduces dual-source drift.

### 11.9 Enablement

Teams are being asked to author in a format none of them have used.

- A worked reference example per domain, in `_governance/schema-templates/`,
  showing a complete good document rather than a skeleton.
- A single onboarding page: how to add a document, how to get it approved, who
  to ask.
- The `create-knowledge-doc` scaffolder (open decision) materially raises
  conformance; the alternative is six local interpretations of one standard.
- The role prompt playbook is the adoption artifact for non-authors — it is
  what makes the layer visibly useful to someone who never writes a document.

### 11.10 Indicative cost

Rough order of magnitude, for sponsor conversations. Refine after Phase 0.

| Phase | Indicative effort |
|---|---|
| 0. Decide | 1–2 weeks elapsed, small group, low effort |
| 1. Foundation (structure, CI validation) | ~1 week engineering |
| 2. Generators | 1–2 weeks engineering |
| 3. Authored domains (pilot area) | ~2–4 days per owning team |
| 4. Validation + arbitration | ~2 days Dev + QA |
| 5. Copilot wiring | ~1 week engineering |
| 6. Evaluate | ~1 week, plus reviewer time for ~20 tasks |
| **Steady state per team** | **Target under 2 hours per sprint** — measured as a metric in Section 10, not assumed |

The steady-state figure is the number that determines whether this survives.
It is deliberately a measured metric rather than an estimate.

### 11.11 Exit criteria

Phase 5 has pass/fail criteria (Section 13). Phase 6 must have them too, or
the evaluation becomes a formality that momentum wins.

**Continue to scale-out** when: agent output quality improves measurably
against the no-AKL baseline; coverage in the pilot area exceeds 70%; and
steady-state authoring cost is under the target above.

**Stop, or reduce scope, when:** no measurable output improvement; or
steady-state authoring cost exceeds roughly 4 hours per team per sprint; or
coverage stalls below 40% despite the phase completing.

**If stopped:** derived domains are retained regardless — they are near-zero
cost and independently useful. Authored domains are either narrowed to the
highest-value subset (typically `business-rules` and `anti-patterns`) or
archived with a pointer from the wiki. The exit is a scope reduction, not a
deletion.

Pre-committing to these thresholds before the data exists is what makes the
evaluation credible, and is the protection against sunk-cost reasoning.

---

## 12. Precedent & Industry Validation

**Nothing in this design is unproven except the combination.** Each load-bearing
decision maps to an established practice with independent evidence at
enterprise scale. This section exists so reviewers can check the design against
prior art rather than take it on faith.

### 12.1 Docs-as-code in the repo — Spotify Backstage / TechDocs

The closest large-scale analogue to this entire proposal. Spotify's engineers
write technical documentation in Markdown that lives with the code; CI builds
the doc site, and metadata such as owner is layered on top — the same shape as
our frontmatter and `akl-generate` pipeline.

- TechDocs runs 5,000+ documentation sites with ~10,000 average daily hits.
- It is Spotify's most-used Backstage plugin at ~20% of all traffic despite
  being one of 130+ plugins — which Spotify attributes directly to the
  docs-like-code approach making docs something people actually use.
- Backstage has 3,400+ adopting companies including American Airlines,
  Expedia, LinkedIn, HP, Siemens, Vodafone, Mercedes-Benz, IKEA and CVS Health.
  Expedia rolled it out to 5,000+ developers across 15+ brands and ~20,000
  microservices.
- Google runs the same pattern internally via its "g3doc" tool, which locates
  documentation next to the source code.

**Counter-evidence we are deliberately hedging against:** Backstage rollouts at
enterprise scale have a known reputation for becoming 6–12 month efforts. Our
bounded single-feature pilot (Phase 0–6) is the direct response. We are not
proposing a platform programme.

### 12.2 Derived-not-authored — API/spec governance

The Section 2 decision to generate rather than hand-write schema and contract
docs is the best-evidenced choice in this design:

- Roughly **75% of production APIs do not match their specs**, causing security
  audit failures and broken integrations.
- Industry guidance frames the remedy exactly as we have: the fix is not better
  documentation discipline, it is eliminating the gap where drift happens —
  governance enforced at the spec level means documentation cannot drift,
  because it rebuilds from the same contract CI validates.
- The OpenAPI Initiative recommends a single source of truth and warns against
  duplicating API information in multiple places, with CI verification that
  code and spec agree. Our `<!-- GENERATED -->` markers plus the
  generated-block integrity check implement precisely that.

### 12.3 Agent context files — now a formal open standard

The AI-facing half of this design is not speculative:

- **AGENTS.md** was formalised as an open specification in August 2025 (led by
  OpenAI, with Google, Cursor and Factory), donated to the Linux Foundation's
  Agentic AI Foundation in December 2025, and by December 2025 had 60,000+
  open-source projects adopting it across 20+ supporting tools.
- **Scoped over monolithic context is the documented best practice:** large
  repositories require scoped context because a single root file cannot encode
  module-specific constraints without becoming noisy; hierarchical files let
  context scale from general to specific. This validates our `applyTo` design
  (Section 8).
- **Staleness harms agents more than humans:** stale docs merely annoy humans,
  who carry enough skepticism to discount them, but agents read documentation
  on every request, so stale information actively poisons context. This is the
  strongest available justification for churn-based staleness (Section 7.2).
- Peer-reviewed work now describes agent context files as persistent long-term
  memory that spares developers from re-explaining rules, with version control
  helping the agent stay consistent as the codebase evolves. A study of 466
  projects found **no established content structure yet** and wide variation in
  how context is provided — the governed structure proposed here is precisely
  what most adopters currently lack.

### 12.4 Federated governance — proven in the data domain

Our model is federated computational governance (from data mesh) applied to
application knowledge. Global governance ensures interoperability and enforces
organisation-wide standards while sovereign domains govern their own products —
with the centralisation/decentralisation balance being the acknowledged
challenge, which Section 5 addresses by restricting governance review to
`_governance/` only. The "computational" half validates Section 6: federated
computational governance implements governance, security, compliance and
quality *as code* — declarative policies and scripts — ensuring consistency and
automating routine compliance checks rather than relying on manual audit.

### 12.5 Architecture Decision Records — the most settled practice here

Thoughtworks placed Lightweight ADRs in the **Adopt** ring, specifically
recommending source control over a wiki so the record stays in sync with the
code, and stating they see no reason most projects would not use the technique.
Practitioner guidance goes further: where the records live is the single
biggest determinant of whether the practice survives, and they should sit in the
same repository as the code in a stable directory. Our `/knowledge/decisions/`
placement follows this directly.

### 12.6 What is genuinely novel

| Component | Status |
|---|---|
| Docs-as-code, owner metadata, PR review | Proven — Spotify, Google, 3,400+ companies |
| Spec/migrations as generated source of truth | Standard API governance practice |
| Federated computational governance | Proven in data mesh at enterprise scale |
| ADRs in source control | Thoughtworks "Adopt" |
| Agent context files, scoped hierarchically | Linux Foundation standard, 60,000+ adopters |
| **Unifying all of the above into one governed layer serving humans *and* agents** | **Novel — this is what Phase 6 evaluates** |

The ask is therefore not faith in an unproven idea. It is a bounded pilot to
test whether a set of individually proven practices composes well in our
environment.

---

## 13. Rollout

| Phase | Owner | Scope | Depends on |
|---|---|---|---|
| **0. Decide** | Tech Mgmt + Architecture | ID namespacing (4.2), security posture + classification mapping (9), arbitration path (5.2), eval definition and baseline (10), named steward (11.1), AI-governance alignment (11.6), consumption path (11.8) | — |
| **1. Foundation** | BA + Dev | `/knowledge/` structure, `_governance/`, CODEOWNERS, **`akl-validate` CI** | Phase 0 |
| **2. Generators** | Backend Dev | `akl-generate` for db-schema + api-contracts; verify round-trip on real migrations | Phase 1 |
| **3. Authored domains** | BA, Frontend, Architecture | business-rules, workflows, pages, elements, NFRs, glossary for the pilot area | Phase 1 (parallel with 2) |
| **4. Validation + arbitration** | Dev + QA | validation-rules; exercise the co-review and arbitration path deliberately | Phases 2–3 |
| **5. Copilot wiring** | Dev | Scoped instructions derived from `tracks:`; staleness workflow live | Phases 1–4 |
| **6. Evaluate** | Tech Mgmt | Run the Section 10 eval; decide on scale-out with data | Phase 5 |
| **7. Scale out** | All teams | Additional feature areas / second application | Phase 6 |

**Phase 0 is new and non-negotiable.** Each of its four decisions is either
irreversible (ID namespacing), a sponsor blocker (security), a week-two
deadlock (arbitration), or unmeasurable-in-hindsight (eval baseline).

**Phase 2 is new** and is the difference between a durable system and a
decaying one — build the generators before asking anyone to hand-write a
schema doc they'll never update.

**Pass/fail for Phase 5** (v1.0 left this a vibe check). For 10 sampled files
across the pilot area, all four must hold:

1. Copilot surfaces the correct governed document without prompting in ≥8 cases.
2. No `draft` or `restricted` content is surfaced in any case (precision floor).
3. No more than 2 irrelevant documents surface per case — over-retrieval fails
   the phase just as under-retrieval does.
4. AKL content consumes ≤15% of the context budget (Section 8.5).

**Cold start is the adoption risk in this phase.** The layer delivers least
value exactly when adoption is being asked for: an empty or thin `/knowledge/`
gives agents nothing, developers conclude "this changed nothing," and that
first impression is difficult to reverse — this is a documented cause of
stalled Backstage rollouts (Section 12.1). Two mitigations are built into the
plan: Phases 3–4 seed the pilot area to meaningful density *before* Copilot is
wired in Phase 5; and the pilot area should be chosen where the team currently
feels the pain of undocumented rules, not the cleanest or best-understood
module.

---

## 14. Future-Proofing

Everything is plain Markdown + YAML in git. That is a deliberate bet: whatever
AI tooling looks like in two years, the source of truth doesn't migrate — only
the read path changes.

| Path | Status | Scale trigger |
|---|---|---|
| VS Code / Copilot instructions | Shipping now | — |
| MCP server (structured queries) | Additive | >300 docs **or** >2 repos — glob maintenance and cross-repo linking both break down around there |
| RAG / vector retrieval | Additive | When natural-language lookup over the corpus becomes a stated need |
| Other enterprise agents (Copilot Studio etc.) | Additive | When a non-VS-Code agent needs the same grounding |

Naming the trigger matters more than naming the option — v1.0 listed these as
vague possibilities, which means nobody ever decides it's time.

---

## 15. Remaining Open Decisions

1. Pilot feature area — enough business-rule complexity to stress the model,
   bounded enough to validate in one cycle, and an area where the team already
   asks each other questions about intended behaviour (see cold start,
   Section 13).
2. Whether `decisions/` (ADRs) migrates existing ADRs or starts fresh.
3. Generator implementation choice for `api-contracts` — spec-first (OpenAPI
   is source) vs. code-first (annotations generate the spec). Affects who owns
   the contract in practice.
4. Whether to build a `create-knowledge-doc` scaffolder in Phase 1. Spotify
   pairs its catalog and docs with Software Templates that standardise tooling
   to preferred practices; a scaffolder would materially raise conformance
   versus asking contributors to copy a template by hand.

---

## Appendix A — Candidate Domains & Selection Criteria

The eleven domains in Section 3 are the committed set. This appendix records
the wider candidate list, the classification of each, and the test used to
decide what earns a place. It exists so that future additions are argued
against a standard rather than added by enthusiasm.

### A.1 The selection test

Apply both, in order:

1. **Agent uplift test.** Would an agent produce *meaningfully worse output*
   without this domain? If the honest answer is "no, but it would be nice for
   humans," it belongs in the wiki or ADO — not in a layer whose maintenance
   cost is justified by agent grounding.
2. **Generation test.** Can it be derived from an existing machine-readable
   source? If yes, it is nearly free and should be added. If it must be
   hand-authored *and* changes weekly, be sceptical.

**The failure mode this guards against:** a knowledge layer with twenty domains
that is 60% stale is worse than one with eight domains that is trustworthy —
because agents cannot tell the difference, and neither can the teams relying on
them.

### A.2 Tier 1 — high agent uplift, add next

| Domain | Type | Rationale |
|---|---|---|
| `entity-lifecycle` | Authored | Valid states and transitions for core objects (order, claim, refund). Agents routinely invent illegal transitions. The highest-value gap in the current set. |
| `calculations` | Authored | Tax, discount, pricing, interest, proration. Business rules state *when*; this states *how*, precisely. Highly error-prone for an agent to infer from code. |
| `permissions` | Hybrid | Roles and what each may do per resource. Agents guess at authorization checks constantly. Derive the role list from config; author the intent. |
| `error-catalog` | Hybrid | Error codes, meanings, user-facing messages, retry semantics. Prevents invented error codes and inconsistent handling. |
| `events` | Derived | Topics, message schemas, publishers and subscribers (AsyncAPI). `api-contracts` covers synchronous interfaces only; this is the matching asynchronous gap. |
| `anti-patterns` | Authored | Deliberate divergences from common practice. Models reproduce statistically common patterns, so intentional deviations need explicit defense. |

`anti-patterns` deserves particular emphasis: it is cheap to write and
disproportionately effective. A single line — "we do not use the ORM's cascade
delete here, see [[DEC-004]]" — prevents an entire class of confidently-wrong
refactors.

**Recommended for the pilot itself:** `entity-lifecycle` and `anti-patterns`.
Both are small, high-signal, and should show up clearly in the Section 10 eval
metrics. The remaining Tier 1 domains wait for Phase 7, so the eval data can
indicate which domains actually moved the numbers.

### A.3 Tier 2 — valuable, situational

| Domain | Type | Adopt when |
|---|---|---|
| `configuration` | Derived | Feature-flag count is non-trivial and agents need to know what is toggleable |
| `scheduled-jobs` | Hybrid | There is meaningful background or batch processing |
| `notifications` | Hybrid | Customer communications are a real surface (email, SMS) |
| `data-lifecycle` | Authored | Retention, archival, PII classification — compliance-adjacent, likely mandatory here |
| `observability` | Authored | Ops maturity warrants splitting SLOs and runbooks out of `non-functional` |
| `metrics` | Authored | Metric definitions are contested (e.g. what counts as an active user) |
| `localization` | Authored | Multi-region: currency, timezone, date format, units |
| `test-strategy` | Authored | Feeds the QA automation roadmap directly |
| `migration-state` | Authored | Mid-refactor: "this pattern is being replaced, do not extend it" |

### A.4 Tier 3 — deliberately excluded

| Candidate | Why not |
|---|---|
| User personas / journeys | Valuable to product, rarely changes agent output |
| Coding standards | Belongs in linters and `copilot-instructions.md` |
| Sequence diagrams | High maintenance, low agent uplift; `workflows` already carries the semantics |
| Tech debt register | A backlog, not knowledge — keep in ADO |
| File / folder structure | Actively harmful: paths change and mislead agents (see Section 4.1) |
| Caching strategy | Usually a paragraph in an ADR, not a domain |

### A.5 Adding a domain later

Any new domain requires: a passing result on both A.1 tests; a named owning
team and fallback owner in `OWNERS.md`; a template in
`_governance/schema-templates/`; a CODEOWNERS entry; and — if derived or
hybrid — a generator before any content is authored by hand.

---

## Appendix B — Authored domain template

```markdown
---
id: <APP>-<DOMAIN>-<NNN>
domain: <business-rules|workflows|validation-rules|non-functional|glossary|decisions>
title: <short descriptive title>
owner_team: <ba|frontend|backend|qa|architecture>
status: draft
sensitivity: internal
last_reviewed: <YYYY-MM-DD>
tracks:
  - <code path glob this describes>
related:
  - <related-doc-id>
superseded_by: null
authored_by: human        # human | agent (see 8.4)
---

## Description
<plain-language explanation of the behavior>

## Constraints
<what an implementer or AI agent must not violate>

## Rationale
<why it works this way — prevents "helpful" refactors that undo deliberate choices>
```

## Appendix C — Derived domain template

```markdown
---
id: <APP>-DB-<table>
domain: db-schema
generated_from: migrations/
generator_version: 1.0
status: approved
sensitivity: internal
---

<!-- GENERATED:START — do not edit by hand -->
<!-- generator output -->
<!-- GENERATED:END -->

## Intent
<the only human-maintained section: why these constraints exist>
```

## Appendix D — Glossary

| Term | Meaning |
|---|---|
| AKL | Application Knowledge Layer |
| Derived domain | Generated from code; never hand-authored |
| Authored domain | Human-written; the AKL doc is the source of truth |
| Hybrid domain | Inventory generated, behavior contract authored |
| `tracks:` | Code paths a doc describes; powers churn-based staleness |
| Churn-based staleness | Drift detected by code commits, not calendar dates |
| CODEOWNERS | GitHub mechanism requiring a team's approval on given paths |
| `applyTo` | Glob field scoping an instructions file to specific paths |
| Precedence order | Ranking that decides which document wins when two conflict (8.3) |
| Write-back | An agent proposing a draft doc via PR to close a coverage gap (8.4) |
| Coverage | % of code matched by some doc's `tracks:` glob |
| Retrieval precision | Irrelevant docs surfaced alongside correct ones |
