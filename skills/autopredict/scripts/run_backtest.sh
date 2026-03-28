#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Run an AutoPredict backtest safely.

Usage:
  bash skills/autopredict/scripts/run_backtest.sh [OPTIONS]

Options:
  --dir DIR          AutoPredict repo directory (default: ./autopredict)
  --python BIN       Python executable to use (default: python3)
  --config FILE      Strategy config JSON (default: strategy_configs/baseline.json)
  --dataset FILE     Dataset JSON. If omitted, uses the bundled sample dataset when available.
  --score            Also print score-latest after the backtest
  --output FILE      Save the backtest metrics JSON to FILE
  --help, -h         Show this help text
EOF
}

die() {
  echo "Error: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

DIR="autopredict"
PYTHON_BIN="python3"
CONFIG="strategy_configs/baseline.json"
DATASET=""
SCORE=false
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir)
      [[ $# -ge 2 ]] || die "--dir requires a value"
      DIR="$2"
      shift 2
      ;;
    --python)
      [[ $# -ge 2 ]] || die "--python requires a value"
      PYTHON_BIN="$2"
      shift 2
      ;;
    --config)
      [[ $# -ge 2 ]] || die "--config requires a value"
      CONFIG="$2"
      shift 2
      ;;
    --dataset)
      [[ $# -ge 2 ]] || die "--dataset requires a value"
      DATASET="$2"
      shift 2
      ;;
    --score)
      SCORE=true
      shift
      ;;
    --output)
      [[ $# -ge 2 ]] || die "--output requires a value"
      OUTPUT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

need_cmd "$PYTHON_BIN"
[[ -d "$DIR" ]] || die "Repo directory not found: $DIR"
[[ -f "$DIR/autopredict/cli.py" ]] || die "$DIR is not an AutoPredict checkout (missing autopredict/cli.py)"

cd "$DIR"

[[ -f "$CONFIG" ]] || die "Config file not found: $CONFIG"

if [[ -z "$DATASET" ]]; then
  sample_dataset="autopredict/_defaults/datasets/sample_markets.json"
  if [[ -f "$sample_dataset" ]]; then
    DATASET="$sample_dataset"
    echo "No dataset supplied. Using bundled sample dataset: $DATASET"
  else
    die "No dataset supplied and bundled sample dataset not found. Pass --dataset explicitly."
  fi
fi

[[ -f "$DATASET" ]] || die "Dataset file not found: $DATASET"

echo "=== AutoPredict Backtest ==="
echo "Repo: $(pwd)"
echo "Time: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "Config: $CONFIG"
echo "Dataset: $DATASET"
echo

tmp_output="$(mktemp)"
trap 'rm -f "$tmp_output"' EXIT

"$PYTHON_BIN" -m autopredict.cli backtest --config "$CONFIG" --dataset "$DATASET" | tee "$tmp_output"

if [[ -n "$OUTPUT" ]]; then
  mkdir -p "$(dirname "$OUTPUT")"
  cp "$tmp_output" "$OUTPUT"
  echo
  echo "Saved metrics JSON to: $OUTPUT"
fi

if [[ "$SCORE" == true ]]; then
  echo
  echo "=== score-latest ==="
  "$PYTHON_BIN" -m autopredict.cli score-latest
fi

echo
echo "Note: calling autopredict.cli backtest without --dataset is broken upstream because config.json sets default_dataset to null."
