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
| [babysit-pr](./skills/babysit-pr) | Create, monitor, and shepherd a GitHub pull request through CI, review, merge, and best-effort deployment validation | Respecting repo PR templates when opening PRs; watching CI after each push; handling review comments and score-based feedback; validating deployment signals after merge |
| [codex-advisor](./skills/codex-advisor) | Get second opinions from [OpenAI Codex CLI](https://github.com/openai/codex) for plan reviews, code reviews, and hard problems | Reviewing implementation plans before starting work; code review for security-sensitive changes; debugging problems you've been stuck on for 30+ minutes; validating assumptions about unfamiliar codebases |
| [coreml-optimizer](./skills/coreml-optimizer) | Optimize [CoreML](https://developer.apple.com/documentation/coreml) models for iOS and macOS deployment with quantization, palettization, pruning, and Neural Engine targeting | Converting PyTorch/TensorFlow models to CoreML; optimizing model size and inference latency; debugging Neural Engine issues; profiling with Instruments; troubleshooting accuracy degradation after compression |
| [ios-app-tester](./skills/ios-app-tester) | Test iOS apps using [AXe CLI](https://github.com/AXe-app/axe-cli) for accessibility auditing, UI automation, and simulator control | Automating iOS Simulator UI tests; auditing accessibility labels for VoiceOver; recording test execution videos; scripting repeatable QA scenarios; CI/CD pipeline integration |
| [macos-apps](./skills/macos-apps) | Build professional native macOS apps in Swift with SwiftUI and AppKit, CLI-only without Xcode | Full app lifecycle from project setup to shipping; SwiftUI views with AppKit integration; debugging and testing; performance optimization |
| [systematic-debugging](./skills/systematic-debugging) | Systematic approach to debugging bugs, test failures, and unexpected behavior before proposing fixes | Root cause analysis; reproducing failures; isolating issues; avoiding shotgun debugging |
| [github-actions-templates](./skills/github-actions-templates) | Create production-ready GitHub Actions workflows for automated testing, building, and deploying | Setting up CI/CD pipelines; automating development workflows; creating reusable workflow templates |

### Visual & Design

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [gemini-visual](./skills/gemini-visual) | Front-end development assistant powered by [Google Gemini](https://ai.google.dev/) for UI analysis, design comparison, and screenshot-to-code | Analyzing screenshots for layout issues and accessibility; comparing before/after design mockups; extracting color palettes from images; converting screenshots to HTML/CSS; generating designs from text briefs |
| [gemini-image-generator](./skills/gemini-image-generator) | Generate images using [Google Gemini API](https://ai.google.dev/) for text-to-image, editing, and multi-image reference | Generating app icons and logos; creating marketing banners and social graphics; prototyping UI with AI-generated placeholders; creating game sprites and 2D assets; style transfer from reference images |
| [nano-banana](./skills/nano-banana) | Generate and edit AI images using Google's Gemini 3 Pro Image model via MCP | Creating images from text prompts; editing and inpainting photos; generating graphics with text rendering; visual content creation |
| [imagegen](./skills/imagegen) | Generate and edit images via the OpenAI Image API with a bundled CLI | Text-to-image generation; inpainting and masking; background removal/replacement; product shots; batch variant generation |
| [tui-designer](./skills/tui-designer) | Design and implement retro/cyberpunk/hacker-style terminal UIs with CRT effects, neon glow, and scanlines | Building terminal-aesthetic interfaces in React ([Tuimorphic](https://github.com/douglance/tuimorphic)) or SwiftUI (Metal shaders); implementing CRT monitor effects; choosing cyberpunk color palettes; writing terminal-style copy; adding phosphor glow and scanline effects |
| [shadertoy](./skills/shadertoy) | GLSL fragment shaders and procedural graphics for Shadertoy and WebGL | Writing .glsl files; implementing visual effects; creating generative art; working with WebGL shader code; Shadertoy conventions |

### Marketing & Communications

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [direct-mail-strategist](./skills/direct-mail-strategist) | Expert direct mail marketing strategist for copywriting, design, and measurement | Planning direct mail campaigns; writing compelling mailer copy; designing high-converting postcards and letters; setting up incremental lift measurement and holdout tests |
| [poplar-direct-mail](./skills/poplar-direct-mail) | Design and send programmatic direct mail using [Poplar's](https://heypoplar.com) HTML templates and API | Creating HTML templates for postcards and letters; building triggered/programmatic mail campaigns; integrating direct mail into marketing automation; sending personalized transactional mail |
| [poke-assistant](./skills/poke-assistant) | Send messages and notifications to [Poke](https://poke.com) via webhook API | Notifying yourself when long-running tasks complete; sending error alerts that need attention; providing status updates on builds, tests, or deployments; sending reminders or daily summaries |
| [content-trend-researcher](./skills/content-trend-researcher) | Analyze trends across Google Analytics, Trends, Substack, Medium, Reddit, LinkedIn, X, and more for data-driven content strategy | Researching trending topics; generating article outlines based on user intent analysis; competitive content analysis |
| [seo-optimizer](./skills/seo-optimizer) | Analyze HTML/CSS websites for SEO optimization and implement best practices | SEO audits; meta tag improvements; schema markup; sitemap generation; search engine optimization |

### AI & LLM

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [llm-evaluation](./skills/llm-evaluation) | Implement comprehensive evaluation strategies for LLM applications using automated metrics, human feedback, and benchmarking | Testing LLM performance; measuring AI application quality; establishing evaluation frameworks |
| [prompt-factory](./skills/prompt-factory) | Generate production-ready mega-prompts across 15 professional domains with quality validation | Creating role-specific prompts; multi-format output (XML/Claude/ChatGPT/Gemini); prompt testing and variations |
| [llm-advisor](./skills/llm-advisor) | Consult other LLMs (GPT-5.2, GPT-5, Gemini 3) for second opinions on complex problems | Getting alternative perspectives on bugs; cross-validating architectural decisions; comparing approaches |
| [mcp-builder](./skills/mcp-builder) | Guide for creating high-quality MCP servers in Python (FastMCP) or Node/TypeScript | Building MCP servers; integrating external APIs; designing well-structured tool interfaces |

### Security

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [blockchain-auditor](./skills/blockchain-auditor) | Security audit smart contracts for exploitable vulnerabilities from an unprivileged context | Analyzing Solidity contracts; reviewing bytecode; testing exploits on forks; vulnerability ranking; PoC exploit generation |
| [security-best-practices](./skills/security-best-practices) | Language and framework-specific security reviews for Python, JavaScript/TypeScript, and Go | Security best practices guidance; secure-by-default coding; security review reports |
| [security-threat-model](./skills/security-threat-model) | Repository-grounded threat modeling with trust boundaries, assets, attacker capabilities, and mitigations | Threat modeling codebases; enumerating abuse paths; AppSec threat modeling; writing threat model docs |

### Infrastructure

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [cloudflare-manager](./skills/cloudflare-manager) | Comprehensive Cloudflare account management for Workers, KV, R2, Pages, DNS, and Routes | Deploying Workers; managing KV/R2 storage; configuring DNS and routing; Pages deployments |

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

### Research & Analysis

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [scientific-critical-thinking](./skills/scientific-critical-thinking) | Evaluate research rigor including methodology, experimental design, statistical validity, and biases | Assessing evidence quality (GRADE, Cochrane ROB); critical analysis of scientific claims; reviewing study methodology |
| [qmd](./skills/qmd) | Local hybrid search for markdown notes and docs | Searching indexed note collections; finding related content; retrieving documents by semantic or keyword match |

### Planning & Process

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [brainstorming](./skills/brainstorming) | Structured exploration of user intent, requirements, and design before implementation | Pre-implementation design exploration; feature scoping; requirement analysis |
| [executing-plans](./skills/executing-plans) | Execute written implementation plans in separate sessions with review checkpoints | Following multi-step plans; checkpoint-based implementation; session-aware execution |
| [writing-plans](./skills/writing-plans) | Create implementation plans from specs or requirements before touching code | Breaking down specs into actionable steps; architecture planning; task decomposition |

### Meta & Skill Management

| Skill | Description | Example Use Cases |
|-------|-------------|-------------------|
| [skill-finder](./skills/skill-finder) | Proactively discover, install, and create skills from the [claude-plugins.dev](https://claude-plugins.dev) registry | Matrix-style "I want to know kung-fu" requests; auto-discovering skills when specialized domains are encountered; creating custom skills when no match exists; expanding Claude's capabilities on-demand |

## Skill Origins & Attribution

Some skills in this collection originate from external projects:

- **Design skills** (adapt, animate, audit, bolder, clarify, colorize, critique, delight, distill, extract, frontend-design, harden, normalize, onboard, optimize, polish, quieter, teach-impeccable, ui-design) — From [Impeccable Design](https://impeccable.design). Systematic, opinionated UI/UX design constraints for building better interfaces with agents. Install the full set from their site.

- **App Store Connect skills** (asc-*) — From [app-store-connect-cli-skills](https://github.com/rudrankriyam/app-store-connect-cli-skills) by Rudrank Riyam. Skills for managing the full iOS/macOS release pipeline via the `asc` CLI.

## Installation

### skills.sh (recommended)

Install any skill with [skills.sh](https://skills.sh):

```bash
# Interactive — browse and select skills to install
npx skills add ckorhonen/claude-skills

# Install a specific skill directly
npx skills add ckorhonen/claude-skills --skill <skill-name>
```

### Manual

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
