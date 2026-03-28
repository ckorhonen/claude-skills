---
name: llm-advisor
description: "Consult other LLMs (GPT-4.1, o4-mini, Gemini 2.5 Pro, Claude Opus) for second opinions on complex bugs, hard problems, planning, and architecture decisions. Use proactively when stuck for 15+ minutes or facing complex debugging. Use when user says 'ask Gemini/GPT/Claude about X' or 'get a second opinion'."
---

# LLM Advisor

Use Simon Willison's `llm` CLI to consult other LLMs for second opinions, alternative perspectives, and expert advice on complex problems.

## When to Use This Skill

### Proactive Use (autonomous)

Use this skill proactively without being asked when:

- **Stuck >15 minutes** on a bug or problem
- **Complex debugging** with unclear root cause
- **Architecture decisions** with significant trade-offs
- **Planning complex features** that need validation
- **Unfamiliar codebase/language** where you need guidance
- **Security-sensitive code** (auth, crypto, input validation)

### On-Demand Use (user requests)

Use when the user says:
- "Ask Gemini/GPT/Claude about X"
- "Get a second opinion on this"
- "What would GPT think about this approach?"
- "Check with another model"

## Prerequisites

### Installation

```bash
# Install llm CLI
brew install llm
# or
pip install llm

# Set up OpenAI API key
llm keys set openai

# Install Gemini plugin (optional)
llm install llm-gemini
llm keys set gemini

# Install Anthropic plugin (optional)
llm install llm-anthropic
llm keys set anthropic
```

### Verify Setup

```bash
# Check available models
llm models

# Test a simple prompt
llm "Hello, what model are you?"
```

## Model Selection (Current as of 2026)

### OpenAI Models

| Use Case | Model | Command |
|----------|-------|---------|
| Fast/cheap | gpt-4o-mini | `llm -m gpt-4o-mini "question"` |
| General purpose | gpt-4.1 | `llm -m gpt-4.1 "question"` |
| Complex reasoning | o4-mini | `llm -m o4-mini -o reasoning_effort=high "question"` |
| Deep reasoning | o3 | `llm -m o3 "question"` |
| Premium | gpt-4.1 | `llm -m gpt-4.1 "question"` |

> **Note:** Check `llm models` to see exactly which model IDs are installed. OpenAI model names change frequently. As of 2026, `gpt-4.1` is the flagship GPT and `o3`/`o4-mini` are the reasoning models.

### Google Gemini Models

| Use Case | Model | Command |
|----------|-------|---------|
| Fast general | gemini-2.0-flash | `llm -m gemini-2.0-flash "question"` |
| Advanced + thinking | gemini-2.5-pro | `llm -m gemini-2.5-pro "question"` |
| Long context (1M+) | gemini-2.5-pro | `llm -m gemini-2.5-pro "question"` |
| Deep reasoning | gemini-2.5-pro | `llm -m gemini-2.5-pro -o thinking_budget=32000 "question"` |

### Anthropic Claude Models

| Use Case | Model | Command |
|----------|-------|---------|
| Fast / cost-efficient | claude-haiku-4 | `llm -m claude-haiku-4 "question"` |
| General purpose | claude-sonnet-4-5 | `llm -m claude-sonnet-4-5 "question"` |
| Highest quality | claude-opus-4-5 | `llm -m claude-opus-4-5 "question"` |

### Model Selection Guidelines

1. **Quick questions**: Use `gpt-4o-mini` or `gemini-2.0-flash`
2. **General advice**: Use `gpt-4.1` or `claude-sonnet-4-5`
3. **Complex debugging**: Use `o4-mini -o reasoning_effort=high` or `gemini-2.5-pro -o thinking_budget=32000`
4. **Code review**: Use `gpt-4.1` or `claude-sonnet-4-5` for thorough analysis
5. **Architecture / deep reasoning**: Use `o3` or `claude-opus-4-5`
6. **Long context (>100K tokens)**: Use `gemini-2.5-pro` (1M+ context window)

## Command Reference

### Basic Prompts

```bash
# Simple question
llm "What's the best way to handle rate limiting in a REST API?"

# With specific model
llm -m gpt-4.1 "Explain this error: <error message>"

# With system prompt
llm -s "You are a senior software architect" "Review this design: <design>"
```

### Piped Input

```bash
# Analyze code from file
cat src/auth.ts | llm -m gpt-4.1 "Review this authentication code for security issues"

# Analyze git diff
git diff | llm -m gpt-4.1 "Review these changes for bugs"

# Analyze error logs
cat error.log | llm -m gpt-4o-mini "What's causing these errors?"
```

### Options

```bash
# Control reasoning effort (OpenAI o-series)
llm -m o4-mini -o reasoning_effort=high "Complex question"
llm -m o4-mini -o reasoning_effort=low "Simple question"

# Enable thinking mode (Gemini)
llm -m gemini-2.5-pro -o thinking_budget=32000 "Complex reasoning task"

# Extract code blocks from response
llm -x "Write a function to parse JSON safely"
```

