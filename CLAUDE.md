# Claude Code Project Instructions

## Self-Learning Memory System

This project includes a self-learning memory subsystem that allows you to accumulate and retrieve learnings across sessions.

### Available Commands

- `!save-learning [--global|--scope=X]` - Save the pending learning to the database
- `!discard-learning` - Discard the pending learning
- `!pending-learning` - Show the current pending learning
- `!learnings [query] [--global|--scope=X]` - Search for learnings matching the query

### Scope Levels

Learnings can be scoped to different levels (from broadest to narrowest):
- **global**: Applies everywhere across all projects
- **organization**: Applies to all repos by the same owner
- **repository**: Applies to a specific repo (default)
- **directory**: Applies to a specific directory within a repo

### Proposing Learnings

When you discover a reusable insight worth remembering for future sessions, output at the **END** of your response:

```
<proposed_learning>
{"title":"Brief descriptive title","context":"When this applies","learning":"The actual insight or rule","confidence":"medium","type":"rule","scope":"repository"}
</proposed_learning>
```

Then tell the user: "To save this learning, type: `!save-learning` (or `!discard-learning` to dismiss)."

### Learning Schema

- **title** (required): Brief descriptive title
- **context** (required): When this learning applies
- **learning** (required): The actual insight, rule, or pattern
- **confidence**: `low`, `medium`, or `high`
- **type**: `rule`, `heuristic`, `source`, `process`, or `constraint`
- **scope**: `global`, `organization`, `repository` (default), or `directory`
- **tags** (optional): Array of relevant tags

### Examples

**Rule about code patterns:**
```
<proposed_learning>
{"title":"Use early returns for validation","context":"When validating function inputs","learning":"Prefer early returns for input validation to reduce nesting and improve readability. Check for invalid cases first and return/throw early.","confidence":"high","type":"rule"}
</proposed_learning>
```

**Process learning:**
```
<proposed_learning>
{"title":"Run tests before committing hooks","context":"When modifying Claude Code hooks","learning":"Always test hooks with fake JSON input before committing. Use: echo '{...}' | python3 hooks/hook_name.py","confidence":"high","type":"process"}
</proposed_learning>
```

### Setup Requirements

1. **Docker**: Run `docker compose -f memory/docker-compose.yml up -d` to start the pgvector database
2. **OpenAI API Key**: Set `OPENAI_API_KEY` environment variable for embeddings (optional, for semantic search)
3. **Python Dependencies**: Run `pip install -e memory/` to install the agent_memory package

### Graceful Degradation

If the database or OpenAI API key is unavailable, the memory system will:
- Continue to work without injecting context
- Display a message indicating memory is offline
- Not block any operations or cause errors
