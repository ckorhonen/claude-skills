#!/usr/bin/env python3
"""
Stop Hook
Runs when a Claude Code session stops.
Extracts proposed learnings from the transcript and saves them as pending.
Also performs automatic learning extraction via LLM analysis.
"""

import json
import os
import sys
import re
from datetime import datetime

# Determine if we're running from global hooks or local
# Support both ~/.claude/hooks/ and repo-local hooks/
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir.startswith(os.path.expanduser("~/.claude/hooks")):
    # Running from global hooks - use the memory module from the skills repo
    # The CLAUDE_SKILLS_ROOT env var should point to the skills repo
    skills_root = os.environ.get("CLAUDE_SKILLS_ROOT",
        os.path.expanduser("~/conductor/workspaces/claude-skills/beirut"))
    memory_dir = os.path.join(skills_root, "memory")
else:
    # Running from repo-local hooks
    repo_root = os.path.dirname(script_dir)
    memory_dir = os.path.join(repo_root, "memory")

sys.path.insert(0, memory_dir)


def parse_transcript(transcript_path):
    """Parse JSONL transcript and extract messages."""
    messages = []
    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        message = json.loads(line)
                        messages.append(message)
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    return messages


def extract_proposed_learning(message_content):
    """Extract proposed learning from message content."""
    if not isinstance(message_content, str):
        return None

    # Look for <proposed_learning>JSON</proposed_learning> block
    pattern = r'<proposed_learning>\s*(\{.*?\})\s*</proposed_learning>'
    match = re.search(pattern, message_content, re.DOTALL)

    if match:
        try:
            learning_json = match.group(1)
            learning_data = json.loads(learning_json)
            return learning_data
        except json.JSONDecodeError:
            pass

    return None


def get_last_assistant_message(messages):
    """Get the last assistant message from the transcript."""
    for message in reversed(messages):
        if message.get('role') == 'assistant':
            # Get content from the message
            content = message.get('content')
            if isinstance(content, list):
                # Content is an array of content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text_parts.append(block.get('text', ''))
                return '\n'.join(text_parts)
            elif isinstance(content, str):
                return content
    return None


def save_learning_to_db(learning_data, session_id, cwd):
    """Save learning directly to the database (auto-save mode)."""
    try:
        from agent_memory import hook_db

        # Get scope from learning data (default: repository)
        scope_level = learning_data.get('scope', 'repository')

        # Determine repo_identifier and directory_path based on scope
        if scope_level == 'global':
            repo_identifier = None
            directory_path = None
        elif scope_level == 'organization':
            repo_id = hook_db.get_repo_identifier(cwd)
            repo_identifier = hook_db.get_org_identifier(repo_id)
            directory_path = None
        elif scope_level == 'directory':
            repo_identifier = hook_db.get_repo_identifier(cwd)
            directory_path = hook_db.get_relative_path(cwd)
        else:
            # Default: repository scope
            scope_level = 'repository'
            repo_identifier = hook_db.get_repo_identifier(cwd)
            directory_path = None

        # Map learning fields to database fields
        title = learning_data.get('title', 'Untitled Learning')
        content = learning_data.get('learning', learning_data.get('content', ''))
        context = learning_data.get('context', '')
        confidence = learning_data.get('confidence', 'medium')
        learning_type = learning_data.get('type', 'heuristic')

        # Build full content with context
        full_content = f"{content}\n\n**Context**: {context}" if context else content

        # Extract tags from the learning type and confidence
        tags = learning_data.get('tags', [])
        if learning_type and learning_type not in tags:
            tags.append(learning_type)
        if confidence and confidence not in tags:
            tags.append(confidence)

        # Save to database with scope
        learning_id = hook_db.save_learning(
            repo_identifier=repo_identifier,
            title=title,
            content=full_content,
            category=learning_type,
            tags=tags,
            session_id=session_id,
            metadata={'confidence': confidence, 'context': context},
            scope_level=scope_level,
            directory_path=directory_path
        )

        return learning_id is not None
    except ImportError:
        return False
    except Exception:
        return False


