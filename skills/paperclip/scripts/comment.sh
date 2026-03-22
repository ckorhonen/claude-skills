#!/bin/bash
# Add a comment to a Paperclip issue
# Usage: ./comment.sh <identifier> <body> [agent-id]

IDENTIFIER="$1"
BODY="$2"
AGENT_ID="$3"

if [ -z "$IDENTIFIER" ] || [ -z "$BODY" ]; then
  echo "Usage: comment.sh <identifier> <body> [agent-id]"
  exit 1
fi

if command -v paperclip &>/dev/null; then
  if [ -n "$AGENT_ID" ]; then
    paperclip comment "$IDENTIFIER" --body "$BODY" --agent "$AGENT_ID"
  else
    paperclip comment "$IDENTIFIER" --body "$BODY"
  fi
else
  TOKEN=$(env | grep '^PAPERCLIP_API_KEY=' | cut -d= -f2-)
  API="${PAPERCLIP_API_URL:-http://127.0.0.1:3100}"

  if [ -z "$TOKEN" ] || [ -z "$PAPERCLIP_COMPANY_ID" ]; then
    echo "Error: PAPERCLIP_API_KEY and PAPERCLIP_COMPANY_ID must be set"
    exit 1
  fi

  # Resolve identifier to issue ID
  ISSUE_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "$API/api/companies/$PAPERCLIP_COMPANY_ID/issues" | \
    IDENTIFIER="$IDENTIFIER" python3 -c "
import json, sys, os
issues = json.load(sys.stdin)
matches = [i['id'] for i in issues if i['identifier'] == os.environ['IDENTIFIER']]
print(matches[0] if matches else '')
")

  if [ -z "$ISSUE_ID" ]; then
    echo "Issue $IDENTIFIER not found"
    exit 1
  fi

  PAYLOAD=$(COMMENT_BODY="$BODY" python3 -c "import json,os; print(json.dumps({'body': os.environ['COMMENT_BODY']}))")
  if [ -n "$AGENT_ID" ]; then
    PAYLOAD=$(COMMENT_BODY="$BODY" AGENT_ID="$AGENT_ID" python3 -c "import json,os; print(json.dumps({'body': os.environ['COMMENT_BODY'], 'agentId': os.environ['AGENT_ID']}))")
  fi

  curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "$API/api/issues/$ISSUE_ID/comments" > /dev/null && echo "Comment added."
fi
