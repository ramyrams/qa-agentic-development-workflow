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
