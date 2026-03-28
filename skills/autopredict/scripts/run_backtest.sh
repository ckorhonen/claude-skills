#!/usr/bin/env bash
set -euo pipefail
# Run an AutoPredict backtest with a given strategy config.
#
# Usage:
#   bash scripts/run_backtest.sh [OPTIONS]
#
# Options:
#   --dir DIR              AutoPredict directory (default: ./autopredict)
#   --config FILE          Strategy config JSON (default: strategy_configs/baseline.json)
#   --dataset FILE         Dataset file for backtesting
#   --score                Also print the latest score after backtest
#   --output FILE          Save metrics JSON to file

DIR="autopredict"
CONFIG=""
DATASET=""
SCORE=false
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="$2"; shift 2 ;;
    --config) CONFIG="$2"; shift 2 ;;
    --dataset) DATASET="$2"; shift 2 ;;
    --score) SCORE=true; shift ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 [--dir DIR] [--config FILE] [--dataset FILE] [--score] [--output FILE]"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

cd "$DIR"

echo "=== AutoPredict Backtest ==="
echo "Time: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "Config: ${CONFIG:-default}"
echo ""

BT_ARGS=("backtest")
[[ -n "$CONFIG" ]] && BT_ARGS+=("--config" "$CONFIG")
[[ -n "$DATASET" ]] && BT_ARGS+=("--dataset" "$DATASET")

python3 -m autopredict.cli "${BT_ARGS[@]}" 2>&1

if [[ "$SCORE" == true ]]; then
  echo ""
  echo "=== Latest Score ==="
  METRICS=$(python3 -m autopredict.cli score-latest 2>&1)
  echo "$METRICS"

  if [[ -n "$OUTPUT" ]]; then
    echo "$METRICS" > "$OUTPUT"
    echo ""
    echo "Metrics saved to: $OUTPUT"
  fi
fi
