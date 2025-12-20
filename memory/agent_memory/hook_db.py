#!/usr/bin/env python3
"""
Simple database operations for hooks.
Uses psycopg2 directly for lightweight operations without heavy dependencies.

Supports hierarchical scoping:
- global: applies everywhere
- organization: applies to all repos by the same owner
- repository: applies to a specific repo (default)
- directory: applies to a specific directory within a repo
"""

import os
import sys
import json
import time
import subprocess
from typing import List, Dict, Optional, Any, Tuple

# Connection health cache - avoid repeated timeout attempts
_connection_failed_until = 0  # Unix timestamp when connection can be retried
_FAILURE_COOLDOWN_SECONDS = 60  # How long to wait before retrying after failure
_CONNECT_TIMEOUT_SECONDS = 2  # TCP connection timeout
_STATEMENT_TIMEOUT_MS = 3000  # SQL statement timeout in milliseconds

# Git info caching
_git_info_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
_GIT_CACHE_TTL = 300  # 5 minutes

# THREAD SAFETY NOTE:
# These module-level globals (_connection_failed_until, _git_info_cache) are
# intentionally used without locks. This is safe because Claude Code hooks
# execute sequentially in a single-threaded context per session.
# If this module is reused in a multi-threaded environment, wrap access to
# these globals with threading.Lock().


def is_database_available() -> bool:
    """Check if we should attempt connection (respects failure cooldown)."""
    return time.time() > _connection_failed_until


def mark_connection_failed():
    """Mark database as unavailable for a cooldown period."""
    global _connection_failed_until
    _connection_failed_until = time.time() + _FAILURE_COOLDOWN_SECONDS


def get_connection():
    """Get a database connection using psycopg2 with timeouts."""
    # Fast-fail if we recently failed to connect
    if not is_database_available():
        return None

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(
            dbname="ai",
            user="ai",
            password="ai",
            host="localhost",
            port="5532",
            connect_timeout=_CONNECT_TIMEOUT_SECONDS
        )

        # Set statement timeout to prevent long-running queries
        with conn.cursor() as cur:
            cur.execute(f"SET statement_timeout = {_STATEMENT_TIMEOUT_MS}")

        return conn
    except ImportError:
        # psycopg2 not installed
        return None
    except Exception:
        # Connection failed - mark as unavailable for cooldown period
        mark_connection_failed()
        return None


