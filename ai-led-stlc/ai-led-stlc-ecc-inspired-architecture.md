# AI-Led STLC — ECC-Inspired Architecture Layers
### Extending the GitHub Copilot Primitive Framework

ECC (Everything Claude Code) goes beyond the four basic primitives — it adds **hooks** (event-driven automation), **memory** (persistent cross-session context), **security scanning** (a scanning layer ahead of any write action), and a **subagent hierarchy** (many narrow specialists under fewer orchestrators), all packaged to be portable across tools. This document maps each of those onto your existing `.github`/Copilot/ADO stack — honestly, including where the mapping is a genuine equivalent and where it's a partial one.

---

## 1. What ECC Adds, and What's Actually Portable to Copilot

| ECC Layer | What It Does in ECC | Feasibility on GitHub Copilot/.github |
|---|---|---|
| Hooks | Shell commands auto-triggered on the agent's own tool-use events (pre-tool, post-tool, session-start, etc.) | **Partial.** Copilot doesn't expose a hook API into its own tool-use loop the way Claude Code does. The closest real equivalents are git hooks (pre-commit/pre-push) and CI/CD pipeline stages — good for "before this gets committed/merged" automation, not for "before Copilot calls this skill" automation. |
| Memory | Persistent files an agent reads/writes across sessions, so context and learned patterns survive | **Fully portable.** This is just structured files plus a read/write convention — your ledgers already do a version of this; formalize it further (§3). |
| Security scanning | A scanning layer that inspects agent output before it's committed/executed | **Fully portable, and worth prioritizing.** Implementable as a mandatory skill in the write path, or a CI gate — doesn't require Copilot-specific tooling. |
| Subagent hierarchy | Dozens of narrow specialist agents under fewer top-level orchestrators | **Fully portable, optional.** Your 7-agent/23-skill catalog is already a lighter version of this. Worth adopting further only if the catalog grows large enough that flat orchestration gets unwieldy — not a must-have at current scale. |
| Cross-tool portability | Same config works across Claude Code, Cursor, Codex, OpenCode | **Not directly applicable** — you're standardizing on one tool (Copilot) by choice. The relevant lesson to borrow is *keeping business logic in tool-agnostic config* (schemas, taxonomies, thresholds) rather than hardcoded into tool-specific prompt syntax, so a future tool change doesn't mean a full rebuild. |

Two of these (memory, security scanning) are worth building deliberately. Hooks are worth a partial equivalent via CI/git. Subagent hierarchy and cross-tool portability are lower priority given your current scale and single-platform commitment — noted for later, not now.

---

## 2. Priority Recommendation

Build in this order, not ECC's order — sequenced by value-to-effort given what you already have:

1. **Security scanning layer** (§4) — highest value, directly strengthens governance controls already defined (Section 2.4, 2.5, 2.7 of the Governance Model), moderate effort
2. **Formalized memory layer** (§3) — extends your existing ledgers into genuine cross-session agent memory, moderate effort, compounds in value over time
3. **CI/git hook equivalents** (§5) — partial equivalent, lower effort, worth doing but don't oversell it as "the same as ECC hooks"
4. **Subagent hierarchy** (§6) — defer until the catalog outgrows flat orchestration; revisit at a defined trigger point, not on a calendar date

---

## 3. Memory Layer — Formalizing What the Ledgers Already Started

Your failure ledger and case-quality ledger are already a memory layer in substance — they're just scoped narrowly (failure history, case quality). ECC's pattern is broader: every agent gets a memory file it reads before acting and updates after, so it doesn't repeat mistakes or re-derive context each run.

### 3.1 Structure
```
.github/
  memory/
    report-cycle-orchestrator.memory.md
    defect-drafting-orchestrator.memory.md
    test-planning-agent.memory.md
    regression-optimization-orchestrator.memory.md
    ...
```

