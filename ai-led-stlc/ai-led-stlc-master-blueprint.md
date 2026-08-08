# AI-Led STLC — Master Blueprint
### Consolidated Reference: Overview + All Six Phases

---

## Table of Contents
1. Overview & Target Architecture
2. Phase 1 — Execution & Reporting AI
3. Phase 2 — Script Generation Expansion (API Testing)
4. Phase 3 — ADO Defect Drafting
5. Phase 4 — Test Case Design (Functional Tester Surface)
6. Phase 5 — Requirement Analysis & Test Planning
7. Phase 6 — Regression Optimization

---

# AI-Led STLC Blueprint
### For [Your Organization] — QA Function (Functional Testing + Automation Engineering)

**Context this blueprint assumes:**
- ALM/work management: Microsoft ADO (work items, test plans, pipelines)
- AI tooling: GitHub Copilot (licensed for the QA team)
- Existing automation stack: Cypress, Playwright, Node.js, VS Code
- Existing foundation: `.github` agentic customization (agents/skills/instructions/prompts), an eval harness for validating agent/skill quality, a competency ladder (User → Author → Architect), and an AI-initiative workflow catalog split by persona (functional vs. automation)
- Org scale: multi-billion-dollar enterprise — governance, auditability, and change management matter as much as the technology

This blueprint sequences that existing work into a full **Software Testing Life Cycle (STLC)** transformation, not just an automation-scripting upgrade.

---

## 1. Guiding Principle: AI at Every STLC Stage, Not Just Script Generation

Most "AI in QA" efforts stop at test script generation. An AI-led STLC applies AI as a force multiplier at each stage, with a human checkpoint at each handoff:

| STLC Stage | Traditional | AI-Led Target State |
|---|---|---|
| 1. Requirement Analysis | Manual review of user stories in ADO | Agent parses ADO work items/acceptance criteria, flags ambiguity/testability gaps |
| 2. Test Planning | Manual scoping, manual test plan doc | Agent drafts test plan/scope from requirements + historical defect data, human approves |
| 3. Test Case Design | Manual case authoring | Agent generates test cases (positive/negative/edge) from requirements or Swagger/OpenAPI specs, tester reviews |
| 4. Test Data Design | Manual/scripted | Agent generates synthetic/masked test data tied to each case |
| 5. Script Development (Automation) | Manual coding | Agentic plan→explore→script→test workflow (your existing pattern) |
| 6. Test Execution | CI-triggered, manual review of failures | Agent triages failures, classifies as product bug vs. flaky vs. environment issue |
| 7. Defect Management | Manual bug filing in ADO | Agent drafts ADO bug with repro steps, logs, screenshots attached |
| 8. Test Healing/Maintenance | Manual fix of broken locators/scripts | Healer agent (already scoped) auto-repairs and flags for review |
| 9. Reporting & Analytics | Manual weekly Allure review | Automated Allure summarization + failure ledger (already scoped) |
| 10. Regression Optimization | Run everything | Agent recommends risk-based regression subset from change diff |

This table is the spine of the roadmap in Section 5 — each row becomes a workstream.

---

## 2. Target Architecture

**Two integrated environments, one shared backbone:**

1. **Development-side (VS Code + GitHub Copilot)** — where your `.github` agents/skills/instructions/prompts already live. This is where script generation, healing, and code-adjacent AI work happens.
2. **ALM-side (MS ADO)** — where requirements, test plans, test cases, and defects live. This is where planning, case design, and defect-triage AI work needs to plug in.

**Integration layer (the piece most orgs skip):** ADO REST API / Azure DevOps MCP server as the bridge, so agents can:
- Read work items, acceptance criteria, and linked test plans
- Write generated test cases back into ADO Test Plans
- File/update bug work items with structured fields (repro, severity, linked build)
- Pull historical defect data to inform risk-based planning

Recommend evaluating the **Azure DevOps MCP server** (if not already available in your tenant) as the connector so Copilot agents in VS Code and any Copilot Studio agents can act on ADO directly instead of copy-paste handoffs.

**Where Copilot Studio fits:** For functional/manual testers who don't live in VS Code, a Copilot Studio agent (or Teams-embedded agent) is the right interface for requirement analysis, test case drafting, and defect drafting — same underlying skills/prompts, different surface, matching each persona's existing workflow.

---

## 3. Governance Layer (non-negotiable at your scale)

Given the size of the organization, this needs to sit inside your existing AI governance intake process, not bypass it:

1. **Human-in-the-loop by design** — every AI output in the STLC (test case, script, bug, healed locator) is *proposed*, not auto-committed. Reviewer approval is a required gate, logged in ADO.
2. **Eval-before-production policy** — extend your existing "every skill/agent must have a passing eval suite" policy org-wide for this initiative: no agent/skill touches ADO or a pipeline without a passing eval suite, re-validated on every change.
3. **Traceability** — every AI-generated artifact (test case, bug, script) tagged in ADO/commit metadata as AI-assisted, with the source prompt/agent version, for audit purposes.
4. **Data boundary** — confirm what's allowed to leave your ADO/codebase into any AI model context (especially if using cloud-hosted Copilot Studio agents vs. GitHub Copilot's enterprise data boundary). This should go through your governance intake before rollout, not after.
5. **Escalation path** — defined owner (you, as QA manager) for when an AI-suggested change is wrong — ties back to the failure ledger already scoped for Allure reporting.

---

## 4. People & Competency Model

You already have the ladder (User → Author → Architect) and persona-split workflow catalog. Extend it across the full STLC:

- **Functional/manual testers** — primary AI touchpoints: requirement analysis, test case design, defect drafting. Interface: Copilot Studio agent or Teams, not raw VS Code.
- **Automation engineers** — primary AI touchpoints: script generation, healing, regression optimization. Interface: VS Code + GitHub Copilot `.github` primitives (existing).
- **You (QA Manager)** — governance owner, eval policy owner, rollout sequencing owner, and the person accountable for the failure ledger / metrics rollup to leadership.

