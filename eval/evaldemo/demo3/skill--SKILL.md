---
name: cypress-code-review
description: "Use when reviewing, critiquing, or auditing Cypress or JavaScript/TypeScript test code — including PR review, self-review before opening a PR, or a direct request to check a spec file for quality, convention adherence, or flakiness risk."
---

# Cypress/JS Code Review Skill

You are reviewing test code, not writing it. Your job is to find and report problems clearly enough that a human can fix them quickly — never to silently fix them yourself unless explicitly asked to.

## Procedure

1. **Run the deterministic pre-scan first, always.** Execute `scripts/pre-scan.sh <target-file>` before adding any judgment-based findings. This catches every mechanical rule violation for free and with zero risk of missing or hallucinating one — never try to mechanically re-derive what the script already checks.
2. **Layer judgment-based review on top of the pre-scan results**, using `references/review-rubric.md` for the criteria the script can't check mechanically (test independence, assertion strength, naming quality, structural conventions, page-object usage).
3. **Classify every finding as `blocking` or `suggestion`** — never leave a finding unclassified. Blocking findings are policy violations from the team's `.github/instructions/`; suggestions are quality improvements that don't violate a stated rule.
4. **Cite evidence for every finding** — file, line number, and the specific rule or rubric criterion violated. A finding without a citation is not a finding; if you can't point to the line, don't report it.
5. **Never rewrite the code yourself during a review.** Report findings only. If asked to also fix the issues, that's a different task — say so explicitly and ask before switching modes.
6. **End every review with a summary**: total blocking count, total suggestion count, and a one-line overall verdict (`ready to merge` / `blocking issues present`).

## Output Format

```
## Review: <file path>

### Blocking
- [rule-id] Line N: <what's wrong> — <the fix, one line>

### Suggestions
- [rule-id] Line N: <what could be better> — <the improvement, one line>

### Summary
X blocking, Y suggestions — <verdict>
```

## What This Skill Does NOT Do

- Does not modify files. This is a read-only review capability regardless of which agent invokes it.
- Does not review application code, only test code (`*.cy.js`, `*.cy.ts`, and test helpers/page objects).
- Does not replace `/review-test-pr` — that prompt orchestrates a full PR review workflow and can call this skill as part of it; this skill is the reusable review capability itself, callable standalone or through any agent.

## Bundled Resources

- `scripts/pre-scan.sh` — deterministic mechanical checks (selector policy, hard waits, focused tests left in, debug statements, blanket exception suppression). Outputs JSON Lines; exits 0 if no blocking findings, 1 if any blocking findings exist.
- `references/review-rubric.md` — the judgment-based criteria layered on top of the pre-scan.
