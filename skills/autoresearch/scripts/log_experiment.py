#!/usr/bin/env python3
"""Log an autoresearch experiment and refresh derived artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from common import (
    append_jsonl,
    compare_metric,
    csv_path,
    load_session,
    read_jsonl,
    render_html_report,
    report_path,
    results_path,
    write_results_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append an experiment record to .autoresearch/results.jsonl and refresh reports."
    )
    parser.add_argument(
        "--input",
        help="Path to an experiment JSON record. Defaults to reading JSON from stdin.",
    )
    parser.add_argument(
        "--decision",
        choices=("keep", "discard", "checks_failed", "crash"),
        help="Optional manual override for the final disposition.",
    )
    parser.add_argument(
        "--reason",
        help="Optional manual note to append to the auto-generated reason.",
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Append the record without refreshing CSV and HTML artifacts.",
    )
    return parser.parse_args()


def load_record(args: argparse.Namespace) -> dict[str, Any]:
    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("No input record provided. Use --input or pipe JSON on stdin.")
    return json.loads(raw)


def select_current_best(
    results: list[dict[str, Any]], direction: str
) -> dict[str, Any] | None:
    candidates = [
        record
        for record in results
        if record.get("disposition") == "keep" and record.get("summary", {}).get("median") is not None
    ]
    if not candidates:
        return None
    best = candidates[0]
    for record in candidates[1:]:
        incumbent = best["summary"]["median"]
        candidate = record["summary"]["median"]
        if direction == "lower" and candidate < incumbent:
            best = record
        if direction == "higher" and candidate > incumbent:
            best = record
    return best


def decide_disposition(
    record: dict[str, Any], session: dict[str, Any], current_best: dict[str, Any] | None
) -> tuple[str, str, float | None]:
    if record.get("status") == "crash":
        return "crash", record.get("reason", "Experiment crashed."), None

    if record.get("checks") == "failed":
        return "checks_failed", "Correctness checks failed.", None

    median = record.get("summary", {}).get("median")
    if median is None:
        return "crash", "No summary median available.", None

    if record.get("baseline") or current_best is None:
        return "keep", "Initial baseline recorded.", None

    baseline_value = current_best.get("summary", {}).get("median")
    better, improvement_pct = compare_metric(
        float(median), float(baseline_value), session["direction"]
    )
    threshold = float(session.get("min_improvement_pct", 1.0))
    if not better:
        return "discard", "Candidate did not beat the current best result.", improvement_pct
    if improvement_pct is None:
        return "discard", "Unable to compute percent improvement against zero baseline.", None
    if improvement_pct < threshold:
        return (
            "discard",
            f"Improvement of {improvement_pct:.2f}% did not clear the {threshold:.2f}% threshold.",
            improvement_pct,
        )
    return (
        "keep",
        f"Improved by {improvement_pct:.2f}% over the current best and checks passed.",
        improvement_pct,
    )


def main() -> int:
    args = parse_args()
    session = load_session()
    record = load_record(args)

    existing_results = read_jsonl(results_path())
    current_best = select_current_best(existing_results, session["direction"])

    disposition, auto_reason, improvement_pct = decide_disposition(
        record, session, current_best
    )

    if args.decision:
        disposition = args.decision
    reason = auto_reason
    if args.reason:
        reason = f"{reason} {args.reason}".strip()

    final_record = dict(record)
    final_record["disposition"] = disposition
    final_record["reason"] = reason
    if current_best is not None:
        final_record["baseline_ref"] = current_best.get("candidate_ref")
        final_record["baseline_value"] = current_best.get("summary", {}).get("median")
    if improvement_pct is not None:
        final_record["improvement_pct"] = improvement_pct

    append_jsonl(results_path(), final_record)
    all_results = existing_results + [final_record]

    if not args.skip_report:
        write_results_csv(all_results, csv_path())
        render_html_report(session, all_results, report_path())

    sys.stdout.write(json.dumps(final_record, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
