#!/usr/bin/env bash
# Fetch NFT metadata from OpenSea API
# Usage: ./fetch_nft.sh <chain> <contract_address> <token_id>
# Example: ./fetch_nft.sh ethereum 0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D 1234

set -e

# Check for required arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <chain> <contract_address> <token_id>"
    echo "Example: $0 ethereum 0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D 1234"
    echo ""
    echo "Supported chains: ethereum, matic, arbitrum, optimism, base, avalanche, blast, zora, solana"
    exit 1
fi

CHAIN="$1"
CONTRACT="$2"
TOKEN_ID="$3"

# Check for API key
if [ -z "$OPENSEA_API_KEY" ]; then
    echo "Error: OPENSEA_API_KEY environment variable is not set"
    echo "Get your API key at: https://docs.opensea.io/reference/api-keys"
    exit 1
fi

# Check for jq
if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed"
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)"
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

while [ "$retry_count" -lt "$max_retries" ]; do
    response=$(curl -s -w "\n%{http_code}" \
        "https://api.opensea.io/api/v2/chain/${CHAIN}/contract/${CONTRACT}/nfts/${TOKEN_ID}" \
        -H "X-API-KEY: $OPENSEA_API_KEY" \
        -H "Accept: application/json")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        echo "$body" | jq '.'
        exit 0
    elif [ "$http_code" = "429" ]; then
        delay=$((base_delay ** (retry_count + 1)))
        echo "Rate limited. Retrying in ${delay}s..." >&2
        sleep "$delay"
        retry_count=$((retry_count + 1))
    elif [ "$http_code" = "404" ]; then
        echo "Error: NFT not found (chain: $CHAIN, contract: $CONTRACT, token: $TOKEN_ID)" >&2
        exit 1
    else
        echo "Error: HTTP $http_code" >&2
        echo "$body" >&2
        exit 1
    fi
done

echo "Max retries exceeded" >&2
exit 1
