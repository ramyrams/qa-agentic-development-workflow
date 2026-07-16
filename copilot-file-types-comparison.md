# Side-by-Side Comparisons: GitHub Copilot Customization Files
### Companion to the Copilot Customization Framework — for the QA automation team
`*.instructions.md` vs `*.agent.md` vs `SKILL.md` vs `*.prompt.md` (the four customization primitives)

---

## PART A — The Four Customization Primitives, Dimension by Dimension

### A.1 Identity & Location

| Dimension | `*.instructions.md` | `*.agent.md` | `SKILL.md` | `*.prompt.md` |
|---|---|---|---|---|
| **What it is** | Always-on (or path-scoped) background rules | A specialist persona/mode with its own instructions and tool boundaries | A self-contained capability package (instructions + scripts + references + examples) | A reusable, parameterized task template |
| **One-line job** | "How we do things here, always" | "Who is doing the work, and what they're allowed to touch" | "Deep know-how the agent pulls in when the task calls for it" | "A repeatable procedure a human kicks off" |
| **File name pattern** | `NAME.instructions.md` | `AGENT-NAME.md` (agent name = file name) | Always literally `SKILL.md` | `NAME.prompt.md` |
| **Repo location** | `.github/instructions/` (repo-wide variant: `.github/copilot-instructions.md`) | `.github/agents/` | `.github/skills/<skill-name>/SKILL.md` — the skill is the **folder**, not just the file | `.github/prompts/` |
| **Personal / global variant** | VS Code user-profile instructions ("User Data" location) | User-profile agents; org/enterprise via `agents/` in a `.github-private` repo | `~/.copilot/skills/` (personal, all workspaces) | User-profile prompt files |
| **Can bundle other files?** | No — a single Markdown file | No — a single Markdown file (but can reference repo files) | **Yes — its defining feature.** `scripts/`, `references/`, `examples/`, templates alongside SKILL.md | No — a single Markdown file (can link to repo files) |

### A.2 Activation & Context Loading (the distinction that matters most)

| Dimension | `*.instructions.md` | `*.agent.md` | `SKILL.md` | `*.prompt.md` |
|---|---|---|---|---|
| **Who triggers it** | Nobody — automatic | **Human** selects the agent (or a prompt file / handoff specifies it) | **The model** decides, based on task-vs-description match | **Human** invokes `/prompt-name` in chat |
| **When it enters context** | Every request (repo-wide) or every request touching files matched by `applyTo` glob | For the duration of the chat session while that agent is active | Mid-task, when Copilot judges the skill relevant | Once, at the moment of invocation |
| **Loading style** | Full file injected, always | Full agent definition active for the session | **Progressive disclosure**: name+description always visible → full SKILL.md loaded on match → bundled resources read on demand | Full file injected on invocation |
| **Can it be "forgotten" by the user?** | No — that's the point | Yes — user might not select it | No — fires automatically *if* the description is well written | Yes — user must remember it exists |
| **Can it fail to fire?** | Only if `applyTo` glob doesn't match the touched files | N/A (explicit selection) | **Yes — the #1 failure mode.** Vague description = skill never loads | N/A (explicit invocation) |
| **Context cost** | Paid on **every request** — keep it short | Paid per session while active | Near-zero until triggered (only name+description), then pay-as-you-go | Paid only when invoked |
| **Deactivation** | Remove file / narrow the glob | Switch agents | Model simply doesn't load it for unrelated tasks | Don't invoke it |

**Memory hook for the team:** *Instructions = nobody triggers. Prompts = the human triggers. Agents = the human selects. Skills = the model triggers.*

### A.3 Anatomy — Frontmatter & Body

| Dimension | `*.instructions.md` | `*.agent.md` | `SKILL.md` | `*.prompt.md` |
|---|---|---|---|---|
| **Key frontmatter fields** | `applyTo:` (glob — required for path-scoping), `description:` | `name:`, `description:`, `tools:` (allow-list), optionally model | `name:`, `description:` (the trigger condition — most important line), optionally `allowed-tools:`, `license:` | `description:`, `agent:`/`mode:`, `tools:`, `model:` |
| **Body content** | Short declarative rules and conventions; no procedures | Persona definition, behavioral rules, scope boundaries, handoff conditions | Detailed how-to instructions, when/how to run bundled scripts, pointers to references and examples | Step-by-step procedure with a beginning and an end |
| **Supports input variables?** | No | No | No (but scripts can take arguments) | **Yes** — `${input:varName}`, selection/file variables |
| **Ideal length** | Repo-wide: ~50–100 lines. Path-scoped: shorter | Half a page to a page | As long as needed — cost is deferred; push bulk into `references/` | Half a page; move reference bulk into a skill |
| **Contains executable code?** | No | No | **Can** — bundled scripts the agent may run | No (but its procedure may tell the agent to run repo commands) |

