#!/usr/bin/env bash
# Get NYC subway line status overview
# Usage: ./status.sh [line]
# Examples:
#   ./status.sh       # All alerts (service overview)
#   ./status.sh L     # L train status

set -e

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed" >&2
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)" >&2
    exit 1
fi

BASE_URL="${SUBWAY_API_URL:-https://subwayinfo.nyc}"
LINE="${1:-}"

if [ -n "$LINE" ]; then
    # Get alerts for a specific line
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/alerts" \
        -H "Content-Type: application/json" \
        ${SUBWAY_API_KEY:+-H "X-API-Key: $SUBWAY_API_KEY"} \
        -d "{\"line\": \"$LINE\"}")
else
    # Get all alerts for overview
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/alerts" \
        -H "Content-Type: application/json" \
        ${SUBWAY_API_KEY:+-H "X-API-Key: $SUBWAY_API_KEY"} \
        -d '{}')
fi

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
