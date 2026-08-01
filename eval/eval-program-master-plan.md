# Evaluation Implementation Program Plan
### Master Plan for the Agentic Development Workflow Eval Program — For the Tech Manager

**What this document is:** the program-management layer that sits on top of the technical work already specified. Three companion documents define *how* to build each eval — methodology (automation-agent-eval-implementation-plan.md), tooling (copilot-cli-eval-tooling-setup-guide.md), and per-primitive specifics (eval-plans-by-primitive.md). **This document answers the questions only a manager needs answered: who does it, when, how much does it cost, how do you know it's working, what could go wrong, and what do you tell your own leadership.**

---

## 1. Executive Summary

Your team has built a working `.github/` estate — custom agents, skills, instructions, and prompts driving script generation, execution, and healing. It currently ships on trust: nobody can say with evidence how often it works, how it fails, or whether a change made it better or worse. This program builds the missing layer — a CI-gated evaluation harness covering all four customization primitives — so that estate changes are verified before they ship, reliability is a measured number instead of an impression, and the team can answer "does this actually work, every time?" with data.

**Investment:** ~2 engineers at partial allocation for a 12-week build, dropping to ~0.25 FTE ongoing maintenance thereafter (Section 6). **Primary deliverable:** a CI-blocking regression suite plus a quarterly-reported reliability dashboard. **Primary risk being retired:** an unverified healing/automation agent silently masking real product defects — the highest-severity failure mode this program exists to catch (Section 10).

---

## 2. Program Objectives & Success Criteria

| Objective | Success criterion | Reports to |
|---|---|---|
| Make estate changes verifiable before merge | CI regression suite blocks merges to `.github/` on measured regression, not opinion | Engineering leadership |
| Quantify reliability, not just capability | Every skill/agent has a reported pass^k, not just "it worked when I tried it" | Engineering leadership + QE governance |
| Eliminate the single highest-risk failure mode | Healing false-positive rate measured and gated below an explicit threshold | Risk/governance, possibly security |
| Build team capability, not just a tool | Eval-building becomes L2 competency-ladder portfolio work — the team that builds the harness is the team that gains the skill | You, as manager, for headcount/growth conversations |
| Make the initiative's value legible upward | Quarterly reliability + cost-of-quality report your leadership can read in five minutes | Your leadership |

---

## 3. Program Scope

**In scope:** eval coverage for everything currently in `.github/agents/`, `.github/skills/`, `.github/prompts/`, `.github/instructions/` for the script-generation, execution, and healing workflow. CI integration. The tooling and instrumentation layer. Team training on eval-building.

**Explicitly out of scope for this program** (they're real, but they're different initiatives — don't let this program's charter absorb them): the broader agentic-QA workflow catalog (KT-to-test-cases, exploratory agents, production telemetry, etc.) is a separate adoption program; new skill/agent *capability* development is ongoing team work this program evaluates, not builds. Naming this boundary explicitly now prevents scope creep six weeks in, when it will feel natural to fold in "just one more workflow."

---

## 4. Program Structure — Phased Timeline

Twelve weeks to a working, CI-gated harness across all four primitives; ongoing operation from Month 4.

### Phase 0 — Foundation (Weeks 1–2)
- Tool installation and verification (Copilot CLI, hooks, worktree isolation) — tooling guide Parts 1–2
- Confirm every existing agent/skill/prompt/instruction actually loads as expected
- Stand up the eval project scaffold and instrumentation (hook-based tool-call logging) — tooling guide Part 3
- **Gate to exit Phase 0:** one hand-run trial produces a readable, structured tool-call log. If this doesn't work cleanly, nothing downstream will either — do not proceed until it does.

### Phase 1 — Cheapest, Highest-Confidence Evals First (Weeks 3–4)
Per the build-order in the per-primitive plan (Section 5 of that document):
- Skill bundled-script unit tests (pure code — no agent involvement)
- Instruction scope-correctness and cross-layer contradiction checks (static)
- Prompt-to-agent pairing checks (static)
- **Gate:** every deterministic, code-only check in the estate has a passing automated test. This phase should feel fast — it's intentionally the easy 20% that catches real bugs cheaply, building team confidence before the harder work.

### Phase 2 — Routing & Triggering (Weeks 5–6)
- Agent routing suite (Suite A) and skill-triggering suite, built together since they share the hook-log infrastructure
- Balanced positive/negative task sets, confusion-pair probes
- **Gate:** a confusion matrix exists for every skill and every agent-callable skill pairing; known misroutes have been fixed or explicitly accepted with rationale.

### Phase 3 — Capability & Input-Boundary Evals (Weeks 7–9)
- Script-generation, execution, and prompt-input-boundary suites (code + LLM-judge graders)
- Judge model selected and wired as a separate, non-self-grading invocation
- **Gate:** every skill/agent/prompt has at least one capability task with a passing code grader and an LLM-judge score above your provisional bar.

