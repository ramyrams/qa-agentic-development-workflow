# AI-Led STLC — Technical Design Document
### Implementation Architecture for Phases 1–6

This document specifies how each phase gets built: component breakdown, data contracts, integration points, and algorithms. It assumes the reader is implementing against the existing stack — GitHub Copilot `.github` primitives, Copilot Studio, MS ADO, Cypress/Playwright/Node.js, Allure.

---

## 0. Shared Technical Foundations

Everything in Phases 1–6 is built on four shared pieces. Build these first — every phase depends on at least one.

### 0.1 Repository Layout Convention
```
.github/
  agents/
    <phase>-<agent-name>/agent.md
  skills/
    <skill-name>/
      SKILL.md
      eval/
        evals.json
        grading.json
        benchmark.json
  instructions/
    <domain>.instructions.md
  prompts/
    <entry-point>.prompt.md
ledgers/
  failure-ledger.jsonl
  case-quality-ledger.jsonl
```
Keep skill folder names stable once in production — the eval harness and any cross-skill references key off the folder name.

### 0.2 Standard Skill I/O Envelope
Every skill in this initiative returns the same envelope shape, regardless of what it does. This is what makes composite agent orchestration and eval grading consistent across 20+ skills instead of bespoke per skill.

```json
{
  "skill": "failure-classify",
  "version": "1.2.0",
  "input_ref": "<hash or ID of the input processed>",
  "output": { },
  "confidence": 0.0,
  "rationale": "one or two sentences explaining the output",
  "requires_human_review": true,
  "metadata": { "timestamp": "ISO8601", "model": "...", "run_id": "..." }
}
```
`requires_human_review` defaults to `true` for every skill that writes anywhere outside a scratch/staging area. No skill sets this to `false` for itself — it's a policy flag set at the agent/orchestration layer, not something a skill can self-certify.

### 0.3 Failure Ledger — Schema
```json
{
  "test_id": "string",
  "error_signature": "normalized hash string",
  "raw_error_sample": "string, truncated",
  "category": "product_bug | flaky | environment | test_data | stale_locator",
  "confidence": 0.0,
  "first_seen": "ISO8601",
  "last_seen": "ISO8601",
  "occurrence_count": 0,
  "resolution_status": "open | healed | filed | dismissed",
  "linked_ado_bug_id": "string | null",
  "source_phase": "1 | 2"
}
```
**Signature normalization algorithm**: strip timestamps, numeric IDs, UUIDs, and file line numbers from the raw error message via regex, then hash the result (e.g., SHA-256 truncated to 16 chars) for the lookup key. Store the normalization ruleset itself under version control — changing it invalidates historical matches, so treat it as a migration event, not a routine tweak.

Storage: JSONL file in Phase 1, or a lightweight document store (e.g., SQLite/Postgres table) once query volume from Phase 5/6 justifies it — don't over-build this at Phase 1.

### 0.4 ADO Connector — Interface Contract
Regardless of whether you use the Azure DevOps MCP server or a direct REST wrapper, define one internal interface every skill codes against, so swapping the underlying connector later doesn't touch skill code:

```
ado.getWorkItem(id) -> WorkItem
ado.queryWorkItems(wiql) -> WorkItem[]
ado.createWorkItem(type, fields, tags) -> WorkItemId   // requires human-approved flag in payload
ado.updateWorkItem(id, fields) -> void
ado.linkWorkItems(sourceId, targetId, linkType) -> void
```
Every write call (`createWorkItem`, `updateWorkItem`, `linkWorkItems`) must include an `ai_assisted: true` tag/field and a `reviewed_by` field populated from the human approval step — this is what makes the traceability requirement enforceable rather than a policy on paper. Reject any write call at the connector layer that lacks `reviewed_by`.

**Auth**: service principal with write scope limited to the specific ADO project/area path used by this initiative — do not grant org-wide write scope. Confirm this scope with governance before Phase 3 build starts.

### 0.5 Eval Harness Pattern (per skill)
Reuse the existing agentskills.io-style pattern already in use for the eval harness:
- `evals.json` — labeled test cases (input → expected output)
- `with_skill` / `without_skill` comparison run
- `grading.json` — rubric for subjective outputs (e.g., report quality), pass/fail for objective ones (e.g., did it extract the right fields)
- `benchmark.json` — aggregate pass rate, tracked over time per skill version
- Re-run required on every skill version bump before deployment; CI gate blocks merge if eval pass rate drops below the skill's baseline

---

## Phase 1: Execution & Reporting AI

### 1.1 Components
`allure-parse` → `failure-classify` → `report-summarize` + `ledger-update` (parallel), and separately `healer` (triggered off `failure-classify` output where category = `stale_locator`).

