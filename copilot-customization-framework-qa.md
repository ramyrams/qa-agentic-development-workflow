# GitHub Copilot Customization Framework for QA Automation Teams
### Agents vs. Skills vs. Instructions vs. Prompt Files — a decision framework, starter kit, and training plan

**Audience:** QA automation engineers using Cypress + VS Code + Node.js + GitHub Copilot for web UI and backend/API test automation.
**Purpose:** Eliminate confusion between the four customization primitives, establish a repo-level framework, and give the team a phased path to expertise.

---

## 1. The Mental Model (Read This First)

Every Copilot agent request is built from a **system prompt** plus whatever context gets attached. The four customization primitives differ in exactly **one dimension that matters most: how and when they enter the model's context.**

| Primitive | How it enters context | Analogy |
|---|---|---|
| **Custom Instructions** | Automatically, on every request (or every request touching matching files) | The **employee handbook** — always in force, nobody invokes it |
| **Prompt Files** | Manually, when a user runs `/prompt-name` in chat | A **runbook you pull off the shelf** for a specific repeatable task |
| **Custom Agents** | Manually, when a user selects the agent (persona + tool restrictions) | A **specialist role** — "hand this to the test reviewer" |
| **Skills** | Automatically **but conditionally** — the agent decides to load it when the task matches the skill's description | A **reference binder + toolkit** the specialist grabs only when the job calls for it |

One sentence each, for the team:

1. **Instructions** = always-on rules. *"In this repo, we always do X."*
2. **Prompt files** = user-triggered task templates. *"Run our standard 'generate API test' procedure."*
3. **Agents** = who is doing the work — persona, allowed tools, and behavior boundaries. *"Act as the test planner, not the implementer."*
4. **Skills** = agent-triggered capability packages (instructions + scripts + examples in a folder). *"When debugging a flaky test, load the flaky-test-triage kit."*

The confusion usually comes from the fact that **all four are Markdown files that contain instructions.** The content overlaps; the **loading mechanism and scope do not.** Teach the loading mechanism, and the confusion disappears.

---

## 2. The Four Primitives in Depth

### 2.1 Custom Instructions — always-on repo context

**Where they live:**

```
.github/copilot-instructions.md          ← repo-wide, applies to everything
.github/instructions/*.instructions.md   ← path-specific, applies via glob patterns
AGENTS.md (repo root)                     ← open standard, read by Copilot and third-party agents
```

**How they load:** Automatically appended to every Copilot request in the repo. Path-specific instruction files use an `applyTo:` glob in their YAML frontmatter, so they only load when the task touches matching files.

**What belongs here (QA-specific):**
- Repo architecture: where specs, fixtures, commands, page objects, and API clients live
- Non-negotiable conventions: selector strategy (`data-cy` attributes only), no hard waits (`cy.wait(ms)` banned), intercept-based network control, naming conventions
- How to run things: `npm run cy:open`, `npm run test:api`, lint/test gates before PR
- What NOT to do: never commit credentials, never modify fixtures in `prod-data/`

