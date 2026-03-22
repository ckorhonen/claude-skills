#!/usr/bin/env bash
# PreToolUse hook: Block edits to protected files
set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path','') or d.get('tool_input',{}).get('path',''))" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

BASENAME=$(basename "$FILE_PATH")

# Block edits to LICENSE
if [[ "$BASENAME" == "LICENSE" || "$BASENAME" == "LICENSE.md" ]]; then
  echo "BLOCKED: Editing LICENSE is not allowed without explicit user approval." >&2
  exit 2
fi

# Block edits to .env files and credentials
if [[ "$BASENAME" == .env* || "$BASENAME" == "credentials.json" || "$BASENAME" == "secrets.json" || "$BASENAME" == ".secrets" ]]; then
  echo "BLOCKED: Editing credential/secret files ($BASENAME) is not allowed." >&2
  exit 2
fi

exit 0
