# Full End-to-End Eval Demo — The Article's Own `csv-analyzer` Example
### Following https://agentskills.io/skill-creation/evaluating-skills exactly, with real, verified artifacts

**This is the same example the article itself uses** — a `csv-analyzer` skill, evaluated on exactly its two scenarios: "top 3 months by revenue, make a bar chart" and "clean up missing emails and report the count." Every deterministic part of this demo was actually built and executed in a sandbox before being written down.

**What's genuinely real here, and it's more than last time:** unlike the earlier Cypress demo (where the with-skill output is the agent's *prose review*, which needs a live LLM call to produce), this skill's actual deliverables — the chart PNG and the cleaned CSV — are the direct, deterministic output of its bundled scripts. **I ran both scripts for real, against real fixture data, and generated a real chart image and a real cleaned CSV** — those are provided as `csvskill-reference--chart.png`, `csvskill-reference--chart.meta.json`, and `csvskill-reference--customers-cleaned.csv`. The grading script was then run for real against those real outputs. **The one thing I still can't do in this sandbox is invoke a live Copilot session** — so the *decision* to call these scripts in response to a natural-language prompt, and the `without_skill` baseline comparison, are the parts you'll run yourself.

**Files provided:** `csvskill--SKILL.md`, `csvskill--top_months_chart.py`, `csvskill--clean_missing_emails.py`, `csvskill--check_assertions.py`, `csvskill--evals.json`, `csvskill-fixture--sales_2025.csv`, `csvskill-fixture--customers.csv`, `csvskill-reference--chart.png`, `csvskill-reference--chart.meta.json`, `csvskill-reference--customers-cleaned.csv`.

---

## Step 1 — Install the skill

```bash
mkdir -p csv-analyzer/scripts
cp csvskill--SKILL.md csv-analyzer/SKILL.md
cp csvskill--top_months_chart.py csv-analyzer/scripts/top_months_chart.py
cp csvskill--clean_missing_emails.py csv-analyzer/scripts/clean_missing_emails.py
chmod +x csv-analyzer/scripts/*.py
```

## Step 2 — Design test cases

```bash
mkdir -p csv-analyzer/evals/files
cp csvskill-fixture--sales_2025.csv csv-analyzer/evals/files/sales_2025.csv
cp csvskill-fixture--customers.csv csv-analyzer/evals/files/customers.csv
cp csvskill--evals.json csv-analyzer/evals/evals.json
```
The two prompts are written the way the article recommends: realistic, specific, mentioning real file paths — one relatively precise ("I have a CSV of monthly sales data in data/sales_2025.csv...") and one more casual ("there's a csv in my downloads called customers.csv, some rows have missing emails..."), matching its own guidance to vary phrasing and formality across cases rather than testing the same register twice.

## Step 3 — Set up the workspace

```bash
mkdir -p csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs
mkdir -p csv-analyzer-workspace/iteration-1/eval-top-months-chart/without_skill/outputs
mkdir -p csv-analyzer-workspace/iteration-1/eval-clean-missing-emails/with_skill/outputs
mkdir -p csv-analyzer-workspace/iteration-1/eval-clean-missing-emails/without_skill/outputs
```

## Step 4 — Generate the with-skill reference outputs (already done for you, for real)

This is what actually happened in the sandbox — running the skill's own bundled scripts directly, which is exactly what a with-skill agent run does once it decides to call them:

```bash
$ python3 csv-analyzer/scripts/top_months_chart.py csv-analyzer/evals/files/sales_2025.csv output/chart.png 3
Top 3 months by revenue: November ($95,000), July ($89,000), March ($72,000)
Chart saved to output/chart.png
Chart metadata saved to output/chart.meta.json
```
The real chart is `csvskill-reference--chart.png` — open it and look: a labeled bar chart, three bars (March, July, November — kept in chronological order on the axis), dollar values above each bar, titled "Top 3 Months by Revenue."

```bash
$ python3 csv-analyzer/scripts/clean_missing_emails.py csv-analyzer/evals/files/customers.csv output/customers_cleaned.csv
Cleaned CSV written to output/customers_cleaned.csv
Missing emails found and flagged: 3
```
The real cleaned CSV is `csvskill-reference--customers-cleaned.csv` — three rows (Bob, David, Frank) now read `MISSING` in the email column instead of being silently dropped, and the other four are untouched.

Copy these into the workspace as your Step 4 with-skill outputs:
```bash
cp csvskill-reference--chart.png csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/chart.png
cp csvskill-reference--chart.meta.json csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/chart.meta.json
cp csvskill-reference--customers-cleaned.csv csv-analyzer-workspace/iteration-1/eval-clean-missing-emails/with_skill/outputs/customers_cleaned.csv
```

## Step 5 — Generate the without-skill baseline (run this yourself)

This is the part that needs a live agent, because "what does the model do with no script to call" is inherently not deterministic:

```bash
copilot -p "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?" \
  -s --no-ask-user \
  # (no --agent / skill path — this is the baseline) \
  > csv-analyzer-workspace/iteration-1/eval-top-months-chart/without_skill/outputs/response.txt
```
Repeat for the second prompt into `eval-clean-missing-emails/without_skill/outputs/`.

**What to expect, and why it's an interesting comparison:** without the skill, a capable agent will likely still produce *a* chart and *a* cleaned CSV — probably by writing inline pandas/matplotlib code on the spot. The real question isn't "can it do this at all," it's whether it does it as **reliably**: does it remember to label both axes every time, does it flag missing values instead of silently dropping rows, does it correctly say "3" rather than miscounting. That reliability gap — not raw capability — is usually where a skill actually earns its keep, and it's exactly what `benchmark.json`'s `stddev` numbers are designed to expose (a wide-swinging without-skill pass rate across repeated runs is the tell).

## Step 6 — Grade the outputs

**The mechanically-checkable assertions — real, tested, verified:**
```bash
cd csv-analyzer
python3 evals/check_assertions.py chart \
  ../csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/chart.png \
  ../csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/chart.meta.json
```
**Actual output from running this in the sandbox:**
```
PASS: output includes a bar chart image file
PASS: the chart shows exactly 3 months
PASS: both axes are labeled
PASS: the chart title or caption mentions revenue

Mechanical check summary: 4 passed, 0 failed, 4 total
```
```bash
python3 evals/check_assertions.py cleanup \
  ../csv-analyzer-workspace/iteration-1/eval-clean-missing-emails/with_skill/outputs/customers_cleaned.csv 3
```
**Actual output:**
```
PASS: the cleaned CSV file exists
PASS: missing emails are flagged, not silently dropped (found 3 flagged rows)
PASS: row count is preserved (no customer records lost)

Mechanical check summary: 3 passed, 0 failed, 3 total
```

**One assertion worth noting as a genuinely good example of the article's point about not everything needing a hard check:** "both axes are labeled" *is* mechanically checkable here — but only because the script was deliberately built to emit a metadata sidecar recording its own label text. Without that sidecar, this exact assertion would have needed either OCR on the PNG or a human/LLM-with-vision look at the image — a legitimate case where a skill's own design choice (emit structured metadata alongside a visual artifact) is what moves an assertion from "needs human review" to "script-checkable." That's a deliberate, reusable pattern worth pointing out to your team: **if you want an assertion to be cheaply automatable, sometimes the fix is changing what the skill outputs, not writing a cleverer grader.**

Run the same grading against your **without-skill** outputs once you've captured them — that comparison is the real signal (Step 8).

## Step 7 — Capture timing and aggregate into benchmark.json

```json
{
  "total_tokens": 2900,
  "duration_ms": 8200
}
```
*(Illustrative shape — your real numbers come from the Copilot CLI session's completion data for each run.)*

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 1.0, "stddev": 0.0 },
      "time_seconds": { "mean": 9.0, "stddev": 1.0 },
      "tokens": { "mean": 2900, "stddev": 200 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.6, "stddev": 0.2 },
      "time_seconds": { "mean": 14.0, "stddev": 4.0 },
      "tokens": { "mean": 4100, "stddev": 800 }
    },
    "delta": { "pass_rate": 0.4, "time_seconds": -5.0, "tokens": -1200 }
  }
}
```
*(Illustrative — but the shape of this particular story is a common and realistic one worth flagging: a bundled-script skill is often not just more reliable but also **faster and cheaper** than an agent improvising the same work inline, because it isn't spending tokens writing and reasoning about analysis code it already has a tested script for. A negative `delta.time_seconds`/`delta.tokens` — the skill costing less, not more — is a stronger result than the earlier Cypress demo's trade-off story, and it's a realistic outcome for this specific kind of skill.)*

## Step 8 — Analyze patterns

Apply the article's own diagnostic questions once you have real numbers:
- Did any assertion pass in **both** with and without skill? (Plausible candidate: "the cleaned CSV file exists" — a capable baseline agent will probably produce *some* output file either way.) That assertion isn't discriminating anything — consider dropping it or tightening it (e.g., "the output CSV preserves the original row count" is a stronger, more discriminating version).
- Did the without-skill `stddev` come out high? That's the reliability gap made visible — the model doing this differently well from run to run, versus the script doing it identically every time.

## Step 9 — Human review

```json
{
  "eval-top-months-chart": "",
  "eval-clean-missing-emails": ""
}
```
Empty means it looked right on review — for this skill, that's a plausible real outcome given how deterministic its two scripts are, unlike the earlier Cypress skill's prose review, which has much more room for stylistic feedback.

## Step 10 — Iterate

If everything passed cleanly on iteration 1 (a realistic outcome for a skill this deterministic), the more interesting next iteration isn't fixing failures — it's **expanding the eval set**: a CSV with an unexpected column order, a revenue column containing currency symbols or commas the script doesn't strip, an empty file. The article's own edge-case guidance applies here directly — these are exactly the boundary conditions worth adding once the happy path is solid.

---

## What Actually Differs From the Cypress Version of This Demo

| | csv-analyzer (this demo) | cypress-code-review (earlier demo) |
|---|---|---|
| With-skill output | Deterministic script output — fully reproducible, verified for real | Agent's written prose — needs a live LLM every time |
| What needs a live agent call | Only the *decision* to invoke the script + the without-skill baseline | The entire with-skill output |
| Likely benchmark story | Skill may be faster/cheaper AND more reliable | Skill costs more time/tokens for higher reliability |
| Hardest assertion to grade | "Axes are labeled" — solved by emitting metadata, not by a cleverer grader | Classification/verdict wording — genuinely needs LLM or human judgment |

Both are legitimate applications of the same methodology — the difference in how much of each demo I could verify directly comes entirely from what kind of skill each one is, which is itself a useful thing for your team to notice: **skills that produce deterministic artifacts are dramatically cheaper to eval than skills that produce prose.**
