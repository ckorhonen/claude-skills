# Claude Skills Collection

A collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex](https://openai.com/index/introducing-codex/) that extend agent capabilities with specialized knowledge and workflows.

## About

Here are some skills I've found useful for various projects I've been building. Would love feedback if anyone else finds them useful—have at it! If you're interested in some of my writings on AI and software development, follow me at [CDD.dev](https://cdd.dev).

## Self-Learning Memory System

This repository includes a **self-learning memory subsystem** that allows Claude Code to accumulate and retrieve learnings across sessions using pgvector for hybrid search.

### Quick Start

```bash
# 1. Start the database
docker compose up -d

# 2. Install Python dependencies
pip install -e .

# 3. Set your OpenAI API key (for embeddings)
export OPENAI_API_KEY=sk-...

# 4. Copy hooks to your project or use this repo directly
cp -r hooks/ /path/to/project/.claude/hooks/
cp .claude/settings.local.json /path/to/project/.claude/
```

### Memory Commands

- `!save-learning` - Save the pending learning to the database
- `!discard-learning` - Discard the pending learning
- `!pending-learning` - Show the current pending learning
- `!learnings <query>` - Search for learnings matching the query

See [CLAUDE.md](./CLAUDE.md) for detailed usage instructions.

---

## Available Skills

Skills are located in the `skills/` directory.

### Development & Testing

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [codex-advisor](./skills/codex-advisor) | Get second opinions from [OpenAI Codex CLI](https://github.com/openai/codex) for plan reviews, code reviews, and hard problems | Reviewing implementation plans before starting work; code review for security-sensitive changes; debugging problems you've been stuck on for 30+ minutes; validating assumptions about unfamiliar codebases |
| [ios-app-tester](./skills/ios-app-tester) | Test iOS apps using [AXe CLI](https://github.com/AXe-app/axe-cli) for accessibility auditing, UI automation, and simulator control | Automating iOS Simulator UI tests; auditing accessibility labels for VoiceOver; recording test execution videos; scripting repeatable QA scenarios; CI/CD pipeline integration |
| [coreml-optimizer](./skills/coreml-optimizer) | Optimize [CoreML](https://developer.apple.com/documentation/coreml) models for iOS and macOS deployment with quantization, palettization, pruning, and Neural Engine targeting | Converting PyTorch/TensorFlow models to CoreML; optimizing model size and inference latency; debugging Neural Engine issues; profiling with Instruments; troubleshooting accuracy degradation after compression |

### Visual & Design

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [gemini-visual](./skills/gemini-visual) | Front-end development assistant powered by [Google Gemini](https://ai.google.dev/) for UI analysis, design comparison, and screenshot-to-code | Analyzing screenshots for layout issues and accessibility; comparing before/after design mockups; extracting color palettes from images; converting screenshots to HTML/CSS; generating designs from text briefs |
| [gemini-image-generator](./skills/gemini-image-generator) | Generate images using [Google Gemini API](https://ai.google.dev/) for text-to-image, editing, and multi-image reference | Generating app icons and logos; creating marketing banners and social graphics; prototyping UI with AI-generated placeholders; creating game sprites and 2D assets; style transfer from reference images |

### Marketing & Communications

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [direct-mail-strategist](./skills/direct-mail-strategist) | Expert direct mail marketing strategist for copywriting, design, and measurement | Planning direct mail campaigns; writing compelling mailer copy; designing high-converting postcards and letters; setting up incremental lift measurement and holdout tests |
| [poplar-direct-mail](./skills/poplar-direct-mail) | Design and send programmatic direct mail using [Poplar's](https://heypoplar.com) HTML templates and API | Creating HTML templates for postcards and letters; building triggered/programmatic mail campaigns; integrating direct mail into marketing automation; sending personalized transactional mail |
| [poke-assistant](./skills/poke-assistant) | Send messages and notifications to [Poke](https://poke.com) via webhook API | Notifying yourself when long-running tasks complete; sending error alerts that need attention; providing status updates on builds, tests, or deployments; sending reminders or daily summaries |

### Graphics & 3D

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [gsplat-optimizer](./skills/gsplat-optimizer) | Optimize 3D Gaussian Splat scenes for real-time rendering on iOS, macOS, and visionOS using Metal | Analyzing `.ply`/`.splat` files for device targets; generating pruning plans (opacity/size thresholds); LOD scheme design (LODGE, FLoD); compression recommendations (SOGS, CodecGS); Metal profiling checklists |

### Web3 & Blockchain

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [opensea-api](./skills/opensea-api) | Interact with [OpenSea's](https://opensea.io) NFT marketplace API for metadata, listings, and events | Fetching NFT metadata and ownership info; getting collection stats and floor prices; tracking sales and transfers; building NFT dashboards; real-time monitoring with Stream API |

### Meta & Skill Management

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [skill-finder](./skills/skill-finder) | Proactively discover, install, and create skills from the [claude-plugins.dev](https://claude-plugins.dev) registry | Matrix-style "I want to know kung-fu" requests; auto-discovering skills when specialized domains are encountered; creating custom skills when no match exists; expanding Claude's capabilities on-demand |

## Installation

### Skills

Copy the skill folder to the appropriate location:

#### Claude Code

```bash
# Project-level (share with team via version control)
cp -r skills/<skill-name> /path/to/project/.claude/skills/

# User-level (available across all projects)
cp -r skills/<skill-name> ~/.claude/skills/
```

#### Codex

```bash
cp -r skills/<skill-name> ~/.codex/skills/
```

### Memory System Hooks

To use the self-learning memory system in another project:

```bash
# Copy hooks and configuration
cp -r hooks/ /path/to/project/hooks/
cp .claude/settings.local.json /path/to/project/.claude/

# Or install as a Python package
pip install -e /path/to/this/repo
```

## Project Structure

```
beirut/
├── skills/                    # Claude Code skills
│   ├── codex-advisor/
│   ├── coreml-optimizer/
│   ├── direct-mail-strategist/
│   ├── gemini-image-generator/
│   ├── gemini-visual/
│   ├── gsplat-optimizer/
│   ├── ios-app-tester/
│   ├── opensea-api/
│   ├── poke-assistant/
│   ├── poplar-direct-mail/
│   └── skill-finder/
├── hooks/                     # Memory system hooks
│   ├── session_start.py
│   ├── user_prompt_submit.py
│   ├── stop.py
│   └── pre_tool_use.py
├── agent_memory/              # Python package
│   ├── config.py
│   ├── knowledge.py
│   ├── formatting.py
│   ├── transcript.py
│   └── cli.py
├── scripts/
│   ├── ensure_db.sh
│   └── test_hooks.md
├── .claude/
│   ├── settings.local.json
│   └── learnings/
├── docker-compose.yml
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## Contributing

To add a new skill:

1. Create a new directory in `skills/` with your skill name (use kebab-case)
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
