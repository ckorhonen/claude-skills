---
name: codex-advisor
description: Get a second opinion from OpenAI Codex CLI for plan reviews, code reviews, architecture decisions, and hard problems. Use when you need external validation, want to compare approaches, or are stuck on a difficult problem.
---

# Codex Advisor

## Overview

Use OpenAI's Codex CLI as a second-opinion advisor when you need external validation on plans, code reviews, or are stuck on hard problems. Codex runs locally and provides an independent perspective using OpenAI's reasoning models.

## When to Use

- Reviewing implementation plans before starting work
- Code review for complex or security-sensitive changes
- Architecture decisions with significant trade-offs
- Debugging problems where you've been stuck for >30 minutes
- Getting alternative approaches to a solution
- Validating assumptions about unfamiliar codebases

## Prerequisites

- OpenAI API key or ChatGPT Plus/Pro/Business account
- Codex CLI installed

### Installation

```bash
# Via npm
npm install -g @openai/codex

# Or via Homebrew
brew install --cask codex
```

### Authentication

```bash
# Option 1: API key
export OPENAI_API_KEY="your-key"

# Option 2: First run will prompt for ChatGPT login
codex
```

## Default Configuration

All commands use GPT-5.2 with maximum reasoning effort (`xhigh`) for thorough analysis:

```bash
# Base command pattern
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" "your prompt"
```

## Command Reference

### Plan Review

Get feedback on an implementation plan before starting:

```bash
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" "Review this implementation plan. Identify potential issues, missing edge cases, security concerns, or better approaches:

<paste plan here>"
```

For plans involving the current codebase:

```bash
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" --path . "Review this implementation plan in the context of this codebase. Identify potential issues, conflicts with existing patterns, or better approaches:

<paste plan here>"
```

### Code Review

Review code changes for bugs, security issues, and improvements:

```bash
# Review specific file
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" --path . "Review this file for bugs, security vulnerabilities, performance issues, and suggest improvements. Focus on: <specific concerns>"

# Review a diff
git diff | codex -m gpt-5.2 -c model_reasoning_effort="xhigh" "Review this diff for bugs, security issues, and improvements"

# Review staged changes
git diff --staged | codex -m gpt-5.2 -c model_reasoning_effort="xhigh" "Review these changes before commit. Check for bugs, security issues, and adherence to best practices"
```

### Hard Problem Solving

When stuck on a difficult problem:

```bash
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" --path . "I'm stuck on this problem: <description>

What I've tried:
1. <attempt 1>
2. <attempt 2>

Error/behavior I'm seeing: <details>

Suggest solutions or debugging approaches."
```

### Architecture Decisions

Get input on design trade-offs:

```bash
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" --path . "I need to decide between these approaches for <feature>:

Option A: <description>
Option B: <description>

Given this codebase, which approach is better and why? Consider maintainability, performance, and consistency with existing patterns."
```

### Alternative Approaches

When you want a fresh perspective:

```bash
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" --path . "Here's my current approach to <problem>: <description>

What are alternative ways to solve this? What am I missing?"
```

## Workflow Examples

### Pre-Implementation Review

Before implementing a complex feature:

```bash
# 1. Write your plan
# 2. Get Codex review
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" --path . "Review this implementation plan for a user authentication system:

1. Add JWT middleware to Express routes
2. Create /auth/login and /auth/register endpoints
3. Store refresh tokens in Redis
4. Add rate limiting on auth endpoints

Identify missing pieces, security concerns, or better approaches."
```

### Pre-Commit Review

Before committing complex changes:

```bash
# Review staged changes
git diff --staged | codex -m gpt-5.2 -c model_reasoning_effort="xhigh" "Review these changes for a PR. Check for:
- Bugs or logic errors
- Security vulnerabilities
- Performance issues
- Missing error handling
- Test coverage gaps

Provide specific line-by-line feedback."
```

### Debugging Session

When stuck on a bug:

```bash
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" --path . "I have a race condition in my async queue processor.

Symptoms:
- Jobs occasionally process twice
- Happens under high load
- Logs show overlapping job IDs

Relevant files: src/queue/processor.ts, src/queue/worker.ts

Help me identify the cause and fix."
```

## Model Selection

This skill defaults to GPT-5.2 with `xhigh` reasoning for maximum quality. Adjust for different needs:

```bash
# Default: GPT-5.2 with xhigh reasoning (best quality, slower)
codex -m gpt-5.2 -c model_reasoning_effort="xhigh" "Complex review..."

# Faster responses with lower reasoning (for simpler tasks)
codex -m gpt-5.2 -c model_reasoning_effort="medium" "Quick question..."

# Use o3 for alternative perspective
codex -m o3 -c model_reasoning_effort="high" "Architecture question..."
```

### Reasoning Effort Levels

| Level | Use Case |
|-------|----------|
| `minimal` | Quick lookups, simple questions |
| `low` | Basic syntax checks |
| `medium` | Standard code review (faster) |
| `high` | Complex analysis |
| `xhigh` | Deep reasoning, security review, architecture (default) |

## Best Practices

### When to Use Codex Advisor

- Complex changes affecting multiple systems
- Security-sensitive code (auth, crypto, input validation)
- Performance-critical sections
- Unfamiliar codebases or languages
- When you've been stuck for >30 minutes

### When NOT to Use

- Simple, obvious changes (typos, formatting)
- Trivial bug fixes with clear solutions
- When you need to move fast on low-risk changes
- Repetitive tasks where the pattern is established

### Tips for Better Results

1. **Provide context**: Include relevant file paths, error messages, and what you've tried
2. **Be specific**: Ask focused questions rather than "review everything"
3. **Use `--path .`**: Let Codex see your codebase for context-aware advice
4. **Iterate**: Ask follow-up questions to dig deeper
5. **Verify suggestions**: Always validate Codex's recommendations against your codebase

## Security Considerations

- Codex sends code to OpenAI's servers for analysis
- Review your organization's policies before sharing proprietary code
- Avoid sending sensitive credentials, API keys, or PII in code samples
- Use API keys with appropriate rate limits for usage monitoring

## Troubleshooting

### "Command not found"

```bash
# Check installation
which codex

# Reinstall if needed
npm install -g @openai/codex
```

### Authentication errors

```bash
# Re-authenticate
codex --login

# Or set API key
export OPENAI_API_KEY="your-key"
```

### Rate limiting

For heavy usage, use an API key with appropriate tier limits rather than ChatGPT authentication.
