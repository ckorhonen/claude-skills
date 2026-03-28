#!/usr/bin/env python3
"""Evaluate a task-agent variant: run warmups, measured trials, and optional checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import (
    compute_secondary_metrics,
    current_git_ref,
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
        description="Evaluate a hyperagent variant with warmup + measured trials."
    )
    parser.add_argument("--id", required=True, help="Variant identifier (e.g. gen-001).")
    parser.add_argument("--hypothesis", required=True, help="Why this variant should improve.")
    parser.add_argument("--change-summary", required=True, help="Short summary of changes.")
    parser.add_argument("--parent", help="Parent variant ID this was derived from.")
    parser.add_argument("--generation", type=int, help="Generation number.")
    parser.add_argument("--command", help="Override task command from session.")
    parser.add_argument("--metric-name", help="Override metric name from session.")
    parser.add_argument("--warmups", type=int, help="Override warmup count.")
    parser.add_argument("--trials", type=int, help="Override measured trial count.")
    parser.add_argument("--checks-command", help="Override checks command.")
    parser.add_argument("--skip-checks", action="store_true", help="Skip correctness checks.")
    parser.add_argument("--timeout-seconds", type=int, default=600, help="Per-trial timeout.")
    parser.add_argument("--checks-timeout-seconds", type=int, default=300, help="Checks timeout.")
    parser.add_argument("--file", action="append", default=[], help="File touched (repeatable).")
    parser.add_argument("--candidate-ref", help="Git ref for this variant.")
    parser.add_argument("--baseline", action="store_true", help="Mark as initial baseline.")
    parser.add_argument("--meta-modifications", action="append", default=[],
                        help="Description of meta-level modification (repeatable).")
    parser.add_argument("--output", help="Save JSON record to file.")
    return parser.parse_args()


def run_single_trial(command: str, timeout: int) -> tuple[str, dict[str, float], str]:
    try:
        result = run_shell_command(command, timeout_seconds=timeout)
    except TimeoutError:
        return "timeout", {}, "Benchmark timed out."
    if result.returncode != 0:
        diag = stderr_tail(result.stderr or result.stdout)
        return "error", {}, diag or f"Exited with {result.returncode}."
    metrics = parse_metric_lines(result.stdout)
    if not metrics:
        return "error", {}, "No parseable METRIC lines in output."
    return "ok", metrics, stderr_tail(result.stderr)


def main() -> int:
    args = parse_args()
    session = load_session()

    command = args.command or session["task_command"]
    metric_name = args.metric_name or session["metric_name"]
    warmups = args.warmups if args.warmups is not None else int(session["warmups"])
    trials = args.trials if args.trials is not None else int(session["trials"])

    checks_command = None
    if not args.skip_checks:
        checks_command = args.checks_command or session.get("checks_command")

    warmup_trials: list[float] = []
    measured_trials: list[float] = []
    trial_metrics: list[dict[str, float]] = []
    status = "ok"
    error_message = ""

    # Warmups
    for _ in range(warmups):
        s, m, d = run_single_trial(command, args.timeout_seconds)
        if s != "ok":
            status = "crash"
            error_message = d
            break
        if metric_name not in m:
            status = "crash"
            error_message = f"Metric '{metric_name}' not in output. Found: {', '.join(sorted(m)) or 'none'}"
            break
        warmup_trials.append(m[metric_name])

    # Measured trials
    if status == "ok":
        for _ in range(trials):
            s, m, d = run_single_trial(command, args.timeout_seconds)
            if s != "ok":
                status = "crash"
                error_message = d
                break
            if metric_name not in m:
                status = "crash"
                error_message = f"Metric '{metric_name}' not in output. Found: {', '.join(sorted(m)) or 'none'}"
                break
            measured_trials.append(m[metric_name])
            trial_metrics.append(m)

    # Checks
    checks_status = "skipped"
    checks_output = ""
    if status == "ok" and checks_command:
        try:
            cr = run_shell_command(checks_command, timeout_seconds=args.checks_timeout_seconds)
            checks_output = stderr_tail(cr.stderr or cr.stdout, limit=80)
            checks_status = "passed" if cr.returncode == 0 else "failed"
        except TimeoutError:
            checks_status = "failed"
            checks_output = "Checks timed out."

    record: dict = {
        "id": args.id,
        "generation": args.generation,
        "parent_id": args.parent,
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
        "secondary_metrics": compute_secondary_metrics(trial_metrics, metric_name) if trial_metrics else {},
        "checks": checks_status,
        "checks_output": checks_output,
        "meta_modifications": args.meta_modifications,
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