**What does NOT belong here:** Step-by-step task procedures (that's a prompt file), tool restrictions (that's an agent), large reference material like your full API contract (that's a skill — always-on instructions burn context tokens on every single request, so keep them short).

**Rationale:** Because instructions are injected into *every* request, they are the highest-leverage and highest-cost primitive. A bloated instructions file degrades every interaction; a tight one silently raises the floor of every generation.

**Path-specific example split for your stack:**

```
.github/instructions/
├── cypress-e2e.instructions.md      # applyTo: "cypress/e2e/**/*.cy.{js,ts}"
├── api-tests.instructions.md        # applyTo: "tests/api/**/*.{js,ts}"
├── page-objects.instructions.md     # applyTo: "cypress/support/pages/**"
└── fixtures.instructions.md         # applyTo: "cypress/fixtures/**"
```

---

### 2.2 Prompt Files — reusable task templates you invoke on demand

**Where they live:**

```
.github/prompts/*.prompt.md
```

**How they load:** Only when a user explicitly invokes them in chat (e.g., `/generate-e2e-test`). They support YAML frontmatter (`description`, `agent`/`mode`, `tools`, `model`) and input variables like `${input:featureName}`.

**What belongs here (QA-specific):**
- `/generate-e2e-test` — scaffold a Cypress spec for a user story, following your page-object and intercept conventions
- `/generate-api-test` — build a backend test from an endpoint definition or OpenAPI fragment
- `/review-test-pr` — run your team's test-review checklist against a diff
- `/convert-manual-case` — transform a manual test case (pasted or from a file) into an automated spec skeleton
- `/coverage-gap-analysis` — compare specs against a feature list and report untested paths

**What does NOT belong here:** Rules that should apply even when nobody remembers to invoke the prompt. If forgetting to run it would cause a convention violation, it belongs in instructions instead.

**Rationale:** Prompt files encode *procedures with a beginning and an end*. They make your best engineer's prompting technique a shared, versioned team asset instead of something living in one person's chat history. This is the fastest win for a team new to agentic workflows because results are immediate and visible.

---

### 2.3 Custom Agents — specialist personas with tool boundaries

**Where they live:**

```
.github/agents/AGENT-NAME.md          # repo-level
# org/enterprise level: agents/ folder in a .github-private repo
```

**How they load:** The user selects the agent in VS Code chat (or the Copilot coding agent uses it). The agent file defines a persona, its own instructions, and — critically — **which tools it may use**. Agents can hand off to other agents.

**What belongs here (QA-specific):**

| Agent | Purpose | Tool posture |
|---|---|---|
| `test-planner` | Turns a user story/requirement into a test plan and case matrix; asks clarifying questions | **Read-only** — no edit, no terminal |
| `test-implementer` | Writes/edits Cypress and API specs following the plan | Edit + read; terminal gated |
| `test-reviewer` | Reviews test PRs for flakiness risks, selector quality, assertion strength | Read-only |
| `flaky-test-investigator` | Analyzes failing runs, reproduces locally, proposes fixes | Read + terminal (run tests), no destructive edits |

**Rationale:** The tool-restriction dimension is what makes agents different from a prompt file with a persona paragraph. A read-only `test-planner` *cannot* start rewriting your specs mid-conversation — the boundary is enforced, not requested. Separating planner → implementer → reviewer also mirrors how you'd sequence the work with humans, and the handoff points become natural review gates.

---

### 2.4 Skills — conditionally loaded capability packages (open standard)

**Where they live:**

```
.github/skills/<skill-name>/
├── SKILL.md            # required: frontmatter (name, description) + instructions
├── scripts/            # optional: runnable helpers
├── references/         # optional: docs, API contracts, selector maps
└── examples/           # optional: gold-standard specs
```

**How they load:** Progressive disclosure. Copilot always sees each skill's `name` + `description`; it loads the full SKILL.md **only when it judges the task matches the description**, and reads bundled scripts/references on demand. Skills follow the open Agent Skills standard, so the same skill works in VS Code, Copilot CLI, Copilot coding agent, and even Claude-based tools — they are your most portable asset.

**What belongs here (QA-specific):**
- `cypress-authoring/` — your full spec-writing playbook: gold-standard example specs, the selector map, custom command reference. Too big for always-on instructions; too foundational to require manual invocation.
- `flaky-test-triage/` — a triage decision tree plus a script that pulls the last N CI runs for a spec and summarizes failure signatures
- `api-contract-testing/` — OpenAPI fragments, schema-validation helpers, gold-standard API test examples
- `test-data-setup/` — scripts and rules for seeding/resetting test data safely
- `ci-failure-debugging/` — how to read your pipeline logs, common failure signatures, artifact locations

**What does NOT belong here:** One-line conventions (instructions) or user-triggered procedures with parameters (prompt files).

**Rationale:** Skills solve the context-economy problem. Your Cypress playbook might be 2,000 lines with examples — injecting that into every request (instructions) would be wasteful and degrade quality, and requiring engineers to remember to invoke it (prompt file) means it gets skipped. The description-based auto-loading gives you "always available, only loaded when relevant."

**The `description` field is the single most important line in a skill.** Copilot decides whether to load the skill based *only* on the description matching the user's task. Write it like a trigger condition: *"Use when writing, editing, or reviewing Cypress end-to-end specs, page objects, or custom commands in this repo."* Vague descriptions = skills that never fire.

---

## 3. The Decision Framework

### 3.1 Four questions, in order

Ask these in order for any guidance you want to give Copilot; stop at the first "yes":

1. **Should this apply to every request (or every request touching certain files) without anyone doing anything?**
   → **Custom instructions** (repo-wide or path-specific). *Test: "If Copilot ignored this, would any task in the repo be wrong?"*
2. **Is this a repeatable procedure a human kicks off, with definable inputs and a clear end state?**
   → **Prompt file**. *Test: "Would I write this as a runbook with parameters?"*
3. **Does this define WHO is working — a role with different permissions, tools, or behavioral boundaries than the default?**
   → **Custom agent**. *Test: "Do I need to restrict tools or change the persona, not just add task steps?"*
4. **Is this specialized knowledge/capability (docs, scripts, examples) that's only relevant to certain tasks, and the agent should decide when to pull it in?**
   → **Skill**. *Test: "Is this too big for always-on, but too important to rely on humans remembering it?"*

### 3.2 Quick disambiguation table

| Symptom of confusion | Resolution |
|---|---|
| "Should our selector rules be an instruction or a skill?" | **Instruction** — one-line rules that must hold everywhere are always-on. The *examples and rationale* behind them can live in a skill. |
| "Is `generate a test for feature X` a prompt file or an agent?" | **Prompt file** — it's a task, not a role. Use an agent only if the task needs a distinct tool posture. |
| "We keep pasting our API contract into chat." | **Skill** — bundle it as a reference in `api-contract-testing/`; Copilot loads it when relevant. |
| "Copilot keeps running destructive commands during planning." | **Agent** — create a read-only `test-planner`. Instructions can't enforce tool boundaries; agents can. |
| "Our prompt file has grown to 800 lines of reference material." | Split: keep the **procedure** in the prompt file, move the **reference material** into a skill it can lean on. |
| "Should we duplicate instructions inside every agent and prompt?" | No — instructions already apply. Agents/prompts should only add what's *different* for that role/task. |

### 3.3 How they compose (the part teams miss)

The primitives **stack** — a single request can involve all four:

> Engineer selects the **`test-implementer` agent** and runs **`/generate-e2e-test featureName=checkout`**. The repo **instructions** (always-on conventions + the `cypress-e2e.instructions.md` path rules) are automatically in context. As Copilot works, it recognizes the task matches the **`cypress-authoring` skill** description and loads the playbook and gold-standard examples.

Design each layer to *not* repeat the others: instructions carry universal rules, the agent carries role and tool posture, the prompt carries the procedure, the skill carries deep reference and helpers.

---

## 4. Recommended `.github` Folder Layout

```
.github/
├── copilot-instructions.md                  # ~50–100 lines max, repo-wide
├── instructions/
│   ├── cypress-e2e.instructions.md          # applyTo: cypress/e2e/**
│   ├── api-tests.instructions.md            # applyTo: tests/api/**
│   ├── page-objects.instructions.md         # applyTo: cypress/support/pages/**
│   └── fixtures.instructions.md             # applyTo: cypress/fixtures/**
├── prompts/
│   ├── generate-e2e-test.prompt.md
│   ├── generate-api-test.prompt.md
│   ├── review-test-pr.prompt.md
│   ├── convert-manual-case.prompt.md
│   └── coverage-gap-analysis.prompt.md
├── agents/
│   ├── test-planner.md
│   ├── test-implementer.md
│   ├── test-reviewer.md
│   └── flaky-test-investigator.md
└── skills/
    ├── cypress-authoring/
    │   ├── SKILL.md
    │   ├── examples/gold-standard.cy.ts
    │   └── references/selector-map.md
    ├── api-contract-testing/
    │   ├── SKILL.md
    │   └── references/openapi-fragments/
    ├── flaky-test-triage/
    │   ├── SKILL.md
    │   └── scripts/pull-ci-history.sh
    └── test-data-setup/
        ├── SKILL.md
        └── scripts/seed-env.sh
```

---

## 5. Starter Templates

### 5.1 `.github/copilot-instructions.md` (repo-wide)

```markdown
# Test Automation Repo — Copilot Instructions

## Architecture
- Cypress e2e specs: `cypress/e2e/` (grouped by feature domain)
- Page objects: `cypress/support/pages/` — all element access goes through these
- Custom commands: `cypress/support/commands.ts`
- API tests: `tests/api/` (Node.js, run with `npm run test:api`)
- Fixtures: `cypress/fixtures/` — never invent fixture data; reuse or ask

## Non-negotiable conventions
- Selectors: `data-cy` attributes ONLY. Never CSS classes, tags, or text selectors.
- No `cy.wait(<milliseconds>)`. Use `cy.intercept()` + alias waits or assertion retries.
- Every spec must be independent: no ordering dependencies between tests.
- API tests must clean up any data they create.
- New specs require at least one negative-path test.

## Commands
- Run e2e locally: `npm run cy:open` | headless: `npm run cy:run`
- Run API tests: `npm run test:api`
- Lint before any PR: `npm run lint`

## Never
- Never commit credentials, tokens, or environment URLs — use `cypress.env.json` (gitignored).
- Never modify anything under `cypress/fixtures/prod-data/`.
```

### 5.2 Path-specific: `.github/instructions/cypress-e2e.instructions.md`

```markdown
---
applyTo: "cypress/e2e/**/*.cy.{js,ts}"
---
- Structure: `describe` per feature, `context` per state, `it` per behavior.
- Test names describe user-visible behavior: "shows validation error when email is invalid".
- Use page objects for all element interaction; if one doesn't exist, create it first.
- Network: intercept and alias all XHR the test depends on; assert on the alias, not on time.
- One logical assertion focus per `it`; setup goes in `beforeEach` or custom commands.
```

### 5.3 Prompt file: `.github/prompts/generate-e2e-test.prompt.md`

```markdown
---
description: "Generate a Cypress e2e spec for a feature/user story following team conventions"
agent: test-implementer
---
Generate a Cypress e2e spec for: ${input:featureName}

Procedure:
1. Ask me for the user story / acceptance criteria if I have not provided them.
2. Check `cypress/support/pages/` for an existing page object; extend it, or create one if missing.
3. Draft the test case matrix first (happy path, negative paths, edge cases) and show it to me for approval BEFORE writing spec code.
4. After approval, implement the spec in `cypress/e2e/${input:featureName}/`.
5. Run the spec headlessly and iterate until green.
6. Summarize what is covered and what is intentionally out of scope.
```

### 5.4 Custom agent: `.github/agents/test-planner.md`

```markdown
---
name: test-planner
description: "Turns requirements into test plans and case matrices. Read-only — never writes code."
tools: ["search", "read"]        # no edit, no terminal
---
You are a senior QA test architect. Given a requirement, user story, or feature description:
1. Identify testable behaviors, risks, and boundary conditions.
2. Produce a test case matrix: ID, behavior, type (e2e/API/component), priority, data needs.
3. Flag anything untestable as written and list clarifying questions.
4. Recommend the split between UI (Cypress) and API-level coverage — prefer API where UI adds no value.
You NEVER write or modify spec code. When planning is approved, tell the user to hand off to the test-implementer agent.
```

### 5.5 Skill: `.github/skills/flaky-test-triage/SKILL.md`

```markdown
---
name: flaky-test-triage
description: "Use when a Cypress or API test is failing intermittently, flaky, unstable in CI, or passing locally but failing in the pipeline. Provides a triage decision tree and a CI-history script."
---
# Flaky Test Triage

## Procedure
1. Run `scripts/pull-ci-history.sh <spec-path>` to get the last 20 CI results and failure signatures for the spec.
2. Classify the failure using the taxonomy below BEFORE proposing any fix.
3. Propose the minimal fix for that class; never add `cy.wait(ms)` as a fix.

## Failure taxonomy
- **Timing/race**: assertion fires before network/render settles → fix with intercept alias waits or retry-able assertions.
- **Test pollution**: passes alone, fails in suite → find shared state; enforce isolation in before/after hooks.
- **Data drift**: fixture or seeded data changed → repair via test-data-setup skill, never hardcode around it.
- **Environment**: infra/timeout only in CI → check viewport, resource limits, parallelization config.
- **Genuine bug**: intermittent product defect → file a bug with the CI history attached; do NOT mask it in the test.
```

---

## 6. Governance and Security (Do Not Skip)

1. **Treat all four primitives as code.** They live in the repo, so they go through PR review like any other change. A bad instruction file silently degrades every generation in the repo; review it with the same rigor as a shared library.
2. **Skills are the highest-risk primitive.** Skills can bundle executable scripts, and third-party skills are not verified by GitHub — they can contain prompt injections or malicious scripts. Inspect any external skill's full contents before adoption; prefer writing your own.
3. **Be conservative with `allowed-tools` and shell pre-approval.** Pre-approving shell/bash in a skill or agent removes the human confirmation step for terminal commands, which means a prompt injection could execute arbitrary commands. Default posture: Copilot must ask before running terminal commands; grant exceptions per-agent, deliberately.
4. **Least-privilege agents.** Planner and reviewer agents get read-only tools. Only the implementer gets edit; only the investigator gets terminal. Rationale: enforced boundaries beat instructed boundaries — instructions can be ignored by a misbehaving model; tool restrictions cannot.
5. **Assign ownership.** Name a maintainer (or CODEOWNERS entry) for `.github/` customization files. Untended instruction files rot as the codebase evolves, and stale rules actively mislead the agent.
6. **Version and changelog your instructions.** When generation quality shifts, the first question is "what changed in `.github/`?" — make that answerable with git history.

---

## 7. Team Training & Rollout Plan (6 Weeks)

The sequencing principle: **start with the always-on layer (highest leverage, lowest concept count), add invocable procedures, then roles, then auto-loaded capabilities.** Each phase produces a working asset before introducing the next concept, so the team learns by shipping.

**Week 1 — Foundations & instructions.**
Workshop the mental model in Section 1 (60 min). Then, as a team, write `copilot-instructions.md` by mining your existing style guide and PR review comments — the rules you repeat in reviews are exactly what belongs there. *Exit criteria: repo-wide instructions merged; every engineer has seen Copilot follow (and been shown how to spot it violating) a convention.*

**Week 2 — Path-specific instructions.**
Split conventions into the path-scoped files (e2e, API, page objects, fixtures). Compare generations on the same task before/after to make the effect visible. *Exit: 3–4 `.instructions.md` files merged; team can articulate the "always-on vs. scoped" distinction.*

**Week 3 — Prompt files.**
Each engineer converts one task they do weekly into a prompt file; review them together and merge the best. Start with `/generate-e2e-test` and `/review-test-pr`. *Exit: 3+ prompt files in daily use; team understands "user-triggered procedure."*

**Week 4 — Custom agents.**
Introduce tool restrictions. Build `test-planner` (read-only) and `test-implementer` together; run one real user story through the planner → implementer handoff. *Exit: team has experienced an enforced tool boundary and a handoff.*

**Week 5 — Skills.**
Build `cypress-authoring` (playbook + gold examples) and `flaky-test-triage` (with the CI script). Spend explicit time on writing trigger-style descriptions, and test that skills actually fire on matching tasks. *Exit: two skills merged; team can explain progressive loading and description-based triggering.*

**Week 6 — Integration, evals & governance.**
Run an end-to-end exercise: story → plan → implement → review, all through the customized setup. Establish the governance rules from Section 6. Connect this to your existing eval harness: your trajectory-grading approach and failure taxonomy become the measurement layer for whether customization changes actually improve generation quality — re-run evals whenever `.github/` files change materially. *Exit: ownership assigned, review process for `.github/` changes documented, baseline eval scores recorded.*

**Ongoing cadence:** A 30-minute biweekly "prompt review" where engineers demo one customization improvement. This is the single best mechanism for compounding team expertise — it turns individual discoveries into shared, versioned assets.

---

## 8. Common Confusions — FAQ for the Team

**Q: Instructions and skills both auto-load. What's actually different?**
Instructions load on *every* request (or every request touching matched paths) with no judgment involved. Skills load only when the agent decides the task matches the skill's description, and their bundled resources load on demand. Use instructions for short universal rules; skills for deep, task-specific material.

**Q: Can't I just put everything in one giant copilot-instructions.md?**
You can, and quality will suffer. Every token of always-on instruction competes with your actual task for the model's attention. The whole framework exists to load the *right* context at the *right* time — not all context all the time.

**Q: Prompt file vs. agent — both can have a persona and tools in frontmatter?**
A prompt file *runs once* as a task (and can even specify which agent executes it). An agent is a *persistent mode* you converse in, with enforced tool boundaries and handoffs. Rule of thumb: task → prompt file; role → agent.

**Q: We also use Claude-based tools sometimes. Do we duplicate everything?**
No. Skills follow an open standard portable across Copilot surfaces and other skill-compatible agents, and `AGENTS.md` is an open instructions format read by multiple agents. Prefer those two formats for anything you want to be tool-agnostic.

**Q: How do we know any of this is working?**
Measure, don't vibe: fix a small set of representative generation tasks, grade outputs against your failure taxonomy before and after each customization change, and track trend. (This is exactly what your eval harness is for.)

---

*Maintainer: ________ · Last reviewed: ________ · Review cadence: monthly or on any Copilot feature change*
