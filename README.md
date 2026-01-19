# Claude Skills Collection

A collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex](https://openai.com/index/introducing-codex/) that extend agent capabilities with specialized knowledge and workflows.

## About

Here are some skills I've found useful for various projects I've been building. Would love feedback if anyone else finds them useful—have at it! If you're interested in some of my writings on AI and software development, follow me at [CDD.dev](https://cdd.dev).

## Available Skills

Skills are located in the `skills/` directory.

### Development & Testing

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [agent-browser](./skills/agent-browser) | Headless browser automation using [agent-browser CLI](https://github.com/vercel-labs/agent-browser) with element refs optimized for AI agents | Web scraping with accessibility trees; form automation and submission; browser testing; screenshot capture; multi-session parallel workflows |
| [bird-fast](./skills/bird-fast) | Interact with X/Twitter from the terminal using [bird CLI](https://github.com/steipete/bird) with browser session authentication | Posting tweets from scripts; reading and analyzing tweet threads; searching for mentions; automating social media workflows; testing Twitter integrations |
| [codex-advisor](./skills/codex-advisor) | Get second opinions from [OpenAI Codex CLI](https://github.com/openai/codex) for plan reviews, code reviews, and hard problems | Reviewing implementation plans before starting work; code review for security-sensitive changes; debugging problems you've been stuck on for 30+ minutes; validating assumptions about unfamiliar codebases |
| [coreml-optimizer](./skills/coreml-optimizer) | Optimize [CoreML](https://developer.apple.com/documentation/coreml) models for iOS and macOS deployment with quantization, palettization, pruning, and Neural Engine targeting | Converting PyTorch/TensorFlow models to CoreML; optimizing model size and inference latency; debugging Neural Engine issues; profiling with Instruments; troubleshooting accuracy degradation after compression |
| [ios-app-tester](./skills/ios-app-tester) | Test iOS apps using [AXe CLI](https://github.com/AXe-app/axe-cli) for accessibility auditing, UI automation, and simulator control | Automating iOS Simulator UI tests; auditing accessibility labels for VoiceOver; recording test execution videos; scripting repeatable QA scenarios; CI/CD pipeline integration |

### Visual & Design

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [gemini-visual](./skills/gemini-visual) | Front-end development assistant powered by [Google Gemini](https://ai.google.dev/) for UI analysis, design comparison, and screenshot-to-code | Analyzing screenshots for layout issues and accessibility; comparing before/after design mockups; extracting color palettes from images; converting screenshots to HTML/CSS; generating designs from text briefs |
| [gemini-image-generator](./skills/gemini-image-generator) | Generate images using [Google Gemini API](https://ai.google.dev/) for text-to-image, editing, and multi-image reference | Generating app icons and logos; creating marketing banners and social graphics; prototyping UI with AI-generated placeholders; creating game sprites and 2D assets; style transfer from reference images |
| [tui-designer](./skills/tui-designer) | Design and implement retro/cyberpunk/hacker-style terminal UIs with CRT effects, neon glow, and scanlines | Building terminal-aesthetic interfaces in React ([Tuimorphic](https://github.com/douglance/tuimorphic)) or SwiftUI (Metal shaders); implementing CRT monitor effects; choosing cyberpunk color palettes; writing terminal-style copy; adding phosphor glow and scanline effects |

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

### Media & Video

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [video-editor](./skills/video-editor) | Expert guidance for video editing with [ffmpeg](https://ffmpeg.org/), encoding best practices, and quality optimization | Encoding/transcoding video files; converting between containers (MKV, MP4); optimizing CRF and preset settings; troubleshooting color space issues; hardsubbing; preparing videos for streaming platforms |

### Web3 & Blockchain

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [opensea-api](./skills/opensea-api) | Interact with [OpenSea's](https://opensea.io) NFT marketplace API for metadata, listings, and events | Fetching NFT metadata and ownership info; getting collection stats and floor prices; tracking sales and transfers; building NFT dashboards; real-time monitoring with Stream API |

### Game Development

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [playdate-dev](./skills/playdate-dev) | Build [Playdate](https://play.date) games in Lua with the Playdate SDK, including game loop, sprites, graphics, input (crank, buttons, accelerometer), and simulator workflow | Creating Playdate games from scratch; implementing crank-based mechanics; optimizing for the 1-bit display; setting up pdxinfo metadata; building and testing in the Simulator |

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

## Project Structure

```
claude-skills/
├── skills/                    # Claude Code skills
│   ├── agent-browser/
│   ├── bird-fast/
│   ├── codex-advisor/
│   ├── coreml-optimizer/
│   ├── direct-mail-strategist/
│   ├── gemini-image-generator/
│   ├── gemini-visual/
│   ├── gsplat-optimizer/
│   ├── ios-app-tester/
│   ├── opensea-api/
│   ├── playdate-dev/
│   ├── poke-assistant/
│   ├── poplar-direct-mail/
│   ├── skill-finder/
│   ├── tui-designer/
│   └── video-editor/
├── agents/                    # Agent configurations
├── commands/                  # Custom commands
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
