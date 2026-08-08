# AI-Led STLC — Eval Framework & Determinism Plan
### Quality and Consistency Across Every Agent, Skill, Instruction, and Prompt

This extends the eval harness pattern your team already knows (evals.json / with_skill vs without_skill / grading.json / benchmark.json, the Task↔test-case / Trial↔test-run / Agent-harness↔system-under-test mapping) to cover all four primitive types across the 43-primitive catalog — and adds Part 2, a standalone plan for getting deterministic, repeatable results out of systems that are, by default, non-deterministic.

---

# PART A — Eval Framework by Primitive Type

Each primitive type is tested for something different. Treating all four the same way is the most common mistake teams make when they try to scale eval beyond a single skill.

| Primitive | What Correctness Means | Testing Vocabulary |
|---|---|---|
| Skill | Does this one function produce the right output for a given input? | Test case → test run → skill under test |
| Agent | Does the right sequence of skills fire, in the right order, with the right handoffs, ending in a correct human-review gate? | Scenario → trajectory → agent under test |
| Instructions | Does applying this rule set measurably change/improve the skills that consume it? | Rule → compliance check → consuming skill |
| Prompt | Does this entry point correctly parse varied real-world phrasing into the right agent invocation with the right inputs? | Utterance → intent match → prompt under test |

## A.1 Skill-Level Eval (Extends Your Existing Pattern)

You already have this pattern working for `cypress-code-review`. Apply it identically to all 23 skills in this initiative — no new methodology needed here, just scale:

- `evals.json` — labeled test cases per skill (input → expected output)
- `with_skill` / `without_skill` comparison — confirms the skill actually adds value over baseline Copilot behavior
- `grading.json` — objective pass/fail for structured-output skills (e.g., `spec-parse` — did it extract the right fields), rubric-based scoring for generative skills (e.g., `report-summarize` — does it hit the quality bar)
- `benchmark.json` — pass rate tracked over time, per skill version

**New requirement for this initiative specifically**: every skill's `evals.json` must include cases drawn from real historical data (real Allure reports, real ADO work items, real API specs) — not synthetic-only. Synthetic test cases validate that a skill runs; historical data validates that it's actually right about your organization's real patterns.

## A.2 Agent-Level Eval (Extends Your "Works as Expected All the Time" Goal)

This is the piece you flagged as still needed in prior work — here's the concrete plan.

### A.2.1 Trajectory Grading
For each agent, define expected trajectories: the correct sequence of skill calls for a given scenario. Example for `report-cycle-orchestrator`:
```
Scenario: "Allure report with 3 failures — 1 product bug, 1 flaky, 1 stale locator"
Expected trajectory:
  1. allure-parse called once, extracts 3 failures
  2. failure-classify called 3 times, one per failure
  3. report-summarize called once, on all 3 classified failures
  4. ledger-update called once, appending 3 entries
  5. healer called once, only for the stale_locator failure
  6. Output staged for human review — NOT auto-published
```
Grade the actual trajectory against this: correct skills called, correct order, correct call count, and critically — **did it stop at the human-review gate** rather than proceeding past it. A trajectory that produces the right final output but skips the review gate is a failing trajectory, not a passing one — the gate is part of what's under test, not a separate concern.

### A.2.2 Consistency Across Repeated Trials
"Works as expected all the time" is directly a determinism question — see Part B. The agent-level eval requirement: run each scenario N times (recommend N=10 minimum for pre-production, N=5 for regression checks on minor updates) and measure trajectory consistency, not just single-run correctness.

### A.2.3 Composite (End-to-End) Eval
Beyond individual skill evals, run the full agent on 3-5 realistic end-to-end scenarios per phase (as already planned in each phase's deep-dive) and grade the final output a human would actually see — this catches integration bugs that pass every individual skill eval but fail when chained (e.g., `failure-classify`'s output schema drifts slightly and `report-summarize` silently mishandles a field).

## A.3 Instructions-Level Eval (New Methodology — Instructions Don't Execute, So Test Indirectly)

An instructions file isn't callable, so you can't run it directly against test cases. Test it via the skills/agents that consume it.

### A.3.1 Compliance Testing
For each instructions file, pick 2-3 consuming skills and run their existing eval suites twice: once with the instructions file present, once with it removed (or with a prior version). Compare:
- Does output compliance with the rule set measurably improve? (e.g., does `test-data-generate` actually cover all five categories in `negative-case-taxonomy` consistently, or does it drift toward covering 3 of 5 without the instructions reinforcing it?)
- Does removing/reverting the instructions cause a measurable regression? If not, the instructions file isn't actually influencing behavior and needs rework, not just a documentation update

