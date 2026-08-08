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