def save_pending_learning(learning_data, session_id, cwd=None):
    """Save proposed learning as pending (backup if auto-save fails)."""
    try:
        # Add metadata
        learning_data['session_id'] = session_id
        learning_data['proposed_at'] = datetime.utcnow().isoformat()

        # Determine where to save pending learning
        if cwd:
            learnings_dir = os.path.join(cwd, ".claude", "learnings")
        else:
            learnings_dir = os.path.expanduser("~/.claude/learnings")

        os.makedirs(learnings_dir, exist_ok=True)

        # Write to pending.json
        pending_path = os.path.join(learnings_dir, "pending.json")
        with open(pending_path, 'w') as f:
            json.dump(learning_data, f, indent=2)

        return True
    except Exception:
        return False


def extract_learnings_automatically(messages, session_id, cwd):
    """
    Use LLM to automatically extract learnings from the transcript.

    Args:
        messages: List of transcript messages
        session_id: Current session ID
        cwd: Current working directory

    Returns:
        Number of learnings saved
    """
    try:
        from agent_memory.llm_extractor import extract_learnings
        from agent_memory import hook_db

        # Get existing learnings for deduplication
        existing = hook_db.search_learnings_by_scope(cwd, limit=50)

        # Extract learnings via LLM
        extracted = extract_learnings(messages, existing)

        if not extracted:
            return 0

        saved_count = 0
        for learning in extracted:
            # Map extracted learning fields to database format
            title = learning.get('title', 'Untitled')
            content = learning.get('learning', '')
            context = learning.get('context', '')
            confidence = learning.get('confidence', 'medium')
            learning_type = learning.get('type', 'heuristic')

            # Build full content with context
            full_content = f"{content}\n\n**Context**: {context}" if context else content

            # Extract tags
            tags = [learning_type, confidence] if learning_type else [confidence]

            # Determine scope (default to repository)
            scope_level = learning.get('scope', 'repository')

            # Get identifiers based on scope
            if scope_level == 'global':
                repo_identifier = None
                directory_path = None
            elif scope_level == 'directory':
                repo_identifier = hook_db.get_repo_identifier(cwd)
                directory_path = hook_db.get_relative_path(cwd)
            else:
                scope_level = 'repository'
                repo_identifier = hook_db.get_repo_identifier(cwd)
                directory_path = None

            # Save to database
            learning_id = hook_db.save_learning(
                repo_identifier=repo_identifier,
                title=title,
                content=full_content,
                category=learning_type,
                tags=tags,
                session_id=session_id,
                metadata={'confidence': confidence, 'context': context, 'auto_extracted': True},
                scope_level=scope_level,
                directory_path=directory_path
            )

            if learning_id:
                saved_count += 1

        return saved_count

    except ImportError as e:
        print(f"LLM extractor not available: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error in automatic extraction: {e}", file=sys.stderr)
        return 0


def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        transcript_path = input_data.get("transcript_path")
        stop_hook_active = input_data.get("stop_hook_active", False)
        session_id = input_data.get("session_id")
        cwd = input_data.get("cwd", os.getcwd())

        # If stop_hook_active is true, exit to avoid loops
        if stop_hook_active:
            sys.exit(0)

        # Parse the transcript
        if transcript_path and os.path.exists(transcript_path):
            messages = parse_transcript(transcript_path)

            # Get the last assistant message
            last_message = get_last_assistant_message(messages)

            proposed_learning = None
            if last_message:
                # Extract proposed learning from explicit tags
                proposed_learning = extract_proposed_learning(last_message)

                if proposed_learning:
                    # AUTO-SAVE: Try to save directly to database
                    saved_to_db = save_learning_to_db(proposed_learning, session_id, cwd)

                    if not saved_to_db:
                        # Fallback: Save as pending for manual save
                        save_pending_learning(proposed_learning, session_id, cwd)

            # AUTOMATIC EXTRACTION: If no explicit learning proposed, try LLM extraction
            if not proposed_learning:
                extract_learnings_automatically(messages, session_id, cwd)

    except Exception as e:
        # Always exit successfully to avoid breaking session stop
        # Log error for debugging
        print(f"Stop hook error: {e}", file=sys.stderr)

    # Never block stopping - always exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()
