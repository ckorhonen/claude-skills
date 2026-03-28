#!/usr/bin/env python3
"""Log a variant evaluation to the archive and refresh reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from common import (
    append_jsonl,
    archive_path,
    compare_metric,
    csv_path,
    get_best_variant,
    load_archive,
    load_session,
    render_html_report,
    report_path,
    write_results_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log a variant evaluation to the hyperagent archive."
    )
    parser.add_argument("--input", help="Path to variant JSON record. Defaults to stdin.")
    parser.add_argument("--decision", choices=("keep", "discard", "checks_failed", "crash"),
                        help="Manual override for disposition.")
    parser.add_argument("--reason", help="Additional reason note.")
    parser.add_argument("--skip-report", action="store_true", help="Don't refresh reports.")
    return parser.parse_args()


def load_record(args: argparse.Namespace) -> dict[str, Any]:
    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("No input. Use --input or pipe JSON.")
    return json.loads(raw)


def decide_disposition(
    record: dict[str, Any], session: dict[str, Any], current_best: dict[str, Any] | None
) -> tuple[str, str, float | None]:
    if record.get("status") == "crash":
        return "crash", record.get("reason", "Variant crashed."), None

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
        return "discard", "Variant did not beat the current best.", improvement_pct
    if improvement_pct is None:
        return "discard", "Cannot compute improvement against zero baseline.", None
    if improvement_pct < threshold:
        return (
            "discard",
            f"Improvement {improvement_pct:.2f}% below {threshold:.2f}% threshold.",
            improvement_pct,
        )
    return (
        "keep",
        f"Improved by {improvement_pct:.2f}% over best ({current_best.get('id', '?')}). Checks passed.",
        improvement_pct,
    )


def main() -> int:
    args = parse_args()
    session = load_session()
    record = load_record(args)

    existing = load_archive()
    current_best = get_best_variant(existing, session["direction"])

    disposition, auto_reason, improvement_pct = decide_disposition(record, session, current_best)

    if args.decision:
        disposition = args.decision
    reason = auto_reason
    if args.reason:
        reason = f"{reason} {args.reason}".strip()

    final = dict(record)
    final["disposition"] = disposition
    final["reason"] = reason
    final["children_count"] = 0
    if current_best is not None:
        final["baseline_ref"] = current_best.get("candidate_ref")
        final["baseline_value"] = current_best.get("summary", {}).get("median")
    if improvement_pct is not None:
        final["improvement_pct"] = improvement_pct

    append_jsonl(archive_path(), final)
    all_results = existing + [final]

    if not args.skip_report:
        write_results_csv(all_results, csv_path())
        render_html_report(session, all_results, report_path())

    sys.stdout.write(json.dumps(final, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
