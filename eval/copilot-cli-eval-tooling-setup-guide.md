# Technical Setup Guide: Evaluating Your GitHub Copilot Custom Agents & Skills
### From zero eval-tooling experience to a running, CI-gated eval harness

**What this guide builds:** a working eval harness that drives your existing `.github/agents/`, `.github/skills/`, `.github/prompts/`, `.github/instructions/` through **GitHub Copilot CLI in headless mode** — the scriptable twin of the VS Code experience, reading the exact same customization files since Agent Skills is an open standard shared across VS Code, the CLI, and the coding agent. VS Code itself is a GUI and isn't scriptable; the CLI is how you get repeatable, automatable trials against the identical assets your team already built.

**Before you start — one honesty note the source material itself flags:** Copilot CLI went GA in February 2026 and ships updates constantly — flag names, log formats, and defaults can shift. Every command below was current as of this guide's writing; **run `copilot --help` and check the official docs link at the end of each section before you script against any flag**, especially in Parts 3–4.

---

## PART 1 — Prerequisites & Environment Setup

### 1.1 Install the tools

```bash
# Node.js 20+ (check first)
node --version

# GitHub CLI (gh) — you likely have this already for your repo work
gh --version

# GitHub Copilot CLI — the headless-capable agent runner
npm install -g @github/copilot
# or: brew install copilot-cli   /   winget install GitHub.Copilot.CLI

copilot --version
```

```bash
# Authenticate (once per machine)
copilot
# on first launch, /login if not already authenticated via gh

# jq — you will parse JSON/JSONL logs constantly; install it now
jq --version   # brew install jq / apt install jq / choco install jq
```

### 1.2 Verify your existing assets actually load — do this before writing a single eval

This is the step teams with no eval experience skip, and it's the one that saves you the most debugging later: confirm Copilot can see your `.github/agents`, `.github/skills`, `.github/prompts`, `.github/instructions` **before** you build anything that depends on them.

```bash
cd /path/to/your/repo
copilot
```
Inside the interactive session:
```
/agent          # lists your custom agents from .github/agents/ — confirm each one appears
/skills         # lists loaded skills from .github/skills/ — confirm each SKILL.md appears
/prompt         # or just type / to see your .github/prompts/*.prompt.md entries
```
From a regular shell, you can also check the skills registry tooling directly:
```bash
gh skill search "<keyword from one of your skill descriptions>"
gh skill preview <your-skill-name>
```
**If anything is missing here, stop and fix it before Part 2.** An eval harness built against a skill that silently isn't loading will produce confusing, misleading failures that look like agent quality problems but are actually configuration problems.

### 1.3 Trust the folder for non-interactive use

Copilot CLI requires the working directory to be trusted before it will read/modify files. Interactively, you'll be prompted once and can choose "remember this folder." **For CI and unattended eval runs, this prompt cannot be answered**, so trust the eval sandbox directories ahead of time (Part 2.2 shows exactly where) or run inside an environment where the trust store is pre-seeded — check the current CLI docs for the non-interactive trust mechanism, since this is exactly the kind of flag that has moved during 2026's rapid release cadence.

---

## PART 2 — Eval Project Scaffold

### 2.1 Folder layout

