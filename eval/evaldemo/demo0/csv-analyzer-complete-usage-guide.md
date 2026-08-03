# CSV-Analyzer Skill Eval — Complete Usage Guide
### Every file, every step, every concept from the source — one document, follow it start to finish

**Source:** https://agentskills.io/skill-creation/evaluating-skills. This guide preserves that article's full structure — designing test cases, running with/without comparisons, writing assertions after seeing real output, grading with evidence, aggregating results, analyzing patterns, human review, and iterating — and walks it end to end using the real `csv-analyzer` skill files already built. **You shouldn't need to open the source article or any other document to follow this one.**

---

## The Concepts, Before You Touch a File

Five ideas from the source carry the whole methodology. Understand these first; the steps below are just these five ideas made concrete.

1. **A test case is three things: a realistic prompt, a plain-language description of what success looks like, and (optionally) input files.** Not a pass/fail spec yet — just "here's what someone would type, here's roughly what a good answer looks like."
2. **The core technique is running every test case twice — once with the skill, once without it.** Without this comparison, you only learn that the skill *produces something*; you never learn whether it's actually better than the model would do unaided. This is the single most important idea in the whole methodology.
3. **Don't write pass/fail assertions until after you've seen a first round of real output.** You usually don't know exactly what "good" looks like — precisely which details matter — until you've watched the skill actually run once.
4. **Grading requires concrete evidence, not benefit of the doubt.** A finding that quotes or points at the actual output is trustworthy; a bare opinion isn't. This applies whether the grader is a script or a model.
5. **The iteration loop is: run, grade, analyze patterns, get human feedback, then feed all of that plus the current skill definition back in to propose improvements** — repeated until results stop improving.

---

## Your Complete File Manifest

| File | What it is |
|---|---|
| `csvskill--SKILL.md` | The skill definition — install this into your agent's skills folder |
| `csvskill--top_months_chart.py` | Bundled script: finds top-N months by revenue, draws a labeled bar chart |
| `csvskill--clean_missing_emails.py` | Bundled script: flags missing emails in a CSV, reports the count |
| `csvskill--evals.json` | The two test cases — prompt, expected output, input files, assertions |
| `csvskill--check_assertions.py` | The grading script for the mechanically-checkable assertions |
| `csvskill-fixture--sales_2025.csv` | Input file for test case 1 (12 months of revenue data) |
| `csvskill-fixture--customers.csv` | Input file for test case 2 (7 customers, 3 missing emails) |
| `csvskill-reference--chart.png` | A real, already-generated with-skill output for test case 1 |
| `csvskill-reference--chart.meta.json` | Metadata sidecar (axis labels, title, month count) for grading the chart |
| `csvskill-reference--customers-cleaned.csv` | A real, already-generated with-skill output for test case 2 |
| `report--generate_report.py` | Turns graded results into a readable HTML report (no install required) |
| `report--sample-data.json` | The real graded results from this skill, ready to feed the report generator |

---

## Step 1 — Install the skill
*(Source section: none — this is prerequisite setup, not covered by the article itself.)*

```bash
mkdir -p csv-analyzer/scripts
cp csvskill--SKILL.md csv-analyzer/SKILL.md
cp csvskill--top_months_chart.py csv-analyzer/scripts/top_months_chart.py
cp csvskill--clean_missing_emails.py csv-analyzer/scripts/clean_missing_emails.py
chmod +x csv-analyzer/scripts/*.py
```

## Step 2 — Design test cases
*(Source section: "Designing test cases")*

Concept recap: a test case is a realistic prompt, a plain description of success, and optional input files — nothing more yet. Here they're already written for you, matching the source's own tips: one precise prompt, one casual prompt, both mentioning real file paths rather than vague requests like "process this data."

```bash
mkdir -p csv-analyzer/evals/files
cp csvskill-fixture--sales_2025.csv csv-analyzer/evals/files/sales_2025.csv
cp csvskill-fixture--customers.csv csv-analyzer/evals/files/customers.csv
cp csvskill--evals.json csv-analyzer/evals/evals.json
```

Open `csv-analyzer/evals/evals.json` and read it now. Two entries:
- **id 1**: *"I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?"* — precise phrasing, a specific file path, a specific number (3).
- **id 2**: *"there's a csv in my downloads called customers.csv, some rows have missing emails — can you clean it up and tell me how many were missing?"* — casual phrasing, lowercase, no punctuation discipline — deliberately different register, per the source's advice to vary formality across cases.

## Step 3 — Set up the workspace
*(Source section: "Running evals" → "Workspace structure")*

