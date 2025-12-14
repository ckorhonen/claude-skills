#!/bin/bash
# Get collection statistics from OpenSea API
# Usage: ./collection_stats.sh <collection_slug>
# Example: ./collection_stats.sh boredapeyachtclub

set -e

# Check for required arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <collection_slug>"
    echo "Example: $0 boredapeyachtclub"
    echo ""
    echo "The collection slug is the URL-friendly name from the OpenSea collection page"
    echo "e.g., https://opensea.io/collection/boredapeyachtclub -> boredapeyachtclub"
    exit 1
fi

COLLECTION="$1"

# Check for API key
if [ -z "$OPENSEA_API_KEY" ]; then
    echo "Error: OPENSEA_API_KEY environment variable is not set"
    echo "Get your API key at: https://docs.opensea.io/reference/api-keys"
    exit 1
fi

# Make API request with retry logic
max_retries=4
retry_count=0
base_delay=2

while [ $retry_count -lt $max_retries ]; do
    response=$(curl -s -w "\n%{http_code}" \
        "https://api.opensea.io/api/v2/collections/${COLLECTION}/stats" \
        -H "X-API-KEY: $OPENSEA_API_KEY" \
        -H "Accept: application/json")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        # Pretty print with summary
        echo "=== Collection Stats: $COLLECTION ==="
        echo ""
        echo "$body" | jq -r '
            "Total Volume: " + (.total.volume | tostring) + " ETH",
            "Total Sales: " + (.total.sales | tostring),
            "Floor Price: " + (.total.floor_price | tostring) + " ETH",
            "Average Price: " + (.total.average_price | tostring) + " ETH",
            "Num Owners: " + (.total.num_owners | tostring),
            "Market Cap: " + (.total.market_cap | tostring) + " ETH",
            "",
            "=== 24h Stats ===",
            "Volume (24h): " + (.intervals[0].volume | tostring) + " ETH",
            "Sales (24h): " + (.intervals[0].sales | tostring),
            "Volume Change (24h): " + ((.intervals[0].volume_change * 100) | tostring) + "%"
        ' 2>/dev/null || echo "$body" | jq '.'
        exit 0
    elif [ "$http_code" = "429" ]; then
        delay=$((base_delay ** retry_count))
        echo "Rate limited. Retrying in ${delay}s..." >&2
        sleep $delay
        retry_count=$((retry_count + 1))
    elif [ "$http_code" = "404" ]; then
        echo "Error: Collection '$COLLECTION' not found" >&2
        exit 1
    else
        echo "Error: HTTP $http_code" >&2
        echo "$body" >&2
        exit 1
    fi
done

echo "Max retries exceeded" >&2
exit 1
