# AI-Led STLC — Build Inventory
### Custom Agents, Skills, Instructions & Prompts Required

Counted from the technical design's component lists. This is a planning inventory, not a fixed spec — some items can be merged or split as your team sees fit during build; the reuse notes flag where that's worth doing.

---

## Phase 1 — Execution & Reporting AI
| Type | Name | Purpose |
|---|---|---|
| Agent | `report-cycle-orchestrator` | Runs parse → classify → summarize → ledger-update → healer trigger |
| Skill | `allure-parse` | Extract structured data from Allure output |
| Skill | `failure-classify` | Categorize failures (product bug/flaky/environment/etc.) |
| Skill | `report-summarize` | Draft the manager-facing narrative report |
| Skill | `ledger-update` | Append/update the failure ledger |
| Skill | `healer` | Propose locator fixes for stale-locator failures |
| Instructions | `classification-and-report-style` | Taxonomy definitions, report tone/format |
| Prompt | `report-cycle.prompt` | Entry point: "here's the report path, run it" |

**Subtotal: 1 agent, 5 skills, 1 instructions file, 1 prompt**

## Phase 2 — API Script Generation
| Type | Name | Purpose |
|---|---|---|
| Agent | `api-test-cycle-orchestrator` | Runs plan → explore → script → test |
| Skill | `spec-parse` | Extract endpoints/schemas from OpenAPI spec |
| Skill | `api-explore` | Validate spec against live/sandbox behavior |
| Skill | `test-data-generate` | Produce happy-path + negative data sets |
| Skill | `api-script-generate` | Generate the Node.js test script |
| Instructions | `api-testing-conventions` | Negative-case taxonomy, coding style, Allure integration |
| Prompt | `api-test-cycle.prompt` | Entry point: "here's the spec, run it" |

**Subtotal: 1 agent, 4 skills, 1 instructions file, 1 prompt**

## Phase 3 — ADO Defect Drafting
| Type | Name | Purpose |
|---|---|---|
| Agent | `defect-drafting-orchestrator` | Runs context-gather → duplicate-check → draft-bug → human gate → file |
| Skill | `context-gather` | Assemble logs, screenshots, build/commit info |
| Skill | `duplicate-check` | Query ADO for matching open bugs |
| Skill | `draft-bug` | Compose the structured ADO work item |
| Instructions | `bug-report-quality-bar` | Required fields, severity taxonomy, repro-step standard |
| Prompt | `review-and-file.prompt` | Entry point for reviewing/approving a draft |

**Subtotal: 1 agent, 3 skills, 1 instructions file, 1 prompt**

## Phase 4 — Test Case Design (Copilot Studio)
| Type | Name | Purpose |
|---|---|---|
| Agent | `test-case-design-agent` (Copilot Studio) | Orchestrates the three topics below |
| Skill/Topic | `requirement-fetch` | Pull work item + acceptance criteria |
| Skill/Topic | `ambiguity-check` | Flag untestable acceptance criteria |
| Skill/Topic | `case-generate` | Draft positive/negative/edge cases per criterion |
| Instructions/Knowledge source | `test-case-format-standards` | Case format, taxonomy (reuses Phase 2's), DoR bar |
| Prompt/Trigger | `"Generate test cases for [work item]"` | Conversational entry point |

**Subtotal: 1 agent, 3 skills, 1 instructions file, 1 prompt**

## Phase 5 — Requirement Analysis & Test Planning
| Type | Name | Purpose |
|---|---|---|
| Agent | `requirement-analysis-agent` | Runs dor-check + completeness-gap at refinement |
| Agent | `test-planning-agent` | Runs defect-history-analyze + complexity-signal + plan-draft at release boundary |
| Skill | `dor-check` | Validate story against Definition of Ready |
| Skill | `completeness-gap` | Flag missing (not just wrong) requirement content |
| Skill | `defect-history-analyze` | Query ADO bug history for risk signals |
| Skill | `complexity-signal` | Pull code-churn/dependency risk indicators |
| Skill | `plan-draft` | Compose the risk-tiered test plan with rationale |
| Instructions | `dor-and-scope-tiering` | DoR criteria, scope-tier definitions, plan format |
| Prompt | `test-planning-cycle.prompt` | Entry point at release/feature boundary |

**Subtotal: 2 agents, 5 skills, 1 instructions file, 1 prompt**

## Phase 6 — Regression Optimization
| Type | Name | Purpose |
|---|---|---|
| Agent | `regression-optimization-orchestrator` | Runs change-impact → risk-score → subset-recommend |
| Skill | `change-impact` | Map code/requirement diff to affected test areas |
| Skill | `risk-score` | Combine change-impact with historical ledger/defect signals |
| Skill | `subset-recommend` | Produce the tiered regression set with rationale |
| Instructions | `regression-tiering-policy` | Thresholds, full-regression cadence, uncertainty-defaults-up rule |
| Prompt | `regression-scope.prompt` | Entry point on a release/build candidate |

**Subtotal: 1 agent, 3 skills, 1 instructions file, 1 prompt**

---

## Total Count

| Type | Count |
|---|---|
| Agents | 7 |
| Skills | 23 |
| Instructions | 6 |
| Prompts | 6 |
| **Total primitives** | **42** |

## Consolidation Opportunities

Before your team builds all 42 as separate files, a few are natural candidates to merge or share rather than duplicate:

- **Negative-case taxonomy** — Phase 2's `api-testing-conventions` and Phase 4's `test-case-format-standards` both reference the same underlying positive/negative/edge taxonomy. Define it once as a shared instructions file, referenced by both, instead of duplicating the definition.
- **DoR criteria** — Phase 4's `ambiguity-check` and Phase 5's `dor-check`/`completeness-gap` both need Definition-of-Ready criteria. One canonical DoR document, referenced by both phases, avoids drift between "what Phase 4 checks" and "what Phase 5 checks."
- **Report/plan formatting conventions** — Phase 1's report style, Phase 5's plan format, and Phase 6's regression-scope rationale format could share a single "AI-drafted artifact style guide" instructions file rather than three separate ones, if your team wants consistent tone across every AI-generated document reaching a human reader.

Realistic net-new instruction files after consolidation: **around 3-4**, not 6 — worth deciding this before build starts, since instructions files are the cheapest place to consolidate without touching skill logic.

## Not Counted Here (Already Existing)
Your team's pre-existing agentic workflow — the UI/Cypress agent, `cypress-code-review` skill, and the eval-harness tooling itself — isn't part of this count. Those are foundation the six phases build on top of, not new phase deliverables.
