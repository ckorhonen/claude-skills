# Memory Daemon Architecture

The agent memory system uses a daemon-based architecture for efficient database access with connection pooling and caching.

## Architecture Overview

```
┌─────────────────┐
│  Claude Hooks   │
│  (Python)       │
└────────┬────────┘
         │ Unix Socket
         │ (500ms timeout)
         ▼
┌─────────────────────────────┐
│   Memory Daemon             │
│   (daemon.py)               │
│                             │
│  ├─ Connection Pool (1-3)   │
│  ├─ Repo Cache (5min TTL)   │
│  ├─ Extraction Queue        │
│  └─ Health Check Loop       │
└────────┬────────────────────┘
         │ psycopg2
         ▼
┌─────────────────┐
│  PostgreSQL     │
│  (pgvector)     │
└─────────────────┘
```

## Components

### 1. Daemon Server (`daemon.py`)

Async Unix socket server providing:

- **Connection Pooling**: 1-3 persistent PostgreSQL connections
- **Repository Caching**: 5-minute TTL cache for git repository identifiers
- **Extraction Queue**: Background processing for LLM-based learning extraction
- **Health Checks**: 30-second interval maintenance and monitoring
- **Graceful Shutdown**: Proper cleanup on SIGTERM/SIGINT

**Socket**: `~/.claude/daemon.sock`
**PID File**: `~/.claude/daemon.pid`
**Logs**: `~/.claude/logs/daemon.log`

#### Methods

- `ping()` - Health check
- `search_learnings(cwd, query, limit, scope_filter)` - Search learnings
- `save_learning(...)` - Save a learning
- `get_repo_identifier(cwd)` - Get cached repo identifier
- `queue_extraction(transcript_data, cwd)` - Queue for background extraction
- `init_db()` - Initialize database schema

### 2. Daemon Client (`daemon_client.py`)

Thin client library for hooks:

- **Fast Fail**: 500ms socket timeout for quick degradation
- **Graceful Fallback**: Returns empty/None if daemon unavailable
- **Simple API**: Mirror of daemon methods

#### Usage

```python
from agent_memory import daemon_client

# Check if daemon is running
if daemon_client.is_daemon_running():
    # Search learnings
    learnings = daemon_client.search_learnings(
        cwd="/path/to/repo",
        query="api design",
        limit=10
    )

    # Save a learning
    learning_id = daemon_client.save_learning(
        repo_identifier="owner/repo",
        title="API Design Pattern",
        content="Use RESTful conventions...",
        scope_level="repository"
    )
```

#### Command Line

```bash
# Start daemon
python3 -m agent_memory.daemon_client start

# Check status
python3 -m agent_memory.daemon_client status

# Stop daemon
python3 -m agent_memory.daemon_client stop

# Ping daemon
python3 -m agent_memory.daemon_client ping
```

## Performance Benefits

### Before (Direct Connection)

- Each hook creates new DB connection (100-300ms)
- Repeated git operations (50-100ms per call)
- No caching
- Connection timeout blocks hooks

### After (Daemon)

- Connection reuse from pool (< 1ms)
- Cached repo identifiers (< 1ms)
- Fast fail if daemon down (< 500ms)
- Background extraction doesn't block

## Setup

1. **Start the daemon:**
   ```bash
   python3 -m agent_memory.daemon_client start
   ```

2. **Database must be running:**
   ```bash
   cd memory
   docker compose up -d
   ```

3. **Hooks automatically use daemon** if available, fall back to direct connection otherwise.

## Monitoring

### Check Logs

```bash
tail -f ~/.claude/logs/daemon.log
```

### Check Status

```bash
python3 -m agent_memory.daemon_client status
```

### Health Check

The daemon runs a health check loop every 30 seconds:
- Clears expired cache entries
- Logs pool size, cache size, queue size

## Graceful Degradation

If the daemon is unavailable:

1. Client calls timeout after 500ms
2. Returns empty results (`[]` or `None`)
3. Hooks continue without memory features
4. No errors or crashes

## Configuration

Environment variables:

- `OPENAI_API_KEY` - Required for LLM extraction
- `AUTO_EXTRACT_LEARNINGS` - Set to `false` to disable (default: `true`)
- `EXTRACTION_MODEL` - OpenAI model for extraction (default: `gpt-5-mini`)

## Scope System

Learnings are scoped hierarchically:

- **global**: Applies everywhere
- **organization**: Applies to all repos by same owner
- **repository**: Applies to specific repo (default)
- **directory**: Applies to specific directory

Searches cascade through all applicable scopes.

## Extraction Queue

The daemon processes LLM extractions in the background:

1. Hook queues transcript after session ends
2. Daemon fetches existing learnings for deduplication
3. Calls OpenAI API to extract new learnings
4. Saves unique learnings to database
5. All processing happens async, doesn't block hooks

## Security

- Unix socket only accessible by user
- No network exposure
- PID file prevents multiple instances
- Statement timeout prevents long queries (5s)
- Connection timeout prevents hanging (3s)

## Troubleshooting

### Daemon won't start

```bash
# Check if already running
python3 -m agent_memory.daemon_client status

# Check logs
cat ~/.claude/logs/daemon.log

# Check database
docker ps | grep postgres
```

### Slow responses

- Check connection pool size in logs
- Verify database is responsive
- Check for slow queries in PostgreSQL logs

### Memory leaks

- Monitor daemon process with `ps aux | grep daemon.py`
- Check logs for connection warnings
- Restart daemon if needed

## Development

### Testing

```python
# Test fast-fail
from agent_memory import daemon_client

# Should return False quickly
daemon_client.is_daemon_running()

# Should return empty list
daemon_client.search_learnings('/tmp', 'test')
```

### Debugging

Set logging level in `daemon.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Adding Methods

1. Add method to `MemoryDaemon` class in `daemon.py`
2. Add routing in `handle_client()`
3. Add client method to `DaemonClient` in `daemon_client.py`
4. Add convenience function at module level
