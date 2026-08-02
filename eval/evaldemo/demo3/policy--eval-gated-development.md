# Policy: Eval-Gated Skill & Agent Development
### Effective for all `.github/agents/`, `.github/skills/`, `.github/prompts/`, `.github/instructions/` work

## The Policy, Stated Plainly

1. **No new skill, agent, or prompt merges without an accompanying eval task set.** At minimum: any bundled scripts have unit tests (per eval-plans-by-primitive.md §2.3); the asset has at least the "minimum viable set" cases relevant to it from eval-must-test-checklist.md.
2. **The eval suite must pass before merge.** Not "mostly pass" — the tasks designated as regression-suite members (Section 3 below) must be green.
3. **Any update to an existing skill, agent, prompt, or instruction re-runs that asset's full eval suite, and it must pass again before the update merges.** An update that breaks previously-passing behavior is caught here, not in production.
4. **A failing eval is treated the same as a failing test** — it blocks the merge. It is not a warning, not a suggestion, not something to fix "in a follow-up."

## Why This Is a Policy and Not a Suggestion

The `cypress-code-review` skill's own build is the proof: its bundled script had a real, silent bug — a clean file could report "issues found" and a dirty file could report "clean," purely by accident of which shell command ran last. **A human skim of that script would very plausibly have missed it.** The unit test caught it in one run. That's the entire argument for this policy in one sentence: eval isn't extra rigor layered on top of good work, it's how you find out whether the work is actually good.

## What "An Eval Suite" Minimally Requires, Per Asset Type

| Asset type | Minimum required before merge |
|---|---|
| Skill with bundled scripts | Unit tests for every script (deterministic, no LLM) — non-negotiable, cheapest to build, do first |
| Skill (any) | At least 3 trigger cases: one clear positive, one clear negative, one confusable-adjacent-skill case |
| Agent | At least one tool-boundary negative test if the agent has any restricted permissions |
| Prompt | At least one missing-input case (must ask, not invent) |
| Instruction (new hard rule) | At least one "resist the temptation" compliance case (eval-must-test-checklist.md F1) |

This table is a floor, not a ceiling — build more where the risk warrants it (per eval-must-test-checklist.md's per-category guidance), especially for anything healing-adjacent or anything with write/execute permissions.

## CI Enforcement

```yaml
# .github/workflows/agent-skill-eval.yml — policy-enforcing excerpt
on:
  pull_request:
    paths:
      - '.github/agents/**'
      - '.github/skills/**'
      - '.github/prompts/**'
      - '.github/instructions/**'

jobs:
  policy-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Require an eval task file for every changed asset
        run: |
          for f in $(git diff --name-only origin/main...HEAD -- '.github/agents/**' '.github/skills/**' '.github/prompts/**'); do
            ASSET_NAME=$(basename "$(dirname "$f")")
            EVAL_PATH="eval/tasks/*/${ASSET_NAME}*"
            ls $EVAL_PATH > /dev/null 2>&1 || { echo "POLICY VIOLATION: no eval task file found for ${ASSET_NAME}"; exit 1; }
          done
      - name: Run eval suites for all changed assets
        run: bash eval/runner/run-changed-assets.sh
      - name: Fail merge if regression suite did not pass
        run: bash eval/runner/check-gate.sh eval/results/summary.json 1.0
```

The first step is a **structural gate**: it fails the build if a changed skill/agent/prompt has no matching eval file at all, regardless of what that eval would say — this is what makes "no eval, no merge" actually enforced rather than aspirational. The second and third steps are the familiar regression-gate mechanism from the tooling guide, now applied as policy rather than optional infrastructure.

## Ownership

- **CODEOWNERS on `.github/**` and `eval/**` should be the same reviewers**, so a skill PR and its eval PR are reviewed by someone positioned to judge both together — an eval reviewed by someone who's never seen the skill it's testing is a weaker check.
- **The asset's author writes its eval, not a separate "eval team."** This keeps the eval methodology as a universal engineering skill rather than a specialist silo, and it's exactly the L2 competency-ladder work your training program is already built to recognize.

## Exceptions

The only sanctioned exception is a documented, time-bound waiver signed off by the estate owner (per your audit checklist's ownership model) — for example, a genuine emergency hotfix to an instruction file. Every waiver is logged, and the missing eval work is scheduled, not forgotten. There is no standing exception category; "we'll add the eval later" is the failure mode this policy exists to prevent, and normalizing it once normalizes it permanently.

---

*This policy is enforced by the CI mechanism in copilot-cli-eval-tooling-setup-guide.md Part 7, informed by the case-type guidance in eval-must-test-checklist.md, and demonstrated end to end in eval-demo--cypress-code-review.md. Add this policy's location to document-index.md.*
