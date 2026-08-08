# AI-Led STLC — Governance Model
### Comprehensive Control Framework, Mapped to Each STLC Activity

This is the governance layer that sits across all six rollout phases — organized by the ten STLC activities themselves, not by phase, since governance obligations belong to the activity regardless of which phase introduces AI to it. Read alongside the technical design's connector/eval specifications and the implementation plan's risk register — this document defines the controls; those define how the controls get enforced in code and process.

---

## 1. Governance Principles (Apply to Every Activity, No Exceptions)

1. **Human-in-the-loop is mandatory, not configurable.** No AI output reaches a system of record, a codebase, or a human reader outside QA without an explicit approval step. No activity in this initiative ever runs to full autonomy.
2. **Eval-before-production.** No skill or agent goes live, or stays live after an update, without a passing eval suite validated against that activity's quality bar.
3. **Traceability is enforced technically, not just declared as policy.** Every AI-assisted artifact carries an `ai_assisted` tag and a `reviewed_by` field; the ADO connector rejects writes missing either (per the technical design, §0.4).
4. **Data boundary review happens per activity, not once for the whole initiative.** Requirement content, defect history, and test logs carry different sensitivity — each activity's governance intake is evaluated on its own data, not inherited from an earlier approval.
5. **Least privilege.** Every service identity (ADO service principal, API credentials) is scoped to the minimum project/area path/endpoint set the activity actually needs.
6. **Escalation ownership is named, not implied.** Every activity below has a defined approval authority who is accountable when something goes wrong, not a diffuse "the team" responsibility.
7. **Safety nets are permanent, not training wheels.** Where a control exists to catch AI error (e.g., full regression cadence, shadow mode), it stays in place indefinitely — it is never phased out once trust is established.

---

## 2. Governance Model by STLC Activity

### 2.1 Requirement Analysis
- **AI role**: Flags Definition-of-Ready gaps and testability issues at refinement
- **Risk tier**: High — reaches BAs/product owners, affects what gets built
- **Required control**: Story author and QA lead jointly resolve flagged gaps before a story is marked ready; AI never edits requirement text itself, only flags
- **Data sensitivity**: Business-sensitive (roadmap detail, unreleased features) — governance intake must confirm what model context is permitted here specifically, not assumed from an earlier phase's approval
- **Audit artifact**: Gap-flag log linked to the ADO work item
- **Approval authority**: Business Analyst/Product Owner + QA Lead, jointly
- **Escalation trigger**: Sustained false-flag pattern eroding BA/PO trust; unresolved disagreement over a flagged gap escalates to Program Sponsor

### 2.2 Test Planning
- **AI role**: Proposes risk-based test scope from historical defect/complexity data
- **Risk tier**: High — resourcing and coverage decisions
- **Required control**: QA Lead reviews and approves before the plan is published; every scope decision must show its rationale, never a black-box recommendation
- **Data sensitivity**: Defect history may reflect team/vendor performance patterns — treat as organizationally sensitive
- **Audit artifact**: Published plan with AI-rationale annotations and the approver's sign-off recorded
- **Approval authority**: QA Lead
- **Escalation trigger**: Sparse-data component defaulting to under-coverage; scope dispute with release management

### 2.3 Test Case Design
- **AI role**: Drafts positive/negative/edge test cases per acceptance criterion
- **Risk tier**: Medium — new persona (functional testers), writes to ADO Test Plans
- **Required control**: Case-by-case tester approval; bulk "approve all" is not an available action in the interface, by design
- **Data sensitivity**: Requirement content, generally lower sensitivity than raw requirements review
- **Audit artifact**: `ai-assisted` tag plus linked source-criterion field on each ADO test case
- **Approval authority**: Individual tester, with QA Lead spot-review on a periodic cadence
- **Escalation trigger**: Case approval rate drops below the agreed threshold; traceability link missing on a filed case

### 2.4 Test Data Design
- **AI role**: Generates happy-path and negative test data sets per a fixed taxonomy
- **Risk tier**: Low-to-Medium — elevated if any real or production-like data could enter the generation context
- **Required control**: Synthetic-data-only policy enforced; reviewed before use in any shared/CI environment
- **Data sensitivity**: Must never include real PII, financial data, or production values — this is a hard rule, not a preference
- **Audit artifact**: Data-generation log per endpoint/case, reviewable on request
- **Approval authority**: Automation Engineer
- **Escalation trigger**: Any suspected real or sensitive value appearing in generated data — immediate stop and review, not a routine fix

### 2.5 Script Development
- **AI role**: Drafts automation scripts via plan → explore → script → test
- **Risk tier**: Low-to-Medium — code enters the shared codebase
- **Required control**: Standard PR code review, same process as any human-written change — no AI-specific bypass lane
- **Data sensitivity**: Source code and API contracts; auth/secrets handling in generated scripts is a specific review point
- **Audit artifact**: PR history with `ai-assisted` commit/PR tag
- **Approval authority**: Peer reviewer / Automation Engineering Lead
- **Escalation trigger**: Hardcoded secrets or credentials found in generated code — treated as a security incident, not a code-quality note

