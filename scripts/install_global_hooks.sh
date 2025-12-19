#!/bin/bash
# Install Claude Code memory hooks globally
# This script copies all required files to ~/.claude/ and updates settings.json

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
MEMORY_DIR="$CLAUDE_DIR/memory"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

echo "Installing Claude Code memory hooks..."
echo "Source: $SKILLS_ROOT"
echo "Target: $CLAUDE_DIR"
echo ""

# Create directories
mkdir -p "$HOOKS_DIR"
mkdir -p "$MEMORY_DIR/agent_memory"
mkdir -p "$MEMORY_DIR/scripts"
mkdir -p "$CLAUDE_DIR/logs"

# Copy hooks
echo "Copying hooks..."
cp "$SKILLS_ROOT/hooks/session_start.py" "$HOOKS_DIR/"
cp "$SKILLS_ROOT/hooks/stop.py" "$HOOKS_DIR/"
cp "$SKILLS_ROOT/hooks/user_prompt_submit.py" "$HOOKS_DIR/"
cp "$SKILLS_ROOT/hooks/pre_tool_use.py" "$HOOKS_DIR/"

# Copy memory module
echo "Copying memory module..."
cp "$SKILLS_ROOT/memory/__init__.py" "$MEMORY_DIR/" 2>/dev/null || echo "" > "$MEMORY_DIR/__init__.py"
cp "$SKILLS_ROOT/memory/agent_memory/"*.py "$MEMORY_DIR/agent_memory/"
cp "$SKILLS_ROOT/memory/scripts/ensure_db.sh" "$MEMORY_DIR/scripts/" 2>/dev/null || true

# Make scripts executable
chmod +x "$HOOKS_DIR/"*.py
chmod +x "$MEMORY_DIR/scripts/"*.sh 2>/dev/null || true

echo ""
echo "Files installed:"
ls -la "$HOOKS_DIR/"
echo ""
ls -la "$MEMORY_DIR/agent_memory/"
echo ""

# Check if jq is available for JSON manipulation
if ! command -v jq &> /dev/null; then
    echo "WARNING: jq not found. Please install jq and run again, or manually update $SETTINGS_FILE"
    echo ""
    echo "Required hooks configuration (matcher must be a string):"
    cat << 'EOF'
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/session_start.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/stop.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/user_prompt_submit.py"
          }
        ]
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
  }
EOF
    exit 0
fi

# Backup existing settings
if [ -f "$SETTINGS_FILE" ]; then
    cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup"
    echo "Backed up settings to: $SETTINGS_FILE.backup"
fi

# Define hooks configuration (matcher must be a string, not object)
HOOKS_CONFIG='{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "python3 ~/.claude/hooks/session_start.py"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "python3 ~/.claude/hooks/stop.py"
        }
      ]
    }
  ],
  "UserPromptSubmit": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "python3 ~/.claude/hooks/user_prompt_submit.py"
        }
      ]
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
if [ -f "$SETTINGS_FILE" ]; then
    jq --argjson hooks "$HOOKS_CONFIG" '.hooks = $hooks' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
else
    echo '{}' | jq --argjson hooks "$HOOKS_CONFIG" '.hooks = $hooks' > "$SETTINGS_FILE"
fi

echo "Updated $SETTINGS_FILE with hooks configuration"
echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Restart Claude Code for changes to take effect"
echo "2. Ensure the database is running: docker compose -f $SKILLS_ROOT/memory/docker-compose.yml up -d"
echo "3. Set OPENAI_API_KEY for semantic search (optional)"
echo ""
echo "To verify installation:"
echo "  cat ~/.claude/logs/memory-audit.jsonl"
echo "  !audit (in Claude Code)"
