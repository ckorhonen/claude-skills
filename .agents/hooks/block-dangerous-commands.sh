#!/usr/bin/env bash
# PreToolUse hook: Block dangerous shell commands
set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# Block rm -rf (but allow rm of single files)
if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\b'; then
  echo "BLOCKED: 'rm -rf' is not allowed in this repo. Remove files individually or ask the user." >&2
  exit 2
fi

# Block git push --force / -f
if echo "$COMMAND" | grep -qE 'git\s+push\s+.*(-f|--force)\b'; then
  echo "BLOCKED: 'git push --force' is not allowed. Use --force-with-lease or ask the user." >&2
  exit 2
fi

# Block git reset --hard
if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
  echo "BLOCKED: 'git reset --hard' is not allowed. This discards uncommitted work." >&2
  exit 2
fi

# Block DROP TABLE
if echo "$COMMAND" | grep -qiE 'DROP\s+TABLE'; then
  echo "BLOCKED: 'DROP TABLE' is not allowed." >&2
  exit 2
fi

exit 0
