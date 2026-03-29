#!/usr/bin/env python3
"""
build_workspace.py — Assemble a scenario workspace directory from fixture files.

Creates a temporary directory with the exact file layout the scenario specifies,
so the agent can be run against a realistic filesystem.

Usage:
    python3 build_workspace.py \
        --scenario scenarios/A_resume_accuracy/scenario_01_with_breadcrumbs.json \
        --eval-dir /path/to/eval/breadcrumbs \
        --workspace /tmp/eval-workspace-XXX
"""

import argparse
import json
import os
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()

    eval_dir = Path(args.eval_dir)
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    scenario = json.loads(Path(args.scenario).read_text())
    setup = scenario.get("setup", {})
    structure = setup.get("workspace_structure", {})

    for dest_rel, src_rel in structure.items():
        src = eval_dir / src_rel
        dest = workspace / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)

        if src.exists():
            shutil.copy2(src, dest)
            print(f"  Copied: {src_rel} → {dest_rel}")
        else:
            print(f"  WARNING: Source not found: {src}")

    # Write scenario.json into workspace for reference
    shutil.copy2(args.scenario, workspace / "scenario.json")
    print(f"Workspace ready: {workspace}")


if __name__ == "__main__":
    main()
