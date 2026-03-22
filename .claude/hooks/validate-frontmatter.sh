#!/usr/bin/env bash
# PreToolUse hook: Validates SKILL.md files have required YAML frontmatter (name + description)
set -euo pipefail

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {})
print(ti.get('file_path', '') or ti.get('path', ''))
" 2>/dev/null || echo "")

# Only check SKILL.md files
if [[ "$FILE_PATH" != */SKILL.md ]]; then
  exit 0
fi

# For Write tool, validate the content about to be written
CONTENT=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('content', ''))
" 2>/dev/null || echo "")

# If no content field (Edit tool), skip — we can't easily validate partial edits
if [[ -z "$CONTENT" ]]; then
  exit 0
fi

# Check for YAML frontmatter delimiters
FIRST_LINE=$(echo "$CONTENT" | head -1)
if [[ "$FIRST_LINE" != "---" ]]; then
  echo "SKILL.md must start with YAML frontmatter (---)" >&2
  exit 2
fi

# Extract frontmatter between first and second ---
FRONTMATTER=$(echo "$CONTENT" | sed -n '2,/^---$/p' | head -20)

# Check for required 'name' field
if ! echo "$FRONTMATTER" | grep -q "^name:"; then
  echo "SKILL.md frontmatter missing required 'name' field" >&2
  exit 2
fi

# Check for required 'description' field
if ! echo "$FRONTMATTER" | grep -q "^description:"; then
  echo "SKILL.md frontmatter missing required 'description' field" >&2
  exit 2
fi

exit 0
