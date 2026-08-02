#!/usr/bin/env python3
"""
top_months_chart.py — reads a CSV with month,revenue columns, finds the top N
months by revenue, and writes a labeled bar chart PNG.

Usage: top_months_chart.py <input.csv> <output.png> [top_n]
"""
import csv
import sys
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 3:
        print("Usage: top_months_chart.py <input.csv> <output.png> [top_n]", file=sys.stderr)
        sys.exit(1)

    input_csv, output_png = sys.argv[1], sys.argv[2]
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    rows = []
    with open(input_csv, newline="") as f:
        for r in csv.DictReader(f):
            rows.append((r["month"], float(r["revenue"])))

    top = sorted(rows, key=lambda x: x[1], reverse=True)[:top_n]
    # Keep chronological order on the x-axis for readability, per the top set
    month_order = [m for m, _ in rows]
    top_sorted_chrono = sorted(top, key=lambda x: month_order.index(x[0]))

    months = [m for m, _ in top_sorted_chrono]
    revenues = [v for _, v in top_sorted_chrono]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(months, revenues, color="#4C72B0")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue ($)")
    ax.set_title(f"Top {top_n} Months by Revenue")
    for i, v in enumerate(revenues):
        ax.text(i, v + max(revenues) * 0.01, f"${v:,.0f}", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(output_png, dpi=120)

    meta = {
        "months_plotted": months,
        "month_count": len(months),
        "xlabel": ax.get_xlabel(),
        "ylabel": ax.get_ylabel(),
        "title": ax.get_title(),
    }
    meta_path = output_png.rsplit(".", 1)[0] + ".meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Top {top_n} months by revenue: " + ", ".join(f"{m} (${v:,.0f})" for m, v in top))
    print(f"Chart saved to {output_png}")
    print(f"Chart metadata saved to {meta_path}")

if __name__ == "__main__":
    main()
