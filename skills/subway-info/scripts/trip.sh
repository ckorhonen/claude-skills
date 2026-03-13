#!/usr/bin/env bash
# Plan a trip between two NYC subway stations
# Usage: ./trip.sh <origin> <destination>
# Examples:
#   ./trip.sh "times square" "grand central"
#   ./trip.sh 127 631

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <origin> <destination>"
    echo ""
    echo "Arguments can be station names (searched) or station IDs."
    echo ""
    echo "Examples:"
    echo "  $0 \"times square\" \"grand central\""
    echo "  $0 127 631"
    echo "  $0 \"union square\" \"atlantic barclays\""
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed" >&2
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)" >&2
    exit 1
fi

BASE_URL="${SUBWAY_API_URL:-https://subwayinfo.nyc}"

resolve_station() {
    local input="$1"
    local label="$2"

    # If it looks like a station ID (short alphanumeric), use directly
    if echo "$input" | grep -qE '^[A-Z0-9]{1,4}$'; then
        echo "$input"
        return
    fi

    # Search by name
    local result
    result=$(curl -s -X POST "$BASE_URL/api/stations" \
        -H "Content-Type: application/json" \
        ${SUBWAY_API_KEY:+-H "X-API-Key: $SUBWAY_API_KEY"} \
        -d "{\"query\": \"$input\", \"limit\": 1}")

    local station_id
    station_id=$(echo "$result" | jq -r '.content[0].text' 2>/dev/null | grep -oE 'ID: [A-Za-z0-9]+' | head -1 | sed 's/ID: //')

    if [ -z "$station_id" ] || [ "$station_id" = "null" ]; then
        echo "Error: Could not find $label station matching '$input'" >&2
        return 1
    fi
    echo "Resolved $label: '$input' -> $station_id" >&2
    echo "$station_id"
}

ORIGIN_ID=$(resolve_station "$1" "origin") || exit 1
DEST_ID=$(resolve_station "$2" "destination") || exit 1

response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/trip" \
    -H "Content-Type: application/json" \
    ${SUBWAY_API_KEY:+-H "X-API-Key: $SUBWAY_API_KEY"} \
    -d "{\"origin_station_id\": \"$ORIGIN_ID\", \"destination_station_id\": \"$DEST_ID\"}")

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
