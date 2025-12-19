"""Transcript parsing utilities for extracting learnings from agent conversations."""

import json
import re
from typing import Any


def parse_transcript(path: str) -> list[dict[str, Any]]:
    """
    Parse a JSONL transcript file.

    Args:
        path: Path to the JSONL transcript file

    Returns:
        List of message dictionaries

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    messages = []

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError as e:
                    # Skip invalid lines but continue processing
                    print(f"Warning: Skipping invalid JSON line: {e}")
                    continue

    return messages


def extract_last_assistant_message(transcript: list[dict[str, Any]]) -> str:
    """
    Extract the last assistant message from a transcript.

    Args:
        transcript: List of message dictionaries

    Returns:
        The content of the last assistant message, or empty string if not found
    """
    # Iterate in reverse to find the last assistant message
    for message in reversed(transcript):
        if isinstance(message, dict):
            role = message.get('role', '')
            content = message.get('content', '')

            if role == 'assistant' and content:
                # Handle both string and list content
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Extract text from content blocks
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            text_parts.append(block.get('text', ''))
                    return '\n'.join(text_parts)

    return ""


def extract_proposed_learning(text: str) -> dict[str, Any] | None:
    """
    Extract JSON from <proposed_learning>...</proposed_learning> tags.

    Args:
        text: Text containing proposed_learning tags

    Returns:
        Parsed learning dictionary, or None if not found or invalid
    """
    # Find content between <proposed_learning> tags
    pattern = r'<proposed_learning>\s*(.*?)\s*</proposed_learning>'
    match = re.search(pattern, text, re.DOTALL)

    if not match:
        return None

    json_str = match.group(1).strip()

    # Try to parse as JSON
    try:
        learning = json.loads(json_str)
        return learning if isinstance(learning, dict) else None
    except json.JSONDecodeError:
        return None