### 2.6 Execution
- **AI role**: Classifies test failures (product bug/flaky/environment/etc.)
- **Risk tier**: Low — no writes outside the failure ledger
- **Required control**: Classifications reviewed in the regular weekly cycle; individual run results are not gated per-run
- **Data sensitivity**: Test logs may incidentally contain environment or system configuration data
- **Audit artifact**: Failure ledger entries with confidence scores
- **Approval authority**: Automation Engineer (weekly review), QA Lead (trend review)
- **Escalation trigger**: Classification confidence persistently low for a category, suggesting the taxonomy or normalization logic needs revision

### 2.7 Defect Management
- **AI role**: Drafts ADO bug work items with repro steps, evidence, and duplicate-check
- **Risk tier**: Medium — first activity writing directly to a system of record
- **Required control**: Mandatory human review before filing; duplicate-check surfaces candidates but never auto-suppresses a draft
- **Data sensitivity**: Logs and screenshots may contain sensitive application or customer-adjacent data — governance review specific to this activity, not inherited
- **Audit artifact**: `ai_assisted` and `reviewed_by` fields enforced at the ADO connector layer (technical design §0.4)
- **Approval authority**: QA Engineer filing the bug
- **Escalation trigger**: False-positive filing rate above threshold; a duplicate-suppression error that hid a real new defect

### 2.8 Test Healing
- **AI role**: Proposes fixes for stale-locator script failures
- **Risk tier**: Low — scope is explicitly limited to locators, not test logic
- **Required control**: Engineer approves or rejects every proposed diff; goes through normal code review on approval
- **Data sensitivity**: Minimal — DOM structure and locator data only
- **Audit artifact**: PR/diff record with confidence and matching rationale
- **Approval authority**: Automation Engineer
- **Escalation trigger**: A healed test later found to have masked a real product defect — triggers a review of the healer's category-scoping rules

### 2.9 Reporting
- **AI role**: Summarizes classified failures into a manager-facing report
- **Risk tier**: Low — internal audience, no system-of-record write
- **Required control**: Manager reviews the draft before it's distributed to leadership
- **Data sensitivity**: Generally internal-only; confirm no customer-identifying detail is present before wider distribution
- **Audit artifact**: Draft-vs-sent comparison retained for a defined retention period
- **Approval authority**: QA Manager
- **Escalation trigger**: A materially inaccurate report reaching leadership before being caught

### 2.10 Regression Optimization
- **AI role**: Recommends a risk-tiered regression subset from the change diff and historical data
- **Risk tier**: High — directly affects what ships with reduced test coverage
- **Required control**: QA Lead approval per cycle; mandatory shadow-mode validation before any live skipping is enabled; full regression suite continues on a fixed cadence permanently, regardless of live-mode status
- **Data sensitivity**: Release and defect-risk data; generally internal
- **Audit artifact**: Shadow-mode comparison log; skip-tier rationale retained per cycle
- **Approval authority**: QA Lead, with Program Sponsor sign-off before shadow mode is ever turned into live mode
- **Escalation trigger**: Any missed regression traced back to a skip-tier decision — triggers immediate rollback to full-suite-only until root cause is resolved

---

## 3. Governance Lifecycle for Any New Agent or Skill

Every one of the 42 primitives in the build inventory — and anything added later — moves through the same lifecycle, regardless of which STLC activity it serves:

```
1. Propose        → scope defined, target STLC activity and risk tier identified
2. Governance intake → data boundary reviewed for this specific activity/data type
3. Build + eval    → skill/agent built with a passing eval suite before any live use
4. Pilot           → 100% human review, small user group, defined cycle count
5. Metrics review  → pilot data checked against the activity's acceptance bar
6. Production      → rollout, with the activity's defined ongoing control still in force
7. Ongoing audit   → eval re-validated on every update; metrics tracked continuously
8. Retirement/versioning → superseded skills are formally retired, not silently abandoned
```

No primitive skips step 2 (governance intake) regardless of how low-risk it looks, and no primitive's step 6 control (the "required control" in Section 2) is ever relaxed to full autonomy — that constraint doesn't expire as trust builds.

---

## 4. Escalation Matrix

| Severity | Example | Response |
|---|---|---|
| **Sev1** | Sensitive data exposure; a write bypassing the approval/`reviewed_by` gate; a missed regression that reached production | Immediate halt of the specific skill/agent; Program Sponsor and AI Governance Team notified within 24 hours; root cause required before any restart |
| **Sev2** | An activity's approval/acceptance metric breaches its defined threshold (e.g., defect-draft false-positive rate, healing false-fix rate); a declining calibration agreement rate (Section 6.5) | Pause further rollout expansion for that activity; root-cause review within one week; resume only after a fix and a re-validated eval |
| **Sev3** | An isolated misclassification or false positive within normal tolerance | Logged in the relevant ledger; reviewed in the next steady-state cycle, no rollout pause required |

---

## 5. Governance Health Metrics

