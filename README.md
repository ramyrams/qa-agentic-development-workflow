# qa-agentic-development-workflow



# Document Index — Agentic QA Initiative
### Start here. Everything else in this library assumes you found it through this map.

**19 documents exist as of this writing.** This index is the one you bookmark; nobody should have to guess reading order. Ownership and update dates go in the table below as the estate matures — an index nobody maintains becomes exactly the kind of stale artifact your own audit checklist warns about.

---

## The Library, by Purpose

| # | Document | Purpose in one line | Audience |
|---|---|---|---|
| 1 | `copilot-customization-framework-qa.md` | The mental model — what agents/skills/instructions/prompts are and when to use each | Everyone, first |
| 2 | `copilot-file-types-comparison.md` | Deep side-by-side comparison tables for the four file types, plus README vs. instructions | Anyone authoring assets |
| 3 | `ai-eval-terminology-glossary.md` | Vocabulary to master before touching eval work | Anyone before their first eval task |
| 4 | `qe-curated-catalog.md` | The original high-value starter set (4 instructions, 6 prompts, 4 agents, 5 skills) with examples | Anyone building the initial estate |
| 5 | `copilot-customization-audit-checklist.md` | 72-item enterprise audit/PR-review checklist — the quality bar | Reviewers, auditors, CODEOWNERS |
| 6 | `agentic-competency-ladder.md` | User/Author/Architect levels with assessable criteria | Managers, mentors, career growth |
| 7 | `agentic-kata-set.md` | Six practice exercises + capstone, wired to the ladder | Everyone, ongoing biweekly practice |
| 8 | `allure-analysis-automation-design.md` | The flagship shipped project — Allure report automation + failure ledger | Whoever builds/maintains it |
| 9–14 | `agentic-qa-workflow-catalog.md` (Vol 1–6) | 150 workflow ideas across the full QA lifecycle, business outcomes, and practitioner workbench | Roadmap planning, management shortlisting |
| 15 | `eval-program-master-plan.md` | The manager-level program plan — timeline, roles, budget, risk, governance | You, and whoever approves resourcing |
| 16 | `automation-agent-eval-implementation-plan.md` | The eval methodology — four suites, grading strategy, phased build | Whoever architects the eval harness |
| 17 | `copilot-cli-eval-tooling-setup-guide.md` | Hands-on tool setup — install, hooks, runner scripts, CI wiring | Whoever builds the harness, hands-on |
| 18 | `eval-plans-by-primitive.md` | Why instructions/prompts/skills/agents need different eval approaches, plus specifics for each | Whoever's evaluating something other than an agent |
| 19 | `eval-must-test-checklist.md` | The concrete must-write test cases, with a 15-item minimum viable set | Whoever's writing actual eval specs today |

---

## Reading Paths by Role

**New team member, week one:**
3 (glossary isn't needed yet — skip unless they're touching eval) → 1 → 2 → 4 → 7 (start kata practice immediately, don't wait to "finish reading")

**Engineer about to author a new agent/skill/prompt/instruction:**
1 → 2 → 5 (know the bar before you build, not after) → the relevant workflow catalog volume for inspiration → 19 → 16/17 as needed

**Engineer about to build eval coverage for something they didn't write:**
3 → 16 → 17 → 18 → 19

**You, going to leadership for eval program resourcing:**
15 alone is designed to stand alone for this conversation

**You, going to leadership for the broader initiative (not eval-specific):**
The consolidated management view and shortlisting scorecard live inside Volume 3 of the workflow catalog (`agentic-qa-workflow-catalog-vol3.md`) — this is the one gap worth naming: **that content deserves its own standalone one-pager once you've actually finalized your shortlist**, rather than living inside a 150-item catalog. Build it *after* you've chosen, not before — a charter for an undecided shortlist is just the scorecard restated.

**Auditor doing the quarterly review:**
5, then whatever eval dashboards/outputs 16–19 have produced by then

**Mentor running a kata session:**
7, cross-referenced against 6 for which level each kata is building

---

## Living Documents vs. Read-Once

Most of this library is **read-once, reference-forever** — the framework, comparisons, and glossary don't change often and don't need re-reading once internalized. Three documents are **living** and need actual ownership:

- **5 (audit checklist)** — re-run quarterly per its own cadence; update when Copilot's actual behavior changes.
- **6 + 7 (ladder + katas)** — review annually per the ladder's own instruction; katas cycle continuously.
- **9–14 (workflow catalog)** — this is a backlog, not a finished document; items move out of it as they're built, and it should be pruned, not just added to.

Everything eval-related (15–19) will need a light refresh once the program actually runs for a quarter and reality diverges slightly from plan — expected and fine, not a sign anything was wrong originally.

---

## What's Deliberately Not Built Yet — and When To Build It

Three more documents are real candidates, but building them now would be premature — each has a natural trigger that should come first:

| Document | Build it when... | Why not now |
|---|---|---|
| **Templates pack** — copy-paste starter `SKILL.md`/`agent.md`/`prompt.md`/`instructions.md` | The team starts authoring their second and third assets and you notice people re-deriving the same boilerplate | The examples scattered across docs 1, 4, and 19 are sufficient for the first few builds; extracting them into a standalone templates pack is a 30-minute job once you know which patterns actually recur |
| **Contributing guide** — the intake rule (Section 6 of the workflow catalog) operationalized as a one-page "how to propose a new asset" | Someone outside the original core group wants to propose an addition | Right now you know who's building what; this becomes necessary the moment the estate has contributors who weren't in this conversation |
| **Decision log (ADR-style)** | The first time someone asks "wait, why is the healer scoped to selector/timing only?" and the answer isn't written down anywhere | Decision logs written speculatively before real decisions accumulate end up empty or fabricated — let it start from real questions |

Don't build these preemptively. Each is cheap when its trigger actually fires and mostly wasted effort before that.

---

## The Actual Next Action

Not a document. Per the eval program master plan, Phase 0 (tool installation and verification) is the concrete next step, and per this whole library's own discipline about ideation-without-execution: the highest-value thing that can happen next is your team **running the kata cycle and Phase 0 of the eval build**, not you or me producing document #20. This index exists to make everything already built usable — use it, then go execute.

*Owner: ________ · Last updated: ________ · Update this table whenever a document is added, retired, or materially revised.*
