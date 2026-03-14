#!/usr/bin/env python3
"""Run an autoresearch experiment and emit a structured result record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import (
    compute_secondary_metrics,
    current_git_ref,
    default_checks_command,
    git_status_files,
    load_session,
    now_utc_iso,
    parse_metric_lines,
    run_shell_command,
    stderr_tail,
    summary_stats,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run warmup and measured trials for an autoresearch experiment."
    )
    parser.add_argument("--id", required=True, help="Experiment identifier.")
    parser.add_argument("--hypothesis", required=True, help="Experiment hypothesis.")
    parser.add_argument(
        "--change-summary", required=True, help="Short summary of the planned change."
    )
    parser.add_argument(
        "--command",
        help="Override the benchmark command from .autoresearch/session.json.",
    )
    parser.add_argument(
        "--metric-name",
        help="Override the primary metric name from .autoresearch/session.json.",
    )
    parser.add_argument(
        "--warmups", type=int, help="Override the warmup count from the session."
    )
    parser.add_argument(
        "--trials", type=int, help="Override the measured trial count from the session."
    )
    parser.add_argument(
        "--checks-command",
        help="Override the checks command from the session or autoresearch.checks.sh.",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip correctness checks even if a checks command exists.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=600,
        help="Per-benchmark timeout in seconds.",
    )
    parser.add_argument(
        "--checks-timeout-seconds",
        type=int,
        default=300,
        help="Per-checks timeout in seconds.",
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="Repeatable file path to record as touched. Defaults to git status files.",
    )
    parser.add_argument(
        "--candidate-ref",
        help="Explicit candidate ref. Defaults to the current git HEAD or working-tree.",
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Mark this experiment as the initial baseline run.",
    )
    parser.add_argument(
        "--output",
        help="Optional file path to save the JSON record while still printing it to stdout.",
    )
    return parser.parse_args()


def run_single_trial(command: str, timeout_seconds: int) -> tuple[str, dict[str, float], str]:
    try:
        result = run_shell_command(command, timeout_seconds=timeout_seconds)
    except TimeoutError:
        return "timeout", {}, "Benchmark timed out."
    if result.returncode != 0:
        diagnostic = stderr_tail(result.stderr or result.stdout)
        return "error", {}, diagnostic or f"Benchmark exited with {result.returncode}."
    metrics = parse_metric_lines(result.stdout)
    if not metrics:
        return "error", {}, "Benchmark produced no parseable METRIC lines."
    return "ok", metrics, stderr_tail(result.stderr)


def main() -> int:
    args = parse_args()
    session = load_session()

    command = args.command or session["command"]
    metric_name = args.metric_name or session["metric_name"]
    warmups = args.warmups if args.warmups is not None else int(session["warmups"])
    trials = args.trials if args.trials is not None else int(session["trials"])

    checks_command = None
    if not args.skip_checks:
        checks_command = (
            args.checks_command
            or session.get("checks_command")
            or default_checks_command()
        )

    warmup_trials: list[float] = []
    measured_trials: list[float] = []
    trial_metrics: list[dict[str, float]] = []
    status = "ok"
    error_message = ""

    for _ in range(warmups):
        run_status, metrics, diagnostic = run_single_trial(command, args.timeout_seconds)
        if run_status != "ok":
            status = "crash"
            error_message = diagnostic
            break
        if metric_name not in metrics:
            status = "crash"
            error_message = (
                f"Primary metric '{metric_name}' not found in warmup output. "
                f"Observed metrics: {', '.join(sorted(metrics)) or 'none'}"
            )
            break
        warmup_trials.append(metrics[metric_name])

    if status == "ok":
        for _ in range(trials):
            run_status, metrics, diagnostic = run_single_trial(
                command, args.timeout_seconds
            )
            if run_status != "ok":
                status = "crash"
                error_message = diagnostic
                break
            if metric_name not in metrics:
                status = "crash"
                error_message = (
                    f"Primary metric '{metric_name}' not found in measured output. "
                    f"Observed metrics: {', '.join(sorted(metrics)) or 'none'}"
                )
                break
            measured_trials.append(metrics[metric_name])
            trial_metrics.append(metrics)

    checks_status = "skipped"
    checks_output = ""
    if status == "ok" and checks_command:
        try:
            checks_result = run_shell_command(
                checks_command, timeout_seconds=args.checks_timeout_seconds
            )
            checks_output = stderr_tail(checks_result.stderr or checks_result.stdout, limit=80)
            checks_status = "passed" if checks_result.returncode == 0 else "failed"
        except TimeoutError:
            checks_status = "failed"
            checks_output = "Checks timed out."

    record = {
        "id": args.id,
        "timestamp": now_utc_iso(),
        "baseline": args.baseline,
        "hypothesis": args.hypothesis,
        "change_summary": args.change_summary,
        "files_touched": args.file or git_status_files(),
        "candidate_ref": args.candidate_ref or current_git_ref(),
        "command": command,
        "metric_name": metric_name,
        "direction": session["direction"],
        "warmup_trials": warmup_trials,
        "measured_trials": measured_trials,
        "trial_metrics": trial_metrics,
        "secondary_metrics": compute_secondary_metrics(trial_metrics, metric_name)
        if trial_metrics
        else {},
        "checks": checks_status,
        "checks_output": checks_output,
        "status": status,
    }

    if measured_trials:
        record["summary"] = summary_stats(measured_trials)
    else:
        record["summary"] = {}

    if error_message:
        record["reason"] = error_message

    payload = json.dumps(record, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