Distinct from the delivery metrics in the leadership briefing — these measure whether the *governance model itself* is holding, not whether the initiative is delivering value:

- **Human-review coverage**: % of AI actions with a documented reviewer (target: 100%, always)
- **Traceability tag coverage**: % of AI-assisted ADO items correctly tagged `ai_assisted` with `reviewed_by` populated
- **Eval re-validation compliance**: % of skill/agent version updates that had a re-run, passing eval before deployment
- **Override/rejection rate trend, per activity**: rising rejection rates are an early signal before a Sev2 threshold breach
- **Escalation resolution time**: time from a Sev1/Sev2 trigger to root-cause resolution
- **Governance intake cycle time, per activity**: tracked to identify where the intake process itself is becoming a bottleneck to legitimate rollout

Report these alongside — not instead of — the delivery metrics from the leadership briefing. A phase can be hitting its delivery numbers while quietly eroding governance discipline (e.g., reviewers rubber-stamping under time pressure), and these metrics are what would surface that. Section 5's metrics are necessary but not sufficient on their own — a reviewer who approves 98% of drafts looks identical in this data whether the drafts are genuinely that good or the reviewer stopped reading closely. Section 6 is the check that catches the difference.

---

## 6. Reviewer Calibration Audit

The metrics in Section 5 measure whether the review gate exists. They can't tell you whether the review happening at that gate is still rigorous — a reviewer can approve everything, on time, every cycle, and still have quietly stopped reading closely under volume pressure. This section is the mechanism that catches that specific failure mode before it becomes a pattern, borrowed from the same logic as inter-rater reliability checks in any QA discipline.

### 6.1 What It Is
Each month, a senior reviewer — someone other than the original approver — re-checks a random sample of AI outputs that were already approved and shipped, **without being told they were pre-approved**. The point is a cold, independent second read, not a re-confirmation of the first reviewer's judgment.

### 6.2 Sampling
- Draw randomly across all ten STLC activities, weighted toward the higher-risk ones (Requirement Analysis, Test Planning, Defect Management, Regression Optimization get proportionally larger samples than lower-risk activities like Test Healing)
- Minimum sample: 5% of the prior month's approved AI outputs per activity, or 10 items, whichever is larger
- Include a mix of routine approvals and any edge cases (low-confidence outputs that were still approved, outputs from a reviewer with an unusually high approval rate that month)

### 6.3 Process
1. Auditor selects the sample without input from the original reviewer
2. Auditor evaluates each item cold, against the same acceptance bar the original reviewer should have applied — logs their own approve/edit/reject verdict
3. Compare auditor verdict against the original reviewer's verdict — a mismatch is a **calibration gap**, not automatically a reviewer failure; some gaps are genuinely close judgment calls
4. Calibration gaps are reviewed by the Program Sponsor: pattern of gaps for one reviewer → coaching conversation, not disciplinary by default; pattern of gaps across many reviewers for one activity → the activity's acceptance bar or instructions may be poorly specified, not a people problem at all

### 6.4 Cadence & Owner
- **Cadence**: monthly, fixed on the calendar — not "when there's time," since this is exactly the kind of check that quietly stops happening under the same pressure it's meant to catch
- **Owner**: Program Sponsor / Steward selects the auditor each cycle (rotate among senior QA staff — don't let the same person audit the same reviewer every month, to avoid the audit itself going stale)
- **First audit**: scheduled for the end of the first full month of Phase 1 production use, so the mechanism is running before Phase 3+ starts writing to ADO, not retrofitted later

### 6.5 What Gets Reported
- **Calibration agreement rate** per activity and per reviewer, added to the Section 5 governance health metrics as a standing line item
- Trend over time — a declining agreement rate is itself a Sev2-equivalent trigger (Section 4), even though no single approved item necessarily caused harm
- Findings feed back into two places, not just a report: the relevant instructions file (if the acceptance bar itself was ambiguous) and reviewer training (if it was a judgment gap) — an audit that only produces a score without changing either of those isn't doing its job

### 6.6 Why This Sits Outside Section 5's Automated Metrics
Everything in Section 5 can be computed from system data without a human looking at content again. This audit is deliberately the one governance mechanism that requires a human to re-examine actual output quality — it exists precisely because reviewer rubber-stamping would look identical to genuine rigor in every metric that doesn't involve someone reading the work again.

---

## 7. Roles Summary

| Role | Governance Responsibility |
|---|---|
| AI Governance Team | Enterprise-level data boundary sign-off; per-activity intake approval |
| Program Sponsor / Steward | Day-to-day enforcement of this model; Sev1 escalation owner; holds every phase gate; selects calibration auditors monthly (Section 6.4) |
| Per-activity approval authority (Section 2) | Reviews and approves AI output for that specific activity — named individually, not a shared team responsibility |
| Automation/Functional QA staff | Execute the required control at their activity; report anomalies into the relevant ledger; serve as rotating calibration auditors |
| Calibration Auditor (rotating, monthly) | Cold re-review of a random sample of approved outputs (Section 6); reports calibration gaps to Program Sponsor |
