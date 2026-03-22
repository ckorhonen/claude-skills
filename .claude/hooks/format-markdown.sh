#!/usr/bin/env bash
# PostToolUse hook: Auto-format markdown files after edits
set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path','') or d.get('tool_input',{}).get('path',''))" 2>/dev/null || echo "")

# Only format .md files
if [[ "$FILE_PATH" != *.md ]]; then
  exit 0
fi

# Check if file exists
if [[ ! -f "$FILE_PATH" ]]; then
  exit 0
fi

# Try prettier first, fall back to silently skipping
if command -v npx &>/dev/null; then
  npx --yes prettier --write --prose-wrap preserve "$FILE_PATH" &>/dev/null || true
fi

exit 0