### Phase 4 — Healing Safety Framework (Weeks 8–10, overlaps Phase 3)
**Given first — built in parallel because it's the highest-risk item, not because it's next in sequence.**
- Labeled dataset across all failure categories (selector/timing/data/runtime/rendering/interaction), including adversarial decoys
- Assertion-diff hard gate, false-positive rate instrumentation, escalation-path negative test
- **Gate:** false-positive rate measured on a real labeled set, with an explicit threshold set and a mechanism to block release if it regresses. This gate does not open until this is real, not aspirational.

### Phase 5 — Consistency & CI Integration (Weeks 10–12)
- Multi-trial orchestration (pass@k/pass^k) across all suites built so far
- GitHub Actions workflow live; regression suite blocking, capability suite informational
- **Gate:** at least one real PR to `.github/` has been blocked or passed by the CI gate on real evidence, not a dry run.

### Ongoing Operations (Month 4+)
- Monthly judge-calibration sampling, dataset refresh, pass^k trend review
- Quarterly full-program report (Section 9)
- New skill/agent/prompt/instruction work includes eval coverage as a definition-of-done item, not a follow-up task

---

## 5. Roles & RACI

| Role | Who (suggested) | Responsible for |
|---|---|---|
| **Program owner** | You (tech manager) | Scope, timeline, resourcing decisions, upward reporting |
| **Technical lead / eval architect** | Your strongest L2/L3 engineer | Harness architecture, grader design, judge calibration |
| **Skill/agent authors** | The engineers who built each asset | Providing ground-truth labeled cases for their own asset; first responder when their asset's eval fails |
| **Security reviewer** | Whoever owns your audit checklist's §5.3 | Reviewing bundled scripts, healing-skill safety gate design, sign-off on any tool pre-approval |
| **CI/DevOps support** | Whoever owns your pipeline | Wiring the GitHub Actions workflow, runner capacity, secrets management for CLI auth |

| Activity | Program owner | Eval architect | Asset authors | Security reviewer | CI/DevOps |
|---|---|---|---|---|---|
| Phase gate approval | A | R | C | C | I |
| Grader design | I | A/R | C | C | — |
| Labeled dataset creation | I | C | A/R | C | — |
| Healing safety gate | A | R | C | **A** | — |
| CI workflow | I | C | — | I | A/R |
| Judge calibration | I | R | — | — | — |
| Quarterly report | **A/R** | C | I | I | I |

*(R = Responsible, A = Accountable, C = Consulted, I = Informed)*

---

## 6. Resourcing & Capacity Plan

