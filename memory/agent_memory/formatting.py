"""Formatting utilities for agent learnings."""

from typing import Any


def format_learnings_for_context(learnings: list[dict[str, Any]]) -> str:
    """
    Format learnings as markdown bullets for injection into context.

    Args:
        learnings: List of learning dictionaries

    Returns:
        Markdown-formatted string (~1200 chars max) with title, learning, and applicability
    """
    if not learnings:
        return ""

    lines = []
    total_chars = 0
    max_chars = 1200

    for learning in learnings:
        title = learning.get('title', 'Untitled')
        learning_text = learning.get('learning', '')
        context = learning.get('context', '')
        confidence = learning.get('confidence', 'unknown')

        # Create a one-line summary
        summary = learning_text.split('\n')[0] if learning_text else ''

        # Format: - **Title** (confidence): Learning | When: context
        line = f"- **{title}** ({confidence}): {summary}"
        if context:
            line += f" | When: {context}"
        line += "\n"

        # Check if adding this line would exceed the limit
        if total_chars + len(line) > max_chars and lines:
            break

        lines.append(line)
        total_chars += len(line)

    result = "".join(lines)

    # If we exceeded the limit, truncate and add ellipsis
    if total_chars > max_chars:
        result = result[:max_chars - 4] + "...\n"

    return result