### Conversations

```bash
# Continue previous conversation
llm -c "What about error handling?"

# Start new conversation with context
llm -m gpt-4.1 "I'm debugging a memory leak in a Node.js app..."
llm -c "Here's the heap snapshot: <data>"
```

## Workflow Examples

### Hard Bug Debugging

When stuck on a difficult bug:

```bash
# Describe the problem with context
llm -m o4-mini -o reasoning_effort=high "I'm debugging this issue:

Error: Connection refused on port 5432
Environment: Docker container, Node.js 22
Stack trace: <paste stack trace>

What I've tried:
1. Verified PostgreSQL is running
2. Checked network settings
3. Tested connection from host

What else should I check?"
```

### Architecture Decision

When evaluating design choices:

```bash
llm -m claude-opus-4-5 "I need to decide between these approaches:

Option A: Event-driven with Redis pub/sub
Option B: Direct API calls with circuit breaker

Context:
- Microservices architecture
- ~1000 requests/second
- Eventual consistency is acceptable

What are the trade-offs? Which would you recommend?"
```

### Code Review

Get a second opinion on code changes:

```bash
git diff HEAD~1 | llm -m gpt-4.1 "Review this code change for:
- Bugs or logic errors
- Security vulnerabilities
- Performance issues
- Missing edge cases

Be specific about line numbers and issues."
```

### Plan Validation

Before implementing a complex feature:

```bash
llm -m o3 "Review this implementation plan:

Feature: User authentication with OAuth2
Steps:
1. Add OAuth2 middleware
2. Create /auth/callback endpoint
3. Store tokens in Redis
4. Add refresh token rotation

What am I missing? What could go wrong?"
```

### Long Document Analysis

For large codebases or long documents, use Gemini's large context window:

```bash
# Analyze large codebase
find . -name "*.ts" | head -20 | xargs cat | llm -m gemini-2.5-pro "Summarize the architecture and identify any security concerns"

# Analyze long log files
cat large-app.log | llm -m gemini-2.5-pro "Find patterns indicating memory leaks or performance regressions"
```

### Multi-Model Comparison

For critical decisions, consult multiple models:

```bash
# Ask the same question to different models
QUESTION="Should I use JWT or session cookies for authentication in a Next.js app?"
llm -m gpt-4.1 "$QUESTION"
llm -m claude-sonnet-4-5 "$QUESTION"
llm -m gemini-2.5-pro "$QUESTION"
```

### Alternative Approaches

When you want fresh ideas:

```bash
llm -m gpt-4.1 "Here's my current approach to <problem>:
<describe approach>

What are alternative ways to solve this? What am I missing?"
```

## Best Practices

### Providing Context

1. **Include relevant code** - Pipe files or paste snippets
2. **Describe the environment** - Framework, language version, dependencies
3. **Explain what you've tried** - Helps avoid repeated suggestions
4. **State your constraints** - Performance requirements, compatibility needs

### Formatting Prompts

```bash
# Good: Structured with clear sections
llm -m gpt-4.1 "Problem: <description>

Context:
- Language: TypeScript
- Framework: Express
- Environment: Docker

Error: <error message>

Question: What's causing this and how do I fix it?"

# Bad: Vague without context
llm "Why doesn't this work?"
```

### Interpreting Results

1. **Verify suggestions** - Always test recommendations against your codebase
2. **Consider multiple perspectives** - Run the same question through different models
3. **Cross-reference** - Check suggestions against documentation
4. **Adapt to your context** - Generic advice may need adjustment
5. **Models can be wrong** - Especially about recent APIs; verify against official docs

### When NOT to Use

- Simple, obvious changes (typos, formatting)
- Well-documented operations with clear solutions
- When you need to move fast on low-risk changes
- Repetitive tasks where the pattern is established

## Troubleshooting

### Model Not Found

```bash
# List available models
llm models

# Install missing plugin
llm install llm-gemini
llm install llm-anthropic

# Update to get latest model names
pip install --upgrade llm llm-gemini llm-anthropic
```

### API Key Issues

```bash
# Re-set API key
llm keys set openai
llm keys set gemini
llm keys set anthropic

# Verify key is set
llm keys
```

### Rate Limiting

If you hit rate limits:
1. Switch to a different model temporarily (e.g., `gpt-4o-mini` instead of `gpt-4.1`)
2. Use `reasoning_effort=low` for less token usage
3. Wait and retry after a minute

### Long Responses Truncated

For complex questions that need detailed answers:
```bash
# Use a model with longer output limits
llm -m gemini-2.5-pro "detailed question requiring long answer"
```

### Model Names Drift

OpenAI, Google, and Anthropic update model names frequently. If a model ID doesn't work:
```bash
llm models list  # See all installed models with current IDs
```