### 1.2 Data Flow
```
Allure report (path/zip)
   → allure-parse: extract [test_id, status, duration, error, stack, tags, retries]
   → failure-classify: for each failure, normalize signature, lookup ledger,
       assign category + confidence (LLM classification + rule-based override
       for known signature matches)
   → [fan-out]
       → ledger-update: append/update ledger entry
       → report-summarize: aggregate all classified failures into narrative report
   → [if category == stale_locator]
       → healer: propose locator fix (see 1.4)
   → human review (staging file or PR-style diff)
   → on approval: report sent, ledger finalized, healer diff committed
```

### 1.3 `failure-classify` — Design
Hybrid approach, not pure LLM classification:
1. Normalize error signature (see 0.3)
2. Exact-match lookup against ledger — if signature seen before with resolved human classification, reuse that category at high confidence, no LLM call needed
3. If no match, LLM classifies using error message + stack trace + test metadata as context, against the five-category taxonomy
4. Confidence below a defined threshold (e.g., 0.6) → category set to `unclassified`, routed to manual review instead of guessed

### 1.4 `healer` — Design
1. Input: failed test's locator + a DOM snapshot (captured at failure time by Cypress/Playwright, or re-captured via a headless run against the current app state)
2. Candidate matching: search current DOM for elements matching by (a) same text content, (b) same stable attributes (data-testid, aria-label — prioritize these over CSS class/position), (c) structural similarity to the original locator's position in the DOM tree
3. Score each candidate; if top candidate confidence exceeds threshold, propose it with rationale ("matched by data-testid, unchanged"); otherwise no proposal, flag for manual fix
4. Output: a diff (old locator → new locator) in the script file, not an auto-commit — written to a review branch/PR

### 1.5 Trigger Mechanism
Prompt file entry point (`report-cycle.prompt.md`) invoked manually or via a scheduled task (e.g., a weekly CI job that watches the shared Allure output folder and invokes the agent automatically, still landing in a human-reviewed staging state before anything ships).

### 1.6 Storage & Integration Points
- Ledger: `ledgers/failure-ledger.jsonl` (§0.3)
- Report output: markdown/HTML to a shared location (Teams channel post, email, or a docs page) — human approves before send
- Healer output: standard git branch + PR, reviewed like any code change

---

## Phase 2: API Script Generation

