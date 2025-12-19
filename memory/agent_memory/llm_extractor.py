#!/usr/bin/env python3
"""
LLM-based learning extraction from session transcripts.
Uses OpenAI API to analyze transcripts and extract project-specific knowledge.
"""

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional

# Optimized extraction prompt
EXTRACTION_PROMPT = """You are analyzing a Claude Code session transcript to extract valuable project-specific knowledge.

TASK: Identify learnings that would help Claude work more effectively on this project in future sessions.

INCLUDE only:
- User-stated preferences (coding style, formatting, tooling)
- Project-specific conventions discovered during the session
- Architectural decisions or patterns unique to this codebase
- Domain knowledge the user explained that Claude didn't initially know
- Corrections where the user refined Claude's approach

EXCLUDE:
- General programming knowledge (Claude already knows this)
- Common best practices (e.g., "use descriptive variable names")
- One-time debugging steps or temporary fixes
- Information that's obvious from reading the code
- Vague or context-dependent observations

OUTPUT FORMAT:
Return a JSON array. If no learnings qualify, return [].
Each learning must have:
{
  "title": "Brief, specific title (max 10 words)",
  "context": "When this applies (be specific)",
  "learning": "The actual insight (1-2 sentences)",
  "confidence": "high" | "medium",
  "type": "preference" | "convention" | "architecture" | "domain" | "process"
}

QUALITY BAR:
- Would this learning save Claude time in a future session?
- Is this specific to THIS project, not general knowledge?
- Would a new developer on this project benefit from knowing this?

If uncertain, err on the side of NOT including a learning.

TRANSCRIPT:
{transcript}"""


def truncate_transcript(messages: List[Dict], max_messages: int = 50) -> List[Dict]:
    """
    Truncate transcript to last N messages to fit within token limits.

    Args:
        messages: List of message dicts from the transcript
        max_messages: Maximum number of messages to keep

    Returns:
        Truncated list of messages
    """
    if len(messages) <= max_messages:
        return messages
    return messages[-max_messages:]


def format_transcript(messages: List[Dict]) -> str:
    """
    Format transcript messages into a readable string for the LLM.

    Args:
        messages: List of message dicts

    Returns:
        Formatted transcript string
    """
    formatted_parts = []

    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')

        # Handle content that is a list of content blocks
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get('type') == 'text':
                        text_parts.append(block.get('text', ''))
                    elif block.get('type') == 'tool_use':
                        tool_name = block.get('name', 'unknown')
                        text_parts.append(f"[Tool: {tool_name}]")
                    elif block.get('type') == 'tool_result':
                        text_parts.append("[Tool Result]")
            content = '\n'.join(text_parts)

        # Skip empty messages
        if not content or not content.strip():
            continue

        # Truncate very long messages
        if len(content) > 2000:
            content = content[:2000] + "... [truncated]"

        formatted_parts.append(f"[{role.upper()}]\n{content}\n")

    return '\n'.join(formatted_parts)


def call_openai_extraction(transcript_text: str, api_key: str, model: str = "gpt-5.1-mini") -> List[Dict]:
    """
    Call OpenAI API to extract learnings from transcript.

    Args:
        transcript_text: Formatted transcript string
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o-mini for cost efficiency)

    Returns:
        List of extracted learning dicts
    """
    try:
        import urllib.request
        import urllib.error

        url = "https://api.openai.com/v1/chat/completions"

        prompt = EXTRACTION_PROMPT.format(transcript=transcript_text)

        data = json.dumps({
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more consistent extraction
            "max_tokens": 2000
        }).encode('utf-8')

        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

        # Extract the response content
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        # Parse JSON from response
        learnings = parse_learnings_json(content)
        return learnings

    except urllib.error.URLError as e:
        print(f"OpenAI API error: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error calling OpenAI: {e}", file=sys.stderr)
        return []


def parse_learnings_json(content: str) -> List[Dict]:
    """
    Parse JSON array of learnings from LLM response.
    Handles various response formats (with or without markdown code blocks).

    Args:
        content: Raw response content from LLM

    Returns:
        List of learning dicts
    """
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', content)
    if json_match:
        content = json_match.group(1)

    # Try to find raw JSON array
    array_match = re.search(r'\[[\s\S]*\]', content)
    if array_match:
        content = array_match.group(0)

    try:
        learnings = json.loads(content)
        if isinstance(learnings, list):
            # Validate each learning has required fields
            valid_learnings = []
            for l in learnings:
                if isinstance(l, dict) and all(k in l for k in ['title', 'learning']):
                    valid_learnings.append(l)
            return valid_learnings
    except json.JSONDecodeError:
        pass

    return []


def compute_similarity(text1: str, text2: str) -> float:
    """
    Compute simple text similarity using word overlap (Jaccard similarity).

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score between 0 and 1
    """
    # Normalize texts
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                  'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                  'as', 'into', 'through', 'during', 'before', 'after', 'above',
                  'below', 'this', 'that', 'these', 'those', 'it', 'its'}

    words1 = words1 - stop_words
    words2 = words2 - stop_words

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union) if union else 0.0


def deduplicate(new_learnings: List[Dict], existing_learnings: List[Dict], threshold: float = 0.6) -> List[Dict]:
    """
    Remove learnings that are too similar to existing ones.

    Args:
        new_learnings: List of newly extracted learnings
        existing_learnings: List of existing learnings from database
        threshold: Similarity threshold above which to consider duplicate

    Returns:
        Filtered list of unique learnings
    """
    unique_learnings = []

    for new in new_learnings:
        new_text = f"{new.get('title', '')} {new.get('learning', '')} {new.get('context', '')}"

        is_duplicate = False
        for existing in existing_learnings:
            existing_text = f"{existing.get('title', '')} {existing.get('content', '')} {existing.get('category', '')}"

            similarity = compute_similarity(new_text, existing_text)
            if similarity >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_learnings.append(new)

    return unique_learnings


def extract_learnings(
    transcript_messages: List[Dict],
    existing_learnings: Optional[List[Dict]] = None,
    min_messages: int = 10
) -> List[Dict]:
    """
    Extract learnings from a session transcript using LLM.

    Args:
        transcript_messages: List of message dicts from the transcript
        existing_learnings: Optional list of existing learnings for deduplication
        min_messages: Minimum number of messages required to attempt extraction

    Returns:
        List of learning dicts ready for saving
    """
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []  # Graceful degradation

    # Skip very short sessions
    if len(transcript_messages) < min_messages:
        return []

    # Check if auto-extraction is disabled
    if os.environ.get("AUTO_EXTRACT_LEARNINGS", "true").lower() == "false":
        return []

    # Get model from environment or use default
    model = os.environ.get("EXTRACTION_MODEL", "gpt-5.1-mini")

    # Truncate transcript if too long
    messages = truncate_transcript(transcript_messages, max_messages=50)

    # Format for LLM
    transcript_text = format_transcript(messages)

    # Skip if transcript is too short after formatting
    if len(transcript_text) < 500:
        return []

    # Call OpenAI API
    learnings = call_openai_extraction(transcript_text, api_key, model)

    # Deduplicate against existing
    if existing_learnings and learnings:
        learnings = deduplicate(learnings, existing_learnings)

    return learnings


if __name__ == "__main__":
    # Test with sample input
    import sys

    if len(sys.argv) > 1:
        # Read transcript from file
        with open(sys.argv[1], 'r') as f:
            messages = []
            for line in f:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        learnings = extract_learnings(messages)
        print(json.dumps(learnings, indent=2))
    else:
        print("Usage: python llm_extractor.py <transcript.jsonl>")
