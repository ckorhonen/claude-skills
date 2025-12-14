#!/bin/bash
# Monitor collection activity (listings and sales) from OpenSea API
# Usage: ./monitor_collection.sh <collection_slug> [event_type] [interval_seconds]
# Example: ./monitor_collection.sh boredapeyachtclub sale 30

set -e

# Check for required arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <collection_slug> [event_type] [interval_seconds]"
    echo "Example: $0 boredapeyachtclub sale 30"
    echo ""
    echo "Event types: sale, listing, transfer, offer, cancel"
    echo "Default interval: 30 seconds"
    exit 1
fi

COLLECTION="$1"
EVENT_TYPE="${2:-sale}"
INTERVAL="${3:-30}"

# Check for API key
if [ -z "$OPENSEA_API_KEY" ]; then
    echo "Error: OPENSEA_API_KEY environment variable is not set"
    echo "Get your API key at: https://docs.opensea.io/reference/api-keys"
    exit 1
fi

# Validate event type
VALID_EVENTS="sale listing transfer offer cancel"
if ! echo "$VALID_EVENTS" | grep -qw "$EVENT_TYPE"; then
    echo "Error: Invalid event type '$EVENT_TYPE'"
    echo "Valid types: $VALID_EVENTS"
    exit 1
fi

echo "=== Monitoring $COLLECTION for ${EVENT_TYPE}s ==="
echo "Polling every ${INTERVAL} seconds. Press Ctrl+C to stop."
echo ""

last_timestamp=""

fetch_events() {
    local response
    local http_code
    local body

    response=$(curl -s -w "\n%{http_code}" \
        "https://api.opensea.io/api/v2/events/collection/${COLLECTION}?event_type=${EVENT_TYPE}&limit=10" \
        -H "X-API-KEY: $OPENSEA_API_KEY" \
        -H "Accept: application/json")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        echo "$body"
    elif [ "$http_code" = "429" ]; then
        echo "Rate limited, waiting..." >&2
        return 1
    else
        echo "Error: HTTP $http_code" >&2
        return 1
    fi
}

format_event() {
    local event="$1"
    local event_time
    local token_id
    local price
    local from_addr
    local to_addr

    event_time=$(echo "$event" | jq -r '.event_timestamp // "unknown"')
    token_id=$(echo "$event" | jq -r '.nft.identifier // "unknown"')

    case "$EVENT_TYPE" in
        sale)
            price=$(echo "$event" | jq -r '(.payment.quantity | tonumber / 1e18 | . * 10000 | floor / 10000) // "unknown"')
            from_addr=$(echo "$event" | jq -r '.seller[:10] // "unknown"')
            to_addr=$(echo "$event" | jq -r '.buyer[:10] // "unknown"')
            echo "[$event_time] SALE #$token_id | $price ETH | $from_addr... -> $to_addr..."
            ;;
        listing)
            price=$(echo "$event" | jq -r '(.payment.quantity | tonumber / 1e18 | . * 10000 | floor / 10000) // "unknown"')
            from_addr=$(echo "$event" | jq -r '.maker[:10] // "unknown"')
            echo "[$event_time] LISTED #$token_id | $price ETH | by $from_addr..."
            ;;
        transfer)
            from_addr=$(echo "$event" | jq -r '.from_address[:10] // "unknown"')
            to_addr=$(echo "$event" | jq -r '.to_address[:10] // "unknown"')
            echo "[$event_time] TRANSFER #$token_id | $from_addr... -> $to_addr..."
            ;;
        offer)
            price=$(echo "$event" | jq -r '(.payment.quantity | tonumber / 1e18 | . * 10000 | floor / 10000) // "unknown"')
            from_addr=$(echo "$event" | jq -r '.maker[:10] // "unknown"')
            echo "[$event_time] OFFER #$token_id | $price ETH | by $from_addr..."
            ;;
        cancel)
            from_addr=$(echo "$event" | jq -r '.maker[:10] // "unknown"')
            echo "[$event_time] CANCELLED #$token_id | by $from_addr..."
            ;;
    esac
}

while true; do
    events=$(fetch_events 2>/dev/null)

    if [ -n "$events" ]; then
        # Get latest timestamp
        new_timestamp=$(echo "$events" | jq -r '.asset_events[0].event_timestamp // empty')

        if [ -n "$new_timestamp" ] && [ "$new_timestamp" != "$last_timestamp" ]; then
            # Print new events
            echo "$events" | jq -c '.asset_events[]' 2>/dev/null | while read -r event; do
                event_ts=$(echo "$event" | jq -r '.event_timestamp')
                if [ -z "$last_timestamp" ] || [ "$event_ts" \> "$last_timestamp" ]; then
                    format_event "$event"
                fi
            done
            last_timestamp="$new_timestamp"
        fi
    fi

    sleep "$INTERVAL"
done
