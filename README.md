# Claude Skills Collection

A collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex](https://openai.com/index/introducing-codex/) that extend agent capabilities with specialized knowledge and workflows.

## About

Here are some skills I've found useful for various projects I've been building. Would love feedback if anyone else finds them useful—have at it! If you're interested in some of my writings on AI and software development, follow me at [CDD.dev](https://cdd.dev).

## Available Skills

Skills are located in the `skills/` directory.

### Development & Testing

#### [`agent-browser`](./skills/agent-browser)
> Headless browser automation using [agent-browser CLI](https://github.com/vercel-labs/agent-browser) with element refs optimized for AI agents

- `Scrape a product catalog with accessibility trees instead of CSS selectors`
- `Automate a multi-step checkout form submission`
- `Run parallel browser sessions to test race conditions in a web app`

#### [`agent-engineering`](./skills/agent-engineering)
> Battle-tested engineering principles for AI coding agents — plan-first workflow, subagent delegation, self-improvement loops, and verification gates

- `Set up a plan-first coding workflow that prevents agents from writing code before the design is approved`
- `Create a self-improvement loop that benchmarks agent performance and iterates on prompts`
- `Build a verification gate that runs tests before any commit is accepted`

#### [`babysit-pr`](./skills/babysit-pr)
> Create, monitor, and shepherd a GitHub pull request through CI, review, merge, and best-effort deployment validation

- `Open a PR that respects the repo's PR template and required reviewer assignments`
- `Watch CI after each push and summarize failures with fix suggestions`
- `Handle review comments from Greptile and re-request review after fixes are pushed`

#### [`bird-fast`](./skills/bird-fast)
> Interact with X/Twitter from the terminal using [bird CLI](https://github.com/steipete/bird) with browser session authentication

- `Post a thread announcing a new open-source release from a script`
- `Search for mentions of a product and summarize sentiment`
- `Schedule daily tweets from a content queue`

#### [`ceo-review`](./skills/ceo-review)
> Review documents and proposals through a CEO lens — technical depth, data-driven decisions, and long-term strategic vision

- `Review a product spec for whether it aligns with the 3-year platform vision`
- `Critique an engineering proposal on ROI and competitive positioning`
- `Evaluate a go-to-market plan for defensibility and market timing`

#### [`ck-review`](./skills/ck-review)
> Review documents and proposals through the lens of a senior principal engineer — clarity, pragmatism, and shipping velocity

- `Review an architecture decision record for over-engineering and hidden complexity`
- `Critique a technical spec for ambiguous requirements that will block implementation`
- `Evaluate a proposed API design for consistency with existing conventions`

#### [`codex-advisor`](./skills/codex-advisor)
> Get second opinions from [OpenAI Codex CLI](https://github.com/openai/codex) for plan reviews, code reviews, and hard problems

- `Get a second opinion on an implementation plan before starting a large refactor`
- `Validate security assumptions in a cryptographic module`
- `Unblock a tricky bug you've been stuck on for 30+ minutes`

#### [`coreml-optimizer`](./skills/coreml-optimizer)
> Optimize [CoreML](https://developer.apple.com/documentation/coreml) models for iOS and macOS deployment with quantization, palettization, pruning, and Neural Engine targeting

- `Optimize a CoreML model for iPhone 15 Pro Neural Engine with 4-bit palettization`
- `Profile inference latency with Instruments and identify Neural Engine fallbacks`
- `Debug accuracy degradation after applying 8-bit quantization to a vision model`

#### [`cto-review`](./skills/cto-review)
> Review through a CTO lens — platform thinking, mobile-first craft, and iterative execution

- `Review a microservices architecture proposal for platform leverage and team scalability`
- `Critique a mobile app design for offline-first patterns and battery impact`
- `Evaluate a technical roadmap for sequencing risk and iterative milestones`

#### [`github-actions-templates`](./skills/github-actions-templates)
> Create production-ready GitHub Actions workflows for automated testing, building, and deploying

- `Create a CI/CD pipeline for a monorepo with Nx that only re-tests affected packages`
- `Set up a matrix build for a cross-platform Electron app on macOS, Windows, and Linux`
- `Build a deploy workflow with blue/green environment promotion and rollback`

#### [`ios-app-tester`](./skills/ios-app-tester)
> Test iOS apps using [AXe CLI](https://github.com/AXe-app/axe-cli) for accessibility auditing, UI automation, and simulator control

- `Automate a complete onboarding flow test in the iOS Simulator using accessibility identifiers`
- `Audit an app for VoiceOver label gaps and generate a remediation report`
- `Record a test execution video for a critical user journey to attach to a bug report`

#### [`macos-apps`](./skills/macos-apps)
> Build professional native macOS apps in Swift with SwiftUI and AppKit, CLI-only without Xcode

- `Build a native macOS menu bar app with SwiftUI and a persistent popover`
- `Integrate an AppKit NSTableView into a SwiftUI view for complex data display`
- `Set up a Swift Package Manager project with unit tests and a release build pipeline`

#### [`mcp-tester`](./skills/mcp-tester)
> Test and evaluate MCP server tools in the current session — auditing, validation, and test case generation

- `Audit all tools exposed by an MCP server for schema correctness and edge case handling`
- `Generate a comprehensive test suite for a new MCP server before shipping it`
- `Validate that an MCP server returns structured errors rather than stack traces for bad inputs`

#### [`systematic-debugging`](./skills/systematic-debugging)
> Systematic approach to debugging bugs, test failures, and unexpected behavior before proposing fixes

- `Reproduce a flaky test failure deterministically before touching any code`
- `Isolate whether a performance regression is in the database layer or application code`
- `Trace a production 500 error back to its root cause using logs and minimal reproduction`


### Visual & Design

#### [`ascii-pixel-art`](./skills/ascii-pixel-art)
> Transform images into animated ASCII art with subject detection, blurred backgrounds, and cinematic effects (pulse, shine, flicker, hover)

- `Convert a portrait photo into an animated ASCII art piece with phosphor glow`
- `Generate a retro cyberpunk visualization of a city skyline with scanline effects`
- `Create an interactive web art piece with hover-triggered ASCII animation`

#### [`evangelion-design`](./skills/evangelion-design)
> Evangelion-inspired NERV-like command-center interfaces with sharp geometry, tactical typography, and danger-first palettes

- `Build a real-time monitoring dashboard styled after NERV's command center with warning-red accents`
- `Design a terminal UI with sharp hexagonal geometry and alert-state color progressions`
- `Create a login screen with tactical HUD typography and animated scan-line overlays`

#### [`gemini-image-generator`](./skills/gemini-image-generator)
> Generate images using [Google Gemini API](https://ai.google.dev/) for text-to-image, editing, and multi-image reference

- `Generate a set of consistent app icons in a flat design style from a text brief`
- `Create marketing banner variants for A/B testing with different color schemes`
- `Produce game sprite sheets for a 2D platformer based on character descriptions`

#### [`gemini-visual`](./skills/gemini-visual)
> Front-end development assistant powered by [Google Gemini](https://ai.google.dev/) for UI analysis, design comparison, and screenshot-to-code

- `Convert a Figma screenshot into production-ready HTML/CSS with accurate spacing and typography`
- `Compare before/after design mockups and identify all layout regressions`
- `Extract a full color palette and typography scale from a brand screenshot`

#### [`imagegen`](./skills/imagegen)
> Generate and edit images via the OpenAI Image API with a bundled CLI

- `Generate product photography variants on white backgrounds for an e-commerce listing`
- `Inpaint a person out of a stock photo and replace with a branded background`
- `Batch-generate 10 social media card variants from a template description`

#### [`nano-banana`](./skills/nano-banana)
> Generate and edit AI images using Google's Gemini 3 Pro Image model via MCP

- `Create an illustration for a blog post from a detailed text description`
- `Edit a product photo to change the background to an outdoor setting`
- `Generate a logo concept from a brand brief with multiple style variations`

#### [`practical-typography`](./skills/practical-typography)
> Professional typography guidance based on Matthew Butterick's Practical Typography

- `Audit a marketing landing page for line-length, leading, and font-pairing violations`
- `Choose a type system for a long-form reading app that maximizes legibility`
- `Fix a PDF template that uses body text for headings and has inconsistent spacing`

#### [`shadertoy`](./skills/shadertoy)
> GLSL fragment shaders and procedural graphics for Shadertoy and WebGL

- `Write a raymarched SDF scene with ambient occlusion and soft shadows in GLSL`
- `Implement a procedural noise-based animated background for a website hero section`
- `Port a Shadertoy effect to a Three.js ShaderMaterial for a WebGL project`

#### [`skimmable`](./skills/skimmable)
> Enforce code readability and state minimisation before PRs — reduce arguments, remove optionality, and make diffs shorter

- `Refactor a function with 8 parameters into a well-named options object before opening a PR`
- `Remove optional state flags that have been defaulting to the same value for 6 months`
- `Shrink a 400-line diff by extracting pure helper functions into a separate module`

#### [`tui-designer`](./skills/tui-designer)
> Design and implement retro/cyberpunk/hacker-style terminal UIs with CRT effects, neon glow, and scanlines

- `Build a terminal-aesthetic dashboard in React with Tuimorphic including CRT scanline and phosphor glow effects`
- `Implement a hacker-style progress screen in SwiftUI using Metal shaders for real-time noise`
- `Design a cyberpunk color palette and typography system for a CLI tool`

#### [`ui-design`](./skills/ui-design)
> Opinionated constraints for building better interfaces — Tailwind, motion/react, Radix/Base UI, and accessibility

- `Build an accessible modal dialog with Radix UI and Tailwind that traps focus and announces to screen readers`
- `Add enter/exit animations to a sidebar nav using Framer Motion without layout jank`
- `Audit a form for WCAG 2.1 AA compliance and generate a fix list`


### Marketing & Communications

#### [`app-marketing-copy`](./skills/app-marketing-copy)
> App Store/Google Play listings, ASO keywords, taglines, screenshot captions, ad copy, landing page copy, and email campaigns

- `Write a 4000-character App Store description for a productivity app with keyword-optimized headers`
- `Generate 10 screenshot caption variants for A/B testing the onboarding flow screens`
- `Craft a launch email sequence (3 emails) for a new iOS app release`

#### [`content-trend-researcher`](./skills/content-trend-researcher)
> Analyze trends across Google Analytics, Trends, Substack, Medium, Reddit, LinkedIn, X, and more for data-driven content strategy

- `Research rising search trends in the "developer tools" niche to plan a quarter's content calendar`
- `Analyze competitor Substack newsletters for topics that drive high engagement`
- `Generate article outlines ranked by search intent and estimated traffic potential`

#### [`direct-mail-strategist`](./skills/direct-mail-strategist)
> Expert direct mail marketing strategist for copywriting, design, and measurement

- `Write a 6×9 postcard mailer for a SaaS product targeting SMB owners with a 30-day trial offer`
- `Design a measurement plan with holdout groups for a 50,000-piece mailing`
- `Critique a draft letter for response rate optimization using proven direct mail frameworks`

#### [`freshdesk-api`](./skills/freshdesk-api)
> Freshdesk helpdesk API for building integrations, managing tickets, contacts, and automating support workflows

- `Build a webhook integration that auto-creates Freshdesk tickets from Stripe payment failure events`
- `Write a script to bulk-close all tickets older than 90 days with a resolved status`
- `Create a dashboard that pulls open ticket counts by product area via the API`

#### [`poke-assistant`](./skills/poke-assistant)
> Send messages and notifications to [Poke](https://poke.com) via webhook API

- `Notify yourself when a 2-hour model training job completes on a remote server`
- `Send an alert when a production health check fails with a link to the incident dashboard`
- `Deliver a daily build summary with pass/fail counts and a link to the CI report`

#### [`poplar-direct-mail`](./skills/poplar-direct-mail)
> Design and send programmatic direct mail using [Poplar's](https://heypoplar.com) HTML templates and API

- `Build a triggered postcard campaign that mails to users 3 days after they abandon a shopping cart`
- `Create a personalized HTML letter template with dynamic first-name and offer fields`
- `Integrate Poplar's API into a CRM workflow to send win-back mailers to churned customers`

#### [`seo-optimizer`](./skills/seo-optimizer)
> Analyze HTML/CSS websites for SEO optimization and implement best practices

- `Audit a marketing site for missing meta descriptions, duplicate title tags, and broken canonical URLs`
- `Add structured data (JSON-LD) for a recipe blog to enable rich results in Google Search`
- `Generate a sitemap.xml and robots.txt for a Next.js static site`


### AI & LLM

#### [`autopredict`](./skills/autopredict)
> Polymarket prediction market trading agent framework — scan markets, evaluate edges, backtest strategies, and tune parameters

- `Scan all open Polymarket markets and rank by estimated edge vs. current odds`
- `Backtest a news-momentum strategy against 3 months of resolved markets`
- `Tune confidence threshold parameters to maximize Sharpe ratio on historical trades`

#### [`hyperagent`](./skills/hyperagent)
> Self-referential self-improving agent loop — meta-agent modifies task-agent code to optimize any measurable target (based on Facebook Research Hyperagents paper)

- `Set up a hyperagent loop that iteratively improves a code generation agent's pass@1 score on HumanEval`
- `Run a self-improving prompt optimizer that rewrites its own system prompt based on eval feedback`
- `Build a meta-agent that tunes a classification pipeline to minimize false positives on a labeled dataset`

#### [`llm-advisor`](./skills/llm-advisor)
> Consult other LLMs (GPT-5.2, GPT-5, Gemini 3) for second opinions on complex problems

- `Get GPT-5 and Gemini's independent assessments of a distributed systems design before committing to it`
- `Compare how three frontier models approach a tricky regex edge case`
- `Use a cross-model vote to decide between two competing database schema designs`

#### [`llm-evaluation`](./skills/llm-evaluation)
> Implement comprehensive evaluation strategies for LLM applications using automated metrics, human feedback, and benchmarking

- `Build an automated eval harness for a RAG pipeline using RAGAS metrics (faithfulness, relevance, context recall)`
- `Set up a human preference labeling workflow for comparing two prompt variants at scale`
- `Create a regression benchmark that alerts when a model update degrades performance on golden test cases`

#### [`mcp-builder`](./skills/mcp-builder)
> Guide for creating high-quality MCP servers in Python (FastMCP) or Node/TypeScript

- `Build a FastMCP server that wraps the Stripe API with typed tool schemas and proper error handling`
- `Create a TypeScript MCP server that exposes a PostgreSQL database as queryable tools`
- `Design a multi-tool MCP server for a SaaS product's internal APIs with auth middleware`

#### [`paperclip`](./skills/paperclip)
> Interact with Paperclip control plane API for task management, agent coordination, and goal tracking

- `Create and assign tasks to a fleet of specialized agents via the Paperclip API`
- `Query goal completion status across multiple running agent sessions`
- `Coordinate a multi-agent workflow where downstream agents are triggered by upstream task completions`

#### [`prompt-factory`](./skills/prompt-factory)
> Generate production-ready mega-prompts across 15 professional domains with quality validation

- `Generate a system prompt for a customer support agent with escalation rules, tone guidelines, and refusal policies`
- `Create a code review prompt tuned for a TypeScript/React codebase with team-specific conventions`
- `Produce XML-formatted prompts optimized for Claude with chain-of-thought and output schema`


### Security

#### [`blockchain-auditor`](./skills/blockchain-auditor)
> Security audit smart contracts for exploitable vulnerabilities from an unprivileged context

- `Audit a Solidity DEX contract for reentrancy vulnerabilities and flash loan attack surfaces`
- `Analyze an ERC-20 token contract's bytecode for hidden mint/burn backdoors`
- `Generate a PoC exploit for an integer overflow in an AMM pricing function and test it on a local fork`

#### [`security-best-practices`](./skills/security-best-practices)
> Language and framework-specific security reviews for Python, JavaScript/TypeScript, and Go

- `Review a Python FastAPI service for SQL injection, SSRF, and insecure deserialization vulnerabilities`
- `Audit a Node.js Express app for prototype pollution and path traversal issues`
- `Generate a secure-by-default configuration checklist for a new Go microservice`

#### [`security-threat-model`](./skills/security-threat-model)
> Repository-grounded threat modeling with trust boundaries, assets, attacker capabilities, and mitigations

- `Generate a STRIDE threat model for a multi-tenant SaaS API with enumerated abuse paths and mitigations`
- `Document trust boundaries for a mobile app that handles PII and payment data`
- `Write a threat model document for an OAuth 2.0 integration covering token theft and PKCE bypass scenarios`


### Infrastructure

#### [`cloudflare-manager`](./skills/cloudflare-manager)
> Comprehensive Cloudflare account management for Workers, KV, R2, Pages, DNS, and Routes

- `Deploy a Cloudflare Worker with KV storage for edge-side session caching`
- `Configure DNS records and route rules for a multi-origin application behind Cloudflare`
- `Set up an R2 bucket with a Worker proxy for private asset serving with signed URL support`

#### [`google`](./skills/google)
> Google Workspace assistant via gog CLI — Gmail, Calendar, Drive, Sheets, Tasks, and Contacts

- `Draft and send a Gmail message with an attachment pulled from Google Drive`
- `Create a recurring Google Calendar event for a weekly team standup with video link`
- `Update a Google Sheet with the latest data from a CSV export and share it with a team`

#### [`markdown-fetch`](./skills/markdown-fetch)
> Fetch web content as clean Markdown via markdown.new — 80% fewer tokens than raw HTML

- `Fetch the Stripe API documentation for webhook events as clean Markdown for analysis`
- `Convert a competitor's pricing page to Markdown to compare tier structures`
- `Retrieve a GitHub README as Markdown to summarize a library's features`

#### [`subway-info`](./skills/subway-info)
> Real-time NYC subway information via [subwayinfo.nyc](https://subwayinfo.nyc) REST API

- `Check real-time arrival times for the A train at West 4th Street`
- `Get current service alerts for the L line before commuting`
- `Find the nearest station to a given address and show live departures`


### Graphics & 3D

#### [`gsplat-optimizer`](./skills/gsplat-optimizer)
> Optimize 3D Gaussian Splat scenes for real-time rendering on iOS, macOS, and visionOS using Metal

- `Analyze a 2M-splat `.ply` file and generate a pruning plan targeting 60fps on iPhone 15`
- `Design a LOD scheme for a visionOS experience that switches between detail levels based on distance`
- `Benchmark a Gaussian splat scene with Instruments and identify Metal shader bottlenecks`


### Media & Video

#### [`video-editor`](./skills/video-editor)
> Expert guidance for video editing with [ffmpeg](https://ffmpeg.org/), encoding best practices, and quality optimization

- `Transcode a 4K ProRes file to H.265 with optimal CRF settings for streaming delivery`
- `Hardsub an SRT subtitle file onto an MP4 while preserving HDR metadata`
- `Batch-convert a folder of MKV files to MP4 with AAC audio for web compatibility`


### Web3 & Blockchain

#### [`opensea-api`](./skills/opensea-api)
> Interact with [OpenSea's](https://opensea.io) NFT marketplace API for metadata, listings, and events

- `Fetch all NFTs owned by a wallet address with their current floor price estimates`
- `Track real-time sales events for a collection to alert on significant trades`
- `Pull collection stats (volume, floor, holders) for a competitive market analysis report`


### Game Development

#### [`playdate-dev`](./skills/playdate-dev)
> Build [Playdate](https://play.date) games in Lua with the Playdate SDK, including game loop, sprites, graphics, input (crank, buttons, accelerometer), and simulator workflow

- `Build a Playdate puzzle game where the crank controls a rotating mechanism to solve each level`
- `Implement a sprite-based platformer with parallax scrolling on the 1-bit display`
- `Set up a pdxinfo manifest and Simulator build pipeline for submitting to the Catalog`


### Research & Analysis

#### [`autoresearch`](./skills/autoresearch)
> Run rigorous autonomous experiment loops with explicit hypotheses, repeated trials, structured logs, and local HTML reports

- `Run 20 iterations of a prompt variant test with structured win/loss logging and a final HTML report`
- `Benchmark two embedding models on a retrieval task with statistical significance testing`
- `Iterate on a hyperparameter sweep for a classification pipeline with keep/discard decisions per run`

#### [`qmd`](./skills/qmd)
> Local hybrid search for markdown notes and docs

- `Search a local Obsidian vault for notes related to "authentication patterns" using semantic + keyword hybrid search`
- `Find all notes that mention a specific project name across a large document collection`
- `Retrieve the most relevant design decisions from a markdown wiki for a given technical question`

#### [`scientific-critical-thinking`](./skills/scientific-critical-thinking)
> Evaluate research rigor including methodology, experimental design, statistical validity, and biases

- `Apply GRADE criteria to assess the evidence quality of a clinical study before sharing its findings`
- `Identify p-hacking and HARKing in a published machine learning paper`
- `Critique the experimental design of an A/B test report for confounds and underpowering`


### Self-Improvement & Optimization

#### [`continuous-learning`](./skills/continuous-learning)
> Auto-monitors interactions to identify learning opportunities and create new skills when patterns repeat

- `Detect recurring database migration patterns across sessions and auto-generate a migration skill`
- `Surface a gap in agent capabilities after three failed attempts at the same task type`
- `Propose and scaffold a new skill file when a workflow has been manually repeated 3+ times`


### Planning & Process

#### [`brainstorming`](./skills/brainstorming)
> Structured exploration of user intent, requirements, and design before implementation

- `Explore 5 alternative architectures for a feature before picking one to implement`
- `Scope a vague "add notifications" request into specific user stories and acceptance criteria`
- `Map out edge cases and failure modes for a payment flow before writing a line of code`

#### [`executing-plans`](./skills/executing-plans)
> Execute written implementation plans in separate sessions with review checkpoints

- `Run a 12-step database migration plan with a checkpoint after each destructive operation`
- `Execute a feature rollout plan across three services with rollback gates between each deployment`
- `Implement a refactoring plan that touches 20 files with progress tracking and diff review at each checkpoint`

#### [`writing-plans`](./skills/writing-plans)
> Create implementation plans from specs or requirements before touching code

- `Turn a 2-page product spec into a phased implementation plan with clear task dependencies and time estimates`
- `Create an architecture plan for a new microservice that sequences schema, API, and client work`
- `Decompose a "migrate from REST to GraphQL" initiative into safe, reviewable milestones`


### Meta & Skill Management

#### [`skill-finder`](./skills/skill-finder)
> Proactively discover, install, and create skills from the [claude-plugins.dev](https://claude-plugins.dev) registry

- `Install the right skill for an unfamiliar domain on-demand using a "matrix kung-fu" style request`
- `Discover and compare three candidate skills for a task before selecting the best fit`
- `Create a custom skill when no existing registry match covers a recurring workflow`


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
