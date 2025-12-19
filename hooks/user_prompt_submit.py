#!/usr/bin/env python3
"""
UserPromptSubmit Hook
Runs when a user submits a prompt.
Handles learning commands and injects relevant context for normal prompts.

Supports scope-aware commands:
- !learnings [query] [--global|--scope=X]
- !save-learning [--global|--scope=X]
"""

import json
import os
import sys
import re

# Determine if we're running from global hooks or local
# Support both ~/.claude/hooks/ and repo-local hooks/
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir.startswith(os.path.expanduser("~/.claude/hooks")):
    # Running from global hooks - use the memory module from the skills repo
    skills_root = os.environ.get("CLAUDE_SKILLS_ROOT",
        os.path.expanduser("~/conductor/workspaces/claude-skills/beirut"))
    memory_dir = os.path.join(skills_root, "memory")
    repo_root = skills_root
else:
    # Running from repo-local hooks
    repo_root = os.path.dirname(script_dir)
    memory_dir = os.path.join(repo_root, "memory")

sys.path.insert(0, memory_dir)


def parse_scope_flags(command: str) -> tuple:
    """
    Parse scope flags from a command string.

    Args:
        command: Command string (e.g., "!learnings foo --global")

    Returns:
        Tuple of (command_without_flags, scope_filter)
        scope_filter is one of: None, 'global', 'organization', 'repository', 'directory'
    """
    scope_filter = None

    # Check for --global flag
    if '--global' in command:
        command = command.replace('--global', '').strip()
        scope_filter = 'global'

    # Check for --scope=X flag
    scope_match = re.search(r'--scope=(\w+)', command)
    if scope_match:
        scope_filter = scope_match.group(1)
        command = re.sub(r'--scope=\w+', '', command).strip()

    # Clean up multiple spaces
    command = ' '.join(command.split())

    return command, scope_filter


