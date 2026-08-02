# The Eval-to-QA Rosetta Stone
### Every eval term, mapped one-to-one against the testing vocabulary your team already knows

**The premise of this document:** none of this is as new as it sounds. Your team has spent years mastering test cases, test runs, assertions, and regression suites. AI evaluation is largely the same discipline, renamed for a system that behaves less predictably than the code you're used to testing. **Where the mapping is exact, trust it completely — you already know that concept.** Where it's close-but-not-quite, the gap is called out explicitly, because a false "it's exactly the same" assumption is more dangerous than not knowing the term at all. Read this alongside `ai-eval-terminology-glossary.md` if you want the deeper definitions — this document's only job is the translation.

---

## The Core Mapping (learn this table first — everything else builds on it)

| AI-Eval Term | Traditional QA Equivalent | Match | Notes |
|---|---|---|---|
| **Task** | **Test case** | Exact | A defined ask plus a defined success condition — same thing, same idea, same purpose. If you've ever written "given X, expect Y," you've written a Task. |
| **Trial** | **Test run / test execution** | Exact | One execution of a test case. The only reason "trial" exists as a separate word is that you'll run the same Task multiple times on purpose (see pass@k / pass^k below) — something you'd only occasionally do with a traditional deterministic test. |
| **Agent harness** | **System Under Test (SUT)** | Exact | The thing being tested. Your Cypress app-under-test and an agent harness occupy the exact same conceptual slot — the difference is only that this SUT can take multiple different actions for the same input. |
| **Evaluation harness** | **Test framework / test runner** | Exact | Cypress, Mocha, JUnit — whatever runs your tests, records results, and reports them is your evaluation harness's direct ancestor. Your bash runner script *is* one. |
| **Transcript / Trajectory** | **Execution log / test trace** | Close | Same idea — a record of what happened during the run — but richer: it includes which tools/skills were called and often the model's stated reasoning, not just log lines and stack traces. |
| **Outcome** | **Actual result** | Exact | What actually happened, checked against what should have happened. Same concept you've been comparing "actual vs. expected" against your whole career. |
| **Grader** | **Assertion** | Close | A grader decides pass/fail, exactly like an assertion does — but a grader can be a script (a normal assertion), a model (something new), or a human (a manual test step). Traditional assertions are always the first kind only. |
| **Suite** | **Test suite** | Exact | Literally the same word, same concept. No translation needed. |

---

## Grading & Judging

| AI-Eval Term | Traditional QA Equivalent | Match | Notes |
|---|---|---|---|
| **Code grader** | **Assertion** (`expect(...).to.equal(...)`) | Exact | This is just an assertion. Nothing new here at all. |
| **LLM-as-judge** | **A manual QA reviewer's judgment call, automated** | Close | Think of the step where a human tester looks at a screen and says "yes, that looks right" — for something too subjective for a hard assertion (visual polish, tone, coverage completeness). An LLM judge automates that specific kind of call, no more and no less. |
| **Rubric** | **Acceptance criteria checklist** | Exact | A rubric is your acceptance-criteria checklist, scored dimension by dimension instead of one pass/fail. |
| **Holistic score** | **A single "looks good to me" sign-off with no detail** | Exact (as a warning) | You already know why this is weak in traditional QA review too — "LGTM" tells you nothing actionable. Same weakness, same reason to avoid it. |
| **Self-grading bias** | **Letting a developer sign off their own QA** | Exact | Your team already enforces separation of duties for exactly this reason — a developer approving their own change is a known conflict of interest. Letting a model grade its own output is the identical problem in a different costume. |
| **Judge calibration** | **Auditing your QA lead's manual sign-offs against a second reviewer** | Close | The periodic "does this reviewer's judgment still match the team's standard" check — same purpose, applied to a model instead of a person. |
| **Ground truth / labeled data** | **Expected results** | Exact | The known-correct answer you grade against. Same concept, same word almost. |
| **Confusion matrix** | *(No strong direct equivalent — closest: a defect-classification accuracy report)* | Partial | Traditional QA doesn't usually formalize "which category did we predict vs. which category was it actually" this explicitly — this concept is closer to something out of data/ML QA than classic functional testing. Worth learning as genuinely new. |
| **Precision / Recall** | *(No strong direct equivalent — closest: false-alarm rate vs. miss rate for a monitoring/alerting system)* | Partial | If you've ever tuned a flaky-test detector or an alerting threshold, you've felt this trade-off even without the vocabulary. Genuinely worth learning as new terminology, not just relabeling something you already had a name for. |

