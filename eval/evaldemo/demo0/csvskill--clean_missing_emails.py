#!/usr/bin/env python3
"""
clean_missing_emails.py — reads a customer CSV, flags rows with missing emails,
writes a cleaned CSV, and reports how many were missing.

"Cleaned" here means: rows with a missing email get an explicit, visible
placeholder ("MISSING") rather than being silently dropped — dropping rows
would lose customer records, which is a worse outcome than flagging them.

Usage: clean_missing_emails.py <input.csv> <output.csv>
"""
import csv
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: clean_missing_emails.py <input.csv> <output.csv>", file=sys.stderr)
        sys.exit(1)

    input_csv, output_csv = sys.argv[1], sys.argv[2]

    rows = []
    missing_count = 0
    with open(input_csv, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            if not r["email"].strip():
                r["email"] = "MISSING"
                missing_count += 1
            rows.append(r)

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Cleaned CSV written to {output_csv}")
    print(f"Missing emails found and flagged: {missing_count}")

if __name__ == "__main__":
    main()
