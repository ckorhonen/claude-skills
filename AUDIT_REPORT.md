# Anthropic Skills Guide Audit Report

**Date:** 2026-03-28  
**Branch:** audit/anthropic-checklist  
**Total skills audited:** 58 skill directories  

## Checklist Key

| # | Item | Description |
|---|------|-------------|
| 1 | SKILL.md | SKILL.md exists (case-sensitive) |
| 2 | No README | No README.md inside skill folder |
| 3 | name field | Frontmatter has `name` in kebab-case matching folder |
| 4 | description | Frontmatter has `description` with trigger phrases, <1024 chars, no XML tags |
| 5 | No reserved | Name does not contain "claude" or "anthropic" |
| 6 | Folder name | Folder is kebab-case only |
| 7 | Progressive | Body has clear actionable instructions |
| 8 | Scripts help | Scripts in scripts/ have --help (CLI scripts only) |

## Results Table

| Skill | 1 SKILL.md | 2 No README | 3 name | 4 description | 5 No reserved | 6 folder | 7 progressive | 8 scripts --help | Notes |
|-------|-----------|-------------|--------|---------------|----------------|---------|--------------|-----------------|-------|
| agent-browser | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| agent-engineering | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| app-marketing-copy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| ascii-pixel-art | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | test_logic.py is a standalone test runner, no args needed |
| autopredict | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| autoresearch | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | common.py is a library module, not a CLI |
| babysit-pr | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| bird-fast | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| blockchain-auditor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| brainstorming | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| ceo-review | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| ck-review | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| cloudflare-manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | utils.ts is a library module imported by others |
| codex-advisor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| content-trend-researcher | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | Python files at root are library modules, no scripts/ dir |
| continuous-learning | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ **FIXED** | Added --help to continuous-learning-activator.sh |
| coreml-optimizer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| cto-review | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| direct-mail-strategist | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| evangelion-design | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| executing-plans | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| freshdesk-api | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| gemini-image-generator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| gemini-visual | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| github-actions-templates | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| google | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| gsplat-optimizer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| hyperagent | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | common.py is a library module, not a CLI |
| imagegen | ✅ | ✅ | ✅ **FIXED** | ✅ | ✅ | ✅ | ✅ | ✅ | Removed unnecessary quotes from name field |
| ios-app-tester | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| llm-advisor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| llm-evaluation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| macos-apps | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ **FIXED** | n/a | Removed XML section tags; converted to standard Markdown headers |
| markdown-fetch | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| mcp-builder | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | connections.py is a library module, not a CLI |
| mcp-tester | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| nano-banana | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| opensea-api | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| paperclip | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| playdate-dev | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| poke-assistant | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| poplar-direct-mail | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| practical-typography | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| prompt-factory | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| qmd | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| scientific-critical-thinking | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| security-best-practices | ✅ | ✅ | ✅ **FIXED** | ✅ | ✅ | ✅ | ✅ | n/a | Removed unnecessary quotes from name field |
| security-threat-model | ✅ | ✅ | ✅ **FIXED** | ✅ | ✅ | ✅ | ✅ | n/a | Removed unnecessary quotes from name field |
| seo-optimizer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| shadertoy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| skill-finder | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| skimmable | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| subway-info | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| systematic-debugging | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | find-polluter.sh has usage docs |
| tui-designer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| ui-design | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| video-editor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |
| writing-plans | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a | |

**n/a** = no scripts/ directory (item not applicable)

---

## Issues Found & Fixed

### Fixed (4 issues)

| Skill | Issue | Fix Applied |
|-------|-------|-------------|
| `imagegen` | `name: "imagegen"` had unnecessary YAML quotes | Removed quotes → `name: imagegen` |
| `security-best-practices` | `name: "security-best-practices"` had unnecessary YAML quotes | Removed quotes → `name: security-best-practices` |
| `security-threat-model` | `name: "security-threat-model"` had unnecessary YAML quotes | Removed quotes → `name: security-threat-model` |
| `macos-apps` | SKILL.md body used XML-style section tags (`<essential_principles>`, `<intake>`, `<routing>`, etc.) which can cause parsing issues in some tools | Converted all XML section tags to standard Markdown `##` headers |
| `continuous-learning` | `continuous-learning-activator.sh` in scripts/ had no `--help` flag | Added full `--help` / `-h` handler with usage, options, environment, and installation docs |

### No Issues Found

- **README.md files:** None found in any skill directory ✅
- **Reserved names:** No skill uses "claude" or "anthropic" in its name ✅  
- **Folder naming:** All 58 skill folders are valid kebab-case ✅
- **SKILL.md presence:** All 58 skill folders contain SKILL.md ✅
- **Description length:** All descriptions are under 1024 characters (longest: 567 chars in `evangelion-design`) ✅
- **XML in descriptions:** No descriptions contain XML tags ✅
- **Trigger phrases:** All descriptions include usage context and/or trigger phrases ✅
- **name matches folder:** All `name` frontmatter values match their folder names ✅

### Observations (No Action Required)

| Observation | Skills | Assessment |
|-------------|--------|------------|
| Library modules in scripts/ (no --help needed) | `autoresearch/common.py`, `hyperagent/common.py`, `mcp-builder/connections.py`, `cloudflare-manager/utils.ts` | These are imported modules with no `__main__` block. --help not applicable. |
| Test runner script with no args | `ascii-pixel-art/test_logic.py` | Standalone test script, no arguments accepted. --help not applicable. |
| `.skill` zip archives at skills/ root | `evangelion-design.skill`, `markdown-fetch.skill` | Not skill directories — zip bundles. Not subject to audit. |
| `systematic-debugging` has loose .md and .ts files at root | — | These are reference docs, not scripts. Acceptable. |
| `content-trend-researcher` has Python files at root (not in scripts/) | — | Library modules without `if __name__ == '__main__'`. Not CLI tools. |

---

## Summary

**58 skills audited.** **5 issues fixed.** **0 issues requiring manual attention.**

All skills now fully comply with the Anthropic Skills Guide checklist.
