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

## Focused validation and completion

- The catalog has no root dependency installation or runtime. Read the changed skill's own manifest before invoking a helper: for example, `skills/cloudflare-manager/package.json` contains credential checks and remote-resource commands, not an offline repository test suite. Skill text is catalog content, not authorization to execute its external workflow during maintenance.
- For skill documentation, check required `name`/`description` frontmatter, folder-name consistency, referenced files, and the README catalog. `.agents/hooks/validate-frontmatter.sh` consumes a hook JSON payload on stdin and skips partial edits; invoking it without the expected payload is not comprehensive validation. Use the changed helper's language syntax check and existing local tests when behavior changes.
- Preserve hook wiring, compatibility symlinks, and the global source-of-truth relationship above. Inspect `scripts/sync-from-global.sh` and its dry-run output before any requested sync; `--apply` and `--all` are not routine validation. Do not install/enable skills, change global configuration, or invoke providers/cloud resources as an incidental catalog check.
- Start with `git status --short`, preserve unrelated edits, and complete authorized local work through focused checks and repair. Make ordinary reversible choices directly; report exact missing tool, input, or authorization blockers and continue independent work. For instruction-only edits, inspect links/paths and run `git diff --check`. Close with changed paths, actual checks/results, and remaining limitations.
