---
name: csv-analyzer
description: "Use when asked to analyze a CSV file — finding top/bottom values, building charts from tabular data, cleaning missing or malformed fields, or reporting data-quality issues in spreadsheet-style data."
---

# CSV Analyzer

## Procedure

1. Identify which operation the request needs: a **chart/summary** request (e.g., "top N by column X") or a **data-cleaning** request (e.g., "handle missing values in column Y").
2. For chart/summary requests, run `scripts/top_months_chart.py <input.csv> <output.png> [top_n]`. It writes both the chart PNG and a `.meta.json` sidecar describing what was plotted — read the sidecar to confirm the chart matches what was asked before reporting success.
3. For data-cleaning requests, run `scripts/clean_missing_emails.py <input.csv> <output.csv>`. It flags missing values explicitly rather than silently dropping rows, and reports the count.
4. Report back in plain language: what was found/produced, the specific numbers involved (counts, top values), and where the output file was saved.
5. Never fabricate a number that should have come from the data — if a script fails or the CSV doesn't have the expected columns, say so and ask, rather than guessing a plausible-looking answer.

## Bundled Resources

- `scripts/top_months_chart.py` — top-N-by-value bar chart generator with a metadata sidecar for verification.
- `scripts/clean_missing_emails.py` — missing-value flagging and reporting for CSV data.

## What This Skill Does NOT Do

Does not handle CSVs with formats these scripts don't already expect (different column names, non-CSV delimiters) without being adapted first — say so rather than forcing a mismatched file through the script.
