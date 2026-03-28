#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Wrapper around predict.py for live market scanning and one-off fair-prob checks.

Usage:
  bash skills/autopredict/scripts/scan_markets.sh [OPTIONS] [-- extra predict.py args]

Options:
  --dir DIR              AutoPredict repo directory (default: ./autopredict)
  --python BIN           Python executable to use (default: python3)
  --output FILE          Save stdout to FILE
  --help, -h             Show this help text

Common predict.py examples:
  --top 10 --verbose
  --events --top 10
  --fair 0.60 <condition_id>
  --category politics --min-liquidity 5000 --json

All unrecognized arguments are passed through to predict.py unchanged.
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
OUTPUT=""
ARGS=()

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
    --output)
      [[ $# -ge 2 ]] || die "--output requires a value"
      OUTPUT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        ARGS+=("$1")
        shift
      done
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

need_cmd "$PYTHON_BIN"
[[ -d "$DIR" ]] || die "Repo directory not found: $DIR"
[[ -f "$DIR/predict.py" ]] || die "$DIR is not an AutoPredict checkout (missing predict.py)"

cd "$DIR"

echo "=== AutoPredict Market Scan ==="
echo "Repo: $(pwd)"
echo "Time: $(date -u '+%Y-%m-%d %H:%M UTC')"
if [[ ${#ARGS[@]} -eq 0 ]]; then
  echo "Args: <none>"
else
  echo "Args: ${ARGS[*]}"
fi
echo

if [[ -n "$OUTPUT" ]]; then
  mkdir -p "$(dirname "$OUTPUT")"
  "$PYTHON_BIN" predict.py "${ARGS[@]}" | tee "$OUTPUT"
  echo
  echo "Saved stdout to: $OUTPUT"
else
  "$PYTHON_BIN" predict.py "${ARGS[@]}"
fi

echo
echo "Notes:"
echo "  - Network access is required for live Polymarket reads."
echo "  - predict.py --fair uses the repo's default AgentConfig rather than strategy_configs/*.json."
