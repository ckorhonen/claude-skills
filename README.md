# Claude Skills Collection

A collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex](https://openai.com/index/introducing-codex/) that extend agent capabilities with specialized knowledge and workflows.

## Available Skills

| Skill | Description |
|-------|-------------|
| [codex-advisor](./codex-advisor) | Get second opinions from OpenAI Codex CLI for plan reviews, code reviews, and hard problems |
| [gemini-image-generator](./gemini-image-generator) | Generate images using Google's Gemini API for text-to-image, editing, and multi-image reference |
| [ios-app-tester](./ios-app-tester) | Test iOS apps using AXe CLI for accessibility auditing, UI automation, and simulator control |

## Installation

Copy the skill folder to the appropriate location:

### Claude Code

```bash
# Project-level (share with team via version control)
cp -r <skill-name> /path/to/project/.claude/skills/

# User-level (available across all projects)
cp -r <skill-name> ~/.claude/skills/
```

### Codex

```bash
cp -r <skill-name> ~/.codex/skills/
```

## Contributing

To add a new skill:

1. Create a new directory with your skill name (use kebab-case)
2. Add a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: your-skill-name
description: Brief description of what the skill does
---

# Skill Title

Your skill documentation here...
```

3. Submit a pull request

## License

MIT License - see [LICENSE](./LICENSE) for details.
