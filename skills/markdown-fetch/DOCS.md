# Markdown Fetch Skill

Efficiently fetch web content as clean Markdown using the markdown.new service.

## Features

- **80% fewer tokens** than raw HTML
- **5x more content** fits in context window
- **No external dependencies** except jq
- **Three-tier conversion** (Markdown-first, AI fallback, browser rendering)
- Handles JS-heavy sites with browser rendering
- Returns clean Markdown with metadata

## Installation

```bash
# Install the skill (assuming you have the .skill file)
openclaw skills install markdown-fetch.skill

# Or manually:
unzip markdown-fetch.skill -d ~/.openclaw/skills/
```

## Usage

The skill provides a `fetch.sh` script for fetching web content:

```bash
# Basic usage
~/.openclaw/skills/markdown-fetch/scripts/fetch.sh "https://example.com"

# Use browser rendering for JS-heavy sites  
~/.openclaw/skills/markdown-fetch/scripts/fetch.sh "https://example.com" --method browser

# Save to file
~/.openclaw/skills/markdown-fetch/scripts/fetch.sh "https://example.com" --output article.md

# Retain images
~/.openclaw/skills/markdown-fetch/scripts/fetch.sh "https://example.com" --retain-images
```

## Requirements

- `jq` - JSON processor
  ```bash
  brew install jq
  ```

## How It Works

The skill wraps the markdown.new service which:

1. Tries Markdown-first (Accept: text/markdown header)
2. Falls back to Cloudflare Workers AI conversion
3. Falls back to browser rendering for JS-heavy content

## Conversion Methods

- **auto** (default) - Smart fallback between methods
- **ai** - Cloudflare Workers AI conversion
- **browser** - Full browser rendering for dynamic content

## Output Format

```markdown
---
title: Page Title
url: https://example.com
method: Cloudflare Browser Rendering
duration_ms: 1068
fetched_at: 2026-02-15T01:03:42Z
---

# Page content as Markdown...
```

## Examples

```bash
# Fetch a blog post
./scripts/fetch.sh "https://blog.example.com/article" --output article.md

# Fetch JS-heavy content with browser rendering
./scripts/fetch.sh "https://app.example.com" --method browser

# Quick extraction to stdout
./scripts/fetch.sh "https://example.com" | grep -A 10 "^#"
```

## Use Cases

- Extracting articles, documentation, or blog posts
- Building RAG pipelines with web content  
- Summarizing web pages
- Converting sites to Markdown format
- Preparing training data for LLMs

## Why This Matters

Traditional HTML parsing wastes tokens:
- **HTML**: `<h2 class="section-title" id="about">About Us</h2>` = 12-15 tokens
- **Markdown**: `## About Us` = 3 tokens

A typical blog post: 16,180 tokens (HTML) → 3,150 tokens (Markdown) = **80% reduction**

## Credits

Built on top of the [markdown.new](https://markdown.new/) service by [growthmarketing.ai](https://growthmarketing.ai)