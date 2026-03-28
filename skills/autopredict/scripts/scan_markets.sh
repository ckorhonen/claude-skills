#!/usr/bin/env bash
set -euo pipefail
# Scan live Polymarket markets with configurable filters.
#
# Usage:
#   bash scripts/scan_markets.sh [OPTIONS]
#
# Options:
#   --dir DIR              AutoPredict directory (default: ./autopredict)
#   --top N                Number of markets to show (default: 20)
#   --category CAT         Filter by category (e.g., politics, crypto, sports)
#   --min-liquidity N      Minimum liquidity threshold
#   --events               Show event-level mispricing instead
#   --verbose              Show order book details
#   --output FILE          Save JSON output to file

DIR="autopredict"
ARGS=()
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --top|--category|--min-liquidity)
      ARGS+=("$1" "$2"); shift 2 ;;
    --events|--verbose)
      ARGS+=("$1"); shift ;;
    --help|-h)
      echo "Usage: $0 [--dir DIR] [--top N] [--category CAT] [--min-liquidity N] [--events] [--verbose] [--output FILE]"
      exit 0 ;;
    *) ARGS+=("$1"); shift ;;
  esac
done

cd "$DIR"

echo "=== AutoPredict Market Scan ==="
echo "Time: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "Args: ${ARGS[*]:-none}"
echo ""

if [[ -n "$OUTPUT" ]]; then
  python3 predict.py "${ARGS[@]}" 2>&1 | tee "$OUTPUT"
else
  python3 predict.py "${ARGS[@]}" 2>&1
fi
