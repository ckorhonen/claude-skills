"""Agent Memory - Self-learning memory subsystem for Claude Code.

Uses lazy imports to avoid loading heavy dependencies (agno) until needed.
hook_db can be imported without loading the full agno stack.
"""

__all__ = [
    "DB_URL",
    "EMBEDDING_MODEL",
    "search_learnings",
    "save_learning",
    "format_learnings_for_context",
    "parse_transcript",
    "extract_last_assistant_message",
    "extract_proposed_learning",
    # Daemon client exports
    "DaemonClient",
    "get_client",
    "is_daemon_running",
    "start_daemon",
    "stop_daemon",
]

__version__ = "0.1.0"


def __getattr__(name):
    """Lazy import of submodules to avoid loading heavy dependencies until needed."""
    if name in ("DB_URL", "EMBEDDING_MODEL"):
        from .config import DB_URL, EMBEDDING_MODEL
        return DB_URL if name == "DB_URL" else EMBEDDING_MODEL
    elif name in ("search_learnings", "save_learning"):
        from .knowledge import search_learnings, save_learning
        return search_learnings if name == "search_learnings" else save_learning
    elif name == "format_learnings_for_context":
        from .formatting import format_learnings_for_context
        return format_learnings_for_context
    elif name in ("parse_transcript", "extract_last_assistant_message", "extract_proposed_learning"):
        from .transcript import parse_transcript, extract_last_assistant_message, extract_proposed_learning
        if name == "parse_transcript":
            return parse_transcript
        elif name == "extract_last_assistant_message":
            return extract_last_assistant_message
        else:
            return extract_proposed_learning
    # Daemon client exports
    elif name == "DaemonClient":
        from .daemon_client import DaemonClient
        return DaemonClient
    elif name == "get_client":
        from .daemon_client import get_client
        return get_client
    elif name == "is_daemon_running":
        from .daemon_client import is_daemon_running
        return is_daemon_running
    elif name == "start_daemon":
        from .daemon_client import start_daemon
        return start_daemon
    elif name == "stop_daemon":
        from .daemon_client import stop_daemon
        return stop_daemon
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
