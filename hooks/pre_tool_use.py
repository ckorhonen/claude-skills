#!/usr/bin/env python3
"""Pre-tool-use hook - guard dangerous bash commands.

This hook blocks potentially dangerous bash commands that could harm the system.
"""

import json
import re
import sys
from typing import Any, Optional

# Dangerous patterns to block (with explanations)
DANGEROUS_PATTERNS = [
    (r'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\s+/', "Recursive force delete from root"),
    (r'rm\s+-rf\s+/\s*$', "Delete entire filesystem"),
    (r'rm\s+-rf\s+~\s*$', "Delete home directory"),
    (r'rm\s+-rf\s+\*\s*$', "Delete all files in current directory"),
    (r'git\s+push\s+.*--force\s+.*(?:main|master)', "Force push to main/master"),
    (r'git\s+push\s+-f\s+.*(?:main|master)', "Force push to main/master"),
    (r'>\s*/dev/sd[a-z]', "Write to raw disk device"),
    (r'dd\s+if=.*of=/dev/sd[a-z]', "DD to raw disk device"),
    (r'mkfs\s+', "Format filesystem"),
    (r':()\{\s*:\|:&\s*\};:', "Fork bomb"),
    (r'chmod\s+-R\s+777\s+/', "Recursive chmod 777 from root"),
    (r'chown\s+-R\s+.*\s+/', "Recursive chown from root"),
]


def read_stdin() -> dict[str, Any]:
    """Read and parse JSON from stdin safely."""
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, Exception):
        return {}


def emit_output(
    permission_decision: Optional[str] = None,
    reason: Optional[str] = None,
) -> None:
    """Emit hook output."""
    output: dict[str, Any] = {}

    if permission_decision:
        output["hookSpecificOutput"] = {
            "permissionDecision": permission_decision
        }

    if reason:
        output["reason"] = reason

    if output:
        print(json.dumps(output))


def check_command(command: str) -> tuple[str, Optional[str]]:
    """Check command for dangerous patterns.

    Returns (decision, reason) where decision is "allow" or "deny".
    """
    # Check dangerous patterns
    for pattern, reason in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "deny", f"Blocked: {reason}"

    # Safe command
    return "allow", None


def main() -> int:
    """Main entry point."""
    try:
        input_data = read_stdin()

        tool_name = input_data.get("tool_name", "")

        # Only process Bash commands
        if tool_name != "Bash":
            return 0

        tool_input = input_data.get("tool_input", {})
        command = tool_input.get("command", "")

        if not command:
            return 0

        decision, reason = check_command(command)

        if decision == "deny":
            emit_output(permission_decision="deny", reason=reason)
        # Don't emit anything for allow - let it pass through

    except Exception as e:
        # Log to stderr but don't crash
        print(f"pre_tool_use error: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
