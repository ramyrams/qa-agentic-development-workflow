#!/usr/bin/env python3
"""
check_assertions.py — grades the mechanically-verifiable assertions for the
csv-analyzer skill's two eval cases, using the real output artifacts
(the chart PNG + its metadata sidecar, or the cleaned CSV) rather than
asking a model to judge anything a script can check directly.

Usage:
  check_assertions.py chart <chart.png> <chart.meta.json>
  check_assertions.py cleanup <cleaned.csv> <expected_missing_count>
"""
import sys
import os
import json
import csv

def check(desc, cond):
    print(("PASS: " if cond else "FAIL: ") + desc)
    return 1 if cond else 0

def grade_chart(png_path, meta_path):
    passed = 0
    total = 0

    total += 1; passed += check("output includes a bar chart image file",
                                  os.path.exists(png_path) and os.path.getsize(png_path) > 0)

    if not os.path.exists(meta_path):
        print(f"FAIL: no metadata sidecar found at {meta_path} — cannot grade remaining assertions")
        total += 3
        return passed, total

    with open(meta_path) as f:
        meta = json.load(f)

    total += 1; passed += check("the chart shows exactly 3 months",
                                  meta.get("month_count") == 3)
    total += 1; passed += check("both axes are labeled",
                                  bool(meta.get("xlabel")) and bool(meta.get("ylabel")))
    total += 1; passed += check("the chart title or caption mentions revenue",
                                  "revenue" in meta.get("title", "").lower())

    return passed, total

def grade_cleanup(csv_path, expected_missing):
    passed = 0
    total = 0

    total += 1; passed += check("the cleaned CSV file exists",
                                  os.path.exists(csv_path) and os.path.getsize(csv_path) > 0)

    if not os.path.exists(csv_path):
        total += 2
        return passed, total

    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))

    missing_flagged = sum(1 for r in rows if r.get("email") == "MISSING")
    total += 1; passed += check(f"missing emails are flagged, not silently dropped (found {missing_flagged} flagged rows)",
                                  missing_flagged == int(expected_missing))
    total += 1; passed += check("row count is preserved (no customer records lost)",
                                  len(rows) == 7)  # known input row count for this fixture

    return passed, total

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "chart":
        p, t = grade_chart(sys.argv[2], sys.argv[3])
    elif mode == "cleanup":
        p, t = grade_cleanup(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(2)

    print(f"\nMechanical check summary: {p} passed, {t - p} failed, {t} total")
    sys.exit(0 if p == t else 1)
