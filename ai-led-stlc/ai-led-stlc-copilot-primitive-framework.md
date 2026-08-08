# AI-Led STLC — GitHub Copilot Primitive Framework
### End-to-End QA, Structured on Agents / Skills / Instructions / Prompts

This formalizes the same four-primitive pattern your team already uses for Copilot customization — and extends it, coherently, across all ten STLC activities instead of just automation scripting. One repository structure, one set of composition rules, one catalog. This is the reference architecture; the technical design document specifies what each primitive does internally.

---

## 1. The Four Primitives — Roles, Not Just File Types

| Primitive | Role | Analogy |
|---|---|---|
| **Instructions** | Persistent context and rules, applied automatically whenever a matching skill/agent runs — never manually invoked | The style guide / house rules everyone already knows |
| **Skill** | A single-purpose capability with a defined input → output contract and its own eval suite | One well-defined job |
| **Agent** | Orchestrates a sequence of skills to accomplish an end-to-end activity, applies the human-review gate, and calls external systems (ADO, CI) | The workflow conductor |
| **Prompt** | The manual or triggered entry point a human (or a scheduled job) actually invokes to kick off an agent | The "start button" |

**Composition rule, stated once so it doesn't need repeating per phase**: a *prompt* triggers an *agent*; the *agent* calls one or more *skills* in sequence, applying any matching *instructions* automatically at each step; the *agent* is also the only primitive allowed to call `ado.*` write methods or commit code, and only after the human-review gate defined for that activity (Governance Model, Section 2) has been satisfied.

No skill calls another skill directly, and no skill writes to a system of record — that's the agent's job. This constraint is what keeps 23 skills composable instead of turning into a tangle of skill-to-skill dependencies nobody can trace.

---

## 2. Repository Structure — Full End-to-End Layout

```
.github/
  agents/
    report-cycle-orchestrator/agent.md
    api-test-cycle-orchestrator/agent.md
    defect-drafting-orchestrator/agent.md
    requirement-analysis-agent/agent.md
    test-planning-agent/agent.md
    regression-optimization-orchestrator/agent.md
    # (test-case-design-agent lives in Copilot Studio, not here — see §6)

  skills/
    allure-parse/            {SKILL.md, eval/}
    failure-classify/        {SKILL.md, eval/}
    report-summarize/        {SKILL.md, eval/}
    ledger-update/           {SKILL.md, eval/}
    healer/                  {SKILL.md, eval/}
    spec-parse/               ...
    api-explore/               ...
    test-data-generate/        ...
    api-script-generate/       ...
    context-gather/            ...
    duplicate-check/           ...
    draft-bug/                 ...
    dor-check/                 ...
    completeness-gap/          ...
    defect-history-analyze/    ...
    complexity-signal/         ...
    plan-draft/                ...
    change-impact/             ...
    risk-score/                ...
    subset-recommend/          ...

  instructions/
    negative-case-taxonomy.instructions.md      # shared: Phase 2 + Phase 4
    definition-of-ready.instructions.md          # shared: Phase 4 + Phase 5
    ai-artifact-style-guide.instructions.md      # shared: Phase 1 + 5 + 6 report/plan tone
    bug-report-quality-bar.instructions.md
    regression-tiering-policy.instructions.md

  prompts/
    report-cycle.prompt.md
    api-test-cycle.prompt.md
    review-and-file.prompt.md
    test-planning-cycle.prompt.md
    regression-scope.prompt.md
```

This applies the consolidation from the build inventory: three shared instructions files instead of six duplicated ones. Each references which agents/skills it applies to in its own frontmatter (§4), so ownership is explicit rather than implied by folder proximity.

---

## 3. Primitive Templates

Use these as the literal file skeletons — every new primitive starts here, so review and onboarding don't require re-learning structure each time.

### 3.1 `agent.md` Template
```markdown
---
name: report-cycle-orchestrator
stlc_activity: [Execution, Test Healing, Reporting]
risk_tier: low
calls_skills: [allure-parse, failure-classify, report-summarize, ledger-update, healer]
applies_instructions: [ai-artifact-style-guide]
triggered_by: [report-cycle.prompt]
writes_to: [failure-ledger]
human_review_required: true
version: 1.0.0
eval_status: passing
---

## Purpose
[One paragraph: what this agent accomplishes end to end.]

## Orchestration Sequence
1. Call `allure-parse` with [input]
2. Call `failure-classify` per extracted failure
3. Fan out to `report-summarize` and `ledger-update`
4. If category == stale_locator, call `healer`
5. Stage output for human review — DO NOT auto-publish or auto-commit
6. On approval, execute write actions

## Human Review Gate
[What the reviewer sees, what they can approve/edit/reject, and what happens on each outcome.]

## Failure Handling
[What happens if a skill call fails or returns low confidence — does the agent halt, skip, or flag for manual handling?]
```

### 3.2 `SKILL.md` Template
```markdown
---
name: failure-classify
stlc_activity: Execution
input_schema: ./input-schema.json
output_schema: ./output-schema.json  # must conform to the standard envelope (tech design §0.2)
eval: ./eval/evals.json
version: 1.2.0
eval_status: passing
last_eval_run: 2026-08-01
---

## Purpose
[What this skill does, in one or two sentences — single responsibility only.]

## Input Contract
[Schema reference + one example.]

## Output Contract
[Schema reference + one example, using the standard envelope.]

## Failure Modes
[What does this skill do when it can't confidently produce an answer — return low confidence, or refuse?]
```

