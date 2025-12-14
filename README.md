# Claude Skills Collection

A collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex](https://openai.com/index/introducing-codex/) that extend agent capabilities with specialized knowledge and workflows.

## About

Here are some skills I've found useful for various projects I've been building. Would love feedback if anyone else finds them useful—have at it! If you're interested in some of my writings on AI and software development, follow me at [CDD.dev](https://cdd.dev).

## Available Skills

### Development & Testing

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [codex-advisor](./codex-advisor) | Get second opinions from [OpenAI Codex CLI](https://github.com/openai/codex) for plan reviews, code reviews, and hard problems | Reviewing implementation plans before starting work; code review for security-sensitive changes; debugging problems you've been stuck on for 30+ minutes; validating assumptions about unfamiliar codebases |
| [ios-app-tester](./ios-app-tester) | Test iOS apps using [AXe CLI](https://github.com/AXe-app/axe-cli) for accessibility auditing, UI automation, and simulator control | Automating iOS Simulator UI tests; auditing accessibility labels for VoiceOver; recording test execution videos; scripting repeatable QA scenarios; CI/CD pipeline integration |

### Visual & Design

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [gemini-visual](./gemini-visual) | Front-end development assistant powered by [Google Gemini](https://ai.google.dev/) for UI analysis, design comparison, and screenshot-to-code | Analyzing screenshots for layout issues and accessibility; comparing before/after design mockups; extracting color palettes from images; converting screenshots to HTML/CSS; generating designs from text briefs |
| [gemini-image-generator](./gemini-image-generator) | Generate images using [Google Gemini API](https://ai.google.dev/) for text-to-image, editing, and multi-image reference | Generating app icons and logos; creating marketing banners and social graphics; prototyping UI with AI-generated placeholders; creating game sprites and 2D assets; style transfer from reference images |

### Marketing & Communications

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [direct-mail-strategist](./direct-mail-strategist) | Expert direct mail marketing strategist for copywriting, design, and measurement | Planning direct mail campaigns; writing compelling mailer copy; designing high-converting postcards and letters; setting up incremental lift measurement and holdout tests |
| [poplar-direct-mail](./poplar-direct-mail) | Design and send programmatic direct mail using [Poplar's](https://heypoplar.com) HTML templates and API | Creating HTML templates for postcards and letters; building triggered/programmatic mail campaigns; integrating direct mail into marketing automation; sending personalized transactional mail |
| [poke-assistant](./poke-assistant) | Send messages and notifications to [Poke](https://poke.com) via webhook API | Notifying yourself when long-running tasks complete; sending error alerts that need attention; providing status updates on builds, tests, or deployments; sending reminders or daily summaries |

### Web3 & Blockchain

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [opensea-api](./opensea-api) | Interact with [OpenSea's](https://opensea.io) NFT marketplace API for metadata, listings, and events | Fetching NFT metadata and ownership info; getting collection stats and floor prices; tracking sales and transfers; building NFT dashboards; real-time monitoring with Stream API |

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