Recommend adding a **fourth ladder rung** above Architect: "Steward" — someone (likely you initially) accountable for the eval suite and governance compliance of every agent/skill in production, across both personas.

---

## 5. Phased Rollout Roadmap

Sequenced by dependency and risk, building on what's already built:

**Phase 0 — Foundation (mostly done)**
- `.github` customization framework, eval harness, competency ladder, workflow catalog ✅

**Phase 1 — Execution & Reporting AI (lowest risk, highest immediate ROI)**
- Automated Allure report summarization + failure ledger (already scoped)
- Test healing agent for automation scripts (already scoped)
- Rationale: these touch only your own pipeline artifacts, not ADO work item creation — lowest governance risk to start

**Phase 2 — Script Generation Expansion**
- Extend agentic plan/explore/script/test workflow from UI (Cypress) to API testing via Swagger/OpenAPI (already scoped)
- Formalize eval suites for each new skill before team-wide use

**Phase 3 — ADO Integration for Defect Management**
- Agent drafts ADO bugs from failed test runs (repro steps, logs, linked build) — tester/engineer approves before filing
- Requires ADO API/MCP connector; governance review before go-live (data boundary + human approval gate)

**Phase 4 — Test Case Design AI (functional tester surface)**
- Agent generates test cases from ADO requirements/acceptance criteria
- Deploy via Copilot Studio agent for functional testers (not VS Code)
- Human review gate before cases are added to ADO Test Plans

**Phase 5 — Requirement Analysis & Test Planning AI**
- Agent flags ambiguous/untestable acceptance criteria at intake, before test design begins
- Agent drafts test plan scope using historical defect data (risk-based)
- Highest-leverage but requires the most mature eval/governance foundation — sequenced last deliberately

**Phase 6 — Regression Optimization**
- Agent recommends a risk-based regression subset from code/requirement diffs, using accumulated failure ledger data as training signal
- This phase depends on data accumulated in Phases 1–5, which is why it's last

Each phase should follow the same pattern you've already used for the eval demo: build → eval → pilot with one team → institutionalize → measure → next phase.

---

## 6. Metrics to Report to Leadership

Track from Phase 1 onward so you have a data trail by the time you propose Phase 5:

- % of test cases AI-assisted vs. fully manual
- AI-suggested defect acceptance rate (proposed vs. approved without edit)
- Script healing success rate (auto-fixed vs. required manual intervention)
- Time-to-test-case and time-to-script, before/after
- Regression cycle time and defect escape rate
- Eval suite pass rate over time (agent/skill quality trend, not just usage)

---

## 7. Immediate Next Steps

1. Confirm ADO API/MCP connector availability and get it through governance intake (blocks Phase 3+)
2. Finish and ship Phase 1 (Allure summarization + healer) as the proof point for leadership
3. Draft the Copilot Studio agent spec for functional testers (Phase 4 interface) in parallel, since design can start before Phase 4 build
4. Add the "Steward" rung to the competency ladder and formally assign it

---

*This blueprint is a living document — revisit sequencing after each phase's metrics come in, since Phase 1 results may change how aggressively you can move on Phases 3–5.*

---

# Phase 1 Deep Dive: Execution & Reporting AI
### AI-Led STLC — Blueprint Phase 1 of 6

Phase 1 has two workstreams that can run in parallel: **(A) Allure Report Automation + Failure Ledger** and **(B) Test Healing Agent**. Both live entirely inside your existing dev-side environment (VS Code + GitHub Copilot + `.github` primitives) and touch no ADO work items — which is exactly why this phase carries the lowest governance risk and should go first.

---

## A. Allure Report Automation + Failure Ledger

### A.1 Goal
Replace the weekly manual routine (open Allure report → scan failures → write manager summary) with: team drops a report path/zip → agent produces a structured summary + updates a running failure ledger automatically.

### A.2 Workflow (end to end)
1. DevOps pipeline writes Allure results to the shared folder (existing, unchanged)
2. Team member (or a scheduled trigger) provides the report path/zip to the agent
3. **Parse skill** extracts: test name, status (pass/fail/broken/skipped), duration, error message/stack trace, suite/feature tags, retry history
4. **Classification skill** buckets each failure into one of: product bug / flaky test / environment issue / test data issue / stale locator — using error signature matching against the failure ledger's history
5. **Summarization skill** drafts the manager-facing report: pass rate trend, new failures vs. recurring, top failure clusters, flaky test list
6. **Ledger update skill** appends this run's classified failures to the persistent failure ledger (see A.4), so classification improves over time via matched signatures
7. Human review: QA lead/manager reviews the draft before it's sent — this is the approval gate

### A.3 GitHub Copilot Primitives Needed
| Primitive | Purpose |
|---|---|
| **Instructions** (`.github/instructions/`) | House style for the manager report; classification taxonomy definitions (what counts as "flaky" vs "environment") |
| **Skill: allure-parse** | Extract structured data from raw Allure JSON/HTML output |
| **Skill: failure-classify** | Match error signatures against ledger, assign category + confidence |
| **Skill: report-summarize** | Generate the manager-facing narrative report |
| **Prompt file** | The one-shot "here's the report path, run the pipeline" entry point a team member actually types |
| **Agent** | Orchestrates parse → classify → summarize → ledger-update as one workflow, so the human only invokes once |

This maps cleanly onto the four-primitive framework you've already trained the team on — no new concepts, just a new applied workflow.

### A.4 Failure Ledger — Design Points
This is the highest-leverage artifact in Phase 1 because it's what makes Phases 2–6 smarter later (regression optimization in Phase 6 depends on this data existing).

