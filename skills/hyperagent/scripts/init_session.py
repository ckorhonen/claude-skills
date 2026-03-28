#!/usr/bin/env python3
"""Initialize a hyperagent session and scaffold the workspace."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import (
    ensure_artifacts_dir,
    ensure_git_exclude,
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
    budget = f"{args.max_generations} generations" if args.max_generations else "None specified"
    return f"""# Hyperagent: {args.goal}

## Objective
{args.goal}

## Configuration
- Primary metric: {args.metric_name}
- Unit: {args.unit}
- Direction: {args.direction}
- Minimum improvement: {args.min_improvement}%
- Task command: `{args.task_command}`
- Correctness gates: {checks}
- Generation budget: {budget}
- Meta self-modify: {"yes" if args.meta_self_modify else "no"}

## Scope
### In scope
{scope_lines}

### Off limits
{off_limit_lines}

## Decision Rule
- Warmup trials: {args.warmups}
- Measured trials: {args.trials}
- Keep when improvement >= {args.min_improvement}% and checks pass
- Plateau detection: stop after {args.plateau_window} consecutive non-improvements

## Archive
`.hyperagent/archive.jsonl`

## Report
`.hyperagent/report.html`

## Lineage
*Updated as variants are logged.*

## Meta-Strategy
Initial strategy: analyze task agent code and performance history, propose targeted modifications
with clear causal hypotheses, prefer one change per generation, diversify hypothesis types
(algorithmic, structural, prompt-level, parameter-level).

## What We've Learned
- Session initialized on {now_utc_iso()}

## Performance Tracking
No baseline recorded yet.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a hyperagent session and scaffold local artifacts."
    )
    parser.add_argument("--goal", required=True, help="Short goal for the session.")
    parser.add_argument("--metric-name", required=True, help="Primary metric name.")
    parser.add_argument("--unit", required=True, help="Unit for the primary metric.")
    parser.add_argument(
        "--direction", required=True, choices=("lower", "higher"),
        help="Whether lower or higher values are better.",
    )
    parser.add_argument("--task-command", required=True, help="Command to run the task agent.")
    parser.add_argument("--min-improvement", type=float, default=1.0,
                        help="Minimum %% improvement to keep a variant.")
    parser.add_argument("--warmups", type=int, default=2, help="Warmup trials per evaluation.")
    parser.add_argument("--trials", type=int, default=5, help="Measured trials per evaluation.")
    parser.add_argument("--scope", action="append", default=[], help="In-scope path (repeatable).")
    parser.add_argument("--off-limits", action="append", default=[], help="Off-limits path (repeatable).")
    parser.add_argument("--checks-command", help="Correctness validation command.")
    parser.add_argument("--max-generations", type=int, default=50, help="Max generations before stopping.")
    parser.add_argument("--plateau-window", type=int, default=3,
                        help="Stop after N consecutive non-improvements.")
    parser.add_argument("--meta-self-modify", action="store_true", default=True,
                        help="Allow meta-agent to modify its own strategy (default: yes).")
    parser.add_argument("--no-meta-self-modify", dest="meta_self_modify", action="store_false",
                        help="Disallow meta-agent self-modification.")
    parser.add_argument("--rewrite-markdown", action="store_true",
                        help="Overwrite hyperagent.md even if it exists.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()
    artifacts = ensure_artifacts_dir(cwd)
    exclude_updated = ensure_git_exclude(".hyperagent/", cwd)

    session = {
        "goal": args.goal,
        "metric_name": args.metric_name,
        "unit": args.unit,
        "direction": args.direction,
        "task_command": args.task_command,
        "min_improvement_pct": args.min_improvement,
        "warmups": args.warmups,
        "trials": args.trials,
        "scope": args.scope,
        "off_limits": args.off_limits,
        "checks_command": args.checks_command,
        "max_generations": args.max_generations,
        "plateau_window": args.plateau_window,
        "meta_self_modify": args.meta_self_modify,
        "updated_at": now_utc_iso(),
    }

    existing = session_path(cwd)
    if existing.exists():
        prior = json.loads(existing.read_text(encoding="utf-8"))
        session["created_at"] = prior.get("created_at", now_utc_iso())
    else:
        session["created_at"] = now_utc_iso()

    atomic_write_json(session_path(cwd), session)

    markdown_path = cwd / "hyperagent.md"
    scaffolded = False
    if args.rewrite_markdown or not markdown_path.exists():
        atomic_write_text(markdown_path, build_markdown(args))
        scaffolded = True

    payload = {
        "status": "ok",
        "session_path": str(session_path(cwd)),
        "artifacts_dir": str(artifacts),
        "scaffolded_hyperagent_md": scaffolded,
        "exclude_updated": exclude_updated,
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