Concept recap: each pass through the eval loop gets its own `iteration-N/` directory; each test case gets a folder split into `with_skill/` and `without_skill/` sides. This structure is what makes Step 4 vs. Step 5's comparison possible later — skipping the `without_skill` half is the most common shortcut people take, and the one that costs the most: without it you can't tell whether the skill helped.

```bash
mkdir -p csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs
mkdir -p csv-analyzer-workspace/iteration-1/eval-top-months-chart/without_skill/outputs
mkdir -p csv-analyzer-workspace/iteration-1/eval-clean-missing-emails/with_skill/outputs
mkdir -p csv-analyzer-workspace/iteration-1/eval-clean-missing-emails/without_skill/outputs
```

## Step 4 — Generate the with-skill outputs
*(Source section: "Running evals" → "Spawning runs")*

Concept recap: each run should start from a clean context — no leftover state from anywhere else — so the agent follows only what `SKILL.md` says, and you provide the skill path, the prompt, any input files, and an output directory.

**This step is already done for you, for real** — the skill's bundled scripts were actually executed against the real fixtures:

```bash
$ python3 csv-analyzer/scripts/top_months_chart.py csv-analyzer/evals/files/sales_2025.csv output/chart.png 3
Top 3 months by revenue: November ($95,000), July ($89,000), March ($72,000)
Chart saved to output/chart.png
Chart metadata saved to output/chart.meta.json
```
```bash
$ python3 csv-analyzer/scripts/clean_missing_emails.py csv-analyzer/evals/files/customers.csv output/customers_cleaned.csv
Cleaned CSV written to output/customers_cleaned.csv
Missing emails found and flagged: 3
```

Copy the already-generated real outputs into place:
```bash
cp csvskill-reference--chart.png csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/chart.png
cp csvskill-reference--chart.meta.json csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/chart.meta.json
cp csvskill-reference--customers-cleaned.csv csv-analyzer-workspace/iteration-1/eval-clean-missing-emails/with_skill/outputs/customers_cleaned.csv
```
Open `csvskill-reference--chart.png` now and actually look at it: three labeled bars (March, July, November, left-to-right in chronological order), dollar values above each bar, y-axis labeled "Revenue ($)," title "Top 3 Months by Revenue."

## Step 5 — Generate the without-skill baseline
*(Source section: "Running evals" → "Spawning runs," the baseline half)*

Concept recap: same prompt, same input files, but no skill path — this is what tells you whether the skill is actually adding anything. **This is the one step you run yourself** — it needs a live agent session:

```bash
copilot -p "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?" \
  -s --no-ask-user \
  > csv-analyzer-workspace/iteration-1/eval-top-months-chart/without_skill/outputs/response.txt
```
Repeat with the second prompt, saving into `eval-clean-missing-emails/without_skill/outputs/`.

**What to expect:** a capable agent will likely still produce *a* chart and *a* cleaned file even without the skill — probably by writing pandas/matplotlib code inline. The interesting question isn't "can it do this at all" — it's whether it does it as *reliably*: labeled axes every time, missing values flagged rather than dropped every time, the count correct every time.

## Step 6 — Capture timing data
*(Source section: "Capturing timing data")*

Concept recap: timing tells you what the skill costs (tokens, time) relative to the baseline — a skill that's better but three times more expensive is a different trade-off than one that's better *and* cheaper. Record this immediately after each run; it isn't saved anywhere else automatically.

```json
{
  "total_tokens": 2900,
  "duration_ms": 8200
}
```
Save one of these per run (`with_skill/timing.json` and `without_skill/timing.json`), filled with your CLI session's real completion numbers.

## Step 7 — Grade the outputs
*(Source section: "Writing assertions" + "Grading outputs" + "Grading principles")*

Concept recap: assertions should be specific and verifiable ("the output includes a bar chart image file"), not vague ("the output is good"). Use a script wherever a check is mechanical; reserve LLM/human judgment for things a script can't decompose, like writing style. Every PASS needs concrete evidence, not benefit of the doubt.

Run the real, tested grading script:
```bash
cd csv-analyzer
python3 evals/check_assertions.py chart \
  ../csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/chart.png \
  ../csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/chart.meta.json
```
**Real output, actually captured:**
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
**Real output:**
```
PASS: the cleaned CSV file exists
PASS: missing emails are flagged, not silently dropped (found 3 flagged rows)
PASS: row count is preserved (no customer records lost)

Mechanical check summary: 3 passed, 0 failed, 3 total
```

**A concrete lesson in "grading principles" worth understanding, not just running:** "both axes are labeled" is normally a hard-to-automate, human-review-only assertion — you can't easily grep a PNG for labels. It became script-checkable here only because the skill's script was deliberately built to *also* emit a small JSON file recording its own label text alongside the image. That's a reusable idea from the source's grading-principles section made concrete: **if an assertion is hard to verify, sometimes the fix is changing what the skill outputs, not writing a cleverer grader.**

