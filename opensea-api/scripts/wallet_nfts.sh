#!/bin/bash
# Get NFTs owned by a wallet address from OpenSea API
# Usage: ./wallet_nfts.sh <chain> <wallet_address> [limit]
# Example: ./wallet_nfts.sh ethereum 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 50

set -e

# Check for required arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <chain> <wallet_address> [limit]"
    echo "Example: $0 ethereum 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 50"
    echo ""
    echo "Supported chains: ethereum, matic, arbitrum, optimism, base, avalanche, blast, zora, solana"
    exit 1
fi

CHAIN="$1"
ADDRESS="$2"
LIMIT="${3:-50}"

# Check for API key
if [ -z "$OPENSEA_API_KEY" ]; then
    echo "Error: OPENSEA_API_KEY environment variable is not set"
    echo "Get your API key at: https://docs.opensea.io/reference/api-keys"
    exit 1
fi

# Validate chain
VALID_CHAINS="ethereum matic arbitrum optimism base avalanche blast zora solana"
if ! echo "$VALID_CHAINS" | grep -qw "$CHAIN"; then
    echo "Error: Invalid chain '$CHAIN'"
    echo "Supported chains: $VALID_CHAINS"
    exit 1
fi

# Make API request with retry logic
max_retries=4
retry_count=0
base_delay=2

while [ $retry_count -lt $max_retries ]; do
    response=$(curl -s -w "\n%{http_code}" \
        "https://api.opensea.io/api/v2/chain/${CHAIN}/account/${ADDRESS}/nfts?limit=${LIMIT}" \
        -H "X-API-KEY: $OPENSEA_API_KEY" \
        -H "Accept: application/json")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        nft_count=$(echo "$body" | jq '.nfts | length')
        echo "=== NFTs owned by $ADDRESS on $CHAIN ===" >&2
        echo "Found: $nft_count NFTs (limit: $LIMIT)" >&2
        echo "" >&2
        echo "$body" | jq '.'
        exit 0
    elif [ "$http_code" = "429" ]; then
        delay=$((base_delay ** retry_count))
        echo "Rate limited. Retrying in ${delay}s..." >&2
        sleep $delay
        retry_count=$((retry_count + 1))
    else
        echo "Error: HTTP $http_code" >&2
        echo "$body" >&2
        exit 1
    fi
done

echo "Max retries exceeded" >&2
exit 1