### 3.2 What Goes in an Agent's Memory File
Not raw logs — durable, distilled patterns the agent should carry forward:
- Recurring false-positive patterns the reviewer has corrected (e.g., "duplicate-check over-matches on generic timeout errors — deprioritize timeout-only signature matches")
- Threshold/config adjustments the QA Lead has made and why, so a future config change doesn't silently re-introduce a problem already solved
- Known sparse-data areas (which components/services don't have enough history yet) so `plan-draft`/`risk-score` don't need to rediscover this each cycle

### 3.3 Write Discipline
Same principle as any memory system worth trusting: write distilled facts, not everything. An agent should update its memory file after a human-reviewed cycle, summarizing what was learned — not append raw failure data (that's what the ledgers are for). Cap file size and consolidate periodically, same discipline as any long-running memory store.

### 3.4 Where This Changes the Agent Template
Add to the `agent.md` frontmatter (§3.1 of the primitive framework):
```yaml
memory_file: .github/memory/report-cycle-orchestrator.memory.md
reads_memory_before: true
writes_memory_after_review: true
```

---

## 4. Security Scanning Layer

This is the highest-value addition, because it directly hardens governance controls you've already defined rather than adding something new to explain.

### 4.1 What It Scans For
- Secrets/credentials appearing in generated scripts (Phase 2's `api-script-generate` output) — before merge, not after
- Real/production-like data appearing in generated test data sets (Phase 2's `test-data-generate` output) — the synthetic-data-only rule from Governance Model §2.4, actually enforced rather than just stated
- Sensitive content (customer-identifying detail, business-confidential material) in AI-drafted bug reports or requirement-gap flags before they reach a human reviewer, let alone before an ADO write

### 4.2 Where It Sits
As a mandatory skill every write-capable agent calls immediately before its human-review staging step — not optional, not skippable:
```
[agent orchestration]
  → skill produces draft output
  → security-scan skill inspects draft output
  → if flagged: draft is blocked from staging, routed to a security review queue
  → if clean: draft proceeds to normal human-review gate
```

### 4.3 `security-scan` Skill Design
- Pattern-based detection for credentials/tokens (standard secret-scanning patterns — reuse whatever your org's existing secret-scanning tooling already uses, don't reinvent this)
- Rule-based + LLM hybrid for sensitive-content detection (similar hybrid pattern to `failure-classify` in the technical design) — rules catch known-format PII (emails, SSNs, card numbers), LLM catches contextual sensitivity (business-confidential language) that pattern matching misses
- Output: pass/fail plus flagged spans, using the standard skill I/O envelope

### 4.4 Governance Tie-In
Add to the Governance Model: no draft skips `security-scan`, ever — this is a Sev1-triggering control if bypassed (Escalation Matrix, Section 4 of the Governance Model). Worth stating explicitly in that document as an addendum once this skill is built.

---

## 5. Hook Equivalents (Partial, via CI/Git)

Be precise with your team about what this is and isn't: these are *pipeline-triggered automations*, not hooks into Copilot's own reasoning loop. That distinction matters if anyone benchmarks this against actual ECC and expects tool-use-level interception.

| ECC Hook Concept | Practical Equivalent Here |
|---|---|
| Pre-tool-use validation | Git pre-commit hook: blocks commit if `security-scan` hasn't run clean on changed files |
| Post-tool-use logging | CI pipeline step: logs every skill invocation to the monitoring log (technical design's cross-cutting monitoring notes) |
| Session-start context load | Agent's `reads_memory_before: true` behavior (§3.4) — functionally similar, just not literally a "session start" event since Copilot sessions aren't structured that way |
| Automated re-validation on change | CI pipeline stage: any change to a skill's files triggers its eval suite automatically, blocking merge on failure (already specified in the technical design, §0.5 — this *is* your hook equivalent for eval enforcement) |

---

## 6. Subagent Hierarchy — Deferred, With a Trigger Condition

ECC's 28-135 agents make sense at ECC's scale and generality (a general-purpose coding harness used across many teams and languages). Your 7 orchestrator agents over 23 skills is already right-sized for a single QA function with defined scope.

**Defer decomposing into a deeper subagent hierarchy until one of these is true:**
- A single orchestrator agent's orchestration logic becomes hard to review in one sitting (a concrete complexity signal, not a vague feeling)
- Two STLC activities need to share a skill in ways the current flat structure makes awkward to coordinate
- The catalog roughly doubles (from 42 toward 80+ primitives) as the initiative matures beyond the six phases already scoped

If/when that trigger hits, the natural decomposition point is splitting an orchestrator like `test-planning-agent` into narrower subagents per signal type (a `defect-history-subagent`, a `complexity-subagent`) under a lighter coordinating parent — but building that now, before the complexity justifies it, adds review overhead without a corresponding benefit.

---

## 7. Updated Repository Structure

```
.github/
  agents/          # unchanged from the primitive framework
  skills/
    security-scan/           {SKILL.md, eval/}   # NEW
    allure-parse/ ...          # existing 22
  instructions/     # unchanged
  prompts/          # unchanged
  memory/                                          # NEW
    report-cycle-orchestrator.memory.md
    defect-drafting-orchestrator.memory.md
    test-planning-agent.memory.md
    regression-optimization-orchestrator.memory.md
    api-test-cycle-orchestrator.memory.md
    requirement-analysis-agent.memory.md
    regression-optimization-orchestrator.memory.md
```

Total primitive count updates: **43 skills-equivalent** (adding `security-scan`), plus a new memory layer that isn't a "primitive" in the agent/skill/instruction/prompt sense but is now a first-class part of every write-capable agent's contract.

---

## 8. What This Does and Doesn't Change

- **Governance Model**: add `security-scan` as a mandatory step in every write-capable activity's "required control" (Section 2 of that document) — this is a strengthening, not a rewrite
- **Technical design**: `security-scan`'s skill spec slots in next to the existing skill designs, same eval pattern
- **Rollout sequencing**: build `security-scan` early — ideally alongside Phase 1, since it protects every subsequent phase, not scoped to one phase's activity
- **What doesn't change**: your four-primitive model, your risk-ordered phase sequencing, your composition rule (agents orchestrate, skills don't call skills) — ECC's extra layers slot into that model, they don't replace it
