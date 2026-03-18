#!/bin/bash
# Quick company status overview
# Usage: ./status.sh [--json]

if command -v paperclip &>/dev/null; then
  echo "=== Agents ==="
  paperclip agents "$@"
  echo ""
  echo "=== Active Issues ==="
  paperclip issues --status in_progress "$@"
  echo ""
  echo "=== Todo Issues ==="
  paperclip issues --status todo --limit 10 "$@"
else
  TOKEN=$(env | grep '^PAPERCLIP_API_KEY=' | cut -d= -f2-)
  API="${PAPERCLIP_API_URL:-http://127.0.0.1:3100}"

  if [ -z "$TOKEN" ] || [ -z "$PAPERCLIP_COMPANY_ID" ]; then
    echo "Error: PAPERCLIP_API_KEY and PAPERCLIP_COMPANY_ID must be set"
    exit 1
  fi

  echo "=== Agents ==="
  curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    "$API/api/companies/$PAPERCLIP_COMPANY_ID/agents" | \
    python3 -c "
import json, sys
for a in json.load(sys.stdin):
    print(f\"{a['name']} [{a['status']}] {a['role']}\")
"

  echo ""
  echo "=== Active Issues ==="
  curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    "$API/api/companies/$PAPERCLIP_COMPANY_ID/issues" | \
    python3 -c "
import json, sys
for i in json.load(sys.stdin):
    if i['status'] == 'in_progress':
        a = (i.get('assigneeAgentId') or '')[:8] or 'none'
        print(f\"{i['identifier']} [{i['priority']}] {a} {i['title']}\")
"

  echo ""
  echo "=== Todo Issues ==="
  curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    "$API/api/companies/$PAPERCLIP_COMPANY_ID/issues" | \
    python3 -c "
import json, sys
count = 0
for i in json.load(sys.stdin):
    if i['status'] == 'todo' and count < 10:
        a = (i.get('assigneeAgentId') or '')[:8] or 'none'
        print(f\"{i['identifier']} [{i['priority']}] {a} {i['title']}\")
        count += 1
"
fi
