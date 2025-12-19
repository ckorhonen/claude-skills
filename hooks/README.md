# Claude Code Hooks

This directory contains Claude Code hook scripts that provide persistent memory capabilities for Claude sessions.

## Overview

The hooks implement an agent memory system that:
- Stores learnings from Claude sessions in a PostgreSQL database with pgvector
- Retrieves relevant learnings at session start
- Provides commands to manage learnings
- Automatically extracts proposed learnings from session transcripts

## Prerequisites

1. **Docker** - Required to run the PostgreSQL database
2. **Python 3.11+** - Required to run the hook scripts
3. **Python Dependencies** - Install with `pip install -r requirements.txt`

## Setup

1. Install Python dependencies:
```bash
cd /Users/ckorhonen/conductor/workspaces/claude-skills/beirut
pip install -r requirements.txt
```

2. Start the PostgreSQL database:
```bash
docker compose up -d pgvector
```

3. Optionally set `OPENAI_API_KEY` environment variable (required for some features)

## Hook Scripts

### session_start.py

**Runs when:** A Claude Code session starts

**Input:**
- `session_id` - Unique session identifier
- `transcript_path` - Path to session transcript file
- `cwd` - Current working directory

**Behavior:**
1. Runs `../scripts/ensure_db.sh` to ensure database is available
2. Gets repository identifier from git remote or folder name
3. If database is available and `OPENAI_API_KEY` is set:
   - Searches for learnings relevant to the repository
   - Outputs learnings as additional context
4. If unavailable: outputs "memory offline" context

**Output:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "# Agent Memory: <repo>\n\n<learnings>"
  }
}
```

### user_prompt_submit.py

**Runs when:** User submits a prompt

**Input:**
- `user_prompt` - The user's input text
- `transcript_path` - Path to session transcript file
- `cwd` - Current working directory

**Behavior:**

#### Learning Commands

- `!save-learning` - Saves pending learning to database
- `!discard-learning` - Discards pending learning
- `!pending-learning` - Shows current pending learning
- `!learnings [query]` - Searches learnings (optional query filter)

#### Normal Prompts

For non-command prompts:
1. Searches for learnings relevant to the prompt
2. Injects up to 5 relevant learnings as additional context
3. Allows the prompt to proceed

**Output (commands):**
```json
{
  "decision": "block",
  "reason": "<command result message>"
}
```

**Output (normal prompts):**
```json
{
  "decision": "allow",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "# Relevant Learnings\n\n<learnings>"
  }
}
```

### stop.py

**Runs when:** A Claude Code session stops

**Input:**
- `transcript_path` - Path to session transcript file
- `stop_hook_active` - Whether stop hook is already active (to prevent loops)
- `session_id` - Unique session identifier

**Behavior:**
1. If `stop_hook_active` is true: exits immediately (prevents loops)
2. Reads and parses the transcript JSONL file
3. Extracts the last assistant message
4. Looks for `<proposed_learning>JSON</proposed_learning>` block
5. If found: saves to `.claude/learnings/pending.json` with session metadata
6. Never blocks stopping - always exits successfully

**Output:** None (never blocks)

## Agent Memory Module

The `agent_memory` module (`/Users/ckorhonen/conductor/workspaces/claude-skills/beirut/agent_memory/__init__.py`) provides:

### Functions

- `init_db()` - Initialize database schema
- `get_connection()` - Get database connection
- `search_learnings(repo_identifier, query, limit)` - Search for learnings
- `save_learning(repo_identifier, title, content, category, tags, session_id, metadata)` - Save a learning
- `get_repo_identifier(cwd)` - Get repository identifier from git or folder name

### Database Schema

```sql
CREATE TABLE learnings (
    id SERIAL PRIMARY KEY,
    repo_identifier TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    tags TEXT[],
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

## Usage Examples

### Proposing a Learning

In a Claude session:
```
Claude, I want to remember that we use React Testing Library for component tests in this project.
Could you propose that as a learning?
```

Claude will output:
```xml
<proposed_learning>
{
  "title": "Use React Testing Library for Component Tests",
  "content": "This project uses React Testing Library (RTL) for testing React components...",
  "category": "testing",
  "tags": ["react", "testing", "rtl"]
}
</proposed_learning>
```

At session end, this will be saved to `.claude/learnings/pending.json`

### Managing Learnings

In the next session:
```
!pending-learning          # View pending learning
!save-learning             # Save to database
!discard-learning          # Discard without saving
!learnings testing         # Search for learnings about "testing"
!learnings                 # List all learnings for this repo
```

## File Structure

```
beirut/
├── agent_memory/
│   └── __init__.py          # Memory module
├── hooks/
│   ├── session_start.py     # SessionStart hook
│   ├── user_prompt_submit.py # UserPromptSubmit hook
│   ├── stop.py              # Stop hook
│   └── README.md            # This file
├── scripts/
│   └── ensure_db.sh         # Database setup script
├── .claude/
│   └── learnings/
│       └── pending.json     # Pending learning storage
├── docker-compose.yml       # PostgreSQL + pgvector
└── requirements.txt         # Python dependencies
```

## Error Handling

All hooks are designed to:
- Always exit with code 0 (never crash sessions)
- Gracefully handle missing database
- Gracefully handle missing dependencies
- Provide helpful error messages via output reasons
- Log errors to stderr for debugging

## Development

To test hooks locally:

```bash
# Test session_start
cat <<'EOF' | python3 hooks/session_start.py
{"session_id":"test","transcript_path":"/tmp/test.jsonl","cwd":"/path/to/repo"}
EOF

# Test user_prompt_submit
cat <<'EOF' | python3 hooks/user_prompt_submit.py
{"user_prompt":"!pending-learning","transcript_path":"/tmp/test.jsonl","cwd":"/path/to/repo"}
EOF

# Test stop
cat <<'EOF' | python3 hooks/stop.py
{"transcript_path":"/tmp/test.jsonl","stop_hook_active":false,"session_id":"test"}
EOF
```

## Troubleshooting

**Database connection fails:**
- Ensure Docker is running
- Run `docker compose up -d pgvector`
- Check logs: `docker compose logs pgvector`

**Import errors:**
- Ensure Python dependencies are installed: `pip install -r requirements.txt`

**Hooks not executing:**
- Verify hooks are executable: `chmod +x hooks/*.py`
- Check shebang lines: `#!/usr/bin/env python3`
- Ensure hooks are in the correct location

**JSON parsing errors:**
- Hooks expect properly formatted JSON input via stdin
- Use heredocs for testing: `cat <<'EOF' | python3 hooks/script.py`
