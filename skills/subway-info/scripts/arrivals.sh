#!/usr/bin/env bash
# Get real-time train arrivals at a NYC subway station
# Usage: ./arrivals.sh <station_name_or_id> [line] [direction] [limit]
# Examples:
#   ./arrivals.sh "times square"
#   ./arrivals.sh 127 1 N 5
#   ./arrivals.sh "union square" L S

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <station_name_or_id> [line] [direction] [limit]"
    echo ""
    echo "Arguments:"
    echo "  station_name_or_id  Station name (searched) or numeric/alphanumeric ID"
    echo "  line                Filter by line (e.g., 1, A, L)"
    echo "  direction           N=uptown/Bronx, S=downtown/Brooklyn"
    echo "  limit               Max arrivals to return (default: 10)"
    echo ""
    echo "Examples:"
    echo "  $0 \"times square\""
    echo "  $0 127 1 N 5"
    echo "  $0 \"canal street\" A"
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed" >&2
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)" >&2
    exit 1
fi

BASE_URL="${SUBWAY_API_URL:-https://subwayinfo.nyc}"
STATION_INPUT="$1"
LINE="${2:-}"
DIRECTION="${3:-}"
LIMIT="${4:-10}"
AUTH_HEADER=""
if [ -n "$SUBWAY_API_KEY" ]; then
    AUTH_HEADER="-H \"X-API-Key: $SUBWAY_API_KEY\""
fi

# If station input looks like a name (contains spaces or letters only), search first
STATION_ID="$STATION_INPUT"
if echo "$STATION_INPUT" | grep -qE '[a-z ]{2,}'; then
    search_result=$(curl -s -X POST "$BASE_URL/api/stations" \
        -H "Content-Type: application/json" \
        ${SUBWAY_API_KEY:+-H "X-API-Key: $SUBWAY_API_KEY"} \
        -d "{\"query\": \"$STATION_INPUT\", \"limit\": 1}")

    STATION_ID=$(echo "$search_result" | jq -r '.content[0].text' 2>/dev/null | grep -oE 'ID: [A-Za-z0-9]+' | head -1 | sed 's/ID: //')

    if [ -z "$STATION_ID" ] || [ "$STATION_ID" = "null" ]; then
        echo "Error: Could not find station matching '$STATION_INPUT'" >&2
        echo "Try searching with: curl -s -X POST $BASE_URL/api/stations -H 'Content-Type: application/json' -d '{\"query\": \"$STATION_INPUT\"}'" >&2
        exit 1
    fi
    echo "Found station ID: $STATION_ID" >&2
fi

# Build request body
BODY="{\"station_id\": \"$STATION_ID\", \"limit\": $LIMIT"
[ -n "$LINE" ] && BODY="$BODY, \"line\": \"$LINE\""
[ -n "$DIRECTION" ] && BODY="$BODY, \"direction\": \"$DIRECTION\""
BODY="$BODY}"

response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/arrivals" \
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