### 2.1 Components
`spec-parse` → `api-explore` → `test-data-generate` → `api-script-generate` → execution (reuses Phase 1's Allure/ledger pipeline).

### 2.2 `spec-parse` — Design
Use a standard OpenAPI parsing library (e.g., `swagger-parser` for Node.js) rather than hand-rolled parsing — specs are complex enough (refs, oneOf/anyOf, nested schemas) that reinventing this is wasted effort and a reliability risk. Output: a normalized internal model per endpoint:
```json
{
  "path": "/orders/{id}",
  "method": "GET",
  "params": [{"name": "id", "in": "path", "required": true, "type": "string"}],
  "request_schema": {},
  "response_schemas": {"200": {}, "404": {}},
  "auth": "bearer"
}
```

### 2.3 `api-explore` — Design
- **Read-only mode (default)**: only GET/HEAD requests auto-executed against a sandbox or live-but-safe environment
- **Write mode (opt-in per service)**: POST/PUT/DELETE requests require an explicit config flag per API and route through a human-approval step before the explore phase executes them
- Drift detection: compare actual response schema/status codes against the spec's declared schema; flag mismatches as `contract_drift` entries, separate from test failures
- Config: a per-service YAML (`api-config/<service>.yaml`) declaring base URL, auth method, write-mode flag, rate limits

### 2.4 `test-data-generate` — Design
Rule-driven generation against the taxonomy in the earlier blueprint (happy path, missing/invalid, auth, boundary, contract drift), parameterized by the endpoint's schema from `spec-parse`:
- For each required field: one valid value, one missing-value case, one wrong-type case
- For string fields with length constraints: one min-boundary, one max-boundary, one over-max
- For auth: one valid token case, one missing-token case, one expired/invalid-token case (mocked, not real expired credentials)
- Output: structured test data sets keyed by endpoint + scenario name, stored alongside the generated script

### 2.5 `api-script-generate` — Design
Template-based generation, not free-form code generation — use a fixed Node.js/Playwright-API-testing template with slots for endpoint, method, headers, body, and assertions, populated from the validated plan + generated data. Templating keeps output style consistent with the team's existing Cypress conventions and makes generated code easier to review than fully free-form LLM output.

### 2.6 Integration with Phase 1
Generated scripts execute through the same CI pipeline, write to the same Allure output, and failures flow through the same `failure-classify` → ledger pipeline — no parallel infrastructure.

---

## Phase 3: ADO Defect Drafting

### 3.1 Components
`context-gather` → `duplicate-check` → `draft-bug` → human review (staging) → `ado.createWorkItem`.

### 3.2 `context-gather` — Design
Assembles, per failure: logs (from Allure), screenshot/video (Cypress/Playwright native capture, referenced by path/URL — don't inline large binaries into the draft payload), stack trace, linked build/commit ID (from CI metadata), environment tag. Output is a structured bundle, not yet human-readable prose.

### 3.3 `duplicate-check` — Design
1. Compute the same normalized error signature used in the failure ledger (§0.3) — reuse, don't reimplement
2. Query ADO for open bug work items tagged `ai_assisted` or matching a stored signature field (requires adding a custom "error signature" field to your ADO bug template, or storing the mapping in the ledger and querying by linked test ID)
3. Return candidate duplicates ranked by signature match confidence — never auto-suppress, always surface candidates to the human reviewer with the match confidence shown

### 3.4 `draft-bug` — Design
- Repro steps generated by walking the actual test script's steps (parse the Cypress/Playwright command sequence), not paraphrased from the error message
- Severity: rule-based suggestion (e.g., core-flow test → higher severity, cosmetic-assertion test → lower) with an explicit "suggested, adjust as needed" framing in the field
- Field mapping: a config file (`ado-field-map.json`) mapping generic bug fields (title, repro, severity, evidence) to your org's actual ADO bug template fields, including any mandatory custom fields — this file is the thing to update if the ADO template changes, not the skill code

### 3.5 Human Review Staging
Recommend a lightweight review surface rather than building a custom UI: a draft file per candidate bug (markdown or a Teams adaptive card) posted to a review channel, with approve/edit/reject actions. On approve, the orchestrating agent calls `ado.createWorkItem` with `ai_assisted: true` and `reviewed_by: <approver>`.

### 3.6 Write Path
```
draft approved
  → ado.createWorkItem("Bug", fields, tags=["ai-assisted"])
  → ado.linkWorkItems(newBugId, sourceTestCaseId, "Tests")
  → ledger-update: failure ledger entry.resolution_status = "filed", linked_ado_bug_id = newBugId
```

---

## Phase 4: Test Case Design (Copilot Studio)

### 4.1 Components
`requirement-fetch` → `ambiguity-check` → `case-generate` → human review (per-case) → `ado` write to Test Plan.

### 4.2 Copilot Studio Mapping
| VS Code primitive | Copilot Studio equivalent |
|---|---|
| Skill | Topic, or a Power Automate flow called as a plugin action |
| Instructions | Agent's configured instructions + a knowledge source document |
| Prompt file | Trigger phrase / conversational starter |
| Standard I/O envelope (§0.2) | Same JSON shape, passed as the Power Automate flow's output, rendered into an adaptive card for the topic's response |

### 4.3 `requirement-fetch` — Design
`ado.getWorkItem(id)` pulls description, acceptance criteria field, and any linked attachments/docs. If acceptance criteria live in a non-standard field (common in enterprise ADO templates), the field-map config from §3.4 should be extended to cover this, not hardcoded per call.

### 4.4 `ambiguity-check` — Design
Rule + LLM hybrid:
1. Rule-based checks: acceptance criteria field non-empty, contains at least one measurable/testable statement (heuristic: presence of expected-value language), no direct contradictions between criteria (simple keyword-conflict heuristic as a first pass)
2. LLM check: given the full requirement text, assess testability and flag specific gaps (e.g., "no expected behavior specified for invalid input") — output structured as a list of named gaps, not a single pass/fail
3. Output feeds directly into `case-generate`'s prompt as known gaps to work around or explicitly exclude from generated coverage

### 4.5 `case-generate` — Design
One generation pass per acceptance criterion (not one pass for the whole story) — this keeps output traceable 1:1 back to source criteria and makes individual review tractable. For each criterion: one positive case minimum, negative/edge cases per the taxonomy from Phase 2 reused here for consistency. Each generated case includes a `source_criterion_id` field for traceability.

### 4.6 Write Path & Review UX
Cases are presented individually (adaptive card per case: title, steps, expected result, approve/edit/reject buttons) — bulk "approve all" should not exist as an available action in the Copilot Studio topic design; this is a UX constraint, not just a policy statement, so build it as such. On approval:
```
ado.createWorkItem("Test Case", fields, tags=["ai-assisted"])
ado.linkWorkItems(newCaseId, sourceRequirementId, "Tests")
```

---

## Phase 5: Requirement Analysis & Test Planning

### 5.1 Components
`dor-check` + `completeness-gap` (requirement analysis, runs at refinement) and `defect-history-analyze` + `complexity-signal` + `plan-draft` (test planning, runs at release/feature boundary).

### 5.2 `dor-check` / `completeness-gap` — Design
Extends Phase 4's `ambiguity-check` with an earlier trigger point (refinement, not "ready for test") and a "missing content" checklist derived from your org's documented Definition of Ready — if DoR isn't formally documented yet, that's a prerequisite deliverable before this skill can be built meaningfully (a checklist needs criteria to check against).

### 5.3 `defect-history-analyze` — Design
WIQL query against ADO for closed/active bugs, grouped by area path/component, over a rolling window (e.g., trailing 6 months):
```
defect_density(component) = bug_count(component) / story_count(component)
```
Combine with recency weighting (recent defects weighted higher than old ones) and severity weighting (a Sev1 counts more than a Sev4). **Sparse-data fallback**: if a component has fewer than N historical work items, return a `insufficient_history` flag instead of a density score, so downstream `plan-draft` doesn't treat silence as "low risk."

### 5.4 `complexity-signal` — Design
- Code churn: lines changed / commits touching the component's files over the same rolling window (via git log analysis)
- Dependency count: number of other components/services this one integrates with (from an existing architecture doc or a dependency manifest, if one exists — don't have the agent infer this from code alone without a source of truth)
- Combine into a normalized complexity score per component, same 0-1 scale as defect density for easy combination in `plan-draft`

### 5.5 `plan-draft` — Design
Weighted combination, transparent and tunable (not a black-box ML model, at least initially — a black box is much harder to defend in the human review step):
```
risk_score(component) = w1*defect_density + w2*complexity_score
                        + w3*flaky_rate(component)      // from failure ledger
                        + w4*case_quality_gap(component) // from case-quality ledger
```
Weights (`w1..w4`) live in a config file, tunable by the QA lead, not hardcoded — this is a policy lever, and leadership/QA-lead adjustment of these weights should be an explicit, visible action, not a code change. Output tiers components into full-coverage / smoke-only / out-of-scope, each with the contributing scores shown as rationale.

---

## Phase 6: Regression Optimization

### 6.1 Components
`change-impact` → `risk-score` (extends Phase 5's `plan-draft` scoring) → `subset-recommend`.

### 6.2 `change-impact` — Design
Map a code diff to affected test areas via one of, in order of preference:
1. An existing code-ownership/component-mapping file (e.g., CODEOWNERS extended with a test-area mapping) — best option if it exists
2. Static dependency graph analysis (which files import/reference the changed files) — more setup cost, more accurate for indirect impact
3. Tag-based mapping (tests tagged with the component/module they cover, changed files mapped to components via directory convention) — simplest to bootstrap, least precise for cross-cutting changes

Recommend starting with (3) for Phase 6's first pilot and evolving toward (1)/(2) as the org's tooling matures — don't block the pilot on building a full dependency graph first.

### 6.3 `risk-score` — Design
Reuses Phase 5's `plan-draft` scoring formula (§5.5), adding a per-cycle freshness factor: components touched by the current diff get a change-impact multiplier on top of their baseline historical risk score.

### 6.4 `subset-recommend` — Design
```
if risk_score(component) >= must_run_threshold: tier = "must_run"
elif risk_score(component) >= recommended_threshold: tier = "recommended"
elif insufficient_history OR no_prior_cycles_in_shadow_mode: tier = "must_run"  // uncertainty defaults up, not down
else: tier = "safe_to_skip"
```
Thresholds are config values, tuned during shadow mode (§6.5), not hardcoded at build time.

### 6.5 Shadow Mode — Implementation
Run `subset-recommend` in parallel with the full regression suite for N cycles without actually skipping anything. Log, per cycle: which tests were tiered `safe_to_skip`, and whether any of them subsequently failed in the full run. Store this comparison in a `shadow-mode-log.jsonl` — this log is the evidence base for the go/no-go decision on enabling live skipping, and should be reviewable by QA leadership directly, not just summarized.

### 6.6 Live Mode
Once enabled: pipeline runs `must_run` + `recommended` tiers by default; `safe_to_skip` tier is excluded from that cycle's run but the full suite still executes on the fixed cadence (§ governance safety net) regardless of live-mode status — this is a permanent parallel process, not a temporary rollout measure.

---

## Cross-Cutting: Security & Deployment Notes

- **Secrets**: API tokens, ADO service principal credentials, and any test auth tokens live in the CI/CD secrets store — never hardcoded in generated scripts or skill config files, and generated scripts should reference secrets by environment variable, never by literal value, enforced by a lint/review check.
- **Least privilege**: ADO service principal scoped to the specific project/area path in use; API-explore's live-call capability scoped per-service via the config in §2.3, not globally enabled.
- **Monitoring**: log every skill invocation (input ref, output, confidence, human-review outcome) to a central log, separate from the ledgers — this is your audit trail for "what did the AI do and what did a human decide," distinct from the ledgers' role as domain data stores.
- **Versioning**: every skill/agent has a semantic version; the eval harness gate (§0.5) blocks deployment of a version whose eval pass rate regresses versus its predecessor.
