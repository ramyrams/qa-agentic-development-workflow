# Eval Plans by Primitive: Instructions · Prompts · Skills · Agents
### Why one eval methodology doesn't fit all four, and the specific plan for each

**The organizing question for this whole document:** *can this primitive be independently invoked and produce a trial?* If yes, it gets a trial-based eval (Task→Trial→Grader→Outcome, as built in your eval implementation plan). If no, it gets an **effect-based eval** — you measure its influence on something else's behavior instead.

| Primitive | Independently invokable? | Eval paradigm | Consistency metric applies? |
|---|---|---|---|
| **Instructions** | No — always-on, passive | Effect-based: compliance rate + counterfactual delta | Yes, but measures *enforcement stability*, not the artifact itself |
| **Skills — triggering** | No — model decides, given an ask | Effect-based: routing precision/recall | Yes — trigger reliability across repeated identical asks |
| **Skills — content** | No — only exercised via whichever agent loads it | Effect-based: delta (with vs. without) | Yes — same delta, repeated k times |
| **Skills — bundled scripts** | Yes — they're just code | Direct: unit testing | N/A — deterministic code has no consistency question |
| **Prompts** | Yes — `/prompt-name` triggers a full agent run | Trial-based, same paradigm as agents, plus input-boundary tests | Yes — pass^k, identical to agent methodology |
| **Custom agents** | Yes — selected and run directly | Trial-based (fully covered in your existing eval plan/tooling guide) | Yes — pass^k, already specified |

Two primitives (prompts, agents) reuse the trial-based machinery you already built. Two (instructions, skills) need a genuinely different kind of eval, detailed below — **this is the real gap this document closes.**

---

## 1. Instructions — Effect-Based Eval

**The core problem statement:** an instruction file makes a claim — "the agent will always do X in this repo." That claim is falsifiable, but only by watching what agents *actually do* across many unrelated tasks, not by running the instruction file itself.

### 1.1 Compliance-rate eval (the primary suite)

For each **checkable rule** in the instruction file, write a code grader that inspects agent output for that rule specifically, then run a representative set of realistic tasks (15–20, spanning the kinds of asks the repo actually gets) and measure the rule's compliance rate independent of task success.

```yaml
# eval/tasks/instructions/compliance-suite.yaml
rules:
  - rule_id: selector-policy
    source: copilot-instructions.md
    statement: "Selectors: data-cy only. Never CSS classes, tags, or text selectors."
    grader: code
    check: "grep -E \"cy\\.get\\(['\\\"]\\.[\\w-]+\" <diff> → FAIL if match"
  - rule_id: no-hard-waits
    source: cypress-e2e.instructions.md
    statement: "No cy.wait(<milliseconds>)."
    grader: code
    check: "grep -E \"cy\\.wait\\([0-9]+\\)\" <diff> → FAIL if match"
  - rule_id: negative-path-required
    source: copilot-instructions.md
    statement: "Every new feature: at least one negative-path test."
    grader: llm-judge   # not mechanically checkable — needs semantic judgment
    rubric: "Does the generated spec include a test for at least one failure/invalid-input case?"
```

**Run every task in your existing task library (routing/capability/e2e tasks from the agent eval plan) through these rule graders as a secondary pass** — you don't need a separate task set; you're extracting an additional signal from trials you're already running for other reasons. Report **compliance rate per rule**, not one aggregate score — a 95% aggregate can hide one rule sitting at 60%, and that's the rule you need to fix.

### 1.2 Counterfactual (ablation) eval — proves the instruction is doing anything at all

This is the formalized, automated version of the instruction-delta kata your team already practices manually:

1. Run a task set **with** the instruction file present.
2. Run the **identical** task set with that specific instruction file removed (or one rule commented out) — everything else unchanged.
3. Diff compliance rates per rule between the two runs.

**A rule whose compliance rate doesn't drop when removed is not being enforced by the instruction — the model was already doing it anyway, or the instruction isn't reaching the model for that task type (glob problem, or the rule is buried in a bloated file and getting lost).** This is the single most valuable eval you can run on instructions, because it separates "rules I wrote" from "rules that are actually working" — and teams almost never check this.