- **Storage**: structured, queryable format (JSON lines or a lightweight DB) — not just a text log — so classification skill can match against it and future agents can query it
- **Schema per entry**: test ID, error signature (normalized, not raw stack trace), first-seen date, last-seen date, occurrence count, category, resolution status, resolved-by/linked-fix reference
- **Signature normalization**: strip timestamps, line numbers, dynamic IDs from error messages before hashing/matching, or every failure looks "new"
- **Retention/decay**: define when an entry is considered stale/resolved (e.g., not seen in N runs) vs. actively recurring
- **Ownership**: who reviews/corrects misclassifications — feeds back into classification skill accuracy over time

### A.5 Eval Requirements (per your existing policy)
- **allure-parse**: eval against a set of real historical Allure reports with known-correct extracted fields
- **failure-classify**: eval against a labeled set of past failures (ground truth = category a human already assigned) — track precision/recall per category, not just overall accuracy
- **report-summarize**: eval against human-quality bar — does it match the level of detail/tone the team already sends? (subjective, use rubric-based grading like your csv-analyzer eval pattern)
- Re-run all three evals on every skill update, per your standing policy

### A.6 Governance/Risk Notes
- No ADO writes, no code changes committed — lowest-risk workstream, good pilot
- Data boundary: confirm Allure reports don't contain sensitive customer data before they pass through any cloud-hosted model context
- Misclassification risk is reputational (wrong report to manager), not systemic — still needs the human review gate, but stakes are lower than Phase 3+

### A.7 Rollout Steps
1. Build allure-parse skill + eval, validate on 5-10 historical reports
2. Build failure-classify skill + eval, seed the ledger with historical data if available (backfill)
3. Build report-summarize skill + eval, compare output against last 2-3 real manager reports the team sent manually
4. Wire into agent + prompt file, pilot with one person for 2-3 weekly cycles
5. Team-wide rollout once pilot output matches manual quality bar

---

## B. Test Healing Agent

### B.1 Goal
When a Cypress/Playwright script fails due to a stale locator (not a real product bug), agent proposes the fix automatically instead of an engineer manually re-inspecting the DOM.

### B.2 Workflow
1. Test execution fails; failure-classify skill (from workstream A) tags it as "stale locator" category
2. **Healer skill** triggered only for that category — re-explores the live application (or a captured DOM snapshot) to find the element's current selector
3. Healer proposes a diff: old locator → new locator, with confidence score
4. **Human review gate**: engineer approves/rejects the diff — this should NOT auto-commit, even at high confidence, at least initially
5. Approved fixes commit to the script; rejected ones fall back to manual investigation and get logged as a "healing miss" in the failure ledger

### B.3 Design Points
- **Trigger discipline**: healer should only fire on locator-classified failures, not all failures — otherwise it risks masking real product bugs as "just needs healing"
- **Confidence thresholding**: define a minimum confidence score below which the agent doesn't even propose a fix, just flags for manual review
- **Explainability**: the diff proposal should include *why* it picked the new locator (e.g., matched by text content, matched by nearby stable attribute) so the reviewing engineer can sanity-check quickly rather than blindly trust
- **Scope boundary**: healing locators is in scope; healing test *logic* (assertions, flow) is explicitly out of scope for this phase — keep the blast radius small

### B.4 Eval Requirements
- Eval set: deliberately break a set of known-good scripts (change locators) and verify the healer proposes the correct fix
- Track: fix-acceptance rate (how often engineers approve the proposed diff unchanged), false-fix rate (approved but later found wrong), miss rate (flagged as unfixable but a human could fix it)
- Re-eval on every skill update

### B.5 Governance/Risk Notes
- Commits to test code — even with human approval, this touches the codebase, so should go through the same PR review process as any human-written change, not a special AI bypass lane
- Track healing acceptance rate as a leadership metric (Section 6 of the main blueprint) — this is your strongest quick ROI story