def init_db():
    """Initialize database schema if it doesn't exist."""
    conn = get_connection()
    if not conn:
        return False

    try:
        import psycopg2

        with conn.cursor() as cur:
            # Create extension if not exists
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # Create learnings table (base schema for new installs)
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

            # Migration: Add scope columns and fix constraints
            # This runs BEFORE creating indexes on these columns
            cur.execute("""
                DO $$
                BEGIN
                    -- Add scope_level column if missing
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'learnings' AND column_name = 'scope_level'
                    ) THEN
                        ALTER TABLE learnings ADD COLUMN scope_level TEXT DEFAULT 'repository';
                    END IF;

                    -- Add directory_path column if missing
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'learnings' AND column_name = 'directory_path'
                    ) THEN
                        ALTER TABLE learnings ADD COLUMN directory_path TEXT;
                    END IF;

                    -- Make repo_identifier nullable (for global scope)
                    ALTER TABLE learnings ALTER COLUMN repo_identifier DROP NOT NULL;
                END $$;
            """)

            # Create index on repo_identifier
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_learnings_repo
                ON learnings(repo_identifier);
            """)

            # Create composite index for scope-based queries (after columns are added)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_learnings_scope
                ON learnings(scope_level, repo_identifier, directory_path);
            """)

            conn.commit()
        return True
    except psycopg2.OperationalError as e:
        mark_connection_failed()
        print(f"Error initializing database (connection issue): {e}", file=sys.stderr)
        return False
    except psycopg2.InterfaceError as e:
        mark_connection_failed()
        print(f"Error initializing database (interface issue): {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()


def search_learnings(repo_identifier: str, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search learnings for a given repository.

    Args:
        repo_identifier: Repository identifier (git remote or folder name)
        query: Optional search query to filter learnings
        limit: Maximum number of results to return

    Returns:
        List of matching learnings
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        import psycopg2
        import psycopg2.extras

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if query:
                # Simple text search using LIKE
                cur.execute("""
                    SELECT id, repo_identifier, title, content, category, tags,
                           session_id, created_at, updated_at, metadata
                    FROM learnings
                    WHERE repo_identifier = %s
                      AND (title ILIKE %s OR content ILIKE %s OR %s = ANY(tags))
                    ORDER BY updated_at DESC
                    LIMIT %s;
                """, (repo_identifier, f"%{query}%", f"%{query}%", query, limit))
            else:
                # Return all learnings for this repo
                cur.execute("""
                    SELECT id, repo_identifier, title, content, category, tags,
                           session_id, created_at, updated_at, metadata
                    FROM learnings
                    WHERE repo_identifier = %s
                    ORDER BY updated_at DESC
                    LIMIT %s;
                """, (repo_identifier, limit))

            results = cur.fetchall()
            return [dict(row) for row in results]
    except psycopg2.OperationalError as e:
        mark_connection_failed()
        print(f"Error searching learnings (connection issue): {e}", file=sys.stderr)
        return []
    except psycopg2.InterfaceError as e:
        mark_connection_failed()
        print(f"Error searching learnings (interface issue): {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error searching learnings: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()


def save_learning(
    repo_identifier: Optional[str],
    title: str,
    content: str,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict] = None,
    scope_level: str = "repository",
    directory_path: Optional[str] = None
) -> Optional[int]:
    """
    Save a learning to the database.

    Args:
        repo_identifier: Repository identifier (git remote or folder name).
                        Can be None for global scope, or org name for organization scope.
        title: Learning title
        content: Learning content
        category: Optional category
        tags: Optional list of tags
        session_id: Optional session ID
        metadata: Optional metadata dictionary
        scope_level: Scope level ('global', 'organization', 'repository', 'directory')
        directory_path: Relative path for directory-scoped learnings

    Returns:
        ID of saved learning, or None if failed
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        import psycopg2

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
            return learning_id
    except psycopg2.OperationalError as e:
        mark_connection_failed()
        print(f"Error saving learning (connection issue): {e}", file=sys.stderr)
        return None
    except psycopg2.InterfaceError as e:
        mark_connection_failed()
        print(f"Error saving learning (interface issue): {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error saving learning: {e}", file=sys.stderr)
        return None
    finally:
        conn.close()


def get_git_info(cwd: str) -> Dict[str, Any]:
    """
    Get all git info in a single cached subprocess call.
    Returns dict with: repo_identifier, git_root, relative_path, org_identifier
    """
    now = time.time()

    # Check cache
    if cwd in _git_info_cache:
        cached_info, cached_time = _git_info_cache[cwd]
        if now - cached_time < _GIT_CACHE_TTL:
            return cached_info

    # Default result
    result = {
        'repo_identifier': os.path.basename(os.path.abspath(cwd)),
        'git_root': None,
        'relative_path': None,
        'org_identifier': None
    }

    try:
        # Get git root
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=1  # Reduced from 5s
        )

        if proc.returncode == 0 and proc.stdout.strip():
            result['git_root'] = proc.stdout.strip()

            # Get remote URL
            remote_proc = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=1
            )

            if remote_proc.returncode == 0 and remote_proc.stdout.strip():
                remote = remote_proc.stdout.strip()
                if remote.endswith('.git'):
                    remote = remote[:-4]
                parts = remote.split('/')
                if len(parts) >= 2:
                    result['repo_identifier'] = f"{parts[-2]}/{parts[-1]}"
                    result['org_identifier'] = parts[-2]

            # Calculate relative path
            abs_cwd = os.path.abspath(cwd)
            if abs_cwd != result['git_root']:
                try:
                    rel = os.path.relpath(abs_cwd, result['git_root'])
                    if rel and rel != '.':
                        result['relative_path'] = rel
                except ValueError:
                    pass
    except (subprocess.TimeoutExpired, Exception):
        pass

    # Cache result
    _git_info_cache[cwd] = (result, now)
    return result


def get_repo_identifier(cwd: str) -> str:
    """Get repository identifier with caching."""
    git_info = get_git_info(cwd)
    return git_info.get('repo_identifier', os.path.basename(os.path.abspath(cwd)))


def get_git_root(cwd: str) -> Optional[str]:
    """Get the root directory of the git repository (cached)."""
    return get_git_info(cwd).get('git_root')


def get_relative_path(cwd: str) -> Optional[str]:
    """Get the relative path from git root (cached)."""
    return get_git_info(cwd).get('relative_path')


def get_org_identifier(repo_identifier: str) -> Optional[str]:
    """
    Extract organization identifier from repo identifier.

    Args:
        repo_identifier: Repository identifier (e.g., "owner/repo")

    Returns:
        Organization identifier (e.g., "owner"), or None
    """
    if not repo_identifier or '/' not in repo_identifier:
        return None
    return repo_identifier.split('/')[0]


def get_path_ancestors(path: str) -> List[str]:
    """
    Get all ancestor paths for a given path.

    Args:
        path: Relative path (e.g., "apps/web/components")

    Returns:
        List of ancestor paths including the path itself
        (e.g., ["apps/web/components", "apps/web", "apps"])
    """
    if not path:
        return []

    ancestors = [path]
    while '/' in path:
        path = os.path.dirname(path)
        if path:
            ancestors.append(path)
    return ancestors


def search_learnings_by_scope(
    cwd: str,
    query: Optional[str] = None,
    limit: int = 10,
    scope_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search learnings across all applicable scopes (cascading).

    Retrieves learnings from:
    - global scope
    - organization scope (if in a repo)
    - repository scope (if in a repo)
    - directory scope (if in a subdirectory)

    Args:
        cwd: Current working directory
        query: Optional search query to filter learnings
        limit: Maximum number of results to return
        scope_filter: Optional scope filter ('global', 'organization', 'repository', 'directory')

    Returns:
        List of matching learnings with scope_level included
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        import psycopg2
        import psycopg2.extras

        # Use cached git info instead of multiple subprocess calls
        git_info = get_git_info(cwd)
        repo_id = git_info.get('repo_identifier')
        org_id = git_info.get('org_identifier')
        rel_path = git_info.get('relative_path')
        path_ancestors = get_path_ancestors(rel_path) if rel_path else []

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Build the scope conditions
            conditions = []
            params = []

            if scope_filter:
                # Filter to specific scope only
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
                # Cascade: include all applicable scopes
                # 1. Global scope
                conditions.append("(scope_level = 'global')")

                # 2. Organization scope
                if org_id:
                    conditions.append("(scope_level = 'organization' AND repo_identifier = %s)")
                    params.append(org_id)

                # 3. Repository scope
                if repo_id:
                    conditions.append("(scope_level = 'repository' AND repo_identifier = %s)")
                    params.append(repo_id)

                # 4. Directory scope (current + ancestors)
                if repo_id and path_ancestors:
                    dir_placeholders = ', '.join(['%s'] * len(path_ancestors))
                    conditions.append(f"(scope_level = 'directory' AND repo_identifier = %s AND directory_path IN ({dir_placeholders}))")
                    params.append(repo_id)
                    params.extend(path_ancestors)

            # Build WHERE clause
            scope_where = ' OR '.join(conditions) if conditions else 'TRUE'

            if query:
                # Add text search
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
            return [dict(row) for row in results]

    except psycopg2.OperationalError as e:
        mark_connection_failed()
        print(f"Error searching learnings by scope (connection issue): {e}", file=sys.stderr)
        return []
    except psycopg2.InterfaceError as e:
        mark_connection_failed()
        print(f"Error searching learnings by scope (interface issue): {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error searching learnings by scope: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()


def find_similar_learnings(
    cwd: str,
    title: str,
    content: str,
    threshold: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Find learnings similar to the given title/content.
    Uses simple keyword overlap for now (could upgrade to embedding similarity later).

    Args:
        cwd: Current working directory
        title: Title to compare
        content: Content to compare
        threshold: Similarity threshold (0-1)

    Returns:
        List of similar learnings
    """
    # Get all learnings in scope
    all_learnings = search_learnings_by_scope(cwd, limit=100)

    if not all_learnings:
        return []

    # Simple similarity check using word overlap
    query_words = set(f"{title} {content}".lower().split())

    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                  'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                  'as', 'into', 'through', 'during', 'before', 'after', 'above',
                  'below', 'this', 'that', 'these', 'those', 'it', 'its'}

    query_words = query_words - stop_words

    similar = []
    for learning in all_learnings:
        learning_text = f"{learning.get('title', '')} {learning.get('content', '')}"
        learning_words = set(learning_text.lower().split()) - stop_words

        if not query_words or not learning_words:
            continue

        intersection = query_words & learning_words
        union = query_words | learning_words
        similarity = len(intersection) / len(union) if union else 0

        if similarity >= threshold:
            similar.append(learning)

    return similar
