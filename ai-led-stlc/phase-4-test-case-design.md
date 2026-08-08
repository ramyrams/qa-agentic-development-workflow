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