Run the same grading against your **without-skill** output once you have it (Step 5) — comparing the two is the actual point (Step 9).

## Step 8 — Aggregate into benchmark.json
*(Source section: "Aggregating results")*

Concept recap: once every run is graded, compute pass-rate/time/token statistics for each configuration and the delta between them. The delta is the answer to "is this skill worth it," expressed as a real trade-off rather than an impression.

```json
{
  "run_summary": {
    "with_skill":    { "pass_rate": {"mean": 1.0, "stddev": 0.0}, "time_seconds": {"mean": 9.0,  "stddev": 1.0}, "tokens": {"mean": 2900, "stddev": 200} },
    "without_skill": { "pass_rate": {"mean": 0.6, "stddev": 0.2}, "time_seconds": {"mean": 14.0, "stddev": 4.0}, "tokens": {"mean": 4100, "stddev": 800} },
    "delta":         { "pass_rate": 0.4, "time_seconds": -5.0, "tokens": -1200 }
  }
}
```
*(Illustrative shape — compute your real numbers once Steps 5–7 are done for real. Worth noting: for a script-backed skill like this one, a negative time/token delta — the skill costing less, not more — is a realistic outcome, since the agent isn't spending tokens reasoning through analysis code it already has a tested script for.)*

## Step 9 — Analyze patterns
*(Source section: "Analyzing patterns")*

Concept recap, applied to your real numbers once you have them:
- **An assertion passing in both configurations** tells you nothing about the skill's value (the baseline handles it fine already) — candidate for removal or tightening.
- **An assertion failing in both** means the assertion itself is broken, or the case is too hard — fix it before blaming the skill.
- **An assertion passing with the skill and failing without it** is where the skill is *proven* to help — expect this to be most or all of the four chart assertions and three cleanup assertions, since a script does the same mechanical thing every time and a model reasoning fresh each run doesn't.
- **High `stddev`** on the without-skill side is the reliability gap made visible.

## Step 10 — Review with a human
*(Source section: "Reviewing results with a human")*

Concept recap: assertion grading only checks what you thought to write assertions for. A human catches what you didn't anticipate, or notices when something is technically correct but misses the point. Feedback should be specific enough to act on.

```json
{
  "eval-top-months-chart": "",
  "eval-clean-missing-emails": ""
}
```
Empty means it looked right — plausible here given how deterministic this skill's two scripts are. Contrast this with a prose-generating skill (like a code-review skill), where human review usually has much more to say.

## Step 11 — Generate a readable report
*(Not in the source article — an addition, folding in `report--generate_report.py`)*

Once you have real graded results, turn them into something easier to read than raw JSON:
```bash
python3 report--generate_report.py report--sample-data.json csv-analyzer-report.html
```
Open `csv-analyzer-report.html` in any browser — a summary card row (test cases, assertions passed/failed, overall pass rate) followed by one card per test case with the prompt, expected output, and a color-coded assertion table with evidence. `report--sample-data.json` already contains the real 7/7 passing results from Step 7 above — replace it with your own once you've graded your own with-skill and without-skill runs, including the without-skill numbers, to see the full comparison rendered side by side.

## Step 12 — Iterate
*(Source section: "Iterating on the skill" + "The loop")*

Concept recap: three signals — failed assertions, human feedback, and (if something looked confusing) the execution transcript — combined with the current `SKILL.md`, become the input for proposing specific improvements. Generalize fixes rather than patching individual examples; keep the skill lean rather than piling on rules; explain *why* an instruction exists rather than just stating it as a rigid rule; and if every run independently reinvents the same helper logic, that's a sign to bundle it as a script (which this skill already does, for exactly this reason).

If iteration 1 passed cleanly (a realistic outcome for a skill this deterministic), the productive next move isn't fixing failures — it's **expanding `evals.json`** with harder cases: a revenue column containing currency symbols or commas, an unexpected column order, an empty file. Add those, go back to Step 3 with a new `iteration-2/` directory, and run the whole loop again. Stop when feedback is consistently empty and pass rates stop improving — not on a fixed schedule.

---

## What You Should Understand Now

If you followed this document start to finish, you should be able to explain, unassisted: why the with/without comparison is the core of the whole methodology; why assertions get written after the first look, not before; why a grading PASS needs quoted evidence rather than an opinion; what makes an assertion worth keeping versus removing during pattern analysis; and why "both axes are labeled" became script-checkable only after the skill's own output was changed to make it so. Those five things are the actual content of the source article — everything else in this guide is just those ideas applied to one real, working skill.
