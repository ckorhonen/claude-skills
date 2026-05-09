# Agent Instructions

## Project Facts

This repository is a collection of reusable AI-agent skills under `skills/`. The README is the public catalog and should stay in sync with skill additions, removals, and renamed skill folders.

## Commands

No repo-wide package manifest or test command is present at the root. Inspect the specific `skills/<skill-name>/` directory before changing a skill; some skills may include their own helper scripts or package manifests.

## Repository Map

- `skills/`: canonical skill directories and `SKILL.md` files.
- `.claude/hooks/`: existing Claude hook scripts for markdown formatting, frontmatter validation, protected-file checks, README sync checks, and dangerous-command blocking.
- `.claude/settings.json`: Claude hook wiring. Preserve this directory; `.claude/` is intentionally not replaced by a top-level symlink in this repo.

## Agent Workflow

- Keep skill edits self-contained to the relevant `skills/<skill-name>/` folder unless the README catalog also needs to change.
- When adding or renaming a skill, update `README.md` in the same pass.
- Do not invent validation commands. Use scripts present in the touched skill folder, or document manual validation if no script exists.
