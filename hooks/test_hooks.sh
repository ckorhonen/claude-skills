#!/usr/bin/env bash
# Test script for Claude Code hooks

set -e

echo "Testing Claude Code Hooks..."
echo "=============================="
echo

cd "$(dirname "$0")"

# Test 1: session_start hook
echo "Test 1: session_start hook"
echo "---------------------------"
cat <<'EOF' | python3 session_start.py
{"session_id":"test123","transcript_path":"/tmp/test.jsonl","cwd":"/Users/ckorhonen/conductor/workspaces/claude-skills/beirut"}
EOF
echo
echo "✓ session_start hook executed successfully"
echo

# Test 2: user_prompt_submit with !pending-learning
echo "Test 2: user_prompt_submit - !pending-learning"
echo "-----------------------------------------------"
cat <<'EOF' | python3 user_prompt_submit.py
{"user_prompt":"!pending-learning","transcript_path":"/tmp/test.jsonl","cwd":"/Users/ckorhonen/conductor/workspaces/claude-skills/beirut"}
EOF
echo
echo "✓ !pending-learning command works"
echo

# Test 3: user_prompt_submit with !discard-learning
echo "Test 3: user_prompt_submit - !discard-learning"
echo "-----------------------------------------------"
cat <<'EOF' | python3 user_prompt_submit.py
{"user_prompt":"!discard-learning","transcript_path":"/tmp/test.jsonl","cwd":"/Users/ckorhonen/conductor/workspaces/claude-skills/beirut"}
EOF
echo
echo "✓ !discard-learning command works"
echo

# Test 4: user_prompt_submit with normal prompt
echo "Test 4: user_prompt_submit - normal prompt"
echo "------------------------------------------"
cat <<'EOF' | python3 user_prompt_submit.py
{"user_prompt":"How do I run tests?","transcript_path":"/tmp/test.jsonl","cwd":"/Users/ckorhonen/conductor/workspaces/claude-skills/beirut"}
EOF
echo
echo "✓ Normal prompt works"
echo

# Test 5: stop hook
echo "Test 5: stop hook"
echo "----------------"
cat <<'EOF' | python3 stop.py
{"transcript_path":"/tmp/test.jsonl","stop_hook_active":false,"session_id":"test123"}
EOF
echo "✓ stop hook executed successfully"
echo

# Test 6: stop hook with stop_hook_active=true (should exit early)
echo "Test 6: stop hook with stop_hook_active=true"
echo "--------------------------------------------"
cat <<'EOF' | python3 stop.py
{"transcript_path":"/tmp/test.jsonl","stop_hook_active":true,"session_id":"test123"}
EOF
echo "✓ stop hook with stop_hook_active=true works"
echo

echo "=============================="
echo "All tests passed! ✓"
echo "=============================="