Sitting alongside `.github/`, not inside it (the eval project isn't a Copilot customization asset itself):

```
your-repo/
├── .github/
│   ├── agents/
│   ├── skills/
│   ├── prompts/
│   └── instructions/
└── eval/
    ├── tasks/                    # eval spec YAML files, one per suite
    │   ├── routing/
    │   ├── capability/
    │   │   ├── generation/
    │   │   ├── execution/
    │   │   └── healing/
    │   └── e2e/
    ├── hooks/                     # instrumentation scripts (Part 3)
    │   └── pre-tool-use.sh
    ├── runner/                    # the harness itself (Part 4)
    │   ├── run-trial.sh
    │   ├── run-suite.sh
    │   └── consistency.sh
    ├── graders/                   # grading scripts (Part 5)
    │   ├── code/
    │   ├── routing/
    │   └── judge/
    ├── runs/                      # output — gitignored, one dir per run
    └── results/                  # aggregated reports — committed, small
```

```bash
mkdir -p eval/{tasks/{routing,capability/{generation,execution,healing},e2e},hooks,runner,graders/{code,routing,judge},runs,results}
echo "eval/runs/" >> .gitignore
```

### 2.2 Trial isolation via git worktree

Every trial must run in a clean, isolated copy of the repo — this is the single most common source of false "flakiness" in eval results (a dirty shared sandbox, not the agent). Git worktrees give you this cheaply, without a full clone per trial:

```bash
# eval/runner/isolate-trial.sh
#!/usr/bin/env bash
set -euo pipefail
TRIAL_ID="$1"                       # e.g. route-001-t3
WORKTREE_DIR="eval/runs/${TRIAL_ID}/workspace"

git worktree add -f "$WORKTREE_DIR" HEAD
echo "$WORKTREE_DIR"
```
Cleanup after grading:
```bash
git worktree remove --force "eval/runs/${TRIAL_ID}/workspace"
```
Pre-trust each worktree path once (Part 1.3) or configure your trust mechanism to cover `eval/runs/**` as a pattern, so trials never hit an interactive prompt.

---

## PART 3 — Instrumentation: Capturing What the Agent Actually Did

**This is the part that makes routing evals and audit trails possible, and it's the part most teams skip because it feels optional. It isn't** — without it, your only evidence of which skill fired is the agent's own prose summary, which is exactly the unreliable signal your earlier eval design correctly avoided trusting.

### 3.1 Use Copilot CLI hooks to log every tool call

Copilot CLI supports **hooks** — scripts that run at defined points in a session (`sessionStart`, `preToolUse`, and related lifecycle events) and can inspect prompts and tool calls, log for auditing, or block execution. This is your structured, ground-truth data source for "which skill/tool got invoked, in what order, with what arguments" — precisely the input Suite A (routing) needs.

Set up hook configuration (check `copilot --help` / current docs for the exact config file name and schema, as this is actively evolving — the shape below reflects the documented pattern):

```bash
# eval/hooks/pre-tool-use.sh
#!/usr/bin/env bash
# Appends a structured record of every tool call to a per-trial JSONL audit log.
# Requires jq. Receives event context as JSON on stdin per the hooks contract.

LOG_FILE="${COPILOT_EVAL_LOG_FILE:-eval/runs/unknown-trial/tool-calls.jsonl}"
mkdir -p "$(dirname "$LOG_FILE")"

INPUT=$(cat)
echo "$INPUT" | jq -c --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '. + {logged_at: $ts}' >> "$LOG_FILE"

# Exit 0 = allow. Non-zero (with structured response per the hooks contract) = block.
exit 0
```

Point the trial runner at a unique log file per trial by exporting `COPILOT_EVAL_LOG_FILE` before each invocation (Part 4). The result: after every trial, `eval/runs/<trial-id>/tool-calls.jsonl` contains one JSON line per tool/skill invocation — this is what your routing grader (Part 5.2) reads.

### 3.2 Full debug transcripts as a backstop

For deeper debugging (not the primary routing signal, but invaluable when a grader result surprises you), Copilot CLI writes detailed logs — including tool call traces — when run with debug-level logging and a specified log directory:

```bash
copilot -p "$PROMPT" \
  --agent "$AGENT_NAME" \
  --log-level debug \
  --log-dir "eval/runs/${TRIAL_ID}/logs" \
  ...
```
These logs are typically JSONL session files. Skills exist in the community ecosystem specifically for parsing and rendering these into readable Markdown/HTML if you want a human-browsable transcript viewer during debugging — worth adopting rather than building your own parser, since the log schema is still evolving and a community tool is more likely to track changes than a one-off script.

**Don't rely on an undocumented `--debug` flag** — as of this writing it's an open feature request in the CLI's issue tracker, not a shipped flag. Use `--log-level debug --log-dir <path>`, which is documented and confirmed working.

---

## PART 4 — The Headless Trial Runner

### 4.1 The core invocation

```bash
copilot -p "$PROMPT" \
  --agent "$AGENT_NAME" \
  -s \
  --no-ask-user \
  --allow-tool "read" --allow-tool "edit" --allow-tool "search" \
  --deny-tool "bash(git push*)" --deny-tool "bash(rm -rf*)" \
  --log-level debug \
  --log-dir "$LOGDIR" \
  > "$OUTPUT_FILE" 2>&1
```

Flag-by-flag, and why each one matters for eval work specifically:

| Flag | Purpose | Why it matters for evals |
|---|---|---|
| `-p` / `--prompt` | One-shot, non-interactive execution — the CLI runs and exits | This is what makes any of this scriptable at all |
| `--agent` | Pins a specific custom agent so behavior is consistent | Without this, you're testing "whatever agent the router picked," which conflates routing and capability — use this to isolate a skill/agent for Suite B capability tasks; omit it for Suite C end-to-end tasks where routing itself is under test |
| `-s` | Suppresses stats/decoration, emits clean agent-response text | Cleaner text for your outcome grader to parse; use full output (omit `-s`) when you specifically want to inspect session metadata |
| `--no-ask-user` | Prevents the agent from pausing for clarification | **Critical for unattended runs** — without this, an ambiguous task hangs your CI job instead of failing fast, which is a very different (and much more expensive) failure mode to debug |
| `--allow-tool` / `--deny-tool` | Fine-grained permission allow/deny list | Use this instead of blanket approval — explicitly scope each trial to only the tools that task type should need (Section 6.2 below has more on why this matters for safety) |
| `--log-level debug` + `--log-dir` | Full session logging to a directory | Your debugging backstop (Part 3.2) |
| `--model` | Pins a specific model | Pin this for capability/consistency suites so you're measuring the skill, not a model-version drift between runs; vary it deliberately only when you're specifically testing cross-model robustness |

**Explicitly avoid `--allow-all-tools` and `--yolo`-style blanket approval in eval automation** — both are flagged in current guidance as unsafe defaults for automation, and for a healing-skill eval in particular (where you're specifically testing whether the agent stays inside a constrained boundary) blanket approval defeats the entire point of the test.

### 4.2 The trial script, end to end

```bash
#!/usr/bin/env bash
# eval/runner/run-trial.sh
# Usage: run-trial.sh <task_yaml_path> <trial_number>
set -euo pipefail

TASK_FILE="$1"
TRIAL_N="$2"
TASK_ID=$(yq '.task_id' "$TASK_FILE")
AGENT=$(yq '.agent // ""' "$TASK_FILE")
PROMPT=$(yq '.ask' "$TASK_FILE")
ALLOWED_TOOLS=$(yq '.allowed_tools[]' "$TASK_FILE" 2>/dev/null || echo "")

TRIAL_ID="${TASK_ID}-t${TRIAL_N}"
TRIAL_DIR="eval/runs/${TRIAL_ID}"
mkdir -p "$TRIAL_DIR"

# 1. Isolate
WORKTREE=$(bash eval/runner/isolate-trial.sh "$TRIAL_ID")

# 2. Instrument
export COPILOT_EVAL_LOG_FILE="${TRIAL_DIR}/tool-calls.jsonl"

# 3. Run headlessly, from inside the isolated worktree
pushd "$WORKTREE" > /dev/null
START=$(date +%s)

TOOL_FLAGS=()
for t in $ALLOWED_TOOLS; do TOOL_FLAGS+=(--allow-tool "$t"); done

AGENT_FLAG=()
[ -n "$AGENT" ] && AGENT_FLAG=(--agent "$AGENT")

copilot -p "$PROMPT" \
  "${AGENT_FLAG[@]}" \
  "${TOOL_FLAGS[@]}" \
  -s --no-ask-user \
  --log-level debug --log-dir "../logs" \
  > "../output.txt" 2>&1 || true    # capture failures as data, don't kill the runner

END=$(date +%s)
popd > /dev/null

# 4. Capture outcome evidence before teardown
git -C "$WORKTREE" diff > "${TRIAL_DIR}/diff.patch"
echo "{\"trial_id\":\"$TRIAL_ID\",\"task_id\":\"$TASK_ID\",\"duration_s\":$((END-START))}" \
  > "${TRIAL_DIR}/meta.json"

# 5. Grade (Part 5), then teardown
bash eval/runner/grade-trial.sh "$TASK_FILE" "$TRIAL_DIR" "$WORKTREE"
git worktree remove --force "$WORKTREE"
```

*(`yq` is the YAML equivalent of `jq` — install via your package manager. If you'd rather not add another dependency, a small Node.js or Python spec-loader works identically; keep whichever language your existing bash runner already uses for consistency.)*

---

## PART 5 — Graders

### 5.1 Code grader (outcome — the primary pass/fail gate)

```bash
# eval/graders/code/generation-outcome.sh
#!/usr/bin/env bash
# Usage: generation-outcome.sh <worktree_dir> <spec_glob>
set -euo pipefail
WORKTREE="$1"
cd "$WORKTREE"

PASS=true

# Lint
npx eslint $(git diff --name-only HEAD | grep '\.cy\.[jt]s$') || PASS=false

# Execute the generated spec
npx cypress run --spec "$(git diff --name-only HEAD | grep '\.cy\.[jt]s$')" || PASS=false

# Selector policy check — deterministic, no AI needed
if git diff | grep -E "cy\.get\(['\"]\.[\w-]+['\"]\)" > /dev/null; then
  echo "FAIL: bare CSS class selector detected"; PASS=false
fi

echo "$PASS"
```

### 5.2 Routing grader — reads the hook log, not the agent's prose

```bash
# eval/graders/routing/check-routing.sh
#!/usr/bin/env bash
# Usage: check-routing.sh <task_yaml> <tool_calls_jsonl>
set -euo pipefail
TASK_FILE="$1"
LOG_FILE="$2"

EXPECTED=$(yq '.expected_skill[]' "$TASK_FILE" 2>/dev/null)
FORBIDDEN=$(yq '.expected_NOT[]' "$TASK_FILE" 2>/dev/null)

INVOKED=$(jq -r 'select(.tool_name | test("skill|agent")) | .skill_name // .tool_name' "$LOG_FILE" | sort -u)

PASS=true
for e in $EXPECTED; do
  echo "$INVOKED" | grep -qx "$e" || { echo "FAIL: expected skill '$e' not invoked"; PASS=false; }
done
for f in $FORBIDDEN; do
  echo "$INVOKED" | grep -qx "$f" && { echo "FAIL: forbidden skill '$f' was invoked"; PASS=false; }
done

echo "$PASS"
```
*(The exact `jq` filter depends on your hook log's actual field names once you inspect real output from Part 3.1 — treat the filter above as a starting shape, and adjust after your first real trial run so it matches what your hook actually emits.)*

### 5.3 LLM-judge grader — a separate, ungrounded call

**Never let the agent grade its own trial output in the same session** — self-grading is systematically biased toward self-consistent-but-wrong judgments. Run the judge as a fresh, separate invocation with no access to the trial's tools:

```bash
# eval/graders/judge/assertion-strength.sh
#!/usr/bin/env bash
DIFF_CONTENT=$(cat "$1")
RUBRIC=$(cat eval/graders/judge/rubrics/assertion-strength.md)

copilot -p "$(cat <<EOF
You are grading a test file, not writing one. Score 1-5 on each rubric dimension below.
Output ONLY a JSON object: {"coverage":N,"assertion_strength":N,"convention_adherence":N,"rationale":"..."}

RUBRIC:
$RUBRIC

TEST DIFF TO GRADE:
$DIFF_CONTENT
EOF
)" -s --no-ask-user --deny-tool "edit" --deny-tool "bash"
```
Notice `--deny-tool "edit"` — the judge invocation should be read-only by construction; it grades, it never modifies anything. Pin `--model` on the judge call too, ideally to a different or stronger model than whichever one the agent-under-test used, and log every judge verdict for the human-calibration sampling in Part 6.4.

### 5.4 Healing-specific safety grader (your highest-scrutiny check)

```bash
# eval/graders/code/healing-safety.sh
#!/usr/bin/env bash
# The single most important grader in the whole harness.
set -euo pipefail
DIFF_FILE="$1"

# Hard rule: a heal may touch locators/selectors and wait/sync logic ONLY.
# Any line touching assertions is an automatic, non-negotiable FAIL.
if grep -E "^\+.*\b(expect|should|assert)\b" "$DIFF_FILE" > /dev/null; then
  echo "FAIL: healing diff modifies an assertion — hard safety violation"
  exit 1
fi

# For should-NOT-heal tasks: the diff must be EMPTY, plus a bug-report artifact must exist
if [ "$(yq '.expected_skill[0]' "$TASK_FILE")" = "none-of-the-above" ]; then
  [ -s "$DIFF_FILE" ] && { echo "FAIL: healer modified files on a should-not-heal case"; exit 1; }
fi

echo "PASS"
```

---

## PART 6 — Multi-Trial Consistency (pass@k / pass^k)

```bash
# eval/runner/run-suite.sh
#!/usr/bin/env bash
# Usage: run-suite.sh <tasks_dir> <k>
set -euo pipefail
TASKS_DIR="$1"
K="${2:-5}"

for TASK_FILE in "$TASKS_DIR"/*.yaml; do
  for i in $(seq 1 "$K"); do
    bash eval/runner/run-trial.sh "$TASK_FILE" "$i"
  done
done
```

```bash
# eval/runner/consistency.sh — aggregate pass@k / pass^k per task
#!/usr/bin/env bash
set -euo pipefail
TASK_ID="$1"
K="$2"

RESULTS=$(jq -s '[.[] | select(.task_id=="'"$TASK_ID"'") | .pass]' eval/runs/*/result.json)
PASSES=$(echo "$RESULTS" | jq '[.[] | select(.==true)] | length')

python3 - "$PASSES" "$K" <<'PY'
import sys
passes, k = int(sys.argv[1]), int(sys.argv[2])
pass_at_k = 1 if passes >= 1 else 0          # at least one success
pass_hat_k = 1 if passes == k else 0          # ALL k succeeded — the reliability number
print(f"pass@{k}: {pass_at_k}   pass^{k} (all {k} succeeded): {pass_hat_k}   raw: {passes}/{k}")
PY
```
Run k=5 as your standard for routing/generation/execution tasks, **k=10 for every healing task** given its risk profile (per the eval methodology this guide implements). Flag any task where pass^k comes in far below what pass@1 alone would suggest — that gap is your signal to tighten a skill description, harden an instruction, or add a missing example, exactly the calibration loop your team already practices.

---

## PART 7 — CI Integration

```yaml
# .github/workflows/agent-skill-eval.yml
name: Agent & Skill Eval Suite
on:
  pull_request:
    paths:
      - '.github/agents/**'
      - '.github/skills/**'
      - '.github/prompts/**'
      - '.github/instructions/**'

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - name: Install Copilot CLI
        run: npm install -g @github/copilot
      - name: Authenticate
        run: echo "${{ secrets.COPILOT_CLI_TOKEN }}" | copilot auth login --with-token
      - name: Run regression suite (blocking)
        run: bash eval/runner/run-suite.sh eval/tasks/regression 5
      - name: Check regression pass rate
        run: bash eval/runner/check-gate.sh eval/results/regression-summary.json 0.95
      - name: Run capability suite (informational)
        if: always()
        run: bash eval/runner/run-suite.sh eval/tasks/capability 3
        continue-on-error: true
      - name: Publish results
        if: always()
        uses: actions/upload-artifact@v4
        with: { name: eval-results, path: eval/results/ }
```

**The distinction that keeps this useful long-term:** only the **regression suite** (tasks that have already demonstrated stable pass^5 ≥ your bar) blocks the merge. The full **capability suite** runs for information on every PR touching `.github/` but never blocks — this is how you keep extending what these agents can do without every experiment turning into a merge-blocking crisis. Graduate a task from capability to regression manually, once, after you've seen it pass consistently across several real runs.

---

## PART 8 — Your First Two Weeks, Concretely

**Day 1–2:** Part 1 end to end. Get `copilot -p "list the files in this repo" -s --no-ask-user` working and returning clean output. Confirm `/agent` and `/skills` show everything you expect.

**Day 3–4:** Part 2 scaffold + Part 3 hook instrumentation. Run one trial by hand, inspect `tool-calls.jsonl`, confirm you can see which skill fired. **This is the step to not rush** — if your hook log doesn't clearly show skill invocations, every grader you build afterward is built on sand.

**Day 5–7:** Write 10 routing tasks (Section 4 of your eval methodology doc — balanced positive/negative pairs) and the routing grader (5.2). Run them once each (k=1). Fix obvious misroutes.

**Week 2, Day 1–3:** Pick your single riskiest skill (almost certainly healing) and build its safety grader (5.4) plus 10–15 labeled healing tasks, including a few deliberate decoys. This is worth doing before capability evals for the other skills — it's your highest-value gate.

**Week 2, Day 4–5:** Wire the consistency runner (Part 6) at k=5 across everything built so far. Look at the pass^k numbers. Expect some surprises — that's the harness working, not the harness being broken.

**Week 2, end:** Wire Part 7's CI workflow with an empty/tiny regression suite (even 3–5 tasks is a real start) and let capability suites run informationally. Grow both suites from here using the phased methodology in your eval implementation plan.

---

## PART 9 — Gotchas Specific to This Tooling

1. **Flags move.** This CLI ships updates constantly. Pin a CLI version in CI (`npm install -g @github/copilot@<version>`) so your eval results are reproducible against a known agent harness version, not whatever shipped that morning.
2. **The trust prompt will silently hang unattended runs** if a worktree path isn't pre-trusted. Test this specifically in CI before you trust your first real pipeline run.
3. **`--no-ask-user` doesn't fix a bad task spec** — it just fails fast instead of hanging, which is what you want, but a spike in "agent asked for clarification and was denied" failures is a signal your task asks are ambiguous, not that the agent is broken (the same "check the task before blaming the agent" principle from your eval methodology).
4. **Hook script output/contract details are exactly the kind of thing that changes between CLI releases** — the shapes in Part 3.1 are illustrative; verify field names against a real captured event before you build graders on top of them.
5. **Don't grade in the same process that ran the trial.** Keep judge calls (5.3) as separate invocations, ideally in a separate container/step in CI, so a compromised or confused trial can't influence its own grade.

---

*Companion docs: the automation-agent eval implementation plan (methodology this guide implements in tooling), the enterprise audit checklist (Section 5 — your healing safety grader is that checklist's script-review requirement, automated). Primary references to verify against as flags evolve: GitHub's own Copilot CLI docs for programmatic/headless use and the Copilot CLI hooks tutorial.*
