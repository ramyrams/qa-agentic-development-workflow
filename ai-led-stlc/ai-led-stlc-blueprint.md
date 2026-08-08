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
