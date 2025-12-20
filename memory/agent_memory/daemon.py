#!/usr/bin/env python3
"""
Memory daemon server - async Unix socket server for agent memory operations.

Provides fast, connection-pooled access to the memory database with:
- Async request handling via Unix socket
- Connection pooling for database operations
- Cached repository identifiers (5 minute TTL)
- Background LLM extraction queue processing
- Graceful shutdown on SIGTERM/SIGINT

Socket: ~/.claude/daemon.sock
PID: ~/.claude/daemon.pid
Logs: ~/.claude/logs/daemon.log
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

# Set up logging
LOG_DIR = Path.home() / ".claude" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "daemon.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
SOCKET_PATH = Path.home() / ".claude" / "daemon.sock"
PID_FILE = Path.home() / ".claude" / "daemon.pid"

# Connection pool configuration
MIN_POOL_SIZE = 1
MAX_POOL_SIZE = 3

# Cache configuration
REPO_CACHE_TTL = 300  # 5 minutes
HEALTH_CHECK_INTERVAL = 30  # 30 seconds

# Extraction queue
extraction_queue = asyncio.Queue()


class RepoCache:
    """Simple TTL cache for repository identifiers."""

    def __init__(self, ttl: int = REPO_CACHE_TTL):
        self.ttl = ttl
        self.cache: Dict[str, tuple[str, datetime]] = {}

    def get(self, cwd: str) -> Optional[str]:
        """Get cached repo identifier if not expired."""
        if cwd in self.cache:
            repo_id, timestamp = self.cache[cwd]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return repo_id
            else:
                del self.cache[cwd]
        return None

    def set(self, cwd: str, repo_id: str):
        """Cache repo identifier with timestamp."""
        self.cache[cwd] = (repo_id, datetime.now())

    def clear_expired(self):
        """Remove expired entries."""
        now = datetime.now()
        expired = [
            cwd for cwd, (_, timestamp) in self.cache.items()
            if now - timestamp >= timedelta(seconds=self.ttl)
        ]
        for cwd in expired:
            del self.cache[cwd]


class ConnectionPool:
    """Simple psycopg2 connection pool."""

    def __init__(self, min_size: int = MIN_POOL_SIZE, max_size: int = MAX_POOL_SIZE):
        self.min_size = min_size
        self.max_size = max_size
        self.connections = []
        self.available = asyncio.Queue()
        self.lock = asyncio.Lock()
        self._closed = False

    async def initialize(self):
        """Initialize the connection pool."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            for _ in range(self.min_size):
                conn = psycopg2.connect(
                    dbname="ai",
                    user="ai",
                    password="ai",
                    host="localhost",
                    port="5532",
                    connect_timeout=3
                )
                # Set statement timeout
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = 5000")

                self.connections.append(conn)
                await self.available.put(conn)

            logger.info(f"Connection pool initialized with {self.min_size} connections")
            return True
        except ImportError:
            logger.error("psycopg2 not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            return False

    async def get_connection(self):
        """Get a connection from the pool."""
        if self._closed:
            return None

        try:
            # Try to get an available connection with timeout
            conn = await asyncio.wait_for(self.available.get(), timeout=5.0)

            # Test if connection is alive
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return conn
            except Exception:
                # Connection is dead, create a new one
                logger.warning("Dead connection detected, creating new one")
                await self._create_new_connection()
                return await self.get_connection()
        except asyncio.TimeoutError:
            # No connections available, try to create a new one if under max
            async with self.lock:
                if len(self.connections) < self.max_size:
                    if await self._create_new_connection():
                        return await self.get_connection()
            logger.warning("Connection pool exhausted")
            return None

    async def _create_new_connection(self):
        """Create a new connection and add to pool."""
        try:
            import psycopg2

            conn = psycopg2.connect(
                dbname="ai",
                user="ai",
                password="ai",
                host="localhost",
                port="5532",
                connect_timeout=3
            )
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = 5000")

            self.connections.append(conn)
            await self.available.put(conn)
            logger.info(f"Created new connection (pool size: {len(self.connections)})")
            return True
        except Exception as e:
            logger.error(f"Failed to create new connection: {e}")
            return False

    async def release_connection(self, conn):
        """Return a connection to the pool."""
        if conn and not self._closed:
            await self.available.put(conn)

    async def close(self):
        """Close all connections in the pool."""
        self._closed = True
        logger.info("Closing connection pool")

        for conn in self.connections:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        self.connections.clear()


class MemoryDaemon:
    """Main daemon server."""

    def __init__(self):
        self.pool = ConnectionPool()
        self.repo_cache = RepoCache()
        self.server = None
        self.shutdown_event = asyncio.Event()
        self.tasks = []

    async def initialize(self):
        """Initialize daemon components."""
        logger.info("Initializing memory daemon")

        # Initialize connection pool
        if not await self.pool.initialize():
            logger.error("Failed to initialize connection pool")
            return False

        # Create socket directory
        SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing socket if present
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()

        return True

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a client connection."""
        try:
            # Read request
            data = await asyncio.wait_for(reader.read(65536), timeout=10.0)
            if not data:
                return

            request = json.loads(data.decode('utf-8'))
            method = request.get('method')
            params = request.get('params', {})

            # Route request to handler
            if method == 'ping':
                response = {'status': 'ok', 'timestamp': time.time()}
            elif method == 'search_learnings':
                response = await self.search_learnings(**params)
            elif method == 'save_learning':
                response = await self.save_learning(**params)
            elif method == 'get_repo_identifier':
                response = await self.get_repo_identifier(**params)
            elif method == 'queue_extraction':
                response = await self.queue_extraction(**params)
            elif method == 'init_db':
                response = await self.init_db()
            else:
                response = {'error': f'Unknown method: {method}'}

            # Send response
            response_data = json.dumps(response).encode('utf-8')
            writer.write(response_data)
            await writer.drain()

        except asyncio.TimeoutError:
            logger.warning("Client request timeout")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON request: {e}")
        except Exception as e:
            logger.error(f"Error handling client: {e}", exc_info=True)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def search_learnings(self, cwd: str, query: Optional[str] = None,
                               limit: int = 10, scope_filter: Optional[str] = None) -> Dict[str, Any]:
        """Search learnings across scopes."""
        conn = await self.pool.get_connection()
        if not conn:
            return {'error': 'Database unavailable', 'results': []}

        try:
            import psycopg2.extras

            # Import hook_db functions for scope logic
            from agent_memory import hook_db

            repo_id = await self.get_repo_identifier(cwd)
            if isinstance(repo_id, dict) and 'repo_id' in repo_id:
                repo_id = repo_id['repo_id']

            org_id = hook_db.get_org_identifier(repo_id)
            rel_path = hook_db.get_relative_path(cwd)
            path_ancestors = hook_db.get_path_ancestors(rel_path) if rel_path else []

            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Build scope conditions
                conditions = []
                params = []

                if scope_filter:
                    if scope_filter == 'global':
                        conditions.append("(scope_level = 'global')")
                    elif scope_filter == 'organization' and org_id:
                        conditions.append("(scope_level = 'organization' AND repo_identifier = %s)")
                        params.append(org_id)
                    elif scope_filter == 'repository' and repo_id:
                        conditions.append("(scope_level = 'repository' AND repo_identifier = %s)")
                        params.append(repo_id)
                    elif scope_filter == 'directory' and repo_id and rel_path:
                        conditions.append("(scope_level = 'directory' AND repo_identifier = %s AND directory_path = %s)")
                        params.extend([repo_id, rel_path])
                else:
                    # Cascade all scopes
                    conditions.append("(scope_level = 'global')")

                    if org_id:
                        conditions.append("(scope_level = 'organization' AND repo_identifier = %s)")
                        params.append(org_id)

                    if repo_id:
                        conditions.append("(scope_level = 'repository' AND repo_identifier = %s)")
                        params.append(repo_id)

                    if repo_id and path_ancestors:
                        dir_placeholders = ', '.join(['%s'] * len(path_ancestors))
                        conditions.append(f"(scope_level = 'directory' AND repo_identifier = %s AND directory_path IN ({dir_placeholders}))")
                        params.append(repo_id)
                        params.extend(path_ancestors)

                scope_where = ' OR '.join(conditions) if conditions else 'TRUE'

                if query:
                    sql = f"""
                        SELECT id, repo_identifier, title, content, category, tags,
                               session_id, created_at, updated_at, metadata,
                               scope_level, directory_path
                        FROM learnings
                        WHERE ({scope_where})
                          AND (title ILIKE %s OR content ILIKE %s OR %s = ANY(tags))
                        ORDER BY
                            CASE scope_level
                                WHEN 'directory' THEN 1
                                WHEN 'repository' THEN 2
                                WHEN 'organization' THEN 3
                                WHEN 'global' THEN 4
                                ELSE 5
                            END,
                            updated_at DESC
                        LIMIT %s;
                    """
                    params.extend([f"%{query}%", f"%{query}%", query, limit])
                else:
                    sql = f"""
                        SELECT id, repo_identifier, title, content, category, tags,
                               session_id, created_at, updated_at, metadata,
                               scope_level, directory_path
                        FROM learnings
                        WHERE ({scope_where})
                        ORDER BY
                            CASE scope_level
                                WHEN 'directory' THEN 1
                                WHEN 'repository' THEN 2
                                WHEN 'organization' THEN 3
                                WHEN 'global' THEN 4
                                ELSE 5
                            END,
                            updated_at DESC
                        LIMIT %s;
                    """
                    params.append(limit)

                cur.execute(sql, params)
                results = cur.fetchall()

                # Convert to list of dicts
                learnings = []
                for row in results:
                    learning = dict(row)
                    # Convert datetime to ISO format
                    if 'created_at' in learning and learning['created_at']:
                        learning['created_at'] = learning['created_at'].isoformat()
                    if 'updated_at' in learning and learning['updated_at']:
                        learning['updated_at'] = learning['updated_at'].isoformat()
                    learnings.append(learning)

                return {'results': learnings}

        except Exception as e:
            logger.error(f"Error searching learnings: {e}", exc_info=True)
            return {'error': str(e), 'results': []}
        finally:
            await self.pool.release_connection(conn)

    async def save_learning(self, repo_identifier: Optional[str], title: str, content: str,
                           category: Optional[str] = None, tags: Optional[List[str]] = None,
                           session_id: Optional[str] = None, metadata: Optional[Dict] = None,
                           scope_level: str = "repository", directory_path: Optional[str] = None) -> Dict[str, Any]:
        """Save a learning to the database."""
        conn = await self.pool.get_connection()
        if not conn:
            return {'error': 'Database unavailable', 'id': None}

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO learnings
                    (repo_identifier, title, content, category, tags, session_id, metadata, scope_level, directory_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (repo_identifier, title, content, category, tags or [], session_id,
                      json.dumps(metadata) if metadata else None, scope_level, directory_path))

                learning_id = cur.fetchone()[0]
                conn.commit()

                logger.info(f"Saved learning #{learning_id}: {title}")
                return {'id': learning_id}

        except Exception as e:
            logger.error(f"Error saving learning: {e}", exc_info=True)
            return {'error': str(e), 'id': None}
        finally:
            await self.pool.release_connection(conn)

    async def get_repo_identifier(self, cwd: str) -> Dict[str, str]:
        """Get repository identifier with caching."""
        # Check cache first
        cached = self.repo_cache.get(cwd)
        if cached:
            return {'repo_id': cached}

        # Compute and cache
        from agent_memory import hook_db
        repo_id = hook_db.get_repo_identifier(cwd)
        self.repo_cache.set(cwd, repo_id)

        return {'repo_id': repo_id}

    async def queue_extraction(self, transcript_data: Dict, cwd: str) -> Dict[str, Any]:
        """Queue transcript for background LLM extraction."""
        try:
            await extraction_queue.put({
                'transcript': transcript_data,
                'cwd': cwd,
                'timestamp': time.time()
            })
            logger.info(f"Queued extraction for {cwd}")
            return {'status': 'queued', 'queue_size': extraction_queue.qsize()}
        except Exception as e:
            logger.error(f"Error queueing extraction: {e}")
            return {'error': str(e)}

    async def init_db(self) -> Dict[str, Any]:
        """Initialize database schema."""
        conn = await self.pool.get_connection()
        if not conn:
            return {'error': 'Database unavailable', 'success': False}

        try:
            with conn.cursor() as cur:
                # Create extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                # Create learnings table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS learnings (
                        id SERIAL PRIMARY KEY,
                        repo_identifier TEXT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        category TEXT,
                        tags TEXT[],
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB
                    );
                """)

                # Add scope columns
                cur.execute("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'learnings' AND column_name = 'scope_level'
                        ) THEN
                            ALTER TABLE learnings ADD COLUMN scope_level TEXT DEFAULT 'repository';
                        END IF;

                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'learnings' AND column_name = 'directory_path'
                        ) THEN
                            ALTER TABLE learnings ADD COLUMN directory_path TEXT;
                        END IF;

                        ALTER TABLE learnings ALTER COLUMN repo_identifier DROP NOT NULL;
                    END $$;
                """)

                # Create indexes
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_learnings_repo
                    ON learnings(repo_identifier);
                """)

                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_learnings_scope
                    ON learnings(scope_level, repo_identifier, directory_path);
                """)

                conn.commit()
                logger.info("Database initialized successfully")
                return {'success': True}

        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
            return {'error': str(e), 'success': False}
        finally:
            await self.pool.release_connection(conn)

    async def process_extraction_queue(self):
        """Background task to process extraction queue."""
        logger.info("Starting extraction queue processor")

        while not self.shutdown_event.is_set():
            try:
                # Wait for item with timeout to allow shutdown checks
                item = await asyncio.wait_for(extraction_queue.get(), timeout=5.0)

                transcript = item['transcript']
                cwd = item['cwd']

                logger.info(f"Processing extraction for {cwd}")

                # Get existing learnings for deduplication
                existing_result = await self.search_learnings(cwd, limit=100)
                existing = existing_result.get('results', [])

                # Extract learnings
                from agent_memory import llm_extractor
                messages = transcript.get('messages', [])
                learnings = llm_extractor.extract_learnings(messages, existing)

                # Save learnings
                repo_result = await self.get_repo_identifier(cwd)
                repo_id = repo_result.get('repo_id')

                for learning in learnings:
                    await self.save_learning(
                        repo_identifier=repo_id,
                        title=learning.get('title', ''),
                        content=learning.get('learning', ''),
                        category=learning.get('type'),
                        metadata={
                            'context': learning.get('context'),
                            'confidence': learning.get('confidence')
                        }
                    )

                logger.info(f"Extracted and saved {len(learnings)} learnings for {cwd}")

            except asyncio.TimeoutError:
                # No items in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing extraction: {e}", exc_info=True)

        logger.info("Extraction queue processor stopped")

    async def health_check_loop(self):
        """Periodic health check and maintenance."""
        logger.info("Starting health check loop")

        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(HEALTH_CHECK_INTERVAL)

                # Clear expired cache entries
                self.repo_cache.clear_expired()

                # Log status
                logger.debug(f"Health check - Pool: {len(self.pool.connections)}, "
                           f"Cache: {len(self.repo_cache.cache)}, "
                           f"Queue: {extraction_queue.qsize()}")

            except Exception as e:
                logger.error(f"Error in health check: {e}")

        logger.info("Health check loop stopped")

    async def start(self):
        """Start the daemon server."""
        if not await self.initialize():
            logger.error("Failed to initialize daemon")
            return False

        # Write PID file
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(str(os.getpid()))
        logger.info(f"PID: {os.getpid()}")

        # Start server
        self.server = await asyncio.start_unix_server(
            self.handle_client,
            path=str(SOCKET_PATH)
        )
        logger.info(f"Listening on {SOCKET_PATH}")

        # Start background tasks
        extraction_task = asyncio.create_task(self.process_extraction_queue())
        health_task = asyncio.create_task(self.health_check_loop())
        self.tasks.extend([extraction_task, health_task])

        # Serve until shutdown
        async with self.server:
            await self.shutdown_event.wait()

        logger.info("Server stopped")
        return True

    async def stop(self):
        """Stop the daemon server."""
        logger.info("Stopping daemon")

        # Signal shutdown
        self.shutdown_event.set()

        # Close server
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # Cancel background tasks
        for task in self.tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)

        # Close connection pool
        await self.pool.close()

        # Remove socket and PID file
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()
        if PID_FILE.exists():
            PID_FILE.unlink()

        logger.info("Daemon stopped cleanly")


# Global daemon instance
daemon = None


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}")
    if daemon:
        asyncio.create_task(daemon.stop())


async def main():
    """Main entry point."""
    global daemon

    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start daemon
    daemon = MemoryDaemon()

    try:
        await daemon.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