### A.3.2 Conflict Linting
As your shared instructions files grow (per the consolidation plan — `negative-case-taxonomy`, `definition-of-ready`, `ai-artifact-style-guide`), add a periodic check: do any two instructions files that apply to the same skill/agent contradict each other? This can start as a manual review checklist and become an automated cross-reference check (using the `applies_to_skills`/`applies_to_agents` frontmatter from the primitive framework) once you have more than a handful of instructions files.

### A.3.3 Grading
Pass/fail isn't quite right here — grade as a **compliance delta**: percentage-point improvement in rule adherence with the instructions present vs. absent, tracked in that instructions file's own `benchmark.json`.

## A.4 Prompt-Level Eval (New Methodology — Testing the Entry Point)

Prompts fail in a specific way: a human (or a scheduler) phrases the request slightly differently than expected, and the wrong agent fires, or the right agent fires with a missing/malformed input.

### A.4.1 Utterance Test Set
For each prompt, build a labeled set of realistic phrasing variations — not just the one example in the prompt file's documentation:
```json
{
  "prompt": "report-cycle.prompt",
  "test_utterances": [
    {"input": "Run the report cycle for this Allure output: /path/to/report.zip", "expected_agent": "report-cycle-orchestrator", "expected_inputs": {"allure_report_path": "/path/to/report.zip"}},
    {"input": "here's this week's allure results, summarize it", "expected_agent": "report-cycle-orchestrator", "expected_inputs": {"allure_report_path": null}, "expected_behavior": "should ask for the path, not guess"},
    {"input": "heal my broken tests", "expected_agent": null, "expected_behavior": "should NOT trigger report-cycle — this is an ambiguous/out-of-scope request, should clarify"}
  ]
}
```
This is especially important for the Copilot Studio conversational triggers (Phase 4), where real phrasing variety is much higher than a VS Code prompt file typically sees.

### A.4.2 Grading
- Intent match rate: % of utterances correctly routed to the intended agent
- Input extraction accuracy: % of required inputs correctly parsed when present
- Graceful-failure rate: % of missing/ambiguous-input cases that correctly ask for clarification instead of guessing or silently proceeding with a wrong assumption — this matters as much as the success cases

---

# PART B — Determinism Plan

