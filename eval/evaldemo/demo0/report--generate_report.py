#!/usr/bin/env python3
"""
generate_report.py — turns a report-data.json (evals + graded assertion
results) into a single, readable, self-contained HTML report.

No dependencies beyond the Python standard library — no npm install,
no pip install, nothing to license or pay for. This is meant to be the
"zero-adoption-cost" option: point it at whatever grading.json-shaped
data your eval runner already produces.

Usage: generate_report.py <report-data.json> <output.html>
"""
import json
import sys
import html
from datetime import datetime, timezone

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Eval Report — {skill_name}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
          background: #f6f7f9; color: #1a1a1a; margin: 0; padding: 2rem; }}
  .wrap {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 0.2rem; }}
  .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }}
  .summary {{ display: flex; gap: 1rem; margin-bottom: 2rem; }}
  .summary .card {{ background: white; border-radius: 8px; padding: 1rem 1.5rem;
                     box-shadow: 0 1px 3px rgba(0,0,0,0.08); flex: 1; }}
  .summary .card .n {{ font-size: 1.8rem; font-weight: 700; }}
  .summary .card .l {{ color: #666; font-size: 0.85rem; }}
  .pass {{ color: #1a7f37; }}
  .fail {{ color: #cf222e; }}
  .case {{ background: white; border-radius: 8px; padding: 1.5rem;
           margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .case h2 {{ font-size: 1.1rem; margin: 0 0 0.5rem 0; }}
  .prompt {{ background: #f0f2f5; border-radius: 6px; padding: 0.75rem 1rem;
             font-size: 0.9rem; margin-bottom: 1rem; font-style: italic; }}
  .expected {{ font-size: 0.85rem; color: #555; margin-bottom: 1rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th {{ text-align: left; padding: 0.4rem 0.5rem; border-bottom: 2px solid #eee;
        color: #666; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }}
  td {{ padding: 0.5rem; border-bottom: 1px solid #f0f0f0; vertical-align: top; }}
  .badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px;
            font-size: 0.75rem; font-weight: 700; }}
  .badge.pass {{ background: #dafbe1; color: #1a7f37; }}
  .badge.fail {{ background: #ffebe9; color: #cf222e; }}
  .evidence {{ color: #555; font-size: 0.85rem; }}
  .case-rate {{ float: right; font-size: 0.9rem; font-weight: 600; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Eval Report — {skill_name}</h1>
  <div class="meta">Iteration {iteration} · generated {generated_at}</div>

  <div class="summary">
    <div class="card"><div class="n">{total_cases}</div><div class="l">Test cases</div></div>
    <div class="card"><div class="n pass">{total_passed}</div><div class="l">Assertions passed</div></div>
    <div class="card"><div class="n {overall_class}">{total_failed}</div><div class="l">Assertions failed</div></div>
    <div class="card"><div class="n">{pass_rate}%</div><div class="l">Overall pass rate</div></div>
  </div>

  {cases_html}
</div>
</body>
</html>
"""

CASE_TEMPLATE = """
  <div class="case">
    <h2>{name} <span class="case-rate {case_class}">{case_passed}/{case_total} passed</span></h2>
    <div class="prompt">&ldquo;{prompt}&rdquo;</div>
    <div class="expected"><strong>Expected:</strong> {expected}</div>
    <table>
      <tr><th style="width:55%">Assertion</th><th style="width:10%">Result</th><th>Evidence</th></tr>
      {rows_html}
    </table>
  </div>
"""

ROW_TEMPLATE = """
      <tr>
        <td>{text}</td>
        <td><span class="badge {cls}">{label}</span></td>
        <td class="evidence">{evidence}</td>
      </tr>
"""

def render(data):
    total_passed = 0
    total_failed = 0
    cases_html = ""

    for case in data["cases"]:
        results = case["assertion_results"]
        c_passed = sum(1 for r in results if r["passed"])
        c_total = len(results)
        total_passed += c_passed
        total_failed += (c_total - c_passed)

        rows_html = ""
        for r in results:
            rows_html += ROW_TEMPLATE.format(
                text=html.escape(r["text"]),
                cls="pass" if r["passed"] else "fail",
                label="PASS" if r["passed"] else "FAIL",
                evidence=html.escape(r["evidence"]),
            )

        cases_html += CASE_TEMPLATE.format(
            name=html.escape(case["name"]),
            case_class="pass" if c_passed == c_total else "fail",
            case_passed=c_passed,
            case_total=c_total,
            prompt=html.escape(case["prompt"]),
            expected=html.escape(case["expected_output"]),
            rows_html=rows_html,
        )

    total = total_passed + total_failed
    pass_rate = round((total_passed / total) * 100, 1) if total else 0.0

    return TEMPLATE.format(
        skill_name=html.escape(data["skill_name"]),
        iteration=data.get("iteration", "?"),
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        total_cases=len(data["cases"]),
        total_passed=total_passed,
        total_failed=total_failed,
        overall_class="fail" if total_failed else "pass",
        pass_rate=pass_rate,
        cases_html=cases_html,
    )

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate_report.py <report-data.json> <output.html>", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    out = render(data)
    with open(sys.argv[2], "w") as f:
        f.write(out)
    print(f"Report written to {sys.argv[2]}")