### 3.3 `*.instructions.md` Template
```markdown
---
name: negative-case-taxonomy
applies_to_skills: [test-data-generate, case-generate]
applies_to_agents: [api-test-cycle-orchestrator, test-case-design-agent]
scope: shared
version: 1.0.0
---

## Rules
[The actual persistent content — taxonomy definitions, format standards, style rules.
This is read automatically by any skill/agent listed in applies_to_* above; it is
never manually invoked.]
```

### 3.4 `*.prompt.md` Template
```markdown
---
name: report-cycle.prompt
triggers_agent: report-cycle-orchestrator
invocation: manual | scheduled
required_inputs: [allure_report_path]
---

## Entry Point
[The literal phrasing/interface a person or scheduler uses to kick this off, and
what input it needs to collect before calling the agent.]
```

---

## 4. Cross-Reference Frontmatter — Why It Matters

Every primitive's frontmatter declares what it calls, what calls it, and which instructions apply to it. This is what makes the catalog auditable without reading every file: a governance reviewer or a new team member can answer "what does this agent touch, and what human-review gate governs it" from the frontmatter alone, cross-referenced against the Governance Model's Section 2 by `stlc_activity`.

This also makes the eval-before-production gate mechanically enforceable: a CI check can scan all `agent.md`/`SKILL.md` files, confirm every `calls_skills` entry has `eval_status: passing`, and block a merge if an agent references a skill whose eval is failing or stale.

---

## 5. End-to-End Catalog, Mapped to the STLC

| STLC Activity | Prompt | Agent | Skills Called | Shared Instructions |
|---|---|---|---|---|
| Requirement Analysis | *(refinement-time trigger, no standalone prompt file — embedded in `test-planning-cycle.prompt`)* | `requirement-analysis-agent` | `dor-check`, `completeness-gap` | `definition-of-ready` |
| Test Planning | `test-planning-cycle.prompt` | `test-planning-agent` | `defect-history-analyze`, `complexity-signal`, `plan-draft` | `ai-artifact-style-guide` |
| Test Case Design | *(Copilot Studio conversational trigger — see §6)* | `test-case-design-agent` | `requirement-fetch`, `ambiguity-check`, `case-generate` | `negative-case-taxonomy`, `definition-of-ready` |
| Test Data Design | `api-test-cycle.prompt` | `api-test-cycle-orchestrator` | `test-data-generate` | `negative-case-taxonomy` |
| Script Development | `api-test-cycle.prompt` | `api-test-cycle-orchestrator` | `spec-parse`, `api-explore`, `api-script-generate` | — |
| Execution | `report-cycle.prompt` | `report-cycle-orchestrator` | `allure-parse`, `failure-classify` | `ai-artifact-style-guide` |
| Defect Management | `review-and-file.prompt` | `defect-drafting-orchestrator` | `context-gather`, `duplicate-check`, `draft-bug` | `bug-report-quality-bar` |
| Test Healing | `report-cycle.prompt` | `report-cycle-orchestrator` | `healer` | — |
| Reporting | `report-cycle.prompt` | `report-cycle-orchestrator` | `report-summarize`, `ledger-update` | `ai-artifact-style-guide` |
| Regression Optimization | `regression-scope.prompt` | `regression-optimization-orchestrator` | `change-impact`, `risk-score`, `subset-recommend` | `regression-tiering-policy` |

This is the single table that answers "what covers what" across the entire initiative — worth keeping visible to the team as the canonical index, separate from the phase-by-phase build order used for rollout sequencing.

---

## 6. The One Exception: Copilot Studio

Everything above lives in `.github` and follows the same file-based pattern GitHub Copilot uses natively. `test-case-design-agent` is the one primitive that doesn't — it's built in Copilot Studio for the functional-tester audience, per the earlier phase design. Its equivalent structure:

| `.github` concept | Copilot Studio equivalent |
|---|---|
| `agent.md` | The Copilot Studio agent's configured topics + orchestration |
| `SKILL.md` | A Topic, or a Power Automate flow called as a plugin action |
| `*.instructions.md` | Agent instructions + a knowledge source document |
| `*.prompt.md` | A trigger phrase / conversational starter |

Recommend documenting this agent's topic logic in a parallel `agent.md`-style markdown file kept in the same `.github/agents/` folder for catalog completeness, even though Copilot Studio doesn't read it directly — this keeps the "one catalog" property intact instead of Copilot Studio becoming an undocumented side-system.

---

## 7. Versioning & Deprecation

- Every primitive's frontmatter carries a semantic version; a version bump requires a re-run, passing eval before merge (technical design §0.5)
- Deprecating a primitive: mark `eval_status: retired` in frontmatter, keep the file (don't delete — audit trail), and update any `calls_skills`/`applies_instructions` references in dependent primitives in the same change
- Breaking changes to a shared instructions file (e.g., `negative-case-taxonomy`) require checking every agent/skill listed in its `applies_to_*` fields before merge — this is exactly what the frontmatter cross-referencing in §4 is for

---

## 8. Rollout of the Framework Itself

This structure should be introduced to the team the same way your existing `.github` customization training already works — reuse that pattern rather than building a second one:

1. Walk the team through the four-primitive roles (§1) using one already-built example (e.g., `report-cycle-orchestrator`) as the reference case
2. Have engineers build their first new skill against the template in §3.2, reviewed against the existing audit/review checklist
3. Extend the team's competency ladder rungs to include "can compose a multi-skill agent with a correct human-review gate," not just "can write a skill in isolation"
4. Functional testers get the Copilot Studio-specific walkthrough (§6) as a separate track, consistent with the persona-split training already planned for Phase 4
