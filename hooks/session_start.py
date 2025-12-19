#!/usr/bin/env python3
"""
SessionStart Hook
Runs when a Claude Code session starts.
Loads relevant learnings from agent memory if available.
"""

import json
import os
import sys
import subprocess

# Determine if we're running from global hooks or local
# Support both ~/.claude/hooks/ and repo-local hooks/
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir.startswith(os.path.expanduser("~/.claude/hooks")):
    # Running from global hooks - use the memory module from the skills repo
    skills_root = os.environ.get("CLAUDE_SKILLS_ROOT",
        os.path.expanduser("~/conductor/workspaces/claude-skills/beirut"))
    memory_dir = os.path.join(skills_root, "memory")
else:
    # Running from repo-local hooks
    repo_root = os.path.dirname(script_dir)
    memory_dir = os.path.join(repo_root, "memory")

sys.path.insert(0, memory_dir)


def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id")
        transcript_path = input_data.get("transcript_path")
        cwd = input_data.get("cwd", os.getcwd())

        # Run ensure_db.sh script
        ensure_db_script = os.path.join(memory_dir, "scripts", "ensure_db.sh")
        try:
            subprocess.run([ensure_db_script], timeout=15, check=False, capture_output=True)
        except Exception as e:
            # Don't fail if database setup fails
            pass

        # Check if database is available
        # Note: hook_db uses direct SQL text search, doesn't need OPENAI_API_KEY
        # OPENAI_API_KEY is only needed for semantic/embedding search via agno

        try:
            from agent_memory import hook_db

            # Initialize database
            db_available = hook_db.init_db()

            if db_available:
                # Get repository identifier for display
                repo_identifier = hook_db.get_repo_identifier(cwd)

                # Search for learnings across all applicable scopes (cascading)
                learnings = hook_db.search_learnings_by_scope(cwd, limit=10)

                if learnings:
                    # Count learnings by scope for the header
                    scope_counts = {}
                    for l in learnings:
                        scope = l.get('scope_level', 'repository')
                        scope_counts[scope] = scope_counts.get(scope, 0) + 1

                    # Build scope summary
                    scope_parts = []
                    for scope in ['global', 'organization', 'repository', 'directory']:
                        if scope in scope_counts:
                            scope_parts.append(f"{scope_counts[scope]} {scope}")
                    scope_summary = " + ".join(scope_parts) if scope_parts else f"{len(learnings)} total"

                    # Format learnings as context
                    context_parts = [
                        f"# Agent Memory: {repo_identifier}",
                        "",
                        f"Found {len(learnings)} previous learnings ({scope_summary}):",
                        ""
                    ]

                    for i, learning in enumerate(learnings, 1):
                        scope_label = f"[{learning.get('scope_level', 'repository')}]"
                        context_parts.append(f"## Learning {i}: {learning['title']} {scope_label}")
                        if learning.get('category'):
                            context_parts.append(f"**Category**: {learning['category']}")
                        if learning.get('tags'):
                            context_parts.append(f"**Tags**: {', '.join(learning['tags'])}")
                        context_parts.append("")
                        context_parts.append(learning['content'])
                        context_parts.append("")
                        context_parts.append("---")
                        context_parts.append("")

                    additional_context = "\n".join(context_parts)

                    # Output hook response with context
                    output = {
                        "hookSpecificOutput": {
                            "hookEventName": "SessionStart",
                            "additionalContext": additional_context
                        }
                    }
                    print(json.dumps(output))
                else:
                    # No learnings found
                    output = {
                        "hookSpecificOutput": {
                            "hookEventName": "SessionStart",
                            "additionalContext": f"# Agent Memory: {repo_identifier}\n\nNo previous learnings found for this repository. Propose learnings using <proposed_learning> tags."
                        }
                    }
                    print(json.dumps(output))
            else:
                # Database not available
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": "# Agent Memory\n\nMemory system offline (database unavailable). Run: docker compose up -d"
                    }
                }
                print(json.dumps(output))

        except ImportError:
            # agent_memory module not available
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "# Agent Memory\n\nMemory system offline (module not found)"
                }
            }
            print(json.dumps(output))

    except Exception as e:
        # Always exit successfully to avoid breaking sessions
        # Output minimal context on error
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"# Agent Memory\n\nMemory system offline (error: {str(e)})"
            }
        }
        print(json.dumps(output))

    # Always exit 0 to avoid breaking sessions
    sys.exit(0)


if __name__ == "__main__":
    main()
