#!/usr/bin/env python3
"""Select a parent variant from the archive for the next generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import (
    detect_plateau,
    improvement_velocity,
    load_archive,
    load_session,
    select_parent_from_archive,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select a parent from the hyperagent archive using performance-weighted exploration-biased sampling."
    )
    parser.add_argument("--output", help="Save selection JSON to file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = load_session()
    archive = load_archive()

    if not archive:
        sys.stderr.write("Archive is empty. Run baseline evaluation first.\n")
        return 1

    parent = select_parent_from_archive(archive, session["direction"])
    if parent is None:
        sys.stderr.write("No kept variants in archive to select from.\n")
        return 1

    # Count this parent's existing children
    parent_id = parent.get("id", "unknown")
    children = sum(1 for r in archive if r.get("parent_id") == parent_id)

    plateau = detect_plateau(archive, session.get("plateau_window", 3))
    velocity = improvement_velocity(archive)

    payload = {
        "selected_parent": parent_id,
        "score": parent.get("summary", {}).get("median"),
        "children_count": children,
        "generation": (parent.get("generation") or 0) + 1,
        "plateau_detected": plateau,
        "improvement_velocity": velocity,
        "archive_size": len(archive),
        "kept_count": sum(1 for r in archive if r.get("disposition") == "keep"),
        "reason": f"Selected {parent_id} (score={parent.get('summary',{}).get('median')}, children={children})",
    }

    if plateau:
        payload["warning"] = (
            f"Plateau detected: last {session.get('plateau_window', 3)} variants were not improvements. "
            "Consider a fundamentally different approach or stopping."
        )

    output = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    sys.stdout.write(output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
