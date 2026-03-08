#!/usr/bin/env python3
"""Resolve the pull request template for the current repository."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


COMMON_TEMPLATE_PATHS = (
    ".github/pull_request_template.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "pull_request_template.md",
    "PULL_REQUEST_TEMPLATE.md",
    "docs/pull_request_template.md",
    "docs/PULL_REQUEST_TEMPLATE.md",
)
COMMON_TEMPLATE_GLOBS = (
    ".github/pull_request_template/*.md",
    ".github/PULL_REQUEST_TEMPLATE/*.md",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Find the repo's pull request template, or fall back to the bundled "
            "default template for the babysit-pr skill."
        )
    )
    parser.add_argument("--repo-root", help="Optional repository root override")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a plain path")
    return parser.parse_args()


def resolve_repo_root(repo_root_override):
    if repo_root_override:
        return Path(repo_root_override).resolve()
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return Path.cwd().resolve()
    return Path(proc.stdout.strip()).resolve()


def default_template_path():
    return (Path(__file__).resolve().parent.parent / "assets" / "default_pr_template.md").resolve()


def find_repo_template(repo_root):
    checked = []
    for rel_path in COMMON_TEMPLATE_PATHS:
        candidate = (repo_root / rel_path).resolve()
        checked.append(str(candidate))
        if candidate.is_file():
            return candidate, checked

    for pattern in COMMON_TEMPLATE_GLOBS:
        matches = sorted((repo_root / ".").glob(pattern))
        checked.extend(str(match.resolve()) for match in matches)
        if matches:
            return matches[0].resolve(), checked

    return None, checked


def main():
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    template_path, checked = find_repo_template(repo_root)
    source = "repo"
    if template_path is None:
        template_path = default_template_path()
        checked.append(str(template_path))
        source = "fallback"

    payload = {
        "repo_root": str(repo_root),
        "template_path": str(template_path),
        "source": source,
        "checked_paths": checked,
    }

    if args.json:
        sys.stdout.write(json.dumps(payload, sort_keys=True) + "\n")
    else:
        sys.stdout.write(f"{template_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
