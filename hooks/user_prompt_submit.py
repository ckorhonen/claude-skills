#!/usr/bin/env python3
"""
UserPromptSubmit Hook
Runs when a user submits a prompt.
Handles learning commands and injects relevant context for normal prompts.

Supports scope-aware commands:
- !learnings [query] [--global|--scope=X]
- !save-learning [--global|--scope=X]
- !audit [filter] [--limit=N]
"""

import json
import os
import sys
import re
import time

# Determine memory module location
# Priority: ~/.claude/memory (global install) > repo-local memory/
script_dir = os.path.dirname(os.path.abspath(__file__))
global_memory_dir = os.path.expanduser("~/.claude/memory")
local_memory_dir = os.path.join(os.path.dirname(script_dir), "memory")

if os.path.exists(global_memory_dir):
    memory_dir = global_memory_dir
    repo_root = os.path.expanduser("~/.claude")
else:
    memory_dir = local_memory_dir
    repo_root = os.path.dirname(script_dir)

sys.path.insert(0, memory_dir)

# Import audit logging (fail-safe)
try:
    from agent_memory.audit_log import log_event, get_recent_logs, format_logs_for_display
except ImportError:
    def log_event(*args, **kwargs): pass
    def get_recent_logs(*args, **kwargs): return []
    def format_logs_for_display(logs): return "Audit logging module not available."


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


def _search_with_fallback(cwd: str, query: str = None, limit: int = 5):
    """
    Search learnings via daemon (fast path) or direct DB (fallback).

    Args:
        cwd: Current working directory
        query: Optional search query
        limit: Maximum results

    Returns:
        List of learning dicts
    """
    # Try daemon first (fast path - sub-10ms)
    try:
        from agent_memory.daemon_client import is_daemon_running, get_client

        if is_daemon_running():
            client = get_client()
            result = client.search_learnings(cwd, query, limit)
            if result is not None:
                return result
    except ImportError:
        pass

    # Fallback to direct database (slower but works without daemon)
    try:
        from agent_memory import hook_db
        return hook_db.search_learnings_by_scope(cwd, query, limit)
    except ImportError:
        return []


def main():
    start_time = time.perf_counter()
    session_id = None
    cwd = None

    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        user_prompt = input_data.get("user_prompt", "")
        transcript_path = input_data.get("transcript_path")
        cwd = input_data.get("cwd", os.getcwd())
        session_id = input_data.get("session_id")

        log_event("hook_invoked", hook_name="user_prompt_submit", session_id=session_id, cwd=cwd)

        # Check for learning commands
        if user_prompt.strip().startswith("!"):
            command = user_prompt.strip()

            # !save-learning command (supports --global, --scope=X)
            if command.startswith("!save-learning"):
                log_event("command_handled", hook_name="user_prompt_submit",
                          data={"command": "save-learning"})
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
                        log_event("learning_saved", hook_name="user_prompt_submit",
                                  session_id=session_id,
                                  data={"learning_id": learning_id, "title": pending.get('title'), "scope": scope_level})
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
                log_event("command_handled", hook_name="user_prompt_submit",
                          data={"command": "discard-learning"})
                clear_pending_learning()
                output = {
                    "decision": "block",
                    "reason": "Discarded pending learning."
                }
                print(json.dumps(output))
                sys.exit(0)

            # !pending-learning command
            elif command == "!pending-learning":
                log_event("command_handled", hook_name="user_prompt_submit",
                          data={"command": "pending-learning"})
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

            # !audit [filter] [--limit=N] command
            elif command.startswith("!audit"):
                log_event("command_handled", hook_name="user_prompt_submit",
                          data={"command": "audit"})

                parts = command.split()
                event_filter = None
                limit = 50

                for part in parts[1:]:
                    if part.startswith("--limit="):
                        try:
                            limit = int(part.split("=")[1])
                        except ValueError:
                            pass
                    elif not part.startswith("--"):
                        event_filter = part

                logs = get_recent_logs(limit=limit, event_filter=event_filter)
                result = format_logs_for_display(logs)

                output = {
                    "decision": "block",
                    "reason": result
                }
                print(json.dumps(output))
                sys.exit(0)

            # !learnings [query] [--global|--scope=X] command
            elif command.startswith("!learnings"):
                log_event("command_handled", hook_name="user_prompt_submit",
                          data={"command": "learnings"})

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
            # Search for learnings relevant to the prompt (uses daemon if available)
            learnings = _search_with_fallback(cwd, user_prompt, limit=5)

            log_event("learnings_searched", hook_name="user_prompt_submit",
                      session_id=session_id, data={"count": len(learnings)})

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
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_event("hook_error", level="ERROR", hook_name="user_prompt_submit",
                  session_id=session_id, cwd=cwd, error=str(e), duration_ms=duration_ms)
        # Log error to stderr for debugging
        import traceback
        print(f"Error in user_prompt_submit hook: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        output = {"decision": "allow"}
        print(json.dumps(output))

    # Log completion
    duration_ms = (time.perf_counter() - start_time) * 1000
    log_event("hook_completed", hook_name="user_prompt_submit",
              session_id=session_id, cwd=cwd, duration_ms=duration_ms)

    # Always exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()