def load_pending_learning():
    """Load pending learning from .claude/learnings/pending.json"""
    try:
        pending_path = os.path.join(repo_root, ".claude", "learnings", "pending.json")
        if os.path.exists(pending_path):
            with open(pending_path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None


def save_pending_learning(data):
    """Save pending learning to .claude/learnings/pending.json"""
    try:
        pending_dir = os.path.join(repo_root, ".claude", "learnings")
        os.makedirs(pending_dir, exist_ok=True)
        pending_path = os.path.join(pending_dir, "pending.json")
        with open(pending_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def clear_pending_learning():
    """Clear pending learning file"""
    try:
        pending_path = os.path.join(repo_root, ".claude", "learnings", "pending.json")
        if os.path.exists(pending_path):
            os.remove(pending_path)
        return True
    except Exception:
        return False


def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        user_prompt = input_data.get("user_prompt", "")
        transcript_path = input_data.get("transcript_path")
        cwd = input_data.get("cwd", os.getcwd())

        # Check for learning commands
        if user_prompt.strip().startswith("!"):
            command = user_prompt.strip()

            # !save-learning command (supports --global, --scope=X)
            if command.startswith("!save-learning"):
                # Parse scope flags
                _, scope_override = parse_scope_flags(command)

                pending = load_pending_learning()
                if not pending:
                    output = {
                        "decision": "block",
                        "reason": "No pending learning found. Create a learning first by asking Claude to propose one."
                    }
                    print(json.dumps(output))
                    sys.exit(0)

                try:
                    from agent_memory import hook_db

                    # Determine scope (override takes precedence, then pending data, then default)
                    scope_level = scope_override or pending.get("scope", "repository")

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

                    # Save the learning with scope
                    learning_id = hook_db.save_learning(
                        repo_identifier=repo_identifier,
                        title=pending.get("title", "Untitled"),
                        content=pending.get("content", ""),
                        category=pending.get("category"),
                        tags=pending.get("tags", []),
                        session_id=pending.get("session_id"),
                        metadata=pending.get("metadata"),
                        scope_level=scope_level,
                        directory_path=directory_path
                    )

                    if learning_id:
                        clear_pending_learning()
                        scope_info = f" [{scope_level}]" if scope_level != 'repository' else ""
                        output = {
                            "decision": "block",
                            "reason": f"Saved learning{scope_info}: {pending.get('title', 'Untitled')} (ID: {learning_id})"
                        }
                    else:
                        output = {
                            "decision": "block",
                            "reason": "Failed to save learning. Database may be unavailable."
                        }

                except ImportError:
                    output = {
                        "decision": "block",
                        "reason": "Agent memory module not available. Cannot save learning."
                    }

                print(json.dumps(output))
                sys.exit(0)

            # !discard-learning command
            elif command == "!discard-learning":
                clear_pending_learning()
                output = {
                    "decision": "block",
                    "reason": "Discarded pending learning."
                }
                print(json.dumps(output))
                sys.exit(0)

            # !pending-learning command
            elif command == "!pending-learning":
                pending = load_pending_learning()
                if pending:
                    summary = f"**Pending Learning: {pending.get('title', 'Untitled')}**\n\n"
                    if pending.get('category'):
                        summary += f"Category: {pending['category']}\n"
                    if pending.get('tags'):
                        summary += f"Tags: {', '.join(pending['tags'])}\n"
                    summary += f"\n{pending.get('content', '')}\n\n"
                    summary += "Use `!save-learning` to save or `!discard-learning` to discard."

                    output = {
                        "decision": "block",
                        "reason": summary
                    }
                else:
                    output = {
                        "decision": "block",
                        "reason": "No pending learning found."
                    }
                print(json.dumps(output))
                sys.exit(0)

            # !learnings [query] [--global|--scope=X] command
            elif command.startswith("!learnings"):
                # Parse scope flags first
                clean_command, scope_filter = parse_scope_flags(command)

                # Extract query from cleaned command
                parts = clean_command.split(maxsplit=1)
                query = parts[1] if len(parts) > 1 else None

                try:
                    from agent_memory import hook_db

                    # Get repository identifier for display
                    repo_identifier = hook_db.get_repo_identifier(cwd)

                    # Search learnings with scope awareness
                    learnings = hook_db.search_learnings_by_scope(
                        cwd=cwd,
                        query=query,
                        limit=20,
                        scope_filter=scope_filter
                    )

                    if learnings:
                        # Count by scope for summary
                        scope_counts = {}
                        for l in learnings:
                            scope = l.get('scope_level', 'repository')
                            scope_counts[scope] = scope_counts.get(scope, 0) + 1

                        scope_parts = []
                        for scope in ['global', 'organization', 'repository', 'directory']:
                            if scope in scope_counts:
                                scope_parts.append(f"{scope_counts[scope]} {scope}")
                        scope_summary = " + ".join(scope_parts)

                        result = f"Found {len(learnings)} learnings"
                        if query:
                            result += f" matching '{query}'"
                        if scope_filter:
                            result += f" (filtered to {scope_filter} scope)"
                        else:
                            result += f" ({scope_summary})"
                        result += f":\n\n"

                        for i, learning in enumerate(learnings, 1):
                            scope_label = f"[{learning.get('scope_level', 'repository')}]"
                            result += f"{i}. **{learning['title']}** {scope_label}"
                            if learning.get('category'):
                                result += f" [{learning['category']}]"
                            result += "\n"
                            if learning.get('tags'):
                                result += f"   Tags: {', '.join(learning['tags'])}\n"
                            # Show first 200 chars of content
                            content = learning.get('content', '')
                            if len(content) > 200:
                                content = content[:200] + "..."
                            result += f"   {content}\n\n"

                        output = {
                            "decision": "block",
                            "reason": result
                        }
                    else:
                        message = f"No learnings found"
                        if query:
                            message += f" matching '{query}'"
                        if scope_filter:
                            message += f" in {scope_filter} scope"
                        message += "."

                        output = {
                            "decision": "block",
                            "reason": message
                        }

                except ImportError:
                    output = {
                        "decision": "block",
                        "reason": "Agent memory module not available."
                    }

                print(json.dumps(output))
                sys.exit(0)

        # Normal prompt - inject relevant learnings as context
        try:
            from agent_memory import hook_db

            # Search for learnings relevant to the prompt (across all applicable scopes)
            learnings = hook_db.search_learnings_by_scope(cwd, user_prompt, limit=5)

            if learnings:
                context_parts = [
                    "# Relevant Learnings",
                    ""
                ]

                for learning in learnings:
                    scope_label = f"[{learning.get('scope_level', 'repository')}]"
                    context_parts.append(f"## {learning['title']} {scope_label}")
                    if learning.get('category'):
                        context_parts.append(f"**Category**: {learning['category']}")
                    context_parts.append("")
                    context_parts.append(learning['content'])
                    context_parts.append("")

                additional_context = "\n".join(context_parts)

                output = {
                    "decision": "allow",
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": additional_context
                    }
                }
            else:
                # No relevant learnings, just allow
                output = {"decision": "allow"}

        except ImportError:
            # agent_memory not available, just allow
            output = {"decision": "allow"}

        print(json.dumps(output))

    except Exception as e:
        # Always exit successfully and allow the prompt
        # Log error to stderr for debugging
        import traceback
        print(f"Error in user_prompt_submit hook: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        output = {"decision": "allow"}
        print(json.dumps(output))

    # Always exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()
