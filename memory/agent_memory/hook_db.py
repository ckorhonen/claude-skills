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
import subprocess
from typing import List, Dict, Optional, Any, Tuple


def get_connection():
    """Get a database connection using psycopg2."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        return psycopg2.connect(
            dbname="ai",
            user="ai",
            password="ai",
            host="localhost",
            port="5532"
        )
    except (ImportError, Exception):
        return None


def init_db():
    """Initialize database schema if it doesn't exist."""
    conn = get_connection()
    if not conn:
        return False

    try:
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
    except Exception as e:
        print(f"Error saving learning: {e}", file=sys.stderr)
        return None
    finally:
        conn.close()


def get_repo_identifier(cwd: str) -> str:
    """
    Get repository identifier from git remote or folder name.

    Args:
        cwd: Current working directory

    Returns:
        Repository identifier string
    """
    try:
        # Try to get git remote URL
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            remote = result.stdout.strip()
            # Normalize the remote URL to a consistent identifier
            # Remove .git suffix if present
            if remote.endswith('.git'):
                remote = remote[:-4]
            # Extract repo name from URL
            parts = remote.split('/')
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1]}"
            return remote
    except Exception:
        pass

    # Fallback to folder name
    return os.path.basename(os.path.abspath(cwd))


def get_git_root(cwd: str) -> Optional[str]:
    """
    Get the root directory of the git repository.

    Args:
        cwd: Current working directory

    Returns:
        Git root path, or None if not in a git repo
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_relative_path(cwd: str) -> Optional[str]:
    """
    Get the relative path from the git root to the current directory.

    Args:
        cwd: Current working directory

    Returns:
        Relative path from git root, or None if at root or not in git repo
    """
    git_root = get_git_root(cwd)
    if not git_root:
        return None

    abs_cwd = os.path.abspath(cwd)
    if abs_cwd == git_root:
        return None  # At root, no subdirectory

    # Get relative path
    try:
        rel_path = os.path.relpath(abs_cwd, git_root)
        if rel_path and rel_path != '.':
            return rel_path
    except ValueError:
        pass
    return None


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
        import psycopg2.extras

        repo_id = get_repo_identifier(cwd)
        org_id = get_org_identifier(repo_id)
        rel_path = get_relative_path(cwd)
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
