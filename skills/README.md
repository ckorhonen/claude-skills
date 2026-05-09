# Skills

This directory is the canonical skill catalog for this repository. Each
subdirectory should contain a `SKILL.md` entrypoint plus any supporting scripts,
references, assets, or examples needed by that skill.

When adding, removing, or renaming a skill:

- keep the change scoped to the relevant `skills/<skill-name>/` folder;
- update the root `README.md` catalog in the same pass;
- preserve existing hook behavior documented in `AGENTS.md`;
- validate with any scripts provided by the touched skill.

The repo-local `.agents/skills` path points here so Codex, Claude, and other
agents all read the same skill source.
