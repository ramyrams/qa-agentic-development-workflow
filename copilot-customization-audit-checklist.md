# Enterprise Audit & Review Checklist
### GitHub Copilot Customization — `*.instructions.md` · `*.agent.md` · `SKILL.md` · `*.prompt.md`

**Purpose:** A repeatable audit instrument to verify that a team's `.github/` customization implementation meets enterprise standards for correctness, security, maintainability, and measurable value.
**How to use:** Score each item **Pass / Fail / N/A**. Items marked ⛔ are **merge/deploy blockers** — a single ⛔ failure fails the audit regardless of overall score. Run the full audit quarterly and the per-type checklist on every PR that touches `.github/` customization files.
**Roles:** Auditor (governance/QE lead) · File owner (per CODEOWNERS) · Security reviewer (required for Section 5 and all skill audits).

---

## SECTION 1 — Foundation & Repo Hygiene (applies before any per-type check)

**1.1 Placement & naming**
- [ ] All customization files live in canonical locations: `.github/copilot-instructions.md`, `.github/instructions/`, `.github/prompts/`, `.github/agents/`, `.github/skills/<name>/SKILL.md` — no strays in repo root or feature folders. *Why: discoverability and org-level tooling depend on canonical paths.*
- [ ] File names follow the required patterns (`*.instructions.md`, `*.prompt.md`, agent-name-as-filename, literal `SKILL.md`) — misnamed files silently never load. ⛔
- [ ] Exactly **one** `copilot-instructions.md` per repo; no duplicated "constitution" content across path files.

**1.2 Version control & change management**
- [ ] Every customization file is in git — none distributed by chat/email/wiki copies. ⛔
- [ ] CODEOWNERS entry covers `.github/instructions/`, `/agents/`, `/skills/`, `/prompts/` and `copilot-instructions.md`, so no change merges without a designated reviewer. ⛔
- [ ] Branch protection applies to `.github/` paths (no direct pushes to default branch).
- [ ] Each file carries a header comment or frontmatter with owner + last-reviewed date, and none is older than the review cadence (quarterly).
- [ ] A CHANGELOG entry (or conventional commit discipline) exists for every material change — "generation quality shifted; what changed in `.github/`?" must be answerable from history.

**1.3 Non-duplication across layers**
- [ ] No rule appears in more than one layer (constitution vs. path instructions vs. agent vs. prompt vs. skill). Duplication = future contradiction. *Spot-check 5 random rules.*
- [ ] No contradictions between repo-wide and path-scoped instructions (layers combine additively; conflicts produce inconsistent generations, not clean overrides). ⛔

---

## SECTION 2 — `*.instructions.md` Audit (always-on layer)

**2.1 Scope correctness**
- [ ] Repo-wide file contains only rules true for **every** request; anything starting with "in the e2e specs…" / "for API tests…" has been pushed to a path file.
- [ ] Every path file has a valid `applyTo:` glob, and the glob has been **tested**: open a matching and a non-matching file, confirm the rules apply/don't apply. ⛔ *(An untested glob is an unverified control.)*
- [ ] Globs don't overlap in ways that stack contradictory rules on the same path.

