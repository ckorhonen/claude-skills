#!/bin/bash
# List Paperclip issues with optional filters
# Usage: ./issues.sh [--status todo] [--assignee prefix] [--priority critical] [--limit 10] [--json]

if command -v paperclip &>/dev/null; then
  paperclip issues "$@"
else
  # Fallback to curl
  TOKEN=$(env | grep '^PAPERCLIP_API_KEY=' | cut -d= -f2-)
  API="${PAPERCLIP_API_URL:-http://127.0.0.1:3100}"

  if [ -z "$TOKEN" ] || [ -z "$PAPERCLIP_COMPANY_ID" ]; then
    echo "Error: PAPERCLIP_API_KEY and PAPERCLIP_COMPANY_ID must be set"
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
