#!/bin/bash
# Install hooks globally in ~/.claude/hooks/
# This script creates symlinks and updates settings.json

set -e

SKILLS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$HOME/.claude/hooks"
SETTINGS_FILE="$HOME/.claude/settings.json"

echo "Installing hooks from: $SKILLS_ROOT/hooks"
echo "To: $HOOKS_DIR"

# Create hooks directory
mkdir -p "$HOOKS_DIR"

# Create symlinks
ln -sf "$SKILLS_ROOT/hooks/session_start.py" "$HOOKS_DIR/session_start.py"
ln -sf "$SKILLS_ROOT/hooks/stop.py" "$HOOKS_DIR/stop.py"
ln -sf "$SKILLS_ROOT/hooks/user_prompt_submit.py" "$HOOKS_DIR/user_prompt_submit.py"
ln -sf "$SKILLS_ROOT/hooks/pre_tool_use.py" "$HOOKS_DIR/pre_tool_use.py"

echo "Created symlinks:"
ls -la "$HOOKS_DIR"

# Check if jq is available for JSON manipulation
if ! command -v jq &> /dev/null; then
    echo ""
    echo "jq not found. Please install jq and run again, or manually add the following to $SETTINGS_FILE:"
    echo ""
    cat << 'EOF'
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/session_start.py"
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/stop.py"
      }
    ],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/user_prompt_submit.py"
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/pre_tool_use.py"
          }
        ]
      }
    ]
  },
EOF
    exit 0
fi

# Backup existing settings
cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup"
echo ""
echo "Backed up settings to: $SETTINGS_FILE.backup"

# Define hooks configuration
HOOKS_CONFIG='{
  "SessionStart": [
    {
      "type": "command",
      "command": "python3 ~/.claude/hooks/session_start.py"
    }
  ],
  "Stop": [
    {
      "type": "command",
      "command": "python3 ~/.claude/hooks/stop.py"
    }
  ],
  "UserPromptSubmit": [
    {
      "type": "command",
      "command": "python3 ~/.claude/hooks/user_prompt_submit.py"
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python3 ~/.claude/hooks/pre_tool_use.py"
        }
      ]
    }
  ]
}'

# Update settings.json with hooks configuration
jq --argjson hooks "$HOOKS_CONFIG" '.hooks = $hooks' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"

echo "Updated $SETTINGS_FILE with hooks configuration"
echo ""
echo "Installation complete! Restart Claude Code for changes to take effect."
echo ""
echo "Environment variable (optional):"
echo "  export CLAUDE_SKILLS_ROOT=\"$SKILLS_ROOT\""
