# Eval Implementation Plan: Automation Agent + Skills
### Script Generation · Execution · Healing — Routing Accuracy, Per-Skill Capability, and Consistency-at-Scale

**System under test (SUT):** one orchestrating agent that receives an ask, selects and calls one or more skills (script generation, execution/triage, healing — and whatever else you've added), and produces an outcome. **The evaluation problem has two layers people usually conflate:** *"does the agent pick the right skill?"* (routing) and *"does that skill do its job well?"* (capability) — plus a third your prompt explicitly names: *"does it do this the same way every time?"* (consistency). This plan builds all three, extending your existing eval harness rather than replacing it.

**Grounding:** this plan adopts Anthropic's agent-evaluation vocabulary and principles (published as *Demystifying evals for AI agents*, Jan 2026) and current self-healing-test-automation practice. Citations to specific claims are in the closing rationale notes; treat vendor percentages as industry-typical ranges to calibrate against, not targets to cite to management until reproduced on your own data.

---

## 1. Vocabulary — mapped onto what you already have

| Anthropic's term | Definition | Maps to your existing harness as |
|---|---|---|
| **Task** | One unit of work with a clear ask and success condition | One entry in your eval spec template |
| **Trial** | One execution of a task (agents are non-deterministic, so a task is run multiple times) | One invocation of your bash runner against one spec entry |
| **Agent harness** | The system that lets the model act as an agent — orchestrates tool/skill calls | Your automation agent + its skill-calling mechanism |
| **Evaluation harness** | The infrastructure that runs tasks, records everything, grades, aggregates | Your bash runner script, extended (Section 8) |
| **Transcript / trajectory** | The full record of what happened: messages, skill/tool calls, reasoning, outputs | Your trajectory grading methodology |
| **Outcome** | The final state of the environment after the trial — not what the agent *said* | New concept to formalize (Section 3) — this is the gap this plan closes |
| **Grader** | What decides pass/fail: code, LLM, or human | New: you need three grader types, not one (Section 5) |
| **Suite** | A collection of tasks, run together, reported together | New: four suites, one per layer (Section 3) |

**The single most load-bearing principle from this framework, and the one most eval efforts get backwards:** grade the **outcome** — the actual file diff, the actual test result, the actual skill that got called — never the agent's *narration* of what it did. "I healed the locator and the test now passes" is a claim; the outcome grader re-runs the test and checks. This distinction is why Section 3 below always specifies an outcome check, not a transcript read, as the primary grader — transcripts are for debugging *why* a grader failed, not for deciding pass/fail themselves.

---

## 2. The Four Eval Suites (the structure of this whole plan)

| Suite | Question it answers | Why it's separate |
|---|---|---|
| **A. Routing** | Given an ask, does the agent call the *right* skill? | A perfect skill behind wrong routing still fails the user. This is the highest-leverage, cheapest suite to build — build it first. |
| **B. Per-skill capability** | Given that a skill *was* correctly invoked, does it do its job well? | Isolates skill quality from routing — a routing failure and a generation-quality failure are different bugs needing different fixes. |
| **C. End-to-end trajectory/outcome** | Given a realistic ask, is the full ask→route→skill(s)→outcome chain correct? | Routing + capability evals in isolation miss interaction bugs (e.g., healer invoked mid-generation, or two skills stepping on each other's output). |
| **D. Consistency** | Does the *same* ask produce the *same quality* result every time? | This is your explicit ask. Non-determinism means A/B/C must each be run multiple times per task, not once — this suite defines how. |

A fifth, cross-cutting concern — **safety gates for the healing skill specifically** — is woven through B, C, and D rather than standing alone, because healing's highest risk (silently masking a real bug) can only be caught by outcome checks embedded in capability and trajectory tasks, detailed in Section 6.

---

## 3. Suite A — Routing / Skill Selection

**Why this matters most, first:** industry work on skill retrieval (SkillResolve-Bench and related research on agent-skill ambiguity) has identified *same-capability ambiguity* as a distinct, measurable failure mode — an agent choosing between two skills that both plausibly apply to an ask, and choosing wrong. For a three-skill agent (generate/execute/heal) the confusion pairs are predictable and testable: "this test is failing, fix it" could mean *heal* (locator drift) or *generate* (the test never existed correctly) or *execute* (just re-run it, it was an infra blip) — the ask alone doesn't disambiguate; context does, and that's exactly what routing eval must verify.

**Design — balanced problem sets, not just "does it work":** Anthropic's guidance is explicit that one-sided evals (only testing when a skill *should* fire) produce agents that over-trigger. Build the task set in pairs:

```yaml
# routing-eval-spec.yaml — one entry shown, repeat per ask pattern
- task_id: route-001
  category: routing
  ask: "The checkout test is failing in the nightly run — the error says element not found for #submit-btn"
  context_provided: {ci_log_snippet: "...", recent_ui_diff: "submit-btn renamed to pay-now-btn"}
  expected_skill: healing
  expected_NOT: [script-generation, execution]
  outcome_grader: code
  outcome_check: "agent_invoked_skills == ['flaky-triage', 'healing'] AND no file changed outside spec's selector line"

- task_id: route-002   # the paired negative — same surface pattern, different correct answer
  category: routing
  ask: "The checkout test is failing in the nightly run — the error says the total shows $0.00 after discount"
  context_provided: {ci_log_snippet: "...", recent_ui_diff: null}
  expected_skill: none-of-the-above   # this is a real bug; agent should flag, not heal
  expected_NOT: [healing]
  outcome_grader: code
  outcome_check: "agent_invoked_skills does NOT include 'healing' AND agent produced a bug_report artifact"

- task_id: route-003
  category: routing
  ask: "Write a test for the new refund flow"
  expected_skill: script-generation
  outcome_grader: code

- task_id: route-004   # adjacent-ambiguity probe: could look like generation, is actually healing
  category: routing
  ask: "The refund flow test doesn't exist yet but there's a similar cancelled-order test that's now failing on the same button"
  expected_skill: [script-generation, healing]   # legitimately both — tests multi-skill routing
  outcome_grader: code
```

**Metric:** a confusion matrix (expected skill × actually-invoked skill) across the full routing suite, reported as **routing precision/recall per skill**, not one aggregate number — a 90% aggregate can hide a healing-skill recall of 60% invoked-when-it's-actually-a-real-bug, which is your most dangerous failure mode (Section 6).

**Dataset sourcing:** mine real asks from your team's chat history with the current agent, PR descriptions, and Slack/ticket phrasing — routing evals fail in production on phrasing real users use, not phrasing engineers write for test specs. Supplement with synthetic adversarial pairs (same surface words, different correct skill) generated explicitly to probe the confusion pairs above.

---

## 4. Suite B — Per-Skill Capability

Each skill gets its own task set, graded on **what it produced**, assuming correct routing (these tasks invoke the skill directly, bypassing the router, to isolate skill quality from routing quality).

### B1. Script-Generation Skill

| Grader type | Checks | Example |
|---|---|---|
| **Code (deterministic)** | Generated spec lints clean, compiles, executes, passes against a known-good app state; selector policy compliance (`data-cy` only); no `cy.wait(ms)`; independence (runs in isolation, not just in full-suite order) | Run your existing lint/test gates as the grader — this is nearly free since it reuses CI tooling |
| **Code (mutation-informed)** | Assertion strength: does the test fail when the feature is deliberately broken? Run against N seeded mutants of the target code; the generated test must catch a defined minimum fraction | Extends your Vol 2 mutation-testing item into an eval grader — the single best defense against "green test that verifies nothing" |
| **LLM-judge (rubric)** | Coverage completeness vs. the ask (happy/negative/edge per the case matrix your `/generate-e2e-test` prompt produces), code readability, convention adherence beyond what lint catches (naming, structure) | Rubric scored 1–5 per dimension, **not** a single holistic score — holistic LLM scores are the least reliable and least actionable grading mode |
| **Human calibration** | Sample 10–15% of LLM-judge-graded trials monthly; a human re-grades blind; track judge-vs-human agreement | Catches judge drift before it silently degrades what "pass" means |

### B2. Execution Skill

| Grader type | Checks |
|---|---|
| **Code** | Correctly triggers the intended run scope (not accidentally the whole suite when asked for one spec); correctly parses and reports pass/fail counts against a known fixture run with pre-labeled expected results |
| **Code** | Failure **classification accuracy** against your failure ledger's labeled historical cases (Vol 1 Allure design) — precision/recall per classification category (timing/pollution/data/environment/genuine-bug), since this skill's whole value is correct triage |
| **LLM-judge** | Quality of the generated summary/report language against your manager-report template rules (facts-only, correct classification citation) |

### B3. Healing Skill (highest scrutiny — see Section 6 for the dedicated safety framework)

| Grader type | Checks |
|---|---|
| **Code** | Given a labeled "genuinely healable" case (real locator/timing drift, seeded), does the fix restore passing behavior without touching assertions? Diff the PR: only locator/wait lines changed, zero lines touching `expect`/`should`/assertion values |
| **Code** | Given a labeled "should NOT heal" case (the failure is a real regression, seeded), does the skill correctly refuse and flag instead of silently patching? This is a **negative task** — its correct outcome is *inaction plus escalation*, and it is graded exactly as rigorously as the positive cases |
| **LLM-judge** | For flagged-not-healed cases: is the escalation report's stated reasoning sound (cites the right evidence for why this isn't locator/timing-class)? |

---

## 5. Suite C — End-to-End Trajectory & Outcome

Realistic asks run through the full agent, unconstrained (router decides everything). This is where interaction bugs surface that A and B individually can't catch.

**Grading order (per Anthropic's guidance, and worth stating as a house rule):**
1. **Outcome first.** Does the final state match the target — the right file changed the right way, the test suite in the right state, the right artifact produced? This is the pass/fail gate.
2. **Transcript second, but only for debugging.** When outcome grading fails, read the trajectory to classify *why* (misrouted? right skill, wrong output? tool misuse? scope creep beyond the ask?) using your existing session-failure taxonomy (WC/SG/TM/SE/SA/AW). Never grade the trajectory as the primary pass/fail signal — outcome is the stable contract; trajectories vary path-to-path even for equally correct solutions, and grading the path punishes valid alternate approaches.
3. **Watch for reward hacking.** Anthropic's own eval work found agents exploiting evaluation loopholes not available to real users (e.g., a coding agent reading privileged history it shouldn't have access to in production). For your agent: watch for a healing task "succeeding" by weakening an assertion instead of fixing the locator (technically restores green, violates the intent) — this is exactly why B3's assertion-diff check exists as a hard code grader, not something left to LLM judgment.

**Task design:** pull 15–20 realistic end-to-end scenarios directly from your team's actual recent asks (the richest source is your own usage logs/PR history once the agent has been in use a few weeks) plus a handful of deliberately multi-skill scenarios (generate a test, run it, watch it fail on a seeded locator issue, confirm the agent heals correctly in the same session).

---

## 6. The Healing Skill's Dedicated Safety Framework

Healing carries categorically more risk than generation or execution: a wrong heal doesn't just produce a bad test, it produces a **falsely green test that hides a real defect** — industry practice on this is unambiguous that this is the core failure mode to design against, and that many practitioners explicitly prefer a red test to a falsely green one, because a false pass costs far more once it reaches production.

**Diagnosis-first is the eval requirement, not just a design nicety.** Current practice categorizes test failures into six root-cause classes — selector, timing, data, runtime/environment, rendering, and interaction — and industry data suggests selector issues are a *minority* of real flakiness (commonly cited around a quarter to a third of cases), with the rest coming from the other categories. **This means your healing eval must have labeled cases across all failure categories your healer is allowed to touch, not just locator-drift cases** — if your healer is scoped to selectors and timing only (as your earlier design specified), the eval must also verify it correctly *declines* to act on data/runtime/rendering-class failures rather than overreaching.

**The four numbers to track on every healing eval run** (industry-standard self-healing KPIs, adapted as eval thresholds you set and defend, not blindly adopted):

| Metric | What it measures | Starting threshold to set (tune from your own data) |
|---|---|---|
| **False positive rate** | Healed a case that was actually a real bug (the assertion-diff + should-not-heal task set in B3) | Treat as a release gate: this is the number that, if it regresses, blocks shipping the healing skill update. Common industry framing targets low single digits. |
| **Automatic repair rate** | Of genuinely healable cases, what fraction resolved without human intervention | Track as a capability metric, not a gate — pushing this up must never come at the expense of the false-positive rate. |
| **Confidence-gated escalation rate** | Fraction of cases where the healer correctly abstained and routed to human review because confidence was insufficient | This should be visible and *reportable as a good thing* — an abstention is the skill working correctly, not failing. |
| **Audit-trail completeness** | Every heal has a full record: original locator, new locator, confidence signal, which skill/model call proposed it | 100% — this is a hard code-grader check, not a percentage to optimize. Ties directly to your audit checklist's traceability requirement. |

**The single highest-value eval task type for this skill:** seed a case where the correct-looking fix is a *decoy* — an element that moved for a legitimate reason (real regression) but happens to have a visually/structurally similar replacement element available (the exact "picks a similar but wrong button, test passes, bug ships" failure pattern documented in current self-healing critiques). Your eval suite needs several of these adversarial decoys, not just "obviously right" and "obviously wrong" cases — the decoys are where a shallow healer fails and a diagnosis-first one succeeds.

---

## 7. Suite D — Consistency (your explicit ask)

**The core statistical tool: pass@k vs. pass^k, and they answer different questions.**
- **pass@k** = probability of at least one success across k trials. Rises as k grows. This measures *capability* — can the agent do this at all, given enough tries.
- **pass^k** = probability of success on **all** k trials. Falls as k grows. This measures *reliability* — will it do this correctly *every time*, unattended, which is what "consistency" and "works as expected all the time" actually mean.

**Your stated goal is a pass^k problem, not a pass@k problem.** A skill with 95% pass@1 but only 77% pass^5 (0.95^5 ≈ 0.77) is not reliable enough to trust unattended for a healing agent that runs nightly against your whole suite — that's roughly one in four five-run sequences containing at least one bad outcome. Report pass^k, not just pass@1, for every suite above, at k=5 as your standard consistency check and k=10 for the healing skill specifically given its risk profile.

**Protocol:**
1. Every task in Suites A–C is run **5 times minimum** (10 for healing tasks) with identical inputs, in isolated trial environments (Section 8) so trials never contaminate each other.
2. Compute per-task pass^k, and separately, **variance in the specific failure mode** when it doesn't pass every time — a task that fails the same way every time (deterministic bug) is a different, easier problem than a task that fails differently each run (genuine model stochasticity, prompt fragility, or a race condition in your harness itself).
3. **Flag, don't just report, high-variance tasks.** Any task with pass^5 < pass@1 by more than a defined margin (e.g., a 20-point gap) goes on a remediation list — usually fixable by tightening the skill's instructions, adding a missing example, or narrowing an ambiguous trigger description, per your existing skill-calibration practice (K4 kata).
4. **A 0% pass^k or pass@k result is a signal to inspect the task/grader first, not the agent** — Anthropic's own finding is that near-zero pass rates at scale are disproportionately caused by ambiguous task specs or broken graders, not incapable agents. Before filing "the healing skill is broken," confirm the task's success condition is unambiguous and the grader is actually checking what you think it's checking.

**Sampling/temperature note:** if your agent harness exposes a temperature or sampling-diversity setting, run consistency suites at your **production setting**, not a lowered/deterministic one — testing consistency at temperature 0 when production runs otherwise measures a different system than the one users get.

---

## 8. Harness Architecture

**Extend, don't replace, what you have.** Your bash runner and eval spec template already provide the trial-execution and result-recording backbone for the two-stage generation pipeline; the additions this plan requires are structural, not a rewrite:

1. **Isolated trial environments.** Each trial (especially healing trials, which mutate files) must run against a fresh sandbox repo state — a git worktree or ephemeral clone per trial — so trial N's outcome never depends on trial N-1's side effects. This is the single most common cause of false "flakiness" in eval results: a dirty shared environment, not the agent.
2. **Skill-invocation logging.** The agent harness must emit, per trial, which skill(s) were invoked, in what order, with what inputs — this is your Suite A grader's raw data. If this isn't currently logged, add it before building Suite A; it's a prerequisite, not a nice-to-have.
3. **Multi-trial orchestration.** Your bash runner needs a loop: run task N times, collect N outcomes, compute pass@k/pass^k, store all N transcripts (not just the last one — you need the failing trials to diagnose variance).
4. **Three grader adapters.** Code graders (shell/Node scripts against the outcome — reuse your existing lint/test infrastructure directly), an LLM-judge adapter (a separate, ideally stronger or at minimum *different*, model than the one being evaluated — never let a skill grade its own output, which biases toward self-consistent-but-wrong judgments), and a human-calibration queue (sampled trials routed for manual review, with agreement tracked against the LLM judge).
5. **Consider a framework for the parts your bash script wasn't built for.** Multi-trial statistical aggregation, LLM-judge orchestration with rubric templates, and trend dashboards are exactly what dedicated eval frameworks (Braintrust, Promptfoo, or the open-source Harbor project, aimed specifically at containerized agent evaluation) are built for — evaluate whether wrapping your existing graders in one of these buys you the aggregation/reporting layer for less effort than building it in bash. Your code graders and task specs port over either way; only the orchestration layer changes.
6. **Suite tagging for CI gating.** Tag every task by suite (A/B1/B2/B3/C/D) and by whether it's a **capability eval** (exploring current ability, informational) or has **graduated to a regression eval** (a previously-passing case that must never regress, CI-blocking). New skill versions run the full capability suite for information; merges are blocked only on regression-suite failures — this is how your estate avoids both false confidence (nothing gates merges) and paralysis (everything blocks every merge).

---

## 9. Step-by-Step Implementation Plan

**Phase 0 — Inventory & prerequisite instrumentation (2–3 days)**
1. Enumerate every skill the agent can call, its trigger description, and its expected output type.
2. Confirm skill-invocation logging exists (Section 8.2); add it if not — everything downstream depends on it.
3. Mine 30–50 real asks from actual usage/PR history; hand-tag each with the "correct" skill(s) — this seeds Suite A and doubles as your first balanced-pairs source.

**Phase 1 — Suite A: Routing (1 week)**
4. Build the routing task set per Section 3: balanced positive/negative pairs, adjacent-ambiguity probes, at least one multi-skill case.
5. Wire the code grader (skill-invocation-log check) into the bash runner.
6. Run once at k=1, review the confusion matrix, fix the obvious misroutes (usually trigger-description calibration, per your K4 kata practice) before proceeding — no point building capability evals on top of broken routing.

**Phase 2 — Suite B: Per-skill capability (2 weeks, parallelizable across skills)**
7. B1 (generation): wire lint/test/independence code graders (reuse CI tooling directly); build the mutation-informed assertion-strength check; draft the LLM-judge rubric (dimension-scored, not holistic).
8. B2 (execution): build the classification-accuracy grader against your labeled ledger history.
9. B3 (healing): build the assertion-diff code grader (Section 6) **first, before anything else in this phase** — it is your highest-risk gate and the cheapest to automate (a diff check, not a judgment call).

**Phase 3 — Healing safety framework (1–2 weeks, can overlap Phase 2)**
10. Build the labeled dataset across all six failure categories (Section 6) — genuinely-healable and should-NOT-heal cases in each, including several adversarial decoys.
11. Instrument the four healing KPIs; set initial thresholds (start conservative — you can loosen a false-positive gate later with evidence, you cannot un-ship a masked bug).
12. Negative-test the escalation path explicitly: confirm low-confidence cases produce a human-review artifact, not a silent skip.

**Phase 4 — Suite C: End-to-end trajectory (1 week)**
13. Build 15–20 realistic multi-skill scenarios from real usage.
14. Confirm outcome-first grading order is implemented (Section 5); spot-check that transcripts are being read for debugging, not for primary grading.

**Phase 5 — Suite D: Consistency layer (3–5 days, mostly orchestration work)**
15. Add the multi-trial loop and pass@k/pass^k computation to the runner (Section 7).
16. Run all of Suites A–C at k=5 (k=10 for B3/healing tasks); flag high-variance tasks for remediation before declaring any suite "done."

**Phase 6 — CI integration & graduation (ongoing from here)**
17. Tag stable, consistently-passing tasks (pass^5 ≥ your bar, typically 90%+) as regression-suite members; wire regression-suite failures as merge blockers for changes to the relevant skill/agent files, per your existing audit checklist's evidence requirement for `.github/` changes.
18. Set a recurring cadence (monthly, or on any skill/instruction change): re-run the full suite set, track pass^k trend over time, refresh the golden dataset with newly-mined real asks and any newly-discovered decoy cases from production healing events.
19. Schedule judge calibration: monthly human-vs-LLM-judge agreement check on a sampled 10–15% of B1/C trials; recalibrate the rubric or swap the judge model if agreement drifts.
20. Close the loop: route eval failures (especially healing false positives and routing misfires) into your estate's self-improvement mechanism — a real eval failure is exactly the kind of "correction pattern" that should produce a proposed instruction/skill amendment PR, not just a red mark in a dashboard.

---

## 10. Metrics & Reporting

**What goes on the dashboard, in order of what management actually needs to see:**

| Metric | Reported as | Why it's the headline |
|---|---|---|
| Healing false-positive rate | % + trend | The one number that, if it moves the wrong way, is a stop-ship signal |
| pass^5 per skill (and pass^10 for healing) | % + trend | This *is* the answer to "does it work consistently" — the direct answer to your original question |
| Routing precision/recall per skill | Confusion matrix + trend | Explains *why* an end-to-end failure happened when it does |
| Regression suite pass rate | % (should sit near 100%; any drop is urgent) | Protects what already works while you keep extending capability |
| Human-vs-judge agreement | % | Tells you whether the other numbers on this table can be trusted |

Feed these into your existing cost-of-quality accounting and the quarterly audit's measurement section — this eval program *is* the evidence layer that audit checklist §6.4 requires, applied to the automation agent itself rather than to the test suite it produces.

---

## 11. What Would Make This Plan Wrong (read before building)

1. **If your agent doesn't currently log skill invocations, everything in Suite A is blocked until it does.** Don't skip Phase 0 step 2 to feel faster — you'll build a routing suite you can't grade.
2. **If the same model that runs a skill also grades that skill's LLM-judge tasks, your capability numbers are inflated and untrustworthy.** Use a distinct judge model or a distinct, colder invocation.
3. **If trial environments aren't isolated, your consistency numbers measure environment flakiness, not agent flakiness** — you'll chase a phantom reliability problem in the wrong system.
4. **If the healing safety dataset only contains "obviously healable" and "obviously not," it will pass and still ship the failure pattern that matters — the plausible decoy.** Section 6's adversarial cases are not optional polish; they're the point of the suite.

*Companion docs: qa-eval-harness (the existing pipeline this extends), enterprise audit checklist §5 and §6.4, Allure analysis design (source of the failure-classification ground truth for B2), agentic kata set K4 (skill-description calibration technique referenced in Phase 1).*