**2.2 Content quality**
- [ ] Repo-wide file ≤ ~100 lines. Every line is a rule, a path, or a command — no narrative, rationale essays, or onboarding prose (that's README material). *Why: always-on tokens tax every request.*
- [ ] Rules are imperative, specific, and testable ("data-cy selectors only", not "use good selectors").
- [ ] Hard prohibitions are stated as "Never …" lines and grouped — models weight explicit negative rules well.
- [ ] Build/test/lint commands listed are current — run each one during audit. Stale commands actively mislead the agent. ⛔
- [ ] No secrets, tokens, internal URLs, or environment credentials anywhere in instruction content. ⛔

**2.3 Effectiveness evidence**
- [ ] Team can produce a before/after example (or eval result) showing at least one convention Copilot now follows because of these files.
- [ ] PR review comments were mined as source material — the rules reviewers repeat weekly appear here.

---

## SECTION 3 — `*.prompt.md` Audit (user-triggered procedures)

**3.1 Justification & design**
- [ ] Each prompt maps to a recurring (≥ weekly) activity — named in the file's `description:`. One-off ceremonies don't belong.
- [ ] `description:` is accurate and distinct enough that `/` autocomplete disambiguates prompts at a glance.
- [ ] Procedure has a defined beginning, end, and output shape; inputs are declared via `${input:…}` variables, not implied.
- [ ] High-consequence prompts (anything generating code or modifying files) contain an explicit **human approval gate** ("present the plan and STOP for approval") before mutation steps. ⛔
- [ ] The prompt adds only task-specific steps — it does not restate repo instructions (already in context) or embed bulk reference material (skill territory). Length ≤ ~1 page.

**3.2 Execution correctness**
- [ ] If the prompt specifies an `agent:`, that agent exists and its tool posture is sufficient for the procedure (a read-only agent can't execute an implementation prompt). ⛔
- [ ] Each prompt has been run end-to-end within the last quarter and produced acceptable output; a sample output is linked or attached to the audit.
- [ ] Failure behavior is defined: what the model should do when inputs are missing (ask, don't invent). *Spot-check: invoke with missing input.*

---

## SECTION 4 — `*.agent.md` Audit (roles & tool boundaries)

**4.1 Existence justification**
- [ ] Every agent has a **distinct tool posture** or enforced behavioral boundary versus the default and versus every other agent. A persona with default tools is a prompt file, not an agent — delete or demote it.
- [ ] Agent count is small and roles are non-overlapping (planner/implementer/reviewer/investigator-style separation). Overlap = users can't choose = agents go unused.

**4.2 Least privilege (the core of this section)**
- [ ] `tools:` is an explicit allow-list on every agent — no agent ships without a tools declaration. ⛔
- [ ] Read-only roles (planner, reviewer) have **no edit and no terminal**. ⛔
- [ ] Terminal access is granted only where the role requires executing something, and never combined with edit unless the role genuinely needs both (implementer only, typically).
- [ ] Boundaries have been **negatively tested**: ask the read-only agent to modify a file and confirm it cannot. Record the test in the audit. ⛔ *(Enforced controls must be verified, not assumed.)*
- [ ] No agent instruction claims elevated permissions or instructs the model to bypass confirmations.

**4.3 Behavioral definition**
- [ ] Each agent file defines: role, scope boundaries ("you never…"), handoff conditions (which agent receives approved work), and refusal behavior for out-of-scope asks.
- [ ] Implementer-class agents include the two enterprise guardrail lines: never expand scope beyond the approved plan without asking; never weaken an assertion / add waits to force green — report discrepancies instead.
- [ ] Org-level agents (distributed via the `.github-private` repo `agents/` folder) are reviewed under the same checklist by the central owner, and repo-level agents don't shadow org agents with the same name.

---

## SECTION 5 — `SKILL.md` Audit (highest-risk primitive — security reviewer required)

**5.1 Trigger correctness**
- [ ] `description:` is written as a trigger condition ("Use when …") naming concrete task types and synonyms (e.g., "flaky, intermittent, unstable in CI, passes locally but fails in pipeline").
- [ ] **Positive trigger test:** run a matching task, confirm the skill loads. **Negative trigger test:** run an adjacent non-matching task, confirm it doesn't. Record both. ⛔ *(A skill that never fires is dead weight; one that over-fires pollutes context.)*
- [ ] Skill name is a stable slug; folder contains `SKILL.md` at its root plus organized `scripts/`, `references/`, `examples/` — no loose sprawl.

**5.2 Content economics**
- [ ] SKILL.md body is instructions and pointers; bulk material lives in `references/` (progressive disclosure preserved — don't defeat it by inlining everything).
- [ ] Skill contains *your* conventions, contracts, examples, and scripts — not wrapped public documentation the model already knows.
- [ ] Examples marked "gold standard" actually pass current lint/test gates — a broken gold example teaches broken patterns. Run them. ⛔

**5.3 Script & supply-chain security (blockers throughout)**
- [ ] Every bundled script has been line-by-line reviewed by the security reviewer; review recorded (who/when/commit SHA). ⛔
- [ ] No script handles credentials outside the approved mechanism; no plaintext secrets, tokens, or internal endpoints in any skill file. ⛔
- [ ] Destructive operations (data reset, deletes) are guarded: protected-environment deny-lists, confirmation requirements, or dry-run defaults. ⛔
- [ ] `allowed-tools:` does **not** pre-approve `shell`/`bash` unless the skill and all referenced scripts are fully trusted and the exception is documented with sign-off — pre-approval removes the human confirmation gate and is the primary prompt-injection execution path. ⛔
- [ ] **Third-party/external skills:** full content inspection (including every script and reference) before adoption; provenance recorded; pinned to a reviewed version — skills are not verified by GitHub and can carry prompt injections or malicious code. ⛔
- [ ] Skill text itself contains no instructions that attempt to override repo instructions, disable safeguards, or instruct the agent to act outside its tool posture (prompt-injection review of the *Markdown*, not just the scripts). ⛔

---

## SECTION 6 — Enterprise Governance Layer (org-wide, beyond any single repo)

**6.1 Ownership & lifecycle**
- [ ] A named owner exists for the customization estate per repo, and a central owner for org-distributed assets; both appear in CODEOWNERS.
- [ ] Quarterly review cadence is calendared; each file's last-reviewed date is updated as evidence.
- [ ] A deprecation path exists: unused prompts/agents/skills (no invocation/trigger in a quarter) are flagged and removed — dead assets are unaudited attack surface and reader confusion.
- [ ] New-asset intake applies the standing rule: proposer names the recurring activity served, why the other three primitives don't cover it, and who maintains it. No answer, no merge.

**6.2 Standardization & reuse across teams**
- [ ] Org-common assets (shared agents, cross-repo skills, the universal instruction subset) are centralized (org `.github-private` / a shared skills repo) rather than copy-pasted per repo — copies fork and drift.
- [ ] Tool-agnostic assets use portable formats where available (Agent Skills open standard; `AGENTS.md` for multi-agent instructions) so the estate survives tooling changes.
- [ ] A discoverability index exists (internal page or repo README section) listing available prompts/agents/skills with one-line purposes — unused-because-unknown is the most common enterprise failure.

**6.3 Security & compliance posture**
- [ ] Default org posture documented: terminal commands require human confirmation; exceptions are per-asset, reviewed, and time-bound.
- [ ] Customization files are in scope for the org's secret-scanning and content-exclusion policies; audit confirms scanners cover `.github/skills/**` scripts.
- [ ] An incident playbook exists for a compromised/malicious customization file (revert path, blast-radius assessment via git history, comms).
- [ ] Personal-scope assets (user-profile agents/prompts, `~/.copilot/skills/`) are addressed by policy: team-relevant assets must be promoted into the repo where they're reviewable; security-relevant rules must never live only in personal scope. *(You cannot audit what lives on laptops.)*

**6.4 Measurement (value must be evidenced, not asserted)**
- [ ] A fixed eval set of representative generation tasks exists; outputs are graded against the failure taxonomy **before and after** material `.github/` changes, and scores are recorded. *(Connects to the existing eval harness — trajectory grading + failure taxonomy are the measurement layer.)*
- [ ] Usage signals are tracked at least coarsely (which prompts get invoked, which agents get selected, which skills fire) to drive the deprecation loop in 6.1.
- [ ] At least one KPI ties the estate to team outcomes (e.g., review-cycle findings per PR, flaky-test recurrence, spec authoring lead time) — token spend is a cost metric, not a value metric.

**6.5 People & process**
- [ ] Onboarding covers the four-primitive mental model and the "who triggers what" rule (instructions=nobody, prompts=human, agents=human selects, skills=model).
- [ ] The prompt-review ritual (biweekly demo of one customization improvement) is running — evidence: last two session notes.
- [ ] Engineers know the escalation path for "Copilot did something unexpected" and it routes to the estate owner, not just individual retries.

---

## SECTION 7 — Instant-Fail Red Flags (scan first; any hit = stop and remediate)

1. ⛔ Secrets, tokens, credentials, or internal environment URLs in any customization file or bundled script.
2. ⛔ `shell`/`bash` pre-approved in a skill or agent without documented review + sign-off.
3. ⛔ A third-party skill adopted without full content inspection and version pinning.
4. ⛔ An agent shipping without an explicit `tools:` allow-list, or a "reviewer/planner" agent holding edit rights.
5. ⛔ Contradictory rules across instruction layers (verified by reading, not assumed).
6. ⛔ Customization files bypassing PR review (direct pushes, no CODEOWNERS coverage).
7. ⛔ A destructive script (env reset, data delete) reachable by an agent without environment deny-lists or confirmation gates.
8. ⛔ Untested controls: `applyTo` globs never verified, agent boundaries never negatively tested, skill triggers never exercised.

---

## Audit Scoring Summary (template)

| Section | Items | Pass | Fail | N/A | ⛔ failures |
|---|---|---|---|---|---|
| 1. Foundation | 10 | | | | |
| 2. Instructions | 10 | | | | |
| 3. Prompts | 8 | | | | |
| 4. Agents | 10 | | | | |
| 5. Skills | 12 | | | | |
| 6. Governance | 14 | | | | |
| 7. Red flags | 8 | | | | |

**Verdict rule:** Any ⛔ failure → **Fail (remediate before next release)**. Otherwise ≥ 90% pass → **Pass**; 75–89% → **Conditional pass** with 30-day remediation plan; < 75% → **Fail**.

*Auditor: ________ · Repo: ________ · Date: ________ · Next audit due: ________*
