#!/usr/bin/env python3
"""Render CSV and HTML summaries from the autoresearch experiment ledger."""

from __future__ import annotations

import argparse
import json
import sys

from common import csv_path, load_session, read_jsonl, render_html_report, report_path, results_path, write_results_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render .autoresearch/results.csv and .autoresearch/report.html from the JSONL ledger."
    )
    parser.add_argument(
        "--print-session",
        action="store_true",
        help="Include the loaded session object in stdout for debugging.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = load_session()
    results = read_jsonl(results_path())
    csv_output = write_results_csv(results, csv_path())
    html_output = render_html_report(session, results, report_path())
    payload = {
        "status": "ok",
        "results_count": len(results),
        "csv_path": str(csv_output),
        "report_path": str(html_output),
    }
    if args.print_session:
        payload["session"] = session
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
