# The Curated QE Catalog
### High-Value Agents, Skills, Instructions & Prompts for Functional + Automation Teams

**Curation rule applied:** an item makes this list only if it (a) addresses a recurring, high-frequency QA activity, (b) does something the other three primitives can't do as well, and (c) would be missed within two weeks if deleted. Everything else is deliberately excluded (see Section 6 for what I cut and why — the exclusions teach the framework as much as the inclusions).

**Stack assumed:** Cypress + VS Code + Node.js + GitHub Copilot · web UI + backend/API testing · functional (manual) + automation engineers in the same repo/org.

**Build order at a glance:** Instructions (week 1) → Prompts P1–P3 → Agent A1 + A2 → Skills S1 + S2 → the rest as pull demands.

---

## 1. INSTRUCTIONS — 4 files, no more

Instructions earn their place only if the rule must hold on *every* matching request. Four files cover a Cypress + API repo; more than that usually means procedures are leaking into the always-on layer.

### I1. `copilot-instructions.md` — the repo constitution
**Why it earns its place:** Every generation in the repo inherits it. This is the single highest ROI file you will write — it converts your PR review comments (the rules you repeat weekly) into rules the AI applies before the PR exists.

```markdown
# QE Repo — Copilot Instructions
## Layout
- E2E specs: cypress/e2e/<feature>/ · Page objects: cypress/support/pages/
- API tests: tests/api/ · Shared clients: tests/api/clients/
- Manual test artifacts: qa/test-cases/ (Markdown, one file per feature)
## Universal rules
- Selectors: data-cy only. Never CSS classes, tag chains, or visible text.
- No cy.wait(<ms>). Use cy.intercept() + alias waits or retryable assertions.
- Every spec independent and self-cleaning. No inter-test ordering.
- Every new feature: at least one negative-path test.
- Never invent test data; use fixtures or the seeding scripts.
## Commands
- E2E: npm run cy:run · API: npm run test:api · Lint gate: npm run lint
## Never
- Never commit credentials/URLs — cypress.env.json (gitignored) only.
- Never touch cypress/fixtures/prod-data/.
```

### I2. `cypress-e2e.instructions.md` (`applyTo: "cypress/e2e/**/*.cy.{js,ts}"`)
**Why:** Spec files have structural rules (describe/it granularity, network discipline) that don't apply to page objects or API tests — scoping keeps the constitution short.

```markdown
---
applyTo: "cypress/e2e/**/*.cy.{js,ts}"
---
- describe per feature, context per state, it per user-visible behavior.
- Test names read as behavior: "shows inline error when email is invalid".
- All element access through page objects; create the page object first if missing.
- Intercept + alias every network call the test depends on; assert on aliases, never time.
- One assertion focus per it; setup in beforeEach or custom commands.
```

### I3. `api-tests.instructions.md` (`applyTo: "tests/api/**"`)
**Why:** API tests have their own non-negotiables — schema validation, cleanup, status-code discipline — that would be noise in UI-spec context.

```markdown
---
applyTo: "tests/api/**"
---
- Validate response schema (not just status) using the shared validators in tests/api/schemas/.
- Assert status code, contract shape, and business values — in that order.
- Any created entity must be deleted in afterEach, even on failure.
- Auth via tests/api/clients/auth.ts helper only; never raw tokens in specs.
- Prefer API-level coverage over UI wherever the behavior isn't visual.
```

