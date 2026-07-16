# Automated Allure Analysis & Failure Intelligence
### Design + Enterprise Implementation Plan — Copilot Agent, Skills, Instructions & Prompts

**Goal:** Replace the weekly manual ritual (open Allure report → review failures → write manager report) with a one-command flow — the engineer provides an Allure report path or zip, everything else is automatic — while building a **failure ledger** that reveals patterns across runs.

---

## 1. Current vs. Target State

| | Current | Target |
|---|---|---|
| Trigger | Team opens Allure report in share folder weekly | Engineer runs `/analyze-test-run <path-or-zip>` |
| Failure review | Manual, person-dependent, hours | Automated parse + AI classification, minutes |
| Manager report | Hand-written weekly | Generated from template; human approves & sends |
| History/patterns | None — each week starts from zero | Git-versioned failure ledger; recurrence, flakiness, and cluster analytics on demand |
| Consistency | Varies by reviewer | Same taxonomy, same signature logic, every run |

**The one human gate that stays:** the engineer approves the generated manager report before it is sent. Everything upstream of that gate is automatic. (Reports to management should never leave the building without a human's name on them — this is a governance decision, not a technical limitation.)

---

## 2. Architecture Principle: Deterministic Extraction, AI Judgment

The single most important design decision — split the work by what each side is good at:

| Layer | Done by | Why |
|---|---|---|
| Unzip, locate, parse Allure JSON; count pass/fail; extract error messages & traces; normalize error signatures; ledger read/write | **Deterministic Node.js scripts** (bundled in skills) | Fast, token-free, testable, identical every run. Never make the model "read" 400 test-case JSONs. |
| Classify each failure (taxonomy), judge new-vs-recurring significance, detect meaningful patterns, write the narrative for managers | **The model** (agent + skill instructions) | Judgment, language, and pattern interpretation are what the model adds. |

Corollary: the scripts output a **compact digest JSON** (one object per failure with signature, message, history), and the model works only on the digest. This keeps the flow cheap, fast, and reliable even for large suites.

**Allure input handling (script responsibility):** auto-detect what was provided —
- **Raw results** (`allure-results/`, files like `*-result.json`): parse `status`, `statusDetails.message`, `statusDetails.trace`, `labels`, `fullName`, timings.
- **Generated report** (`allure-report/` with `data/`, `widgets/`): parse `widgets/summary.json` (totals), `data/test-cases/*.json` (per-test detail), `history/history-trend.json` (trend).
- **Zip of either:** unzip to a temp workspace first.

---

## 3. Component Design (the four primitives)

### 3.1 SKILL — `.github/skills/allure-analysis/`

The parsing + classification capability. Model-triggered whenever Allure work comes up, and the engine behind the prompt.

```
allure-analysis/
├── SKILL.md
├── scripts/
│   ├── extract-failures.mjs      # path|zip → digest.json (deterministic)
│   └── normalize-signature.mjs   # error message/trace → stable signature
├── references/
│   ├── failure-taxonomy.md       # your classification taxonomy (from the eval harness)
│   └── allure-format-notes.md    # where what lives in raw vs generated reports
└── examples/
    └── digest-example.json
```

```markdown
---
name: allure-analysis
description: "Use when analyzing Allure test reports or results, reviewing test execution failures, summarizing a Cypress run, or preparing an execution report from an Allure path or zip."
---
# Allure Analysis
1. ALWAYS start with scripts/extract-failures.mjs <path-or-zip> — never parse report files directly.
   Output: digest.json → { run: {date, total, passed, failed, broken, skipped, durationMs},
   failures: [{testId, fullName, suite, signature, message, traceHead, retries, durationMs}] }
2. Classify each failure using references/failure-taxonomy.md. Cite the evidence line
   (message/trace fragment) for every classification. If evidence is insufficient, classify
   as "needs-human-triage" — never guess.
3. Signatures from normalize-signature.mjs are the dedupe key against the failure ledger
   (see failure-ledger skill). Same signature = same underlying failure.
```

**Signature normalization (the piece that makes pattern-tracking work):** strip volatile tokens from error messages — UUIDs, numeric IDs, timestamps, URLs' query strings, random test data — then hash `errorType + normalizedMessage + failingSelector/endpoint`. Two runs of the same broken behavior must yield the same signature, or recurrence detection is noise.

### 3.2 SKILL — `.github/skills/failure-ledger/`

The memory of the system. Git-versioned so history is auditable and free.

```
failure-ledger/
├── SKILL.md
├── scripts/
│   ├── ledger-append.mjs    # digest + classifications → append run + upsert failures
│   └── ledger-query.mjs     # --recurring --new --flaky --top N --since <date> --by-suite
└── references/
    └── ledger-schema.md
```

**Ledger schema** (`qa/failure-ledger/ledger.json`, one file, append-mostly):

```json
{
  "runs":     [{ "runId": "2026-07-13", "total": 412, "failed": 17, "passRate": 95.9, "reportRef": "<share-path-or-artifact-id>" }],
  "failures": [{
    "signature": "a1f3…", "firstSeen": "2026-05-04", "lastSeen": "2026-07-13",
    "occurrences": 6, "runsSeen": ["…"], "tests": ["checkout/payment.cy.ts::declined card shows error"],
    "classification": "timing/race", "status": "open", "issueRef": "JIRA-1234", "notes": "…"
  }]
}
```

```markdown
---
name: failure-ledger
description: "Use when recording test failures to the ledger, checking whether a failure is new or recurring, tracking flaky tests, or analyzing failure patterns and trends across test runs."
---
# Failure Ledger
- Append via scripts/ledger-append.mjs ONLY — never hand-edit ledger.json.
- New vs recurring: signature match against existing entries. Recurring = same signature ≥ 2 runs.
- Flaky candidate: same test alternating pass/fail across recent runs (script computes from run membership).
- Pattern queries via scripts/ledger-query.mjs; interpret results, don't recompute them.
- issueRef links a signature to a tracker ticket; when present, report "known issue JIRA-x" instead of re-triaging.
```

### 3.3 AGENT — `.github/agents/execution-report-analyst.md`

```markdown
---
name: execution-report-analyst
description: "Analyzes Allure execution results, maintains the failure ledger, and drafts the weekly manager report. Writes only under qa/reports/ and qa/failure-ledger/."
tools: ["search", "read", "terminal", "edit"]
---
You are a QE execution analyst. Your job: turn an Allure report into (a) a classified failure
triage, (b) an updated failure ledger, (c) a manager-ready report draft.
Rules:
- Extraction and ledger writes go through the bundled scripts — never parse report JSON manually,
  never hand-edit ledger.json.
- You may create/modify files ONLY under qa/reports/ and qa/failure-ledger/. Any other write is out of scope — refuse and explain.
- Facts only in manager reports: counts, deltas, classifications with evidence. No speculation
  about causes you cannot evidence; unknowns are listed as "needs human triage".
- Never mark a failure "flaky, ignore" — flaky candidates get flagged for investigation, not dismissed.
- Present the finished report draft and STOP. The human reviews and sends it.
```

*Why this tool posture:* it needs `terminal` (run scripts) and `edit` (write ledger + report). Since tool allow-lists aren't path-granular, the write boundary is enforced by instruction + audit; the compensating control is that `qa/reports/` and `qa/failure-ledger/` are the only paths it touches, which is trivially verifiable in the PR diff.

### 3.4 PROMPT — `.github/prompts/analyze-test-run.prompt.md` (the one command)

```markdown
---
description: "Full Allure run analysis: parse → classify → update ledger → draft manager report"
agent: execution-report-analyst
---
Analyze the test run at: ${input:reportPath}

1. EXTRACT — run allure-analysis/scripts/extract-failures.mjs "${input:reportPath}" → digest.json.
2. CLASSIFY — classify every failure per the taxonomy, evidence line included.
3. RECONCILE — run ledger-query for each signature: mark new / recurring (nth occurrence) /
   known-issue (has issueRef) / flaky-candidate.
4. RECORD — append the run and upsert failures via ledger-append.mjs.
5. REPORT — write qa/reports/YYYY-MM-DD-execution-report.md using the template in
   qa/reports/TEMPLATE.md, plus qa/reports/YYYY-MM-DD-triage-detail.md for the team.
6. PRESENT — show me: headline numbers, top 3 findings, anything classified needs-human-triage.
   STOP for my review. Do not modify anything outside qa/reports/ and qa/failure-ledger/.
```

### 3.5 PROMPT — `.github/prompts/failure-pattern-report.prompt.md`

```markdown
---
description: "Cross-run failure pattern analysis from the ledger (monthly/quarterly)"
agent: execution-report-analyst
---
Period: ${input:since}
1. Run ledger-query.mjs --since ${input:since} with --recurring, --flaky, --top 10, --by-suite.
2. Interpret: chronic offenders (recurring & unresolved), suites with worst failure density,
   flakiness trend, classification mix shift (are timing failures growing?), mean-time-to-close
   for signatures with issueRefs.
3. Produce qa/reports/pattern-analysis-${input:since}.md: findings ranked by cost to the team,
   each with evidence (signatures, counts, dates) and ONE recommended action.
```

### 3.6 INSTRUCTIONS — `.github/instructions/qa-reports.instructions.md`

```markdown
---
applyTo: "qa/reports/**"
---
- Manager reports follow qa/reports/TEMPLATE.md exactly — sections, order, no additions.
- Numbers always come from digest.json / ledger-query output — never estimated or recalled.
- Every failure mention carries its classification and new/recurring/known status.
- Tone: factual, neutral, no blame. Product defects reference the bug ticket, not the developer.
- Reports never include credentials, internal hostnames, or raw stack traces (trace heads only, in the triage detail doc — not the manager report).
```

**Manager report template** (`qa/reports/TEMPLATE.md`) — sections: **Headline** (pass rate, delta vs. previous run, run size/duration) · **What broke** (failures grouped by classification, new vs. recurring counts) · **Known issues status** (open ticket signatures seen again) · **New risks** (new signatures, flaky candidates) · **Actions** (owner + item) · **Appendix link** (triage detail doc).

---

## 4. End-to-End Flow (what "automagic" looks like)

```
Engineer: /analyze-test-run \\share\qa\allure\2026-07-13.zip
   │
   ├─ script: unzip → detect format → digest.json        (seconds, no tokens)
   ├─ model:  classify 17 failures w/ evidence            (taxonomy from skill)
   ├─ script: ledger query per signature                  (new/recurring/known/flaky)
   ├─ script: ledger append (run + upserts)               (git-tracked change)
   ├─ model:  manager report + triage detail from template
   └─ STOP:   headline + top findings presented → human approves → sends report
                                    │
             (git PR containing: ledger.json delta + 2 report files = full audit trail)
```

Weekly time cost after implementation: **minutes of review** instead of hours of analysis — and the ledger gets smarter every run.

---

## 5. Step-by-Step Enterprise Implementation Plan

Sequenced so every phase ships something usable, deterministic parts are proven before AI parts, and the solution passes your own audit checklist at go-live.

**Phase 0 — Decisions & prerequisites (½ day, you + DevOps)**
1. Confirm input contract with DevOps: exact share-folder layout, and whether the pipeline can also **zip + drop the raw `allure-results`** alongside the generated report (raw results parse more reliably; the design handles both).
2. Decide ledger home: `qa/failure-ledger/` in the automation repo (recommended — versioned, reviewable) vs. a separate repo.
3. Decide report distribution: engineer sends manually after approval (start here) vs. later automation.
4. Confirm the taxonomy: reuse the failure taxonomy from your eval harness as `failure-taxonomy.md` v1 — do not invent a second taxonomy.

**Phase 1 — Deterministic core, no AI yet (2–3 days, one engineer)**
5. Build `extract-failures.mjs`: zip/dir detection, raw-vs-generated parsing, digest.json output. Node 20, zero exotic dependencies.
6. Build `normalize-signature.mjs` and **calibrate it**: run against the last 4–6 historical reports; verify the same real-world failure yields the same signature across weeks, and different failures don't collide. This calibration is the make-or-break step for pattern tracking — budget real time for it.
7. Build `ledger-append.mjs` / `ledger-query.mjs` + schema; backfill the ledger from those historical reports so pattern analytics have data from day one.
8. Unit-test the scripts like production code (they are).

**Phase 2 — Skills + instructions (1 day)**
9. Package Phase-1 scripts into the two skills; write trigger-style descriptions; add `qa-reports.instructions.md` and `TEMPLATE.md`.
10. Verify skill triggering (positive + negative test per your audit checklist §5.1).

**Phase 3 — Agent + prompt, shadow mode (1 day build + 2 weeks parallel run)**
11. Create `execution-report-analyst` and `/analyze-test-run`; run end-to-end on last week's report.
12. **Shadow mode for 2 cycles:** team does the manual review as usual AND runs the automated flow; diff the outputs. Fix classification gaps by improving the taxonomy references, not by hand-editing outputs. *Exit: automated report is accepted with ≤ minor edits two weeks running.*

**Phase 4 — Cutover + pattern analytics (week 3)**
13. Manual review retires; the human role becomes "approve & send".
14. Add `/failure-pattern-report`; run the first monthly pattern analysis off the backfilled ledger — this is the deliverable that shows managers value beyond time-saving.

**Phase 5 — Enterprise hardening (run your audit checklist against it)**
15. Security review of all bundled scripts (checklist §5.3), CODEOWNERS on the skills/agent/prompt files and on `qa/failure-ledger/`.
16. Do **not** pre-approve shell/bash for the skills initially — the engineer confirms script executions per run (seconds of friction). Revisit only after several clean weeks, with documented sign-off, per your governance rules.
17. Negative-test the agent's write boundary (ask it to edit a spec file → must refuse). Record in the audit.
18. Add the flow to team onboarding; measure and record time-per-week before/after — that's your ROI evidence.

**Phase 6 (optional, future) — Full pipeline automation**
19. Once trust is established: a scheduled Copilot CLI job in the pipeline runs the same skills after every nightly execution, opening a PR with the ledger delta + draft report; the weekly human action reduces to reviewing a PR. Same skills, zero redesign — this is why the logic lives in skills (portable across VS Code, CLI, and the coding agent) rather than in the prompt body.
20. Optional integrations, each a small extension: Jira/ADO MCP connector so "file a bug for this signature" and issueRef backlinks are automatic; a dashboard generated from ledger.json.

---

## 6. Design Decisions & Trade-offs (so reviewers don't re-litigate them)

1. **Ledger in git, JSON not a database.** At weekly-run scale, a versioned JSON file gives audit trail, diff-based review, and zero infrastructure. Migrate to a DB only if run frequency × suite size makes the file unwieldy — the query script isolates that change.
2. **Signature-based dedupe over test-name dedupe.** The same test can fail for different reasons (two issues), and the same root cause can hit many tests (one issue). Signatures track *causes*; test names track *symptoms*.
3. **Human approval gate kept on the manager report.** Cheap (minutes), and it keeps accountability with a person — consistent with your governance posture. The 80% time saving comes from analysis automation, not from removing the send step.
4. **Scripts confirm-per-run instead of pre-approved shell.** Deliberate friction per your own audit red-flag #2; relax later with sign-off if desired.
5. **Model never sees raw report files.** Digest-only keeps token cost flat regardless of suite size and eliminates "model misread the JSON" as a failure class.

---

*Companion docs: framework guide · file-type comparisons · curated QE catalog · enterprise audit checklist. This solution should itself pass the audit checklist before go-live — Sections 1, 4, 5 especially.*
