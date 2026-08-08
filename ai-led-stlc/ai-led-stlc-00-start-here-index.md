# AI-Led STLC — Start Here: Index & Readiness Gap Analysis

You have 15 documents now. This one ties them together, tells you what order to use them in, and — the actual point of this document — tells you honestly what's still missing before Phase 1 can start for real. Documents answer "what and why"; a handful of concrete artifacts and real-world confirmations still need to exist before anyone writes code.

---

## 1. What You Have — Reading Order

| # | Document | Purpose | Audience |
|---|---|---|---|
| 1 | `ai-led-stlc-blueprint.md` | The original six-phase overview and target architecture | You, then leadership |
| 2 | `ai-led-stlc-master-blueprint.md` | Overview + all six phase deep-dives, consolidated | Team reference |
| 3 | `phase-1` through `phase-6-*.md` | Per-phase design detail (workflow, eval requirements, rollout steps) | Whoever's building that phase |
| 4 | `ai-led-stlc-leadership-briefing.docx` | Business case: traditional vs. AI-led, metrics, business value | Leadership |
| 5 | `ai-led-stlc-technical-design.md` | Implementation architecture: schemas, algorithms, connector contracts | Engineers building it |
| 6 | `ai-led-stlc-implementation-plan.md` | Program plan: governance structure, RACI, timeline, risk register | You, as Program Sponsor |
| 7 | `ai-led-stlc-build-inventory.md` | The 42-primitive count, by phase, with consolidation notes | Engineers, planning |
| 8 | `ai-led-stlc-governance-model.md` | Controls per STLC activity, escalation matrix, health metrics | You + AI Governance Team |
| 9 | `ai-led-stlc-copilot-primitive-framework.md` | The agent/skill/instruction/prompt reference architecture + templates | Engineers building primitives |
| 10 | `ai-led-stlc-ecc-inspired-architecture.md` | Memory layer, security scanning, hook equivalents added on top | Engineers, once Phase 1 is stable |

**If you're about to actually start building**: read #9 and #5 together, then open Phase 1's deep-dive (#3) and the technical design's Phase 1 section side by side.

---

## 2. The Gap: What's Documented vs. What Exists

Everything above is design. None of it is a working system yet. Here's what's still missing, in the order you'll hit it.

### 2.1 Real-World Confirmations (Not Documents — Actions)
These block Phase 1 or Phase 3 regardless of how good the design docs are:

- [ ] **Named people**, not roles, for: Automation Engineering Lead, Functional Testing Lead, ADO/DevOps Admin contact, AI Governance Team contact, BA/PO Sponsor. The RACI table in the implementation plan has role labels — it needs actual names before Phase 1 kickoff.
- [ ] **AI Governance intake submitted** for the ADO connector — this has the longest lead time of anything in the program and should already be in motion, not waiting on Phase 1 to finish.
- [ ] **Confirm your org's actual eval harness tooling** is ready to take on 5 new skills (Phase 1) — you have an eval harness pattern from prior work; confirm it's not still scoped only to the Cypress `cypress-code-review` skill.
- [ ] **Definition of Ready** — Phase 5 needs this formally documented. If it's tribal knowledge today, this needs to become a real artifact well before Phase 5, not scrambled together when you get there.
- [ ] **Copilot Studio licensing/environment** confirmed available for the functional testing team — needed by Phase 4, worth confirming early since procurement can be slow at your org's scale.

### 2.2 First Real Build Artifacts (Not Yet Created)
The templates in the primitive framework (#9) are skeletons. Nobody has filled one in yet:

- [ ] **Populated `agent.md` and `SKILL.md` files for Phase 1's five skills** (`allure-parse`, `failure-classify`, `report-summarize`, `ledger-update`, `healer`) plus the `report-cycle-orchestrator` agent — using the templates in the primitive framework document
- [ ] **`evals.json` seed data for each Phase 1 skill** — pulled from real historical Allure reports and known-correct classifications, per the eval requirements in Phase 1's deep-dive. This is usually the slowest part of "starting" — someone needs to hand-label a real dataset before eval suites mean anything.
- [ ] **The `security-scan` skill**, if you're adopting the ECC-inspired addition — recommended to build alongside Phase 1 per that document's priority call, so it exists before any write-capable agent goes live
- [ ] **The shared instructions files** (§2 of the primitive framework) — `negative-case-taxonomy`, `definition-of-ready`, `ai-artifact-style-guide` — need actual content written, not just the frontmatter template

### 2.3 Operational Tracking (Living Artifacts, Not One-Time Docs)
These need to exist as real, updated-weekly things, not sections in a static document:

- [ ] **A metrics tracker** — even a simple spreadsheet — capturing the metrics from the leadership briefing (time-to-test-case, healing acceptance rate, etc.) as real numbers start coming in from Phase 1. The document defines what to measure; nothing is measuring it yet.
- [ ] **The risk register from the implementation plan, as a living tracker** — not a static table, something reviewed and updated at your reporting cadence
- [ ] **A shadow-mode log** for Phase 6 — far off, but worth knowing it needs to be a real running log, not retrofitted when you reach Phase 6

### 2.4 Team Enablement
- [ ] **A scheduled Phase 1 walkthrough session** with the automation team, using an already-built example once one exists (the primitive framework recommends this pattern — it needs an actual calendar invite)
- [ ] **The "Steward" competency-ladder rung** — recommended in the blueprint, not yet formally added to your existing ladder documentation
- [ ] **The STLC-to-phase mapping** (from the leadership briefing's clarification) — worth presenting to your own team internally too, not just leadership, so nobody on the team is confused by the same "why does Phase 1 start with reporting" question you flagged earlier

---

## 3. Immediate Next 5 Actions

If you want to actually start Monday morning, this is the order that unblocks the most:

1. **Name the people** in Section 2.1 — nothing else can be scheduled without owners
2. **Submit the ADO governance intake** — longest lead time in the whole program, start it now regardless of Phase 1 status
3. **Assign one engineer to build `allure-parse` + its eval**, using the templates in the primitive framework — this is the smallest possible first real artifact and validates the whole pattern end to end before committing to all five Phase 1 skills at once
4. **Start hand-labeling a real eval dataset** from actual historical Allure reports — this is slow and easy to underestimate; starting it in parallel with build, not after, saves the most calendar time
5. **Schedule the Phase 1 walkthrough session** for once step 3 produces a working example — put it on the calendar now with a placeholder date, don't wait until it's ready to even schedule it

Everything else in the 15 documents you already have is sequenced correctly and doesn't need more design work — the gap right now is entirely in these real-world, first-artifact, and living-tracker items, not in more planning.
