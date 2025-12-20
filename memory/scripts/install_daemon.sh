#!/bin/bash
# Install Claude Code memory daemon as a launchd service
# This script installs the daemon to automatically start on login

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

CLAUDE_DIR="$HOME/.claude"
MEMORY_DIR="$CLAUDE_DIR/memory"
LOG_DIR="$CLAUDE_DIR/logs"
PLIST_SRC="$SKILLS_ROOT/memory/launchd/com.claude.memory-daemon.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.claude.memory-daemon.plist"

echo "Installing Claude Code memory daemon..."
echo "Source: $SKILLS_ROOT"
echo "Target: $CLAUDE_DIR"
echo ""

# Create required directories
mkdir -p "$LOG_DIR"
mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$MEMORY_DIR/agent_memory"

# Copy daemon files
echo "Copying daemon files..."
cp "$SKILLS_ROOT/memory/agent_memory/daemon.py" "$MEMORY_DIR/agent_memory/"
cp "$SKILLS_ROOT/memory/agent_memory/daemon_client.py" "$MEMORY_DIR/agent_memory/"

# Check if plist template exists
if [ ! -f "$PLIST_SRC" ]; then
    echo "ERROR: plist template not found at $PLIST_SRC"
    exit 1
fi

# Generate plist with correct paths
echo "Installing launchd service..."
sed -e "s|MEMORY_DIR|$MEMORY_DIR|g" \
    -e "s|LOG_DIR|$LOG_DIR|g" \
    "$PLIST_SRC" > "$PLIST_DEST"

# Unload existing daemon if running
launchctl unload "$PLIST_DEST" 2>/dev/null || true

# Load the daemon
launchctl load "$PLIST_DEST"

echo ""
echo "Installation complete!"
echo ""
echo "Daemon service: com.claude.memory-daemon"
echo "Log files:"
echo "  - Stdout: $LOG_DIR/daemon-stdout.log"
echo "  - Stderr: $LOG_DIR/daemon-stderr.log"
echo ""
echo "Useful commands:"
echo "  launchctl list | grep claude           # Check daemon status"
echo "  launchctl unload $PLIST_DEST           # Stop daemon"
echo "  launchctl load $PLIST_DEST             # Start daemon"
echo "  tail -f $LOG_DIR/daemon-stdout.log     # View daemon output"
echo ""