```bash
# eval/runner/instruction-ablation.sh
#!/usr/bin/env bash
RULE_ID="$1"
INSTRUCTION_FILE="$2"

# Baseline: with instructions
bash eval/runner/run-suite.sh eval/tasks/capability/generation 3
mv eval/results/compliance.json eval/results/compliance-baseline.json

# Ablated: temporarily strip the rule
cp "$INSTRUCTION_FILE" "${INSTRUCTION_FILE}.bak"
sed -i "/${RULE_ID}/d" "$INSTRUCTION_FILE"

bash eval/runner/run-suite.sh eval/tasks/capability/generation 3
mv eval/results/compliance.json eval/results/compliance-ablated.json

mv "${INSTRUCTION_FILE}.bak" "$INSTRUCTION_FILE"   # restore

# Report the delta
jq -s '{baseline: .[0], ablated: .[1], enforcement_gap: (.[0]-.[1])}' \
  eval/results/compliance-baseline.json eval/results/compliance-ablated.json
```

Run this per-rule ablation whenever you're deciding whether a rule belongs in the always-on file at all — a near-zero enforcement gap is evidence the rule should move to a lint rule instead (deterministic enforcement beats advisory instruction every time it's mechanically possible) or be dropped as dead weight.

### 1.3 Scope correctness (path-scoped files) — cheap, deterministic, do this first

```bash
# eval/graders/code/instruction-scope-check.sh
# For each *.instructions.md, verify applyTo glob behavior directly — no agent run needed
MATCHING_FILE="cypress/e2e/checkout/pay.cy.ts"
NON_MATCHING_FILE="cypress/support/pages/checkout.page.ts"

# Positive: does a matching file actually receive this instruction's rules?
# Negative: does a non-matching file NOT receive them?
# (Implementation depends on your CLI's context-inspection capability —
#  at minimum, run one task against each file type and check the compliance
#  grader from 1.1 against a rule unique to that instruction file.)
```
This is a **static + one-shot check**, not a multi-trial suite — glob matching is deterministic, so once verified it doesn't need repeated trials (see the "no consistency question for deterministic checks" row in the summary table).

### 1.4 Cross-layer non-contradiction check

A static-analysis pass over the instruction files themselves (not over agent runs): an LLM-judge or even a simple keyword-overlap script comparing `copilot-instructions.md` against every `*.instructions.md` for rules that could conflict on overlapping paths. Run this whenever any instruction file changes — it's fast and catches the failure mode your earlier audit checklist flags as a blocker (contradictory layers producing inconsistent generations).

### 1.5 Length/bloat regression tracking

```bash
# Trivial but valuable — track over time, not per-PR gate
wc -l .github/copilot-instructions.md .github/instructions/*.instructions.md
```
Since every line here is paid on every request, a monotonically growing file is a silent tax. Track line count in your results dashboard alongside compliance rates; a growing file with flat compliance is a sign of bloat, not improvement.

### 1.6 Consistency for instructions — what it actually measures

Run the compliance suite (1.1) at k=5. **A rule with unstable compliance across identical-condition trials reveals that the instruction is advisory, not enforced** — the model follows it most of the time but not reliably. This is expected and fine for soft/stylistic rules; for hard "never" rules (credentials, destructive commands), an unstable compliance rate is itself the finding — and the fix is usually to promote the rule to a deterministic lint check (Vol 4 L7 from your workflow catalog) rather than trying to word the instruction more forcefully.

---

## 2. Skills — Two Separate Eval Plans

### 2.1 Skill Triggering (routing/dispatch)

**Broader than agent-routing alone.** Your agent eval plan's Suite A tested routing *through your one orchestrating agent*. But a skill's description is evaluated by the model independent of which agent or mode is active — the same skill can be triggered from default Copilot chat, from any custom agent, or from the CLI. **Test triggering across every context where the skill should plausibly fire, not just your one router.**

```yaml
# eval/tasks/skills/trigger-suite.yaml
- task_id: skill-trigger-001
  skill_under_test: cypress-authoring
  ask: "Write a test for the new refund flow"
  context: default-chat          # no custom agent selected
  expected_fires: true
- task_id: skill-trigger-002
  skill_under_test: cypress-authoring
  ask: "Write a test for the new refund flow"
  context: test-implementer-agent
  expected_fires: true
- task_id: skill-trigger-003
  skill_under_test: cypress-authoring
  ask: "Summarize the release notes for this sprint"
  context: default-chat
  expected_fires: false          # negative case — adjacent-but-wrong topic
- task_id: skill-trigger-004      # same-capability ambiguity probe
  skill_under_test: [cypress-authoring, api-contract-testing]
  ask: "The order confirmation isn't showing after checkout"
  context: default-chat
  expected_fires: either-acceptable   # could reasonably be UI or API investigation — check it doesn't fire BOTH redundantly, and log which one it picks for pattern tracking
```

