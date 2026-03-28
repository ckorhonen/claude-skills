#!/usr/bin/env python3
"""Render CSV and HTML reports from the hyperagent archive."""

from __future__ import annotations

import argparse
import json
import sys

from common import (
    csv_path,
    load_archive,
    load_session,
    render_html_report,
    report_path,
    write_results_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render .hyperagent/results.csv and .hyperagent/report.html from the archive."
    )
    parser.add_argument("--print-session", action="store_true",
                        help="Include session config in output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = load_session()
    archive = load_archive()
    csv_out = write_results_csv(archive, csv_path())
    html_out = render_html_report(session, archive, report_path())
    payload = {
        "status": "ok",
        "archive_size": len(archive),
        "csv_path": str(csv_out),
        "report_path": str(html_out),
    }
    if args.print_session:
        payload["session"] = session
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
