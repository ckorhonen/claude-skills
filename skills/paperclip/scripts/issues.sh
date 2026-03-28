#!/bin/bash
# List Paperclip issues with optional filters
# Usage: ./issues.sh [--status todo] [--assignee prefix] [--priority critical] [--limit 10] [--json]
#        ./issues.sh --help

set -euo pipefail

usage() {
  cat <<'EOF'
List Paperclip issues.

Usage: issues.sh [OPTIONS]

Options:
  --status STATUS      Filter by status: todo, in_progress, done
  --assignee PREFIX    Filter by assignee agent id prefix
  --priority PRIORITY  Filter by priority: critical, high, medium, low
  --limit N            Max results (default: all)
  --json               Output raw JSON
  --help, -h           Show this help text

Environment:
  PAPERCLIP_API_KEY     Required
  PAPERCLIP_COMPANY_ID  Required
  PAPERCLIP_API_URL     Optional (default: http://127.0.0.1:3100)
EOF
}

for arg in "$@"; do
  case "$arg" in --help|-h) usage; exit 0 ;; esac
done

if command -v paperclip &>/dev/null; then
  paperclip issues "$@"
else
  # Fallback to curl
  TOKEN=$(env | grep '^PAPERCLIP_API_KEY=' | cut -d= -f2-)
  API="${PAPERCLIP_API_URL:-http://127.0.0.1:3100}"

  if [ -z "$TOKEN" ] || [ -z "$PAPERCLIP_COMPANY_ID" ]; then
    echo "Error: PAPERCLIP_API_KEY and PAPERCLIP_COMPANY_ID must be set" >&2
    exit 1
  fi

  curl -s -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "$API/api/companies/$PAPERCLIP_COMPANY_ID/issues" | \
    python3 -c "
import json, sys
issues = json.load(sys.stdin)
for i in issues:
    assignee = (i.get('assigneeAgentId') or '')[:8] or 'none'
    print(f\"{i['identifier']} [{i['status']}] {i['priority']} {assignee} {i['title']}\")
" 2>&1
fi
