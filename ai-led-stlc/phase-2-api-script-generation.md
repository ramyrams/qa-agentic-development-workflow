# Phase 2 Deep Dive: Script Generation Expansion (API Testing)
### AI-Led STLC — Blueprint Phase 2 of 6

Phase 2 extends the agentic **plan → explore → script → test** pattern your team already uses for UI (Cypress) testing to API testing, driven off a Swagger/OpenAPI spec. Still no ADO writes, still dev-side only — this is why it's sequenced before Phase 3.

---

## 2.1 Goal
Given an OpenAPI/Swagger spec, the agent produces: happy-path + negative test data per endpoint, the corresponding test script, and an execution/reporting path that feeds the same failure ledger and healer built in Phase 1.

## 2.2 Workflow (end to end)
1. Input: Swagger/OpenAPI spec (file or URL) for the service under test
2. **Plan phase** — agent parses the spec, enumerates endpoints, methods, required/optional params, response schemas, and auth requirements; produces a test plan (which endpoints, which scenarios) for human review before any code is written
3. **Explore phase** — agent hits the live/sandbox API (or a mocked version) to validate actual behavior against the spec — specs drift from reality more often than teams expect, so this step catches that early
4. **Script phase** — agent generates the test script (Node.js, matching your existing stack) using the validated understanding from explore
5. **Test phase** — agent runs the generated script, captures results in the same Allure output your Phase 1 pipeline already consumes
6. Human review gate: engineer reviews generated scripts before merge — same PR process as any human-written code, no special bypass

## 2.3 Test Data Design — Per Endpoint
This is the part most teams under-scope. For each endpoint:

| Category | Examples |
|---|---|
| Happy path | Valid required fields, valid optional fields, boundary-valid values |
| Negative — missing/invalid | Missing required field, wrong data type, malformed payload |
| Negative — auth | Missing token, expired token, insufficient permissions |
| Negative — boundary | Min/max length, numeric overflow, empty string vs. null |
| Contract drift | Response schema doesn't match spec (caught in explore phase, flagged even if the API "works") |

Design point: the negative-case taxonomy above should live in an **instructions** file so it's consistent across every endpoint the agent processes, not re-derived ad hoc each time.

## 2.4 GitHub Copilot Primitives Needed
| Primitive | Purpose |
|---|---|
| **Skill: spec-parse** | Extract endpoints/schemas/auth requirements from Swagger/OpenAPI |
| **Skill: api-explore** | Validate spec against live/sandbox behavior, flag drift |
| **Skill: test-data-generate** | Produce happy-path + negative data sets per the taxonomy in 2.3 |
| **Skill: api-script-generate** | Produce the Node.js test script from validated plan + data |
| **Instructions** | Negative-case taxonomy, coding/style conventions matching existing Cypress framework conventions, Allure integration requirements |
| **Prompt file** | Entry point: "here's the spec, run the pipeline" |
| **Agent** | Orchestrates plan → explore → script → test as one workflow |

Note this is a close structural mirror of your UI testing agent — same four-primitive shape, different skills underneath. Worth reusing naming/folder conventions from the UI framework so the team doesn't have to learn a new mental model.

## 2.5 Eval Requirements
- **spec-parse**: eval against specs of varying complexity (nested schemas, oneOf/anyOf, auth schemes) — check extraction completeness, not just "did it run without erroring"
- **api-explore**: eval on specs with known, deliberately-injected drift (e.g., a field marked required in spec but actually optional in the live API) — does it catch it?
- **test-data-generate**: eval against the negative-case taxonomy — does every endpoint get full coverage of the categories in 2.3, or does it silently skip some?
- **api-script-generate**: eval on generated scripts — do they execute without syntax errors, do they correctly assert against expected status/schema, do they integrate with Allure correctly?
- Composite/agent-level eval: full plan→explore→script→test run on 2-3 real internal APIs, graded end to end, not just per-skill

## 2.6 Design Points Worth Deciding Up Front
- **Sandbox vs. live for explore phase**: hitting live APIs during automated exploration has blast-radius risk (rate limits, data pollution, write-endpoint side effects). Decide per-service whether explore runs against a sandbox/mock or requires human approval before hitting live.
- **Write endpoints (POST/PUT/DELETE) get extra scrutiny**: explore phase auto-invoking a write endpoint can create real data or side effects. Recommend read-only auto-explore by default, explicit opt-in for write-endpoint exploration per service.
- **Spec staleness ownership**: when explore phase catches drift, who owns updating the spec vs. filing it as a defect? Define this now — it's a recurring ambiguity, not a one-off.
- **Reuse of Phase 1 infrastructure**: results should route into the *same* failure ledger and healer agent from Phase 1, not a parallel API-specific version — otherwise you fragment your data and double the maintenance surface.

## 2.7 Governance/Risk Notes
- Higher risk than Phase 1 because explore phase makes live API calls, and script phase commits code — both need human gates
- If APIs handle sensitive data (PII, financial), confirm test data generation doesn't produce/log anything resembling real sensitive values, even synthetically
- Auth handling in generated scripts (tokens, credentials) needs a secrets-management review before this goes to any shared/CI environment — don't let the agent hardcode anything

## 2.8 Rollout Steps
1. Build spec-parse + eval, validate on 2-3 real internal API specs of varying complexity
2. Build api-explore + eval in **read-only mode only** first
3. Build test-data-generate + eval against the taxonomy
4. Build api-script-generate + eval, confirm Allure/ledger integration matches Phase 1 pipeline
5. Pilot full agent on one low-risk, read-heavy internal API end to end
6. Expand to write-endpoint exploration (with explicit human approval step) only after read-only pilot is trusted
7. Roll out to automation engineering team broadly

---

## Phase 2 — Definition of Done
- Agent produces a full plan → explore → script → test cycle for at least one real API, human-reviewed and merged
- All four skills have passing eval suites per standing policy
- Results flow into the same Phase 1 failure ledger and are eligible for Phase 1 healer coverage
- Read-only vs. write-endpoint exploration policy documented and enforced

## Transition Criteria to Phase 3
Move to Phase 3 (ADO defect drafting) once:
- Script generation quality is trusted enough that engineers spend more time reviewing than rewriting
- Failure ledger has meaningful API-testing data alongside UI-testing data
- You've had the ADO governance conversation (data boundary, connector approval) in parallel, since Phase 3 is the first workstream to write into ADO