---

## Non-Determinism, Reliability & Consistency

| AI-Eval Term | Traditional QA Equivalent | Match | Notes |
|---|---|---|---|
| **Non-determinism** | *(Closest familiar concept: a flaky test — but read the inversion note below)* | Partial, and important | This is the single biggest mindset shift in the whole document — see "Where the Mapping Breaks Down" below before you assume this is just flakiness. |
| **pass@k** | *("Retried until it passed" — but as a measured metric, not a swept-under-the-rug workaround)* | Partial, and important | Also covered in the breakdown section — traditional QA treats "passed on retry" as something to be suspicious of; eval treats pass@k as a legitimate capability number. |
| **pass^k** | **Running a test N times in CI specifically to catch flakiness** | Close | This one you already do, informally — "let's run this suite 10 times before we trust it's stable." pass^k just gives that existing instinct a name and a formula. |
| **Isolation (isolated trial)** | **Test independence / clean test environment per run** | Exact | The exact same discipline that makes you reset fixtures and avoid test-order dependencies. Same reasoning, same payoff. |
| **Flakiness (of the agent itself)** | *(Closest: an unreliable manual tester whose judgment varies day to day — not a flaky automated test)* | Partial | Careful with this one — see the breakdown section. |

---

## Dataset & Test Design

| AI-Eval Term | Traditional QA Equivalent | Match | Notes |
|---|---|---|---|
| **Golden dataset** | **Regression pack / golden master test set** | Exact | Your curated, trusted set of known-good test cases — same concept, same purpose. |
| **Balanced problem set** | **Positive and negative test cases** | Exact | This is equivalence partitioning — you were taught to always write both the "should happen" and "should NOT happen" case. Same principle, just now applied to whether a skill *fires*, not just whether a function *returns the right value*. |
| **Adversarial case / decoy case** | **A deliberately tricky edge case designed to catch a known bug pattern** | Close | Think of the test case you write specifically because you know a particular kind of mistake is easy to make — that instinct, formalized. |
| **Ablation / counterfactual test** | *(Closest: toggling a config flag on/off and comparing suite results)* | Partial | Less common in traditional functional QA, more familiar if you've done any A/B-style or feature-flag testing — worth learning as a genuinely useful new technique, not just a renamed old one. |
| **Regression suite vs. capability suite** | **Regression suite vs. exploratory/smoke testing** | Close | Regression suite maps exactly. "Capability suite" is closer in spirit to exploratory testing — you're finding out what currently works, not enforcing that it must, and "graduating" a capability task is like promoting a good exploratory finding into a permanent regression case. |
| **Edge case / boundary case** | **Edge case / boundary case** | Exact | Same term. You already own this one completely. |
| **Same-capability ambiguity** | *(Closest: two overlapping test suites both claiming ownership of the same bug)* | Partial | A genuinely newer problem shape — two *skills* competing to handle one ask, rather than two tests covering the same code. |

---

## Agent-Specific Concepts

| AI-Eval Term | Traditional QA Equivalent | Match | Notes |
|---|---|---|---|
| **Routing / dispatch** | **Test selection / which suite runs for which trigger** | Close | Similar to how your CI decides which test suites to run based on what changed — except here the "router" is a model making a judgment call, not a fixed path-matching rule. |
| **Tool call** | **API call / a Cypress command** | Close | Every `cy.get()`, every API request your automation makes — that's the same shape of action, just performed by an agent's own choice rather than a line you wrote. |
| **Skill** | **A shared test utility / library, that only loads when relevant** | Partial | The reusable-capability part is familiar (your custom commands and page objects are exactly this). The "only loads when the ask matches" part — progressive, conditional loading — is genuinely new; nothing in traditional QA tooling decides on its own when to pull in a helper library. |
| **Orchestration** | **CI pipeline orchestration** | Close | Coordinating multiple steps/stages toward one goal — same shape as a multi-stage pipeline, just happening inside one agent's reasoning instead of across pipeline stages. |
| **Multi-agent handoff** | **Staged pipeline (unit → integration → e2e), passing state forward** | Close | Your build pipeline's stage-to-stage handoff is the closest familiar shape. |
| **Autonomy / agentic loop** | **Automated pipeline stage vs. a manual approval gate** | Exact | You already know this trade-off from CD pipelines — some stages run unattended, some wait for a human. Same concept, applied to how many actions an agent takes before checking in. |
| **Tool boundary (least privilege)** | **Restricted test-account permissions / read-only staging access** | Exact | You already provision test accounts with limited scope on purpose. Same discipline, same reasoning, applied to what an agent's allowed to do. |