This is the harder problem, worth its own section because it's the one your team hasn't dealt with yet and it's easy to under-scope. LLM-based systems are non-deterministic by default — same input, different output, run to run. "Deterministic results" doesn't mean forcing identical text every time (that's the wrong bar for generative output); it means **bounded, measured, acceptable variance**, with the acceptable bar defined per primitive type rather than assumed to be 100% identical.

## B.1 Why Outputs Vary, and What You Can Actually Control

| Source of variance | Controllable? | Lever |
|---|---|---|
| Sampling temperature | Yes | Set to 0 or near-0 for extraction/classification skills; can't fully eliminate variance even at 0 due to floating-point non-associativity at scale, but it's the single biggest lever |
| Model version drift (provider updates the underlying model) | Partially | Pin model version where the API allows it; if not pinnable, track model version in your eval's `benchmark.json` and re-baseline on forced upgrades, don't assume silent compatibility |
| Prompt/context assembly order | Yes | Keep instructions/context assembly order fixed and deterministic in the agent orchestration code — don't let context get assembled in a variable order (e.g., from an unordered data structure) |
| Ambiguous or underspecified input | Partially | Tighten skill input schemas (§0.2 of the technical design) so less is left to the model's judgment; validate inputs before the skill call, reject underspecified ones rather than letting the skill guess |
| Natural language generation variance (report tone, phrasing) | No, and don't try to fully eliminate it | This is where you shift the eval bar from "identical" to "semantically consistent" (§B.3) |

## B.2 Determinism Tier by Primitive Type

Not every primitive needs the same bar. Classify each of your 23 skills into one of two tiers before writing its eval:

### Tier 1 — Structured/Extraction Skills (High Determinism Bar)
`allure-parse`, `spec-parse`, `context-gather`, `change-impact`, `duplicate-check` (the matching logic), `defect-history-analyze`, `complexity-signal`

These should produce near-identical structured output for identical input. Target: **≥98% exact-match consistency** across N=10 repeated trials on the same input.

**How to get there:**
- Temperature = 0
- Enforce structured output (JSON schema-constrained generation, not free-form text parsed after the fact) — this alone removes most of the variance for extraction tasks
- Prefer rule-based/deterministic code over an LLM call wherever the task is genuinely mechanical (e.g., signature normalization in §0.3 of the technical design should be pure regex/hashing, not an LLM call at all — reserve LLM calls for the parts that genuinely need judgment)
- Where an LLM call is unavoidable, validate output against the JSON schema and reject/retry on schema violation rather than accepting malformed output as "close enough"

### Tier 2 — Judgment/Generative Skills (Semantic Consistency Bar, Not Exact Match)
`failure-classify`, `report-summarize`, `draft-bug`, `case-generate`, `plan-draft`, `risk-score` (the weighting is deterministic, but any narrative rationale attached isn't), `healer` (candidate ranking is fairly deterministic; the explanation text isn't), `ambiguity-check`, `dor-check`, `completeness-gap`, `subset-recommend`, `test-data-generate`, `api-script-generate`

These will legitimately produce different phrasing run to run — that's fine and expected. What must NOT vary: the underlying decision (category assigned, severity suggested, tier assigned, pass/fail judgment).

**How to get there:**
- Separate the decision from the explanation in the output schema — e.g., `failure-classify` returns `category: "flaky"` (this must be consistent) and `rationale: "..."` (this can vary in phrasing) as distinct fields, graded differently
- Run N=10 trials per eval case; measure **decision consistency** (did `category` come back the same value across all 10 runs?) as a hard pass/fail metric, separately from **rationale quality** (graded on a rubric, allowed to vary in wording)
- Low temperature (0.1-0.3, not 0) for these — some sampling is fine and even desirable for report tone, but keep it low enough that the underlying judgment doesn't flip
- For genuinely close-call decisions (e.g., severity right on a boundary), widen the acceptable-consistency bar deliberately rather than pretending the model should be certain about something inherently ambiguous — flag these cases for human review by design (confidence threshold, per the standard I/O envelope), not as an eval failure

## B.3 Semantic Consistency Grading (For Tier 2 Generative Output)
When exact-match isn't the right bar, grade with:
- **Rubric-based grading** (already your pattern from the agentskills.io methodology) — does the output hit the required content points, regardless of exact phrasing?
- **Semantic similarity check** as an automated pre-filter (embedding similarity between N trial outputs) to flag outputs that drifted meaningfully, then human-reviewed for cases below a similarity threshold — not a replacement for rubric grading, a cheaper first pass to catch obvious drift before a human looks
- **Golden output comparison with tolerance** — maintain 1-2 "golden" example outputs per eval case (not for exact match, but as the human-reviewed reference a grader compares new outputs against for rubric scoring)

## B.4 Repeated-Trial Testing Protocol

Standard protocol to add to every skill's and agent's eval suite, regardless of tier:

```
For each eval case:
  1. Run the skill/agent N times (N=10 for pre-production gate, N=5 for routine regression checks)
  2. Tier 1 skills: compute exact-match rate across the N outputs — must exceed 98%
  3. Tier 2 skills: extract the "decision" fields, compute decision-consistency rate — must exceed
     a defined threshold per skill (recommend starting at 90%, tightening as you gather data)
  4. Log variance over time in benchmark.json — a skill whose consistency degrades after a
     model/version update is a regression, caught by this protocol specifically, not by a
     single-run eval that would look identical to last week's single run
```

## B.5 Version Pinning & Change Control

- Pin the model version per skill/agent wherever the platform allows it; where it doesn't, record the model version at each eval run in `benchmark.json` so a consistency drop can be correlated to a provider-side model update rather than assumed to be your own regression
- Any change to: the skill's prompt/logic, its instructions dependencies, or the underlying model → triggers a full N=10 re-run before merge, not just the standard single-pass eval — this is a stricter gate than routine eval re-validation (technical design §0.5) specifically because determinism regressions don't show up in a single run
- Track a **determinism score** per skill (its measured consistency rate) as a first-class field in `benchmark.json`, reported alongside accuracy — a skill can be accurate on average and still fail this program's bar if its determinism score is unstable, because unstable skills erode the human reviewer's trust even when individual outputs are usually fine

## B.6 What "Deterministic" Realistically Means for This Program

Set this expectation with your team and with leadership now, so nobody is later surprised: **Tier 1 skills will feel deterministic in practice** (>98% exact match is close enough to indistinguishable from fully deterministic for operational purposes). **Tier 2 skills will never be word-for-word deterministic, and design shouldn't chase that** — the actual goal, and the one worth reporting as "deterministic results," is that the *decisions* these skills make are highly consistent even when the *phrasing* isn't. That distinction is worth stating explicitly in the leadership briefing's metrics section if this eval work gets reported upward — "consistent decisions, natural language variation in explanations" is an accurate and still-impressive claim; "fully deterministic" is not accurate for half your skill catalog and shouldn't be claimed.

---

## Summary: What Gets Added to Each Primitive's Eval Suite

| Primitive Type | Existing Pattern | New for This Initiative |
|---|---|---|
| Skill | evals.json, with/without comparison, grading.json, benchmark.json | Tier classification (1 or 2), repeated-trial protocol (§B.4), determinism score in benchmark.json |
| Agent | (not previously built) | Trajectory grading (§A.2.1), human-review-gate compliance as a graded trajectory element, N-trial consistency (§A.2.2) |
| Instructions | (not previously built) | With/without compliance delta (§A.3.1), conflict linting (§A.3.2) |
| Prompt | (not previously built) | Utterance test set (§A.4.1), intent-match + graceful-failure grading (§A.4.2) |