**Grading:** identical mechanism to your agent routing grader (Part 5.2 of the tooling guide) — read the hook-logged tool-call/skill-invocation record, don't trust the model's self-report. Report **per-skill precision/recall**, and specifically build **confusion pairs** — skills whose descriptions are semantically close enough to be mistaken for each other (e.g., `cypress-authoring` vs. a hypothetical `component-testing` skill) — since this is the specific, named failure mode current skill-retrieval research is tracking as *same-capability ambiguity*, and it's the exact thing your K4 kata (trigger-description calibration) trains engineers to fix by hand.

**Consistency:** run each trigger task at k=5. A skill that fires 3/5 times on an unambiguous positive case has a **description problem**, not a random one — this is precisely what the K4 kata's iterative description-rewriting addresses; the eval just makes "did it improve" measurable instead of impressionistic.

### 2.2 Skill Content (does loading it actually help?)

**The eval question here isn't "did it load" (that's 2.1) — it's "does the model behave better when it does."** This requires a delta design:

1. Run a task the skill is meant to help with, **with the skill's trigger description intact**.
2. Run the identical task with the skill folder **temporarily renamed/disabled** so it cannot fire.
3. Grade both outputs with your existing capability graders (Section B of the agent eval plan — lint, assertion strength, convention adherence).
4. The delta is the skill's actual contribution.

```bash
# eval/runner/skill-content-delta.sh
SKILL_DIR=".github/skills/cypress-authoring"
mv "$SKILL_DIR" "${SKILL_DIR}.disabled"
bash eval/runner/run-suite.sh eval/tasks/capability/generation 3
mv eval/results/capability.json eval/results/capability-without-skill.json
mv "${SKILL_DIR}.disabled" "$SKILL_DIR"

bash eval/runner/run-suite.sh eval/tasks/capability/generation 3
mv eval/results/capability.json eval/results/capability-with-skill.json

jq -s '{without: .[0], with: .[1], skill_contribution: (.[1]-.[0])}' \
  eval/results/capability-without-skill.json eval/results/capability-with-skill.json
```

**A skill with near-zero contribution is a candidate for removal or rewrite** — either its content isn't adding information the model doesn't already have (the exact anti-pattern your framework guide warns against: skills wrapping public documentation the model already knows), or the content itself is weak even though the triggering works fine. This delta test is what tells those two failure modes apart from a triggering failure (2.1) — three genuinely different bugs that look identical from the outside ("the skill isn't helping").

### 2.3 Bundled Scripts — direct code eval, no agent involved

Anything in a skill's `scripts/` folder is ordinary code. **Test it exactly like you'd test any other script in your repo — unit tests, no LLM judge, no trial/grader machinery needed at all:**

```bash
# eval/tests/skills/flaky-test-triage/pull-ci-history.test.sh
# Standard unit/integration test — this is just software testing, not agent evaluation
bash .github/skills/flaky-test-triage/scripts/pull-ci-history.sh --dry-run test-spec.cy.ts \
  | assert_json_shape "expected-output-schema.json"
```
This is your **cheapest, highest-confidence eval in the entire program** — deterministic code has no consistency question, no judge-calibration question, no routing ambiguity. Do this for every skill with bundled scripts before spending any effort on the harder evals above; it also happens to satisfy your audit checklist's script-review requirement as a side effect.

### 2.4 Reference/example staleness — a scheduled check, not a per-PR gate

Any skill with a "gold-standard example" makes an implicit claim that the example still passes. Run this monthly, not per-PR:
```bash
for example in .github/skills/*/examples/*.cy.ts; do
  npx cypress run --spec "$example" || echo "STALE: $example no longer passes"
done
```

---

## 3. Prompts — Trial-Based, With Prompt-Specific Additions

Prompts trigger a full agent run, so the entire methodology from your eval implementation plan and tooling guide applies directly — **treat every prompt file as defining a task template, and every invocation as a normal trial.** Layer these prompt-specific checks on top:

### 3.1 Input-boundary tests (the highest-value addition)

```yaml
# eval/tasks/prompts/generate-e2e-test-boundaries.yaml
- task_id: prompt-input-001
  prompt: generate-e2e-test
  inputs: { featureName: "refund-flow" }        # happy path
  expected: normal-execution
- task_id: prompt-input-002
  prompt: generate-e2e-test
  inputs: {}                                     # missing required input
  expected: agent-asks-for-input          # NOT invent a feature name — this is an SA (silent assumption) check
  outcome_grader: code
  outcome_check: "no files created AND transcript contains a clarifying question"
- task_id: prompt-input-003
  prompt: generate-e2e-test
  inputs: { featureName: "the entire checkout and payment and shipping and account and notification system" }
  expected: agent-scopes-or-clarifies     # oversized/ambiguous input must not be silently truncated or silently over-scoped
```

### 3.2 Approval-gate enforcement (trajectory check, not outcome check)

