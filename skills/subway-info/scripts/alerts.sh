#!/usr/bin/env bash
# Check active NYC subway service alerts
# Usage: ./alerts.sh [line] [alert_type]
# Examples:
#   ./alerts.sh           # All alerts
#   ./alerts.sh A         # A train alerts
#   ./alerts.sh L Delays  # L train delay alerts

set -e

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed" >&2
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)" >&2
    exit 1
fi

BASE_URL="${SUBWAY_API_URL:-https://subwayinfo.nyc}"
LINE="${1:-}"
ALERT_TYPE="${2:-}"

# Build request body
BODY="{"
FIRST=true
if [ -n "$LINE" ]; then
    BODY="$BODY\"line\": \"$LINE\""
    FIRST=false
fi
if [ -n "$ALERT_TYPE" ]; then
    [ "$FIRST" = false ] && BODY="$BODY, "
    BODY="$BODY\"alert_type\": \"$ALERT_TYPE\""
fi
BODY="$BODY}"

response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/alerts" \
    -H "Content-Type: application/json" \
    ${SUBWAY_API_KEY:+-H "X-API-Key: $SUBWAY_API_KEY"} \
    -d "$BODY")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo "$body" | jq -r '.content[0].text // .' 2>/dev/null || echo "$body"
elif [ "$http_code" = "429" ]; then
    echo "Error: Rate limited. Wait and try again, or set SUBWAY_API_KEY for higher limits." >&2
    exit 1
else
    echo "Error: HTTP $http_code" >&2
    echo "$body" >&2
    exit 1
fi
