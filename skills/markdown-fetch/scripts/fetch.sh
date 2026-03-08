#!/bin/bash
# Fetch web content as Markdown using markdown.new service

set -euo pipefail

TEMP_JSON=""
TEMP_OUTPUT=""

cleanup() {
    if [[ -n "$TEMP_JSON" && -f "$TEMP_JSON" ]]; then
        rm -f "$TEMP_JSON"
    fi
    if [[ -n "$TEMP_OUTPUT" && -f "$TEMP_OUTPUT" ]]; then
        rm -f "$TEMP_OUTPUT"
    fi
    return 0
}

trap cleanup EXIT

usage() {
    cat << EOF
Usage: $0 <url> [options]

Fetch web content as clean Markdown with 80% fewer tokens than HTML.

Options:
  --method <auto|ai|browser>  Conversion method (default: auto)
  --retain-images             Keep image references in output
  --output <file>             Save to file instead of stdout
  -h, --help                  Show this help

Examples:
  $0 "https://example.com"
  $0 "https://example.com" --method browser
  $0 "https://example.com" --output page.md
  $0 "https://example.com" --method ai --retain-images

Conversion methods:
  auto     - Try Markdown-first, fall back as needed (default)
  ai       - Use Cloudflare Workers AI
  browser  - Full browser rendering for JS-heavy sites
EOF
    exit 0
}

# Parse arguments
URL=""
METHOD="auto"
RETAIN_IMAGES="false"
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        --method)
            METHOD="$2"
            shift 2
            ;;
        --retain-images)
            RETAIN_IMAGES="true"
            shift
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            if [[ -z "$URL" ]]; then
                URL="$1"
            else
                echo "Error: Unknown argument: $1" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$URL" ]]; then
    echo "Error: URL required" >&2
    echo "Try: $0 --help" >&2
    exit 1
fi

# Validate method
if [[ ! "$METHOD" =~ ^(auto|ai|browser)$ ]]; then
    echo "Error: Invalid method '$METHOD'. Must be: auto, ai, or browser" >&2
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed" >&2
    echo "Install with: brew install jq" >&2
    exit 1
fi

# Build request body
REQUEST_BODY=$(jq -n \
    --arg url "$URL" \
    --arg method "$METHOD" \
    --argjson retain_images "$RETAIN_IMAGES" \
    '{
      url: $url,
      method: $method,
      retain_images: $retain_images
    }'
)

# Fetch content
TEMP_JSON=$(mktemp)
HTTP_CODE=$(curl -s -w "%{http_code}" -o "$TEMP_JSON" \
    -X POST "https://markdown.new/" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_BODY")

if [[ "$HTTP_CODE" != "200" ]]; then
    echo "Error: HTTP $HTTP_CODE" >&2
    cat "$TEMP_JSON" >&2
    exit 1
fi

# Extract markdown content from JSON response
MARKDOWN=$(jq -r '.content' "$TEMP_JSON")
if [[ "$MARKDOWN" == "null" || -z "$MARKDOWN" ]]; then
    echo "Error: No content in response" >&2
    cat "$TEMP_JSON" >&2
    exit 1
fi

# Add metadata header
TITLE=$(jq -r '.title // "Untitled"' "$TEMP_JSON")
METHOD_USED=$(jq -r '.method // "unknown"' "$TEMP_JSON")
DURATION=$(jq -r '.duration_ms // 0' "$TEMP_JSON")

TEMP_OUTPUT=$(mktemp)
cat > "$TEMP_OUTPUT" << EOFMD
---
title: $TITLE
url: $URL
method: $METHOD_USED
duration_ms: $DURATION
fetched_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
---

$MARKDOWN
EOFMD

# Output or save
if [[ -n "$OUTPUT" ]]; then
    mv "$TEMP_OUTPUT" "$OUTPUT"
    TEMP_OUTPUT=""
    echo "Saved to: $OUTPUT" >&2
else
    cat "$TEMP_OUTPUT"
fi
