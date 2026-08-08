# Phase 1 Deep Dive: Execution & Reporting AI
### AI-Led STLC — Blueprint Phase 1 of 6

Phase 1 has two workstreams that can run in parallel: **(A) Allure Report Automation + Failure Ledger** and **(B) Test Healing Agent**. Both live entirely inside your existing dev-side environment (VS Code + GitHub Copilot + `.github` primitives) and touch no ADO work items — which is exactly why this phase carries the lowest governance risk and should go first.

---

## A. Allure Report Automation + Failure Ledger

### A.1 Goal
Replace the weekly manual routine (open Allure report → scan failures → write manager summary) with: team drops a report path/zip → agent produces a structured summary + updates a running failure ledger automatically.

### A.2 Workflow (end to end)
1. DevOps pipeline writes Allure results to the shared folder (existing, unchanged)
2. Team member (or a scheduled trigger) provides the report path/zip to the agent
3. **Parse skill** extracts: test name, status (pass/fail/broken/skipped), duration, error message/stack trace, suite/feature tags, retry history
4. **Classification skill** buckets each failure into one of: product bug / flaky test / environment issue / test data issue / stale locator — using error signature matching against the failure ledger's history
5. **Summarization skill** drafts the manager-facing report: pass rate trend, new failures vs. recurring, top failure clusters, flaky test list
6. **Ledger update skill** appends this run's classified failures to the persistent failure ledger (see A.4), so classification improves over time via matched signatures
7. Human review: QA lead/manager reviews the draft before it's sent — this is the approval gate

### A.3 GitHub Copilot Primitives Needed
| Primitive | Purpose |
|---|---|
| **Instructions** (`.github/instructions/`) | House style for the manager report; classification taxonomy definitions (what counts as "flaky" vs "environment") |
| **Skill: allure-parse** | Extract structured data from raw Allure JSON/HTML output |
| **Skill: failure-classify** | Match error signatures against ledger, assign category + confidence |
| **Skill: report-summarize** | Generate the manager-facing narrative report |
| **Prompt file** | The one-shot "here's the report path, run the pipeline" entry point a team member actually types |
| **Agent** | Orchestrates parse → classify → summarize → ledger-update as one workflow, so the human only invokes once |

This maps cleanly onto the four-primitive framework you've already trained the team on — no new concepts, just a new applied workflow.

### A.4 Failure Ledger — Design Points
This is the highest-leverage artifact in Phase 1 because it's what makes Phases 2–6 smarter later (regression optimization in Phase 6 depends on this data existing).

- **Storage**: structured, queryable format (JSON lines or a lightweight DB) — not just a text log — so classification skill can match against it and future agents can query it
- **Schema per entry**: test ID, error signature (normalized, not raw stack trace), first-seen date, last-seen date, occurrence count, category, resolution status, resolved-by/linked-fix reference
- **Signature normalization**: strip timestamps, line numbers, dynamic IDs from error messages before hashing/matching, or every failure looks "new"
- **Retention/decay**: define when an entry is considered stale/resolved (e.g., not seen in N runs) vs. actively recurring
- **Ownership**: who reviews/corrects misclassifications — feeds back into classification skill accuracy over time

### A.5 Eval Requirements (per your existing policy)
- **allure-parse**: eval against a set of real historical Allure reports with known-correct extracted fields
- **failure-classify**: eval against a labeled set of past failures (ground truth = category a human already assigned) — track precision/recall per category, not just overall accuracy
- **report-summarize**: eval against human-quality bar — does it match the level of detail/tone the team already sends? (subjective, use rubric-based grading like your csv-analyzer eval pattern)
- Re-run all three evals on every skill update, per your standing policy

### A.6 Governance/Risk Notes
- No ADO writes, no code changes committed — lowest-risk workstream, good pilot
- Data boundary: confirm Allure reports don't contain sensitive customer data before they pass through any cloud-hosted model context
- Misclassification risk is reputational (wrong report to manager), not systemic — still needs the human review gate, but stakes are lower than Phase 3+

### A.7 Rollout Steps
1. Build allure-parse skill + eval, validate on 5-10 historical reports
2. Build failure-classify skill + eval, seed the ledger with historical data if available (backfill)
3. Build report-summarize skill + eval, compare output against last 2-3 real manager reports the team sent manually
4. Wire into agent + prompt file, pilot with one person for 2-3 weekly cycles
5. Team-wide rollout once pilot output matches manual quality bar

---

## B. Test Healing Agent

### B.1 Goal
When a Cypress/Playwright script fails due to a stale locator (not a real product bug), agent proposes the fix automatically instead of an engineer manually re-inspecting the DOM.

### B.2 Workflow
1. Test execution fails; failure-classify skill (from workstream A) tags it as "stale locator" category
2. **Healer skill** triggered only for that category — re-explores the live application (or a captured DOM snapshot) to find the element's current selector
3. Healer proposes a diff: old locator → new locator, with confidence score
4. **Human review gate**: engineer approves/rejects the diff — this should NOT auto-commit, even at high confidence, at least initially
5. Approved fixes commit to the script; rejected ones fall back to manual investigation and get logged as a "healing miss" in the failure ledger

### B.3 Design Points
- **Trigger discipline**: healer should only fire on locator-classified failures, not all failures — otherwise it risks masking real product bugs as "just needs healing"
- **Confidence thresholding**: define a minimum confidence score below which the agent doesn't even propose a fix, just flags for manual review
- **Explainability**: the diff proposal should include *why* it picked the new locator (e.g., matched by text content, matched by nearby stable attribute) so the reviewing engineer can sanity-check quickly rather than blindly trust
- **Scope boundary**: healing locators is in scope; healing test *logic* (assertions, flow) is explicitly out of scope for this phase — keep the blast radius small

### B.4 Eval Requirements
- Eval set: deliberately break a set of known-good scripts (change locators) and verify the healer proposes the correct fix
- Track: fix-acceptance rate (how often engineers approve the proposed diff unchanged), false-fix rate (approved but later found wrong), miss rate (flagged as unfixable but a human could fix it)
- Re-eval on every skill update

### B.5 Governance/Risk Notes
- Commits to test code — even with human approval, this touches the codebase, so should go through the same PR review process as any human-written change, not a special AI bypass lane
- Track healing acceptance rate as a leadership metric (Section 6 of the main blueprint) — this is your strongest quick ROI story

### B.6 Rollout Steps
1. Build healer skill + eval on a controlled "break and heal" test set
2. Pilot on one test suite with one engineer reviewing every proposed fix
3. Track acceptance/false-fix/miss rates for 2-3 weeks before wider rollout
4. Expand to full automation suite once acceptance rate and false-fix rate hit an agreed bar (define this threshold with your team before starting — don't set it after seeing results)

---

## Phase 1 — Definition of Done
- Both skills (report automation, healer) have passing eval suites per standing policy
- Failure ledger is live and being written to on every run
- At least one full weekly cycle run end-to-end with human approval gate exercised
- Metrics baseline captured (Section 6 of main blueprint) so Phase 2+ has a before/after comparison

## Transition Criteria to Phase 2
Move to Phase 2 (API test script generation expansion) once:
- Failure ledger has enough data to be a meaningful classification signal (not day-one accuracy)
- Healer acceptance rate is stable and trusted by the team without heavy oversight
- Report automation has fully replaced the manual weekly routine, not running in parallel with it