For any prompt with a "present the plan and STOP for approval" step (your `/generate-e2e-test` and `/generate-api-test` both have this): **verify execution actually halts at the gate** — this is one of the rare cases where you grade the trajectory, not just the outcome, because the gate's entire purpose is a mid-process pause, which an outcome-only grader would never observe.

```bash
# eval/graders/routing/check-gate-halted.sh
# Read the tool-call log: confirm no file-mutation tool calls occurred
# AFTER the plan-presentation point and BEFORE trial termination
jq 'select(.timestamp > $gate_timestamp) | select(.tool_name | test("edit|write"))' \
  "$LOG_FILE" | wc -l
# Expected: 0 mutation calls post-gate within a single non-interactive trial
```
Note the limitation: a fully headless `-p` trial can't literally "wait for human approval" mid-run the way an interactive session does — so this grader is really checking that the agent **stops after presenting the plan and doesn't proceed unprompted within that invocation**, which is the headless-mode proxy for gate discipline. Supplement with periodic interactive spot-checks (a human actually runs the prompt in VS Code and confirms the real UX pause behaves as designed).

### 3.3 Declared-agent pairing check — static, cheap, do it first

If a prompt's frontmatter names `agent:`, verify that agent's tool posture is actually sufficient for what the prompt asks it to do — a one-line static check against the agent's `tools:` allow-list, not a trial:
```bash
PROMPT_AGENT=$(yq '.agent' .github/prompts/generate-e2e-test.prompt.md)
AGENT_TOOLS=$(yq '.tools[]' ".github/agents/${PROMPT_AGENT}.md")
echo "$AGENT_TOOLS" | grep -q "edit" || echo "MISMATCH: prompt requires file edits but ${PROMPT_AGENT} lacks edit tool"
```

### 3.4 Consistency

Identical to agent capability suites — run each prompt task at k=5, compute pass^k. Since a prompt is really "an agent trial with a fixed template," there's nothing methodologically new here beyond what your existing consistency runner already does — just point it at prompt invocations (`copilot -p "/generate-e2e-test featureName=refund"` style invocation, or however your CLI version's prompt-file syntax resolves it) instead of raw asks.

---

## 4. Custom Agents — Already Fully Specified

No new methodology needed here — this is exactly what your eval implementation plan (Suites A–D) and tooling setup guide already build: routing, per-skill capability as invoked through the agent, end-to-end trajectory/outcome, and consistency via pass^k, plus the dedicated healing safety framework for any agent whose actions are hard to reverse. **The only addition worth naming explicitly given this document's framing:** an agent's tool-boundary negative test (Section 4.2 of your audit checklist — "ask the read-only agent to edit a file, confirm it can't") is itself an effect-based eval in the same family as instruction compliance-rate testing — you're not grading whether the agent *tried* to do something sensible, you're grading whether an enforced boundary actually held. Keep that framing in mind: agents mix trial-based capability eval with effect-based boundary eval, and both matter.

---

## 5. Build Order Across All Four (revised recommendation)

Given the cost differences now visible across primitive types, build in this order — cheapest and most deterministic first, most expensive (delta/ablation) last:

1. **Skill bundled-script unit tests (2.3)** — pure code, zero LLM involvement, do this today regardless of anything else.
2. **Instruction scope correctness (1.3) + cross-layer contradiction check (1.4)** — static, deterministic, fast.
3. **Prompt declared-agent pairing check (3.3)** — static, one-line-per-prompt.
4. **Skill triggering (2.1)** and **agent routing** (already built) — share the same hook-log infrastructure; build together.
5. **Prompt input-boundary tests (3.1)** and **agent/skill capability suites** (already built) — the bulk of your regular eval work.
6. **Instruction compliance-rate suite (1.1)** — layers onto trials you're already running for other reasons; nearly free once 5 exists.
7. **Prompt approval-gate enforcement (3.2)** — needs the trajectory-reading infrastructure from your tooling guide.
8. **Instruction counterfactual ablation (1.2)** and **skill content delta (2.2)** — most expensive (every task runs twice), highest insight-per-run once you need to decide whether a specific rule or skill is pulling its weight. Run these on-demand when a specific artifact's value is in question, not as a routine per-PR suite.

*Companion docs: automation-agent-eval-implementation-plan.md (the trial-based methodology this document extends to prompts and agent-routing-for-skills), copilot-cli-eval-tooling-setup-guide.md (the runner/grader infrastructure every suite above reuses), enterprise audit checklist (Section 5 for skills, Section 4.2 for agent tool boundaries — this document's effect-based evals are how those checklist items get automated rather than manually re-verified each audit).*
