#!/bin/bash

# Continuous Learning Skill Auto-Activation Hook
# This hook reminds Claude to evaluate sessions for extractable knowledge.
#
# Installation:
#   1. Copy this script to ~/.claude/hooks/
#   2. Make it executable: chmod +x ~/.claude/hooks/continuous-learning-activator.sh
#   3. Add to ~/.claude/settings.json (see README for details)
#
# Opt-out: Set CONTINUOUS_LEARNING=0 to disable this reminder

# Handle --help flag
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    cat << 'HELP'
Usage: continuous-learning-activator.sh [--help]

Auto-Activation Hook for the Continuous Learning skill.
Outputs a reminder to run /retrospective at the end of a session
to capture reusable patterns as new skills.

Options:
  --help, -h    Show this help message and exit

Environment:
  CONTINUOUS_LEARNING=0    Set to disable the reminder output

Installation:
  1. Copy to ~/.claude/hooks/
  2. chmod +x ~/.claude/hooks/continuous-learning-activator.sh
  3. Register in ~/.claude/settings.json as a PostToolUse or Stop hook
HELP
    exit 0
fi

# Check for opt-out
if [ "$CONTINUOUS_LEARNING" = "0" ]; then
    exit 0
fi

cat << 'EOF'

💡 Tip: Run /retrospective (1-2 min) to capture reusable patterns from this session.

Consider extracting a skill if you:
- Discovered a non-obvious solution through investigation
- Fixed a misleading error message
- Found an underdocumented tool/API pattern

Skip if the session was routine or solutions came from standard documentation.

EOF
