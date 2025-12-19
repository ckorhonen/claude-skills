# Hook Testing Guide

This document describes how to manually test the Claude Code hooks for the self-learning memory system.

## Prerequisites

1. Start the database:
   ```bash
   docker compose up -d
   ```

2. Install Python dependencies:
   ```bash
   pip install -e .
   ```

3. Set environment variables:
   ```bash
   export OPENAI_API_KEY=sk-...
   export CLAUDE_PROJECT_DIR=/Users/ckorhonen/conductor/workspaces/claude-skills/beirut
   ```

## Testing Individual Hooks

### 1. Session Start Hook

Tests that the hook initializes the database and retrieves learnings.

```bash
echo '{"session_id":"test-123","transcript_path":"/tmp/transcript.jsonl","cwd":"/tmp"}' | \
  python3 hooks/session_start.py
```

**Expected output (DB available):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "## Relevant Learnings..."
  }
}
```

**Expected output (DB unavailable):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "[Memory system offline: ...]"
  }
}
```

### 2. User Prompt Submit Hook

#### Test normal prompt (should inject context):
```bash
echo '{"user_prompt":"How do I handle errors in Python?","transcript_path":"/tmp/t.jsonl","cwd":"/tmp"}' | \
  python3 hooks/user_prompt_submit.py
```

#### Test !pending-learning command:
```bash
echo '{"user_prompt":"!pending-learning","transcript_path":"/tmp/t.jsonl","cwd":"/tmp"}' | \
  python3 hooks/user_prompt_submit.py
```

**Expected output:**
```json
{
  "decision": "block",
  "reason": "No pending learning."
}
```

#### Test !learnings search command:
```bash
echo '{"user_prompt":"!learnings error handling","transcript_path":"/tmp/t.jsonl","cwd":"/tmp"}' | \
  python3 hooks/user_prompt_submit.py
```

#### Test !save-learning command (with pending):
First create a pending learning:
```bash
mkdir -p .claude/learnings
cat > .claude/learnings/pending.json << 'EOF'
{
  "title": "Test Learning",
  "context": "When testing hooks",
  "learning": "Always test with fake JSON input",
  "confidence": "high",
  "type": "process",
  "created_at": "2025-01-01T00:00:00Z",
  "repo": "test-repo",
  "session_id": "test-123"
}
EOF
```

Then save it:
```bash
echo '{"user_prompt":"!save-learning","transcript_path":"/tmp/t.jsonl","cwd":"/tmp"}' | \
  python3 hooks/user_prompt_submit.py
```

**Expected output:**
```json
{
  "decision": "block",
  "reason": "Saved learning: 'Test Learning'"
}
```

### 3. Stop Hook

Tests extraction of proposed learnings from transcripts.

First create a test transcript:
```bash
cat > /tmp/test_transcript.jsonl << 'EOF'
{"type":"assistant","message":"Here is my response with a learning:\n\n<proposed_learning>\n{\"title\":\"Use early returns\",\"context\":\"When validating\",\"learning\":\"Prefer early returns for validation\",\"confidence\":\"high\",\"type\":\"rule\"}\n</proposed_learning>\n\nTo save this learning, type: !save-learning"}
EOF
```

Then run the stop hook:
```bash
echo '{"transcript_path":"/tmp/test_transcript.jsonl","stop_hook_active":false}' | \
  python3 hooks/stop.py
```

**Expected behavior:** Creates `.claude/learnings/pending.json` with the extracted learning.

Verify:
```bash
cat .claude/learnings/pending.json
```

### 4. Pre-Tool-Use Hook

#### Test safe command (should pass through silently):
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | \
  python3 hooks/pre_tool_use.py
```

**Expected output:** (empty - no output means allow)

#### Test dangerous command (should block):
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | \
  python3 hooks/pre_tool_use.py
```

**Expected output:**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "reason": "Blocked: Recursive force delete from root"
}
```

#### Test force push to main (should block):
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}' | \
  python3 hooks/pre_tool_use.py
```

**Expected output:**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "reason": "Blocked: Force push to main/master"
}
```

## Integration Testing

### Full Flow Test

1. **Start a fresh session** (manually or restart Claude Code)

2. **Check session start context** - should see memory system status

3. **Ask a question** - should see relevant learnings injected (if any exist)

4. **Get Claude to propose a learning** - prompt it to share an insight in the learning format

5. **Check pending** - run `!pending-learning` to see the captured learning

6. **Save or discard** - run `!save-learning` or `!discard-learning`

7. **Search learnings** - run `!learnings <query>` to find saved learnings

## Troubleshooting

### Hook not executing
- Check that hooks are executable: `chmod +x hooks/*.py`
- Verify `.claude/settings.local.json` is properly configured
- Restart Claude Code after modifying hook configuration

### Database connection errors
- Ensure Docker is running: `docker ps`
- Check pgvector container: `docker compose ps`
- Verify database is ready: `docker compose logs pgvector`

### Missing OPENAI_API_KEY
- The system will degrade gracefully without embeddings
- Text-based search will be used as fallback

### Import errors
- Ensure package is installed: `pip install -e .`
- Check Python path includes the project root

## Cleanup

Remove test files:
```bash
rm -f .claude/learnings/pending.json
rm -f /tmp/test_transcript.jsonl
```

Stop database:
```bash
docker compose down
```

Remove database volume (deletes all learnings):
```bash
docker compose down -v
```
