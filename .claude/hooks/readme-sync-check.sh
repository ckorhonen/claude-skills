#!/usr/bin/env bash
# PostToolUse hook: Remind to update README.md when a new skill is added
set -euo pipefail

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {})
print(ti.get('file_path', '') or ti.get('path', ''))
" 2>/dev/null || echo "")

# Only trigger for SKILL.md files under skills/
if [[ "$FILE_PATH" != */skills/*/SKILL.md ]]; then
  exit 0
fi

# Extract skill directory name
SKILL_NAME=$(echo "$FILE_PATH" | sed -n 's|.*skills/\([^/]*\)/.*|\1|p')

if [[ -z "$SKILL_NAME" ]]; then
  exit 0
fi

# Get repo root from cwd in the hook input, or fall back to git
REPO_ROOT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null || echo "")
if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
fi

# Check if this skill is already in the README
if [[ -f "$REPO_ROOT/README.md" ]] && ! grep -q "$SKILL_NAME" "$REPO_ROOT/README.md" 2>/dev/null; then
  echo "NOTE: New skill '$SKILL_NAME' is not listed in README.md — remember to add it to the skill registry table."
fi

exit 0