**Build phase (Weeks 1–12):** realistically 1.5–2 engineers at ~40–50% allocation, not a dedicated pod pulled fully off other work — this program is designed to be absorbable alongside normal sprint commitments if you sequence it deliberately (Phase 1's easy wins first, building momentum before the harder Phase 3/4 work).

**The capacity-funding move worth making explicitly:** frame eval-building as L2 competency-ladder portfolio work (per your team's existing training program) rather than a separate unbudgeted ask. Engineers building graders and labeled datasets are simultaneously earning ladder progression — this is real, not a rebranding trick, since the ladder's L2 criteria already require exactly this kind of shipped, evidenced work. It changes how you justify the time in a resourcing conversation: this is training investment with a working deliverable, not pure overhead.

**Ongoing (Month 4+):** ~0.25 FTE aggregate — monthly calibration sampling, dataset refresh, and responding to eval failures as they occur. Budget this as a standing line, not a one-time project cost; an eval harness that isn't maintained decays exactly like the test suite it's meant to protect.

---

## 7. Tooling & Budget Considerations

| Item | Cost posture | Notes |
|---|---|---|
| GitHub Copilot CLI, `gh`, `jq`, `yq` | Free / already licensed | No new procurement |
| Git worktrees, GitHub Actions | Already in your stack | CI runner minutes increase — estimate and confirm headroom before Phase 5 |
| LLM-judge invocations | **New recurring cost** | Every capability/judge-graded trial makes an additional model call; at k=5 across dozens of tasks this adds up monthly — get a rough per-run cost estimate during Phase 3 before scaling suite size |
| Dedicated eval framework (Braintrust / Promptfoo / Harbor) | **Optional, evaluate don't assume** | Only adopt if Phase 5's orchestration/reporting needs outgrow your bash+jq runner — treat as a build-vs-buy decision made with evidence from Phases 1–4, not a Week 1 purchase |
| Human calibration time | Small but real | 10–15% of judge-graded trials sampled monthly for human review — budget as part of the 0.25 FTE ongoing line |

**The one line item to flag to your own budget owner now, before it surprises anyone:** judge-model call volume. Everything else in this table is close to free; this is the one that scales with how much you evaluate.

---

## 8. Milestones & Gates (the version to put on a status slide)

| Milestone | Target | Evidence required to call it done |
|---|---|---|
| M1 — Instrumentation live | End Week 2 | One trial produces a structured, parseable tool-call log |
| M2 — Deterministic suite complete | End Week 4 | All code-only checks (scripts, scope, static pairing) passing in CI |
| M3 — Routing/triggering measured | End Week 6 | Confusion matrix published for every agent and skill |
| M4 — Capability suites live | End Week 9 | Every asset has ≥1 passing capability task with a calibrated judge score |
| M5 — Healing safety gate active | End Week 10 | False-positive rate measured on a real labeled set; threshold enforced |
| M6 — CI gate enforcing | End Week 12 | A real PR has been blocked or approved by the regression suite |
| M7 — First quarterly report | End Month 4 | Reliability dashboard delivered to leadership (Section 9) |

Each milestone is a **go/no-go checkpoint** — don't let the calendar carry a milestone past its evidence requirement. A slipped M5 (healing safety) is a legitimate reason to delay M6 (CI gate); a slipped M6 is not a reason to relax M5's threshold to make the date.

---

## 9. Governance & Reporting Cadence

- **Weekly (build phase only):** 15-minute standup on phase progress against gates — part of your existing team rhythm, not a new meeting.
- **Monthly (ongoing):** judge-calibration review, pass^k trend check, dataset refresh — owned by the eval architect, reported to you in writing (a short dashboard export, not a meeting).
- **Quarterly (ongoing):** the report that goes to your leadership. Contents: pass^k trend per suite, healing false-positive trend, routing accuracy trend, regression-suite pass rate, and — the line that makes this legible outside QE — an estimate of what the harness caught before it shipped, framed in the cost-of-quality vocabulary your team already uses for other initiatives. This report is the eval program's own accountability artifact: it should look like the quality narrative your team builds for everything else, not a special exception.

---

## 10. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Healing skill produces a false-positive heal that masks a real defect | Medium | **Severe** | This is why Phase 4 is pulled forward and given a hard gate (Section 4) rather than being just another capability suite — treat any regression here as a stop-ship event, not a backlog item |
| Team treats eval-building as overhead, adoption stalls | Medium | High | Frame as L2 ladder work (Section 6); start with Phase 1's fast, visible wins before the harder phases, so the team feels progress early |
| CLI flags/behavior change under the harness (fast-moving tooling) | High | Medium | Pin CLI versions in CI (tooling guide Part 9); budget a small ongoing maintenance tax for this explicitly rather than being surprised by it |
| Judge-model cost grows unchecked as suites scale | Medium | Medium | Track cost per suite run from Phase 3 onward; make suite-size growth a deliberate decision with a cost number attached, not an accident |
| CI gate becomes a false-positive-heavy nuisance, teams route around it | Medium | High | Keep the regression/capability suite split strict (Section 4 Phase 5) — only proven-stable tasks ever block a merge; a noisy gate gets disabled by frustrated engineers faster than it gets fixed |
| Golden datasets go stale as the app changes | High (over time) | Medium | Monthly refresh is already in the ongoing-ops cadence (Section 4); treat a stale dataset as a known, budgeted maintenance item, not a surprise |
| Program scope creeps into the broader workflow catalog | Medium | Medium | Section 3's explicit scope boundary; any request to fold in a new workflow goes through your intake rule, not a mid-program expansion |

---

## 11. Training & Change Management

This program is itself a training vehicle, and treating it that way solves two problems at once — capacity (Section 6) and durable capability:

- **Eval-building work is L2 competency-ladder portfolio material.** The engineers who build graders, labeled datasets, and the healing safety gate are producing exactly the evidenced, shipped-asset portfolio your ladder's L2 assessment requires.
- **Run one kata cycle pointed at the eval program itself** — a K4-style trigger-calibration exercise works unchanged when the "skill" being calibrated is one of your real skills going through Phase 2, turning a program deliverable into a practice session.
- **Communicate the CI-gate change before it lands (end of Phase 4, ahead of M6).** The team needs to know, before their first PR gets blocked, that regression-suite failures are hard gates and capability-suite results are informational — a surprise merge block breeds resentment; an announced one builds trust in the system.

---

## 12. Success Metrics — the Program-Level KPI Set

Beyond the per-suite metrics already specified in the eval methodology (pass^k, routing precision/recall, healing false-positive rate, judge-human agreement), report these at the **program** level:

| KPI | What it tells your leadership |
|---|---|
| % of `.github/` estate under eval coverage | Program completeness — climbs from 0 toward 100% across the 12-week build |
| Regression-suite pass rate (steady-state) | Should sit near 100%; any dip is urgent and self-explanatory |
| Merges blocked by the gate, with root cause | Proof the gate is doing real work, not just running |
| Estimated defects/incidents caught pre-merge | The COQ-style number that translates this program into money and risk avoided |
| Time from asset change to eval verdict | Operational health of the harness itself — should be fast enough that engineers don't route around it |

---

## 13. How the Companion Documents Fit This Plan

| Document | Answers |
|---|---|
| **This document** | Who, when, how much, how do we govern it, what could go wrong |
| automation-agent-eval-implementation-plan.md | What does "correct" mean for each suite — the grading methodology |
| copilot-cli-eval-tooling-setup-guide.md | How do you actually build it — installable tools, runnable scripts |
| eval-plans-by-primitive.md | What's different about evaluating instructions vs. prompts vs. skills vs. agents |

Hand this document to whoever approves your resourcing; hand the other three to whoever's actually building it. That split is deliberate — a manager document that also tries to be the technical spec serves neither audience well.

---

*Owner: ________ (you) · Eval architect: ________ · Program start: Week of Aug 3, 2026 · First quarterly report due: end of Month 4*
