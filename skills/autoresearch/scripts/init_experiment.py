#!/usr/bin/env python3
"""Initialize an autoresearch session."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import (
    ensure_artifacts_dir,
    ensure_git_exclude,
    format_command_for_markdown,
    now_utc_iso,
    session_path,
    atomic_write_json,
    atomic_write_text,
)


def build_markdown(args: argparse.Namespace) -> str:
    scope_lines = "\n".join(f"- {item}" for item in args.scope) if args.scope else "- TBD"
    off_limit_lines = (
        "\n".join(f"- {item}" for item in args.off_limits) if args.off_limits else "- None declared"
    )
    checks = args.checks_command or "None"
    budget = args.budget or "None specified"
    return f"""# Autoresearch: {args.goal}

## Objective
{args.goal}

## Up-Front Answers
- Primary metric: {args.metric_name}
- Unit: {args.unit}
- Direction: {args.direction}
- Minimum meaningful improvement: {args.min_improvement}%
- Workload command: `{format_command_for_markdown(args.command)}`
- Correctness gates: {checks}
- Budget / stop criteria: {budget}

## Scope
{scope_lines}

## Off limits
{off_limit_lines}

## Decision Rule
- Warmup trials: {args.warmups}
- Measured trials: {args.trials}
- Keep when improvement >= {args.min_improvement}% and checks pass

## Experiment Ledger
`.autoresearch/results.jsonl`

## Report Outputs
- `.autoresearch/report.html`
- `.autoresearch/results.csv`
- `.autoresearch/plots/`

## Current Best Result
No baseline recorded yet.

## What We've Learned
- Session initialized on {now_utc_iso()}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize an autoresearch session and scaffold local artifacts."
    )
    parser.add_argument("--goal", required=True, help="Short goal for the session.")
    parser.add_argument(
        "--metric-name", required=True, help="Primary metric name emitted by the benchmark."
    )
    parser.add_argument("--unit", required=True, help="Unit for the primary metric.")
    parser.add_argument(
        "--direction",
        required=True,
        choices=("lower", "higher"),
        help="Whether lower or higher values are better.",
    )
    parser.add_argument(
        "--command",
        required=True,
        help="Benchmark command to execute, usually ./autoresearch.sh.",
    )
    parser.add_argument(
        "--min-improvement",
        type=float,
        default=1.0,
        help="Minimum percent improvement required to keep a change.",
    )
    parser.add_argument(
        "--warmups", type=int, default=2, help="Default warmup trials per experiment."
    )
    parser.add_argument(
        "--trials", type=int, default=5, help="Default measured trials per experiment."
    )
    parser.add_argument(
        "--scope",
        action="append",
        default=[],
        help="Repeatable path or area that is in scope.",
    )
    parser.add_argument(
        "--off-limits",
        action="append",
        default=[],
        help="Repeatable path or area that is off-limits.",
    )
    parser.add_argument(
        "--checks-command",
        help="Correctness validation command, usually ./autoresearch.checks.sh.",
    )
    parser.add_argument("--budget", help="Optional time or compute budget.")
    parser.add_argument(
        "--rewrite-markdown",
        action="store_true",
        help="Overwrite autoresearch.md even if it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()
    artifacts = ensure_artifacts_dir(cwd)
    exclude_updated = ensure_git_exclude(".autoresearch/", cwd)

    session = {
        "goal": args.goal,
        "metric_name": args.metric_name,
        "unit": args.unit,
        "direction": args.direction,
        "command": args.command,
        "min_improvement_pct": args.min_improvement,
        "warmups": args.warmups,
        "trials": args.trials,
        "scope": args.scope,
        "off_limits": args.off_limits,
        "checks_command": args.checks_command,
        "budget": args.budget,
        "updated_at": now_utc_iso(),
    }

    existing = session_path(cwd)
    if existing.exists():
        prior = json.loads(existing.read_text(encoding="utf-8"))
        session["created_at"] = prior.get("created_at", now_utc_iso())
    else:
        session["created_at"] = now_utc_iso()

    atomic_write_json(session_path(cwd), session)

    markdown_path = cwd / "autoresearch.md"
    scaffolded_markdown = False
    if args.rewrite_markdown or not markdown_path.exists():
        atomic_write_text(markdown_path, build_markdown(args))
        scaffolded_markdown = True

    payload = {
        "status": "ok",
        "session_path": str(session_path(cwd)),
        "artifacts_dir": str(artifacts),
        "scaffolded_autoresearch_md": scaffolded_markdown,
        "exclude_updated": exclude_updated,
        "checks_command": args.checks_command,
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