### A.4 Control, Scope & Composition

| Dimension | `*.instructions.md` | `*.agent.md` | `SKILL.md` | `*.prompt.md` |
|---|---|---|---|---|
| **Can restrict tools?** | No — purely advisory text | **Yes — enforced.** The only primitive with hard tool boundaries | Partially — `allowed-tools` pre-approval (a convenience/risk lever, not a restriction mechanism) | Can specify a tool set for the run, and inherits the executing agent's limits |
| **Enforcement strength** | Advisory — model *should* follow, may not always | **Enforced** — a read-only agent cannot edit, period | Advisory instructions + optionally pre-approved tools | Advisory procedure |
| **Scope of effect** | Whole repo, or file paths matched by glob | The active chat session | The specific task the model matched it to | The single invoked run |
| **Combines with the others?** | Applies underneath everything — agents, prompts, and skill-driven work all still receive instructions | Executes prompts; loads skills; layered on top of instructions | Loaded *by* whatever agent is active; complements instructions with depth | Can name an `agent:` to run under; benefits from instructions and any skills that fire |
| **Interaction rule of thumb** | Carries **universal rules** | Carries **role + tool posture** | Carries **deep reference + helpers** | Carries **the procedure** |
| **Duplication anti-pattern** | Don't restate in agents/prompts — it's already in context | Don't paste repo conventions in — only what's *different* for this role | Don't put one-line universal rules here — they belong in instructions | Don't embed the full playbook — reference the skill's territory instead |

### A.5 Portability & Surface Support

| Dimension | `*.instructions.md` | `*.agent.md` | `SKILL.md` | `*.prompt.md` |
|---|---|---|---|---|
| **VS Code Copilot Chat / agent mode** | Yes | Yes | Yes | Yes |
| **Copilot coding agent (cloud)** | Yes (incl. path-specific) | Yes | Yes | Primarily an IDE/chat feature |
| **Copilot code review** | Path-specific instructions apply | Not the mechanism used | Yes — review-relevant skills can be picked up (name review skills clearly, e.g. `code-review`) | No |
| **Copilot CLI** | Yes | Yes | Yes | Limited/varies |
| **Beyond GitHub Copilot** | `AGENTS.md` variant is an open, multi-agent format; `.instructions.md` is Copilot-specific | Copilot-specific format | **Open Agent Skills standard** — portable to other skill-compatible agents (e.g. Claude-based tools; `.claude/skills` is also read) | Copilot/VS Code-specific format |
| **Best choice when tool-agnosticism matters** | Use `AGENTS.md` for the universal subset | — | **Skills — most portable primitive** | — |

*(Surface support evolves quickly — verify against the GitHub customization cheat sheet when onboarding a new surface.)*

### A.6 Risk, Governance & Maintenance

| Dimension | `*.instructions.md` | `*.agent.md` | `SKILL.md` | `*.prompt.md` |
|---|---|---|---|---|
| **Primary risk** | Bloat/staleness silently degrades **every** generation in the repo | Over-permissive `tools:` list defeats the purpose | **Highest risk**: bundled scripts + third-party skills can carry prompt injections or malicious code; `allowed-tools: bash` removes the human confirmation gate | Drift — the procedure stops matching how the team actually works |
| **Review posture** | Highest scrutiny per line (always-on) | Review the tool list like an IAM policy | Inspect full contents incl. scripts before adopting anything external; prefer writing your own | Normal PR review |
| **Staleness blast radius** | Entire repo, every request | Sessions using that agent | Tasks that trigger it | Runs that invoke it |
| **How you notice it's broken** | Generation quality drops everywhere; conventions violated | Agent does things outside its role | Skill never fires (bad description) or fires wrongly | Output no longer matches expectations on invocation |
| **Testing approach** | Before/after eval on representative tasks | Verify tool boundaries by attempting out-of-scope actions | Verify triggering: run matching + non-matching tasks, confirm load behavior | Run it; grade output against your failure taxonomy |

### A.7 QA-Team Decision Summary

| You want to… | Use |
|---|---|
| Ban `cy.wait(ms)` and enforce `data-cy` selectors everywhere | `*.instructions.md` (path-scoped to specs) |
| Give spec files different rules than page objects | Two `*.instructions.md` files with different `applyTo` globs |
| Standardize "turn a user story into a spec" as a runnable procedure with inputs | `*.prompt.md` |
| Guarantee the planning conversation can never edit files | `*.agent.md` with read-only tools |
| Make your 2,000-line Cypress playbook + gold examples available without paying for it on every request | `SKILL.md` (skill folder) |
| Ship a triage decision tree **with a script** that pulls CI history | `SKILL.md` — only skills bundle scripts |
| Make know-how portable to non-Copilot agents | `SKILL.md` (+ `AGENTS.md` for universal rules) |

---

