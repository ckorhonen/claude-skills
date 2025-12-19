"""Agent Memory - Self-learning memory subsystem for Claude Code."""

from .config import DB_URL, EMBEDDING_MODEL
from .knowledge import search_learnings, save_learning
from .formatting import format_learnings_for_context
from .transcript import parse_transcript, extract_last_assistant_message, extract_proposed_learning

__all__ = [
    "DB_URL",
    "EMBEDDING_MODEL",
    "search_learnings",
    "save_learning",
    "format_learnings_for_context",
    "parse_transcript",
    "extract_last_assistant_message",
    "extract_proposed_learning",
]

__version__ = "0.1.0"