### B.6 Rollout Steps
1. Build healer skill + eval on a controlled "break and heal" test set
2. Pilot on one test suite with one engineer reviewing every proposed fix
3. Track acceptance/false-fix/miss rates for 2-3 weeks before wider rollout
4. Expand to full automation suite once acceptance rate and false-fix rate hit an agreed bar (define this threshold with your team before starting — don't set it after seeing results)

---

## Phase 1 — Definition of Done
- Both skills (report automation, healer) have passing eval suites per standing policy
- Failure ledger is live and being written to on every run
- At least one full weekly cycle run end-to-end with human approval gate exercised
- Metrics baseline captured (Section 6 of main blueprint) so Phase 2+ has a before/after comparison

## Transition Criteria to Phase 2
Move to Phase 2 (API test script generation expansion) once:
- Failure ledger has enough data to be a meaningful classification signal (not day-one accuracy)
- Healer acceptance rate is stable and trusted by the team without heavy oversight
- Report automation has fully replaced the manual weekly routine, not running in parallel with it

---

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

---

# Phase 3 Deep Dive: ADO Defect Drafting
### AI-Led STLC — Blueprint Phase 3 of 6

Phase 3 is the first workstream that writes into ADO. Everything before this (Phases 1-2) stayed inside the dev-side environment. This phase closes the loop: a failure classified as a real product bug (not flaky, not environment, not healed) gets a drafted ADO bug work item instead of an engineer manually filing one.

---

## 3.1 Goal
When failure-classify (Phase 1) tags a failure as a genuine product defect, agent drafts a complete ADO bug work item — repro steps, logs, screenshots, linked build — for a human to review and file, not auto-file.

## 3.2 Workflow (end to end)
1. Test run fails; Phase 1's failure-classify skill tags it as "product bug" category (not flaky/environment/locator)
2. **Context-gather skill** pulls everything needed for a good bug report: failure logs, stack trace, screenshot/video if captured (Cypress/Playwright support this natively), the test script itself, linked build/commit ID, environment details
3. **Duplicate-check skill** queries ADO for existing open bugs matching this failure signature (reuse the same signature-normalization logic from the Phase 1 ledger) — avoids flooding the backlog with duplicate filings
4. **Draft-bug skill** composes the ADO work item: title, repro steps, expected vs. actual, severity suggestion, linked test case, linked build
5. **Human review gate**: QA engineer reviews the draft in a staging view (not yet in ADO) — approve as-is, edit, or reject as false-positive
6. On approval, agent creates the actual ADO work item via the ADO connector (Section 3.4) with all fields populated
7. Outcome (approved/edited/rejected) logs back to the failure ledger — this is the feedback loop that makes duplicate-check and severity-suggestion improve over time

## 3.3 Design Points

**Severity suggestion, not severity decision.** The agent can suggest severity based on signal (e.g., blocks core flow vs. cosmetic), but this should always be human-adjustable pre-filing — severity has downstream prioritization consequences you don't want an agent unilaterally deciding.

**Duplicate-check is the highest-value, highest-risk piece.** Get it wrong toward "everything is a duplicate" and real new bugs get suppressed. Get it wrong toward "nothing is a duplicate" and you flood the backlog. Recommend: agent surfaces *candidate* duplicates with confidence scores, human makes the final call — never auto-suppress a draft based on a duplicate match alone.

**Repro steps must come from the test script, not be invented.** The draft-bug skill should translate the actual test script steps into human-readable repro steps, not generate plausible-sounding ones from the error message alone — this is a common failure mode where the draft reads well but doesn't actually reproduce the bug.

**Screenshots/videos need a retention and access policy.** If Cypress/Playwright captures video, decide where that lives (attached to ADO item vs. linked to pipeline artifact storage) before this goes live — ADO attachment size/retention limits are a real constraint at scale.

## 3.4 ADO Integration — What to Confirm Before Building

This is the piece that needs to go through governance intake before any code is written, not after:

1. **Connector**: Azure DevOps MCP server or direct ADO REST API — confirm which is available/approved in your tenant
2. **Auth model**: service principal vs. per-user token — service principal is likely necessary for an unattended draft-review pipeline, but that's a bigger governance conversation (a bot identity filing/creating work items) than a per-user token
3. **Write scope**: does the connector's service account have write access to create work items in the right project/area path, and *only* that scope (least privilege)?
4. **Field mapping**: confirm your ADO bug template's required custom fields (many enterprises add mandatory fields beyond the default bug template) so the draft-bug skill populates all of them, not just title/repro/severity
5. **Data boundary**: if repro steps, logs, or screenshots could contain customer/sensitive data, confirm what's allowed to pass through the model context before drafting — this may mean redaction logic runs before the draft-bug skill, not after

## 3.5 GitHub Copilot Primitives Needed
| Primitive | Purpose |
|---|---|
| **Skill: context-gather** | Assemble logs, screenshots, build/commit info, test script |
| **Skill: duplicate-check** | Query ADO for matching open bugs by normalized signature |
| **Skill: draft-bug** | Compose the structured ADO work item from gathered context |
| **Instructions** | Your org's bug-report quality bar, required custom fields, severity taxonomy |
| **Prompt file** | Entry point for reviewing/approving a draft before filing |
| **Agent** | Orchestrates context-gather → duplicate-check → draft-bug → (human gate) → file |

## 3.6 Eval Requirements
- **context-gather**: eval that all expected artifacts (logs, screenshot, build ID) are captured for a range of failure types
- **duplicate-check**: eval against a labeled set of past failures with known duplicate/non-duplicate pairs — track false-positive (flagged duplicate, wasn't) and false-negative (missed duplicate) rates separately, since they have different costs
- **draft-bug**: eval against a human-quality bar — does the draft contain everything a human would need to act on it without going back to the source? Use the same rubric-grading pattern as your report-summarize eval in Phase 1
- Composite eval: full pipeline run on historical failures, compare agent-drafted bug quality against the actual historical bug a human filed for the same failure, where available

## 3.7 Governance/Risk Notes
- This is the first workstream where an AI action reaches a system of record outside your dev environment — treat the approval gate as mandatory and un-skippable, no "auto-file at high confidence" mode in this phase
- Bot/service identity filing ADO items should be visibly distinguishable in ADO (e.g., a tag or a dedicated field) so anyone reviewing the backlog later knows which bugs were AI-drafted — feeds the traceability requirement from the main blueprint's governance section
- Track false-positive bug drafts (rejected by reviewer) as a leadership metric — this is your main quality signal for this phase

## 3.8 Rollout Steps
1. Confirm ADO connector, auth model, and write scope through governance (start this in parallel with Phase 2, not after)
2. Build context-gather + eval
3. Build duplicate-check + eval, seed against existing ADO bug history if accessible
4. Build draft-bug + eval, calibrate against real historical bugs filed by the team
5. Pilot: agent drafts, but a human manually copies approved drafts into ADO (no live write yet) — validates quality before granting write access
6. Grant write access, pilot live filing with one engineer reviewing every draft for 2-3 weeks
7. Track approval/edit/reject rates before wider rollout

---

## Phase 3 — Definition of Done
- Agent reliably drafts complete, accurate bug reports from failed test runs, reviewed and filed by a human
- Duplicate-check false-positive and false-negative rates are within an agreed threshold (define before, not after, seeing results)
- AI-drafted bugs are visibly tagged as such in ADO
- Draft approval/edit/reject outcomes feed back into the failure ledger

## Transition Criteria to Phase 4
Move to Phase 4 (test case design for functional testers) once:
- The ADO write pathway is trusted and governance-approved — Phase 4 reuses the same connector for writing test cases into ADO Test Plans
- Bug-drafting quality is stable enough that it's not requiring heavy rework, giving you confidence the same draft→review→write pattern will work for test cases
- You've scoped the Copilot Studio agent interface for functional testers, since Phase 4 is the first workstream built for that persona rather than VS Code

---

# Phase 4 Deep Dive: Test Case Design (Functional Tester Surface)
### AI-Led STLC — Blueprint Phase 4 of 6

Phase 4 is a double shift from Phases 1-3: it's the first workstream built for **functional/manual testers** rather than automation engineers, and the first built on **Copilot Studio** rather than VS Code/GitHub Copilot. Same underlying discipline (draft → human review → write to ADO), new interface and new audience.

---

## 4.1 Goal
Given an ADO requirement/user story with acceptance criteria, agent generates a draft set of test cases (positive, negative, edge) for a functional tester to review and add to the ADO Test Plan — replacing manual case authoring from scratch.

## 4.2 Workflow (end to end)
1. Tester provides a work item ID/link (or the agent is triggered off a work item state change, e.g., moved to "Ready for Test")
2. **Requirement-fetch skill** pulls the work item's description, acceptance criteria, linked design/spec docs if attached
3. **Ambiguity-check skill** flags acceptance criteria that are untestable as written (vague, missing expected values, contradictory) — surfaced *before* case generation, so the tester can clarify with the author rather than get cases built on a bad foundation
4. **Case-generate skill** drafts test cases: one per acceptance criterion at minimum, plus negative/edge cases per your existing taxonomy conventions
5. **Human review gate**: tester reviews drafts in the Copilot Studio/Teams interface — approve, edit, reject individually (not just as a batch)
6. On approval, agent writes approved cases into the ADO Test Plan via the same connector built in Phase 3, linked to the source requirement
7. Rejected/heavily-edited cases log to a **case-quality ledger** (parallel to the Phase 1 failure ledger) — tracks which requirement patterns produce good vs. poor draft cases, so you can see where the agent needs more instruction refinement

## 4.3 Design Points

**Ambiguity-check should run before case-generate, not be skipped.** This is the single highest-leverage skill in this phase. Bad acceptance criteria produce plausible-looking but wrong test cases — the agent will confidently generate cases for a vague requirement rather than flagging the gap, unless you explicitly build the check as a separate, earlier step.

**Coverage floor, not coverage ceiling.** Define a minimum: every acceptance criterion gets at least one positive case, negative cases follow your existing taxonomy from the workflow catalog. Don't let the agent decide coverage depth on its own — testers should be able to request "more edge cases" as a follow-up, not have the agent guess how thorough to be.

**Traceability to source requirement is mandatory, not optional.** Every generated case must link back to the specific acceptance criterion it covers in ADO — this is what lets a later requirement change flag which test cases need re-review (a natural Phase 5 dependency).

**Batch vs. individual review.** Recommend individual approve/edit/reject per case, not a single "approve all" button — bulk-approving AI-drafted test cases without individual review is exactly the kind of shortcut that erodes the human-in-the-loop principle from your governance layer. This should be a hard UX constraint in the Copilot Studio agent, not just a policy ask.

## 4.4 Copilot Studio Agent Design — What's Different from VS Code Primitives

You're translating the same instructions/skills/prompts pattern to a different surface:

| VS Code equivalent | Copilot Studio equivalent |
|---|---|
| `.github/instructions/` | Agent instructions/knowledge sources configured in Copilot Studio |
| Skill | Topic or a connected Power Automate flow / plugin action |
| Prompt file | Trigger phrase or conversational entry point |
| Agent orchestration | Copilot Studio agent's topic/flow orchestration |

Key difference: functional testers interact conversationally (Teams-embedded likely, given your Microsoft stack), not via file-based prompts. Design the conversation flow so a tester can say "generate test cases for [work item]" and get a structured, reviewable output inline — not a wall of text they have to parse.

## 4.5 GitHub Copilot / Copilot Studio Primitives Needed
| Primitive | Purpose |
|---|---|
| **Skill/Topic: requirement-fetch** | Pull work item description, acceptance criteria, linked docs from ADO |
| **Skill/Topic: ambiguity-check** | Flag untestable/vague acceptance criteria before generation |
| **Skill/Topic: case-generate** | Draft positive/negative/edge cases per acceptance criterion |
| **Knowledge source/Instructions** | Org test-case format standards, negative-case taxonomy (reuse from Phase 2's), definition-of-ready bar for acceptance criteria |
| **Conversational entry point** | "Generate test cases for [work item ID]" trigger |
| **Write action** | Approved cases → ADO Test Plan via Phase 3's connector |

## 4.6 Eval Requirements
- **requirement-fetch**: eval that all relevant fields/linked docs are retrieved across a range of work item types/templates your org uses
- **ambiguity-check**: eval against a labeled set of past requirements — some genuinely ambiguous, some genuinely clear — track false-flag rate (flagged clear requirements as ambiguous) vs. miss rate (didn't flag actually-ambiguous ones)
- **case-generate**: eval against a human-quality bar — coverage completeness (every acceptance criterion covered), taxonomy adherence (negative/edge cases present), format compliance. Compare against real historical test cases written by your best testers for the same requirements where available
- Composite eval: full pipeline on 5-10 real historical requirements, compare agent-drafted case sets against what a human tester actually produced

## 4.7 Governance/Risk Notes
- First workstream reaching a non-automation-engineering audience — training/change management matters as much as the technical build here (see 4.8)
- Same traceability requirement as Phase 3: AI-drafted cases should be visibly tagged in ADO
- Data boundary: requirement docs may contain more business-sensitive content (roadmap details, unreleased features) than test logs did in Phase 1-3 — confirm this is covered in your governance intake, don't assume the earlier approval carries over automatically
- Since this is a new persona's first exposure to the initiative, a bad first impression (poor-quality drafts) does more organizational damage here than a rough patch in Phase 1-3 would with the automation team, who already trust the pattern

## 4.8 Change Management for Functional Testers
This phase is as much a people rollout as a technical one:

1. Position it as "draft assistant," not "replacement" — explicit framing matters for adoption with a persona that hasn't been through Phases 1-3
2. Pilot with your most ADO-fluent, most bought-in tester first — they'll surface UX friction faster and become an internal advocate
3. Use the ambiguity-check output as a teaching moment — when it flags a requirement, that's useful signal back to business analysts/product owners about acceptance-criteria quality, not just a QA-internal artifact
4. Extend your competency ladder (User/Author/Architect/Steward) explicitly to this persona with its own track, since the workflow catalog already calls for persona-separated tracks

## 4.9 Rollout Steps
1. Build requirement-fetch + eval against real ADO work item templates
2. Build ambiguity-check + eval, calibrate false-flag/miss rates before wide use
3. Build case-generate + eval, benchmark against historical human-written cases
4. Design the Copilot Studio conversational flow, pilot internally with QA team first (not functional testers) to shake out UX issues
5. Pilot with one functional tester for 2-3 requirement cycles, individual case-level review
6. Expand to functional testing team once approval/edit/reject rates and tester feedback hit an agreed bar

---

## Phase 4 — Definition of Done
- Agent reliably drafts complete, traceable test case sets from ADO requirements, reviewed case-by-case and written to ADO Test Plans by testers
- Ambiguity-check false-flag and miss rates are within an agreed threshold
- Case-quality ledger is live and tracking approval/edit/reject patterns
- Functional testing team has been onboarded with training material, not just handed a new tool

## Transition Criteria to Phase 5
Move to Phase 5 (requirement analysis & test planning) once:
- Case-generate quality is stable and trusted by functional testers without heavy rework
- Ambiguity-check has enough historical data to show it's genuinely catching real gaps, not just noise
- The case-quality ledger shows which requirement patterns need the most human intervention — this directly informs what Phase 5's earlier-stage requirement analysis needs to catch before testers ever see the work item

---

# Phase 5 Deep Dive: Requirement Analysis & Test Planning
### AI-Led STLC — Blueprint Phase 5 of 6

Phase 5 is the highest-leverage phase in the blueprint and the most judgment-heavy. It moves AI upstream of Phase 4 — catching requirement problems at intake/refinement, before a work item ever reaches "ready for test" — and adds risk-based test planning using the data your pipeline has been accumulating since Phase 1. It's sequenced last-but-one deliberately: it depends on mature ledgers and a track record of trust from Phases 1-4.

---

## 5.1 Goal
Two connected capabilities:
1. **Requirement analysis** — flag testability/completeness gaps in a user story at refinement time, not at "ready for test" time (earlier than Phase 4's ambiguity-check)
2. **Test planning** — draft a risk-based test scope for a feature/release using historical defect data, complexity signals, and the ledgers built in Phases 1 and 4

## 5.2 Workflow — Requirement Analysis
1. Triggered during backlog refinement (ideally before a story is marked "Ready" in ADO, not after)
2. **Definition-of-Ready check skill** validates the story against your org's DoR criteria (acceptance criteria present, testable, no contradictions, dependencies identified) — this is a deeper, earlier version of Phase 4's ambiguity-check
3. **Completeness-gap skill** flags what's *missing*, not just what's wrong — e.g., no error-handling criteria specified, no mention of expected behavior for edge inputs
4. Output goes to the story author (BA/product owner) and QA lead jointly, in the refinement meeting or as an async comment on the work item — this is a cross-functional output, not QA-internal
5. Story author addresses gaps before the story is marked ready; only then does it flow into Phase 4's case-generation pipeline

## 5.3 Workflow — Test Planning
1. Triggered at feature/release/sprint boundary, not per-story
2. **Defect-history-analyze skill** queries ADO bug history (reusing the connector from Phase 3) to identify which modules/features/components have the highest historical defect density, longest-lived bugs, or most regressions
3. **Complexity-signal skill** pulls supplementary risk signals where available — code churn, number of linked dependencies, number of linked stories in the release
4. **Plan-draft skill** combines these into a proposed test scope: what gets full coverage, what gets smoke-level coverage, what's explicitly out of scope with rationale, plus a rough effort/resourcing estimate
5. **Human review gate**: QA lead (you, or a delegate) reviews and adjusts before the plan is finalized — this is a strategic document with resourcing and priority implications, so review here is non-negotiable, not a formality
6. Approved plan is published to ADO (linked to the release/feature work item) and becomes the scope reference for Phase 4's case-generation work

## 5.4 Design Points

**Requirement analysis needs a cross-functional audience, not just QA.** Unlike every prior phase, the primary consumer of this output includes people outside your org (BAs, product owners). The tone and delivery need to read as collaborative quality signal, not QA gatekeeping — how you introduce this matters as much as the skill's accuracy. Loop in whoever owns your Definition-of-Ready process before building, not after.

**Test planning should propose scope, never decide it unilaterally.** This is the most consequential AI output in the blueprint so far — it affects what gets tested, what ships with less coverage, and where people's time goes. The plan-draft skill's output should read explicitly as a *recommendation with rationale* (here's why this module got full coverage, here's why this one got smoke-only), so the human reviewer can agree, disagree, or partially adjust with visibility into the reasoning — not just accept/reject a black-box scope.

**Defect-history-analyze needs a "sparse data" fallback.** New modules or newly-formed teams won't have historical defect density to draw on. Define what the skill does in that case — falling back to complexity signals alone, or explicitly flagging "insufficient history, defaulting to full coverage" — so it doesn't produce a falsely confident thin-coverage recommendation for something genuinely under-tested-so-far.

**This is where your case-quality ledger (Phase 4) and failure ledger (Phase 1) actually pay off.** If a requirement pattern has historically produced poor draft test cases (per Phase 4's ledger), or a module has a track record of flaky/environment-classified failures rather than real defects (per Phase 1's ledger), the plan-draft skill should surface that as context — this is the first phase where the accumulated data becomes genuinely predictive rather than just historical record-keeping.

## 5.5 GitHub Copilot / Copilot Studio Primitives Needed
| Primitive | Purpose |
|---|---|
| **Skill/Topic: dor-check** | Validate story against Definition-of-Ready criteria |
| **Skill/Topic: completeness-gap** | Flag missing (not just wrong) requirement content |
| **Skill/Topic: defect-history-analyze** | Query ADO bug history for risk signals by module/component |
| **Skill/Topic: complexity-signal** | Pull supplementary risk indicators (churn, dependency count) |
| **Skill/Topic: plan-draft** | Compose the scoped, rationale-annotated test plan |
| **Instructions/Knowledge source** | Your org's DoR criteria, scope-tiering definitions (full/smoke/out-of-scope), historical plan format |
| **Write action** | Approved plan → linked ADO work item |

## 5.6 Eval Requirements
- **dor-check / completeness-gap**: extend Phase 4's ambiguity-check eval set with a "missing content" labeled set — track false-flag and miss rates separately, same discipline as Phase 4
- **defect-history-analyze**: eval against known historically-risky modules — does it correctly surface them, and does it correctly handle the sparse-data case for new modules?
- **plan-draft**: eval against a human-quality bar — compare against real historical test plans QA leads have written for past releases, checking scope reasonableness and rationale clarity, not just "did it produce a plan"
- Composite eval: run the full pipeline on 2-3 past releases where you know the actual outcome (what broke, what didn't) — does the proposed scope, in hindsight, look right?

## 5.7 Governance/Risk Notes
- Highest-stakes phase so far: output affects resourcing and coverage decisions, and reaches an audience beyond QA
- Bug/requirement history may surface sensitive organizational patterns (e.g., a team's or vendor's defect track record) — be thoughtful about who sees defect-history-analyze output and how it's framed; this is a data-sensitivity question worth a specific governance conversation, not an assumption it's covered by Phase 3's approval
- No auto-approval path for test plans — full human review is mandatory here more than in any earlier phase, given the resourcing/priority stakes
- Track plan-draft acceptance rate (approved as-is vs. significantly revised) as a leadership metric — this tells you whether the org actually trusts AI-assisted planning yet, which is useful data before considering any further automation

## 5.8 Rollout Steps
1. Confirm DoR criteria are actually documented and agreed org-wide — if they're informal/tribal knowledge today, formalize them first, since dor-check needs something concrete to check against
2. Build dor-check + completeness-gap + eval, pilot in refinement meetings with QA-only review before looping in BAs/product owners
3. Introduce to one BA/product owner pair once QA-side quality is trusted, framed as collaborative signal
4. Build defect-history-analyze + complexity-signal + eval, backfill against historical ADO bug data
5. Build plan-draft + eval, benchmark against 2-3 real past release plans
6. Pilot test planning on one upcoming release with heavy QA-lead review before wider adoption
7. Track acceptance/revision rates for several release cycles before treating this as steady-state

---

## Phase 5 — Definition of Done
- Requirement analysis is running in refinement meetings and producing feedback that story authors act on before marking stories ready
- Test planning has been piloted on at least one real release, human-reviewed and adjusted before publishing
- Both ledgers (Phase 1 failure ledger, Phase 4 case-quality ledger) are actively feeding into plan-draft's risk signals
- Plan-draft acceptance/revision rates are being tracked as a leadership metric

## Transition Criteria to Phase 6
Move to Phase 6 (regression optimization) once:
- Test planning has run across enough release cycles that the risk-signal data (defect history + complexity + ledger feedback) is genuinely reliable, not just theoretically sound
- The organization has seen enough of Phases 1-5 working that a fully data-driven regression subset recommendation (Phase 6's core ask) will land as a natural next step rather than a leap of trust

---

# Phase 6 Deep Dive: Regression Optimization
### AI-Led STLC — Blueprint Phase 6 of 6

Phase 6 is the payoff phase: instead of running the full regression suite every cycle, the agent recommends a risk-based subset using the data accumulated across every prior phase — the failure ledger (Phase 1), case-quality ledger (Phase 4), defect history and complexity signals (Phase 5). It's sequenced last because it's only as good as that accumulated data, which is why every earlier phase explicitly routed its output into shared ledgers rather than isolated logs.

---

## 6.1 Goal
Given a code change or requirement diff for a release, agent recommends which regression tests must run, which can be safely skipped this cycle, and why — reducing regression cycle time without silently losing coverage on what actually matters.

## 6.2 Workflow (end to end)
1. Triggered on a release/build candidate — input is the code diff and/or the set of requirements/work items included in the release
2. **Change-impact skill** maps the diff to affected modules/components/test areas (via code ownership mapping, dependency graph, or linked work items — whichever your org already has structured)
3. **Risk-score skill** combines change-impact with the accumulated signals: historical defect density for affected areas (Phase 5), flaky/environment classification history (Phase 1 ledger — deprioritize tests that mostly fail for non-product reasons), case-quality patterns (Phase 4 ledger — areas where requirements/cases have historically been weak deserve more scrutiny, not less)
4. **Subset-recommend skill** produces the proposed regression set: must-run (high risk/high impact), recommended (moderate), safe-to-skip-this-cycle (low risk, stable history), with the rationale for each tier
5. **Human review gate**: QA lead reviews and adjusts before the subset is what actually runs in the pipeline — this is a coverage decision with the same stakes as Phase 5's test planning, treated with the same rigor
6. Actual run outcome (did a skipped-tier test area turn out to have a bug reported later) logs back into the risk-score skill's training signal — this is the one skill in the whole blueprint that should visibly improve over time as more cycles run

## 6.3 Design Points

**Default to "must-run" when uncertain, not "safe to skip."** The asymmetry matters: a false "safe to skip" that misses a real regression is far more costly than an unnecessary "must-run" that costs some extra CI time. Build this bias explicitly into the risk-score skill's thresholds, don't leave it implicit.

**Periodic full-regression cadence, independent of the optimization.** Even with a trusted subset-recommendation system, run the complete suite on a fixed cadence (e.g., weekly, or every N releases) regardless of what the agent recommends — this catches anything the risk model's blind spots might miss and gives you an ongoing accuracy check on the recommendations themselves.

**Explainability is not optional here.** Every "safe to skip" recommendation needs a stated reason (e.g., "no changes touched this module, zero defects in 6 months, no flaky history") so the human reviewer can sanity-check quickly rather than trust a black box — same principle as the healer agent's confidence explanation in Phase 1, but higher stakes here.

**Start in recommend-only/shadow mode.** For the first several cycles, run the full regression suite as normal *and* generate the subset recommendation in parallel, without actually skipping anything. Compare: did the "safe to skip" tier ever contain a test that would have caught a real issue? Only start actually skipping once you have enough shadow-mode cycles showing the recommendation was safe.

**This is where the whole ledger investment either pays off or reveals gaps.** If Phase 1's failure ledger has inconsistent classification, Phase 5's defect-history data is thin, or Phase 4's case-quality tracking wasn't maintained, this phase will surface that immediately — treat a rocky Phase 6 pilot as a signal to go back and strengthen earlier ledger discipline, not as a reason to distrust the regression-optimization skill itself.

## 6.4 GitHub Copilot Primitives Needed
| Primitive | Purpose |
|---|---|
| **Skill: change-impact** | Map code/requirement diff to affected test areas |
| **Skill: risk-score** | Combine change-impact with historical ledger/defect signals into a risk score per area |
| **Skill: subset-recommend** | Produce tiered (must-run/recommended/skip) regression set with rationale |
| **Instructions** | Risk-tiering thresholds, full-regression cadence policy, uncertainty-defaults-to-must-run rule |
| **Agent** | Orchestrates change-impact → risk-score → subset-recommend, feeds outcome back to ledgers |

## 6.5 Eval Requirements
- **change-impact**: eval against known past diffs with known-correct affected-area mappings — does it correctly identify what a change touches, including indirect/dependency-driven impact, not just direct file changes?
- **risk-score**: eval against historical releases where you know what actually broke — would the risk score have correctly flagged those areas as high-risk in hindsight?
- **subset-recommend**: shadow-mode eval is the real test here (see 6.3) — run it in parallel with full regression for several real cycles and measure whether anything in the "skip" tier would have caught a real issue
- Track this as an ongoing eval, not a one-time gate — risk-score's accuracy should be re-validated periodically as the org's codebase and defect patterns evolve, not just approved once and left alone

## 6.6 Governance/Risk Notes
- Coverage-reduction decisions carry real product-quality risk if the underlying data is wrong — this is the phase most worth being conservative about, given everything upstream feeds into it
- Track "skip tier led to missed defect" as a standing leadership metric indefinitely, not just during pilot — this is the metric that tells you whether to keep trusting the system as the org evolves
- No phase in this blueprint should ever reach full autonomy (auto-skip with no human review) — Phase 6 is the strongest temptation to do so given the maturity by this point, and the one where getting it wrong is most costly

## 6.7 Rollout Steps
1. Build change-impact + eval against historical diffs
2. Build risk-score + eval, using accumulated ledger data from Phases 1, 4, and 5 — this phase cannot start meaningfully until those ledgers have real history, not just schema
3. Build subset-recommend + eval
4. Run in shadow mode (full regression + parallel recommendation, nothing skipped) for a defined number of cycles
5. Review shadow-mode accuracy with QA leadership before enabling any actual skipping
6. Enable skip-tier for low-stakes releases first, expand as trust and data accumulate
7. Maintain the fixed full-regression cadence indefinitely as an ongoing accuracy check, even after full rollout

---

## Phase 6 — Definition of Done
- Change-impact, risk-score, and subset-recommend all have passing eval suites, re-validated periodically (not just once)
- Shadow-mode results reviewed and approved by QA leadership before any live skipping
- Fixed full-regression cadence is in place as a permanent safety net, not a temporary training-wheels measure
- "Skip tier led to missed defect" is tracked as a standing metric

---

## Closing Note: All Six Phases Now Scoped

You now have a complete, sequenced blueprint from requirement intake through regression optimization, each phase building on the data and trust established by the one before it. A few threads worth keeping visible as you execute:

- **The ledgers (Phase 1 failure ledger, Phase 4 case-quality ledger) are the actual backbone of the whole initiative** — Phases 5 and 6 are only as good as that data, so ledger discipline in the early phases isn't a minor implementation detail, it's the foundation.
- **Human review gates get more consequential, not less, as you move through the phases** — Phase 1's healer diff is low-stakes; Phase 6's regression scope decision affects product quality directly. Resist any pressure to loosen the gate as trust builds; if anything, Phase 5-6 deserve more scrutiny than Phase 1-2, not less.
- **Governance/data-boundary conversations should be running ahead of the build, not behind it** — Phase 3 was the first checkpoint for this; each subsequent phase reaches new data sensitivity and new audiences, so treat governance intake as a per-phase gate, not a one-time approval.