### I4. `manual-test-cases.instructions.md` (`applyTo: "qa/test-cases/**"`)
**Why (functional team's file):** If the functional team drafts/maintains test cases in-repo with Copilot, this file makes every generated case land in the house format — the manual-side equivalent of the spec conventions.

```markdown
---
applyTo: "qa/test-cases/**"
---
- Format per case: ID | Title | Preconditions | Steps (numbered, one action each) | Expected result per step | Priority | Type (functional/regression/smoke).
- Titles describe behavior under test, not UI mechanics.
- Every case tagged with the requirement/story ID it traces to.
- Expected results must be observable and unambiguous — no "works correctly".
```

---

## 2. PROMPT FILES — 6, ranked by frequency of use

A prompt earns its place if the team performs the task at least weekly and quality varies by who prompts it. P1–P3 serve automation, P4–P5 serve functional, P6 serves both.

### P1. `/generate-e2e-test` — story → approved case matrix → green spec
**Why:** The core automation loop. The forced "matrix before code" gate is the value — it prevents the most common agentic failure (plausible-looking spec, wrong coverage).

```markdown
---
description: "Generate a Cypress e2e spec from a user story, with plan approval gate"
agent: test-implementer
---
Feature: ${input:featureName}
1. Ask for the story/acceptance criteria if not provided.
2. Check cypress/support/pages/ for an existing page object; extend or create.
3. Present a case matrix (happy/negative/edge, priority) and STOP for my approval.
4. On approval, implement in cypress/e2e/${input:featureName}/, run headless, iterate to green.
5. Summarize covered vs. deliberately out-of-scope.
```

### P2. `/generate-api-test` — endpoint/OpenAPI fragment → contract + behavior tests
**Why:** Same loop for the backend; encodes the schema-first discipline of I3 so API tests aren't status-code-only.

```markdown
---
description: "Generate API tests from an endpoint description or OpenAPI fragment"
agent: test-implementer
---
Endpoint: ${input:endpoint}
1. If an OpenAPI fragment exists in tests/api/schemas/, load it; else ask me for the contract.
2. Propose cases: happy, auth failures, validation errors (per field), boundary values, idempotency where relevant. STOP for approval.
3. Implement with schema validation + cleanup per repo rules; run npm run test:api; iterate to green.
```

### P3. `/review-test-pr` — the team checklist, applied consistently
**Why:** Review quality is the most person-dependent activity on the team. This makes the checklist executable and identical for every PR.

```markdown
---
description: "Review a test PR against the QE checklist"
agent: test-reviewer
---
Review the current diff. For each spec, check and report PASS/FAIL with line refs:
1. Selector policy (data-cy only) · 2. No time-based waits · 3. Test independence & cleanup
4. Assertion strength (would this fail if the feature broke?) · 5. Negative-path presence
6. Flakiness risks (race conditions, shared state, data assumptions)
End with: merge-blocking issues vs. suggestions, separately.
```

### P4. `/design-test-cases` — requirement → manual test case suite (functional team's P1)
**Why:** The functional team's highest-frequency task. Copilot is strong at systematic case derivation (equivalence classes, boundaries, state transitions) but only if the technique is demanded explicitly.

```markdown
---
description: "Design manual test cases from a requirement using formal techniques"
---
Requirement: ${input:requirement}
1. Ask clarifying questions about ambiguous or untestable statements first.
2. Derive cases using, explicitly labeled: equivalence partitioning, boundary values, state transitions (if stateful), and error guessing.
3. Output in the house format (see qa/test-cases/ rules) with priority and traceability ID.
4. List what you could NOT derive coverage for and why.
```

### P5. `/exploratory-charter` — session charter + debrief scaffold
**Why:** Turns exploratory testing from ad hoc into session-based (charter → time-box → debrief) without imposing heavyweight process — the highest-leverage upgrade for a functional team's exploratory practice.

```markdown
---
description: "Create an exploratory testing session charter and debrief template"
---
Target area: ${input:area}
Produce: 1) Charter (mission, scope in/out, risks to probe, data/personas to use, time-box);
2) A "tours" list — 5–8 concrete exploration heuristics for this area (interruption, back-button, boundary, role-switch, slow-network…);
3) Debrief template: bugs found, questions raised, coverage notes, follow-up automation candidates.
```

### P6. `/bug-report` — raw observation → developer-ready report
**Why:** Serves both teams; bug report quality drives fix turnaround. The prompt forces repro-step discipline and severity/priority separation.

```markdown
---
description: "Turn a raw defect observation into a structured, developer-ready bug report"
---
Observation: ${input:observation}
Produce: Title (behavior, not blame) · Environment · Preconditions · Numbered repro steps (one action each) · Expected vs. Actual · Severity AND Priority (separately, with one-line justification) · Attachments to capture (logs/HAR/screenshot list).
Ask me for any missing repro detail rather than inventing it.
```

---

## 3. AGENTS — 4, defined by tool posture (not persona flavor)

An agent earns its place only if it needs a *different tool boundary* than the default. Personas without boundary differences are prompt-file material — that's why there are only four.

### A1. `test-planner` — read-only
**Why:** Planning must be incapable of mutating the repo. Enforced read-only is the whole point; it also serves the functional team as a requirements-analysis partner.

```markdown
---
name: test-planner
description: "Requirements → test strategy, case matrix, risks. Read-only; never writes code."
tools: ["search", "read"]
---
You are a senior QE architect. For any requirement: identify testable behaviors, risks, boundaries;
produce a case matrix (ID, behavior, level: unit/API/e2e/manual, priority, data needs);
recommend the automation-vs-manual and API-vs-UI split (prefer the lowest level that proves the behavior);
flag untestable statements with clarifying questions. Hand off to test-implementer when approved.
```

### A2. `test-implementer` — edit + gated terminal
**Why:** The only agent allowed to write specs. Concentrating write access in one agent makes "who can change code" auditable.

```markdown
---
name: test-implementer
description: "Implements Cypress and API tests from an approved plan."
tools: ["search", "read", "edit", "terminal"]
---
You implement tests only from an approved plan (from test-planner or the user).
Follow all repo instructions. Run affected tests after every change; iterate to green.
Never expand scope beyond the approved matrix without asking. Never weaken an assertion to make a test pass — report the discrepancy instead.
```

### A3. `test-reviewer` — read-only
**Why:** A reviewer that can edit will "helpfully" fix instead of review, destroying the audit value. Read-only forces findings, not silent changes.

```markdown
---
name: test-reviewer
description: "Reviews test code and test cases for quality and flakiness risk. Read-only."
tools: ["search", "read"]
---
Apply the team checklist (selector policy, waits, independence, assertion strength, negative paths, flakiness risks).
Report findings with file:line references, merge-blocking vs. suggestion, and the WHY for each.
You never modify files — you produce review findings only.
```

### A4. `flaky-test-investigator` — read + terminal, no edit
**Why:** Investigation needs to *run* things (re-run specs, pull CI history) but granting edit invites the classic anti-fix: patching the symptom with a wait. No-edit forces diagnose-then-handoff.

```markdown
---
name: flaky-test-investigator
description: "Diagnoses intermittent test failures. Can run tests and scripts; cannot edit files."
tools: ["search", "read", "terminal"]
---
For a flaky spec: pull CI history (flaky-test-triage skill), classify the failure (timing / pollution / data / environment / genuine bug),
reproduce locally where possible, and produce a diagnosis + minimal-fix recommendation.
Never propose cy.wait(ms). If it's a product bug, draft the bug report instead of a test change.
```

---

## 4. SKILLS — 5, only where bulk knowledge or scripts are involved

A skill earns its place only if it carries material too big for always-on instructions AND too important to rely on humans invoking — or if it must bundle a script. Each description below is written as a trigger condition, because that line decides whether the skill ever fires.

### S1. `cypress-authoring/`
**Why:** Your full spec playbook + gold-standard examples + selector map is thousands of lines — always-on would tax every request; a prompt would get forgotten. This is the canonical skill use case.

```markdown
---
name: cypress-authoring
description: "Use when writing, editing, refactoring, or reviewing Cypress e2e specs, page objects, or custom commands in this repo."
---
# Cypress Authoring Playbook
- Gold-standard spec: examples/gold-standard.cy.ts — mirror its structure.
- Selector map: references/selector-map.md — canonical data-cy names per page.
- Custom commands: references/commands.md — check here before writing raw Cypress.
- Patterns: network discipline, session/auth caching, file upload/download, iframe handling → references/patterns.md
```

### S2. `flaky-test-triage/`
**Why:** Pairs a decision tree with a *runnable script* — the bundled-script capability only skills have. Feeds agent A4.

```markdown
---
name: flaky-test-triage
description: "Use when a test is flaky, intermittent, unstable in CI, or passes locally but fails in the pipeline."
---
1. Run scripts/pull-ci-history.sh <spec-path> → last 20 runs + failure signatures.
2. Classify before fixing: timing/race · test pollution · data drift · environment · genuine bug (taxonomy + tells in references/taxonomy.md).
3. Minimal fix per class; cy.wait(ms) is never a fix; genuine bugs become bug reports, not test edits.
```

### S3. `api-contract-testing/`
**Why:** Houses the OpenAPI fragments and schema validators the team currently pastes into chat — re-pasting contracts is the clearest "should have been a skill" smell.

```markdown
---
name: api-contract-testing
description: "Use when writing or reviewing backend/API tests, validating response schemas, or working from OpenAPI definitions."
---
- Contracts: references/openapi/ (one file per service) — always validate against these, never a hand-typed shape.
- Shared validators: how to use tests/api/schemas/ helpers → references/validators.md
- Gold-standard API test: examples/orders-api.test.ts
- Case checklist per endpoint: happy · authz matrix · per-field validation · boundaries · idempotency.
```

### S4. `test-data-setup/`
**Why:** Data setup/teardown is the most dangerous thing an agent can touch (shared environments). Centralizing the safe scripts + rules in one skill both enables and constrains it. Serves functional testers preparing manual-session data too.

```markdown
---
name: test-data-setup
description: "Use when seeding, creating, resetting, or cleaning up test data or test environments for manual or automated testing."
---
- Seed: scripts/seed-env.sh <env> <dataset> · Reset: scripts/reset-env.sh <env> (NEVER against envs listed in references/protected-envs.md).
- Datasets catalog: references/datasets.md (personas, states, edge-case records).
- Rule: tests create-and-clean their own entities; shared seeded data is read-only.
```

### S5. `requirements-analysis/` (functional team's skill)
**Why:** The functional team's deep material — testability heuristics, ambiguity checklists, house examples of good ACs — is bulk knowledge that should auto-load whenever someone works on requirements or test design, powering P4/P5 and agent A1.

```markdown
---
name: requirements-analysis
description: "Use when analyzing requirements, user stories, or acceptance criteria for testability, ambiguity, or test design."
---
- Ambiguity checklist: references/ambiguity-checklist.md (vague quantifiers, missing actors, undefined states, untestable adverbs).
- Techniques and when each pays off: references/techniques.md (EP, BVA, state transition, decision tables, pairwise).
- House-standard AC examples: examples/good-acs.md — rewrite weak ACs to this bar.
```

---

## 5. How the Catalog Composes — two end-to-end flows

**Automation flow:** story → `test-planner` (A1, read-only; loads S5 for testability analysis) produces matrix → handoff → `/generate-e2e-test` (P1) under `test-implementer` (A2), with I1+I2 always-on and S1 auto-loading → PR → `/review-test-pr` (P3) under `test-reviewer` (A3). A CI flake later routes to A4 + S2.

**Functional flow:** requirement → `/design-test-cases` (P4, with S5 firing) lands cases in `qa/test-cases/` formatted by I4 → `/exploratory-charter` (P5) for session testing, data prepared via S4 → findings become `/bug-report` (P6) outputs, and automation candidates from the debrief feed back into the automation flow via A1.

---

## 6. Deliberately Excluded — and why (this is the curation)

1. **A "QA assistant" general agent.** No distinct tool posture, no distinct role → it's just chat with a costume. Adds a selection step for zero enforcement value.
2. **Per-feature agents (checkout-agent, login-agent…).** Feature knowledge is *context*, not *role*. Feature-specific material belongs in skills/references; agents multiply only when tool boundaries differ.
3. **A `/write-any-test` mega-prompt.** UI and API loops differ enough (page objects vs. contracts) that one prompt serving both degrades both. P1/P2 stay separate on purpose.
4. **`code-style.instructions.md` for generic JS/TS style.** Linters enforce style deterministically and for free; don't spend always-on tokens duplicating ESLint/Prettier.
5. **A `test-fixer` agent with blanket edit+terminal rights.** Highest-risk pattern in QE agentics: it converges on weakening assertions and adding waits to get green. Diagnosis (A4, no edit) and implementation (A2, plan-gated) stay separated on purpose.
6. **A skill wrapping Cypress's public documentation.** The model already knows public Cypress APIs; skills are for *your* conventions, contracts, and scripts — bundling public docs adds load-time and maintenance for near-zero lift.
7. **Prompts for rare ceremonies (release sign-off memo, quarterly report).** Below the weekly-frequency bar; run them ad hoc. Promote to a prompt file only when repetition proves the need.

**Standing rule for growth:** every proposed addition must name the recurring activity it serves, why the other three primitives don't cover it, and who maintains it. If any answer is missing — it doesn't go in `.github/`.