---

## Failure Modes & Risk

| AI-Eval Term | Traditional QA Equivalent | Match | Notes |
|---|---|---|---|
| **Reward hacking** | **"Coverage theater" — writing a test that passes trivially just to hit a metric** | Exact | You've seen this: a test that technically increases code coverage but asserts nothing meaningful. Reward hacking is the exact same failure pattern, just happening inside the agent's own behavior instead of a lazy test author. |
| **Scope expansion (scope creep)** | **Scope creep** | Exact | Same word, same meaning, same reason it's a problem. |
| **Silent assumption** | **An untested, implicit assumption not covered by acceptance criteria** | Exact | The bug class where nobody wrote down what should happen, so someone guessed — same failure, same root cause, whether "someone" is a developer or an agent. |
| **Prompt injection** | **Injection attack (SQL injection, etc.) via unvalidated input** | Close | Same family of vulnerability — untrusted content being interpreted as instructions instead of data. If your team understands why you sanitize inputs, you already understand the shape of this risk. |
| **Hallucination** | *(Closest: a stub/mock returning plausible-but-wrong data)* | Partial | Worth learning as a distinct concept — it's less "the test lied" and more "the system under test invented a fact that sounds real." |
| **Drift** | **A test suite going stale — still green, but no longer reflecting the real app** | Exact | Every QA team has lived this: tests that pass but have quietly stopped meaning anything because the app moved on. Same phenomenon, now also applied to instructions, skills, and judge models. |

---

## Program-Level Concepts

| AI-Eval Term | Traditional QA Equivalent | Match | Notes |
|---|---|---|---|
| **CI gating** | **CI gating** | Exact | Same term, same mechanism — a failing check blocks a merge. |
| **KPI / trend tracking** | **Flaky-test trend dashboard / test metrics over time** | Exact | If you've ever tracked flaky-test rate or pass-rate trend in a dashboard, you've already done this — just aimed at a different set of numbers. |
| **Benchmark** | **An industry-standard test suite vs. your own regression suite** | Close | The distinction between "how do we compare generally" and "does our specific thing work" — same distinction you'd draw between an industry benchmark and your own internal test pack. |

---

## Where the Mapping Breaks Down — Read This Before You Assume It's All the Same

Four places where treating this as "just relabeled QA" will actively mislead you:

**1. pass@k inverts a QA instinct you already trust.** In traditional testing, a test that fails and then passes on retry is treated with suspicion — "why did it fail the first time?" is a real question, and a flaky test that eventually passes is usually a problem to fix, not a result to report. **pass@k treats "succeeded at least once in k tries" as a legitimate, reportable capability number.** That's a genuinely different stance, not a renamed old one — know which framing you're in before you report a number.

**2. Agent non-determinism isn't the same bug class as a flaky test.** A flaky test is usually a *bug in the test* (bad waits, shared state, timing races) — the underlying code is deterministic and the test is at fault. An agent can be non-deterministic **by nature**, with no bug anywhere — it's sampling from probabilities as designed. Don't debug agent inconsistency the way you'd debug test flakiness; the fix for a flaky test (isolate state, add proper waits) often doesn't apply, and the actual fix is usually tightening an instruction or a skill description instead.

**3. "Grading" isn't always an assertion, and that changes what "objective" means.** A code grader is exactly your familiar assertion — fully objective, fully trustworthy in the way you're used to. An LLM judge is not that, even though it produces a pass/fail. It's closer to a manual reviewer's opinion than a deterministic check, and it needs the same skepticism and calibration you'd apply to any human reviewer's judgment — not the blind trust you'd give a green checkmark from an assertion.

**4. "Effect-based eval" (for instructions and skill-content) has no clean traditional-QA parent at all.** You've never had to ask "does this code comment actually change developer behavior" and test *that* — but that's exactly the shape of question an instruction-compliance eval asks. This one is worth learning as genuinely new rather than searching for a QA analogy that doesn't quite exist.

---

## How to Use This Document

Next time someone on the team says *"write a Task with 5 Trials and grade the Outcome with a code grader, then check pass^5,"* mentally run it through this table: *"write a test case, run it 5 times, check the actual result with an assertion, then confirm all 5 runs passed."* **You already know how to do that.** The vocabulary is new; the discipline underneath almost all of it isn't.

*Companion: `ai-eval-terminology-glossary.md` for full definitions and examples of each term in isolation.*
