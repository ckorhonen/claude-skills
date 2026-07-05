# Agent Instructions

## Project Facts

This repository is a collection of reusable AI-agent skills under `skills/`. The README is the public catalog and should stay in sync with skill additions, removals, and renamed skill folders.

## Commands

No repo-wide package manifest or test command is present at the root. Inspect the specific `skills/<skill-name>/` directory before changing a skill; some skills may include their own helper scripts or package manifests.

## Repository Map

- `skills/`: canonical skill directories and `SKILL.md` files.
- `.agents/`: shared agent config (hooks, rules, settings). Both `.claude` and `.codex` are top-level symlinks to `.agents/`, and `.agents/skills` symlinks back to `../skills`, so all agents resolve the same config and skill set.
- `.agents/hooks/`: hook scripts for markdown formatting, frontmatter validation, protected-file checks, README sync checks, and dangerous-command blocking (reachable as `.claude/hooks/`).
- `.agents/settings.json`: hook wiring (reachable as `.claude/settings.json`).

## Agents and Commands

- `agents/`: publishable subagent definitions (7 files, e.g. `code-reviewer.md`, `orchestrator.md`, `security-auditor.md`) mirroring the user's global agent install.
- `commands/`: publishable command definitions (4 files: `add-tests.md`, `install-conductor.md`, `pr-create.md`, `simplify.md`) mirroring the user's global command install.
- `.agents/commands/README.md` points here; these root directories are the catalog copies.

## Source of Truth & Sync

- `~/.agents/skills` on this machine is the live source of truth for skills; this repo is the published catalog and is currently about 2 months stale.
- Refresh catalog copies from the global install with `scripts/sync-from-global.sh` (dry-run by default; pass `--apply` to write, `--all` to also copy new global-only skills).

## Agent Workflow

- Keep skill edits self-contained to the relevant `skills/<skill-name>/` folder unless the README catalog also needs to change.
- When adding or renaming a skill, update `README.md` in the same pass.
- Do not invent validation commands. Use scripts present in the touched skill folder, or document manual validation if no script exists.
