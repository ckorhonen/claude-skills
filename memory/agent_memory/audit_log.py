#!/usr/bin/env python3
"""
Audit logging for the Claude Code memory system.
Provides fail-safe, structured logging with automatic rotation.
"""

import json
import os
import time
from datetime import datetime, timezone
from logging import Logger, getLogger, INFO, DEBUG
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional
from contextlib import contextmanager

# Constants
LOG_DIR = Path.home() / ".claude" / "logs"
LOG_FILE = LOG_DIR / "memory-audit.jsonl"
MAX_BYTES = 5 * 1024 * 1024  # 5MB per file
BACKUP_COUNT = 5  # Keep 5 rotated files

# Singleton logger instance
_logger: Optional[Logger] = None
_initialized = False


def _ensure_log_dir() -> bool:
    """Create log directory if it doesn't exist. Returns True on success."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def _get_logger() -> Optional[Logger]:
    """Get or create the singleton logger instance."""
    global _logger, _initialized

    if _initialized:
        return _logger

    _initialized = True

    # Fail gracefully if we can't create the log directory
    if not _ensure_log_dir():
        return None

    try:
        _logger = getLogger("claude_memory_audit")
        _logger.setLevel(DEBUG)

        # Prevent propagation to root logger
        _logger.propagate = False

        # Only add handler if not already present
        if not _logger.handlers:
            handler = RotatingFileHandler(
                str(LOG_FILE),
                maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT,
                encoding='utf-8'
            )
            handler.setLevel(DEBUG)
            _logger.addHandler(handler)

        return _logger
    except Exception:
        return None


def log_event(
    event: str,
    level: str = "INFO",
    hook_name: Optional[str] = None,
    session_id: Optional[str] = None,
    cwd: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    duration_ms: Optional[float] = None
) -> None:
    """
    Log an audit event. Never raises exceptions.

    Args:
        event: Event type (e.g., 'hook_invoked', 'learning_saved')
        level: Log level (DEBUG, INFO, WARN, ERROR)
        hook_name: Name of the hook (session_start, stop, user_prompt_submit)
        session_id: Claude session ID
        cwd: Current working directory
        data: Event-specific data dictionary
        error: Error message if applicable
        duration_ms: Duration in milliseconds
    """
    try:
        logger = _get_logger()
        if not logger:
            return

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event": event,
        }

        if hook_name:
            entry["hook_name"] = hook_name
        if session_id:
            entry["session_id"] = session_id
        if cwd:
            entry["cwd"] = cwd
        if data:
            entry["data"] = data
        if error:
            entry["error"] = error
        if duration_ms is not None:
            entry["duration_ms"] = round(duration_ms, 2)

        # Write as single-line JSON
        line = json.dumps(entry, default=str)
        logger.info(line)

    except Exception:
        # Never fail - silently ignore logging errors
        pass


@contextmanager
def timed_event(
    event: str,
    hook_name: Optional[str] = None,
    session_id: Optional[str] = None,
    cwd: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
):
    """
    Context manager that logs event start and completion with timing.

    Usage:
        with timed_event("auto_extraction", hook_name="stop") as ctx:
            # ... do work ...
            ctx["learnings_count"] = 5  # Add data to completion log
    """
    start_time = time.perf_counter()
    result_data = dict(data or {})

    log_event(
        event=f"{event}_started",
        level="INFO",
        hook_name=hook_name,
        session_id=session_id,
        cwd=cwd,
        data=result_data
    )

    try:
        yield result_data
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_event(
            event=f"{event}_completed",
            level="INFO",
            hook_name=hook_name,
            session_id=session_id,
            cwd=cwd,
            data=result_data,
            duration_ms=duration_ms
        )
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_event(
            event=f"{event}_error",
            level="ERROR",
            hook_name=hook_name,
            session_id=session_id,
            cwd=cwd,
            data=result_data,
            error=str(e),
            duration_ms=duration_ms
        )
        raise


def get_recent_logs(limit: int = 50, event_filter: Optional[str] = None) -> list:
    """
    Read recent log entries for the !audit command.

    Args:
        limit: Maximum number of entries to return
        event_filter: Optional event type filter (substring match)

    Returns:
        List of log entry dicts, most recent first
    """
    entries = []

    try:
        if not LOG_FILE.exists():
            return []

        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        if event_filter and event_filter not in entry.get('event', ''):
                            continue
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue

        # Return most recent first
        entries.reverse()
        return entries[:limit]

    except Exception:
        return []


def format_logs_for_display(logs: list) -> str:
    """Format log entries for human-readable display."""
    if not logs:
        return "No audit logs found. Logs are stored in ~/.claude/logs/memory-audit.jsonl"

    lines = [f"Recent audit logs ({len(logs)} entries):\n"]

    for entry in logs:
        ts = entry.get('timestamp', 'unknown')[:19]  # Trim to second
        level = entry.get('level', 'INFO')
        event = entry.get('event', 'unknown')
        hook = entry.get('hook_name', '')

        prefix = f"[{ts}] {level}"
        if hook:
            prefix += f" {hook}"

        line = f"{prefix}: {event}"

        if entry.get('error'):
            line += f" ERROR: {entry['error']}"
        elif entry.get('data'):
            data = entry['data']
            details = []
            if 'learnings_count' in data:
                details.append(f"count={data['learnings_count']}")
            if 'title' in data:
                title = data['title'][:30] + ('...' if len(data['title']) > 30 else '')
                details.append(f'"{title}"')
            if 'scope' in data:
                details.append(f"scope={data['scope']}")
            if details:
                line += f" ({', '.join(details)})"

        if entry.get('duration_ms'):
            line += f" [{entry['duration_ms']:.0f}ms]"

        lines.append(line)

    return '\n'.join(lines)
