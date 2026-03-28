#!/usr/bin/env bash
set -euo pipefail
# Grid search over AutoPredict strategy parameters.
#
# Usage:
#   bash scripts/tune_params.sh [OPTIONS]
#
# Options:
#   --dir DIR              AutoPredict directory (default: ./autopredict)
#   --base-config FILE     Base config to vary from (default: strategy_configs/baseline.json)
#   --param NAME VALUES    Parameter to sweep (repeatable). VALUES is comma-separated.
#   --output DIR           Output directory for results (default: state/tuning/<timestamp>)
#
# Example:
#   bash scripts/tune_params.sh \
#     --param min_edge 0.03,0.05,0.08 \
#     --param aggressive_edge 0.10,0.12,0.15

DIR="autopredict"
BASE_CONFIG="strategy_configs/baseline.json"
OUTPUT_DIR=""
declare -a PARAM_NAMES=()
declare -a PARAM_VALUES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="$2"; shift 2 ;;
    --base-config) BASE_CONFIG="$2"; shift 2 ;;
    --param)
      PARAM_NAMES+=("$2")
      PARAM_VALUES+=("$3")
      shift 3 ;;
    --output) OUTPUT_DIR="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 [--dir DIR] [--base-config FILE] [--param NAME val1,val2,...] [--output DIR]"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ ${#PARAM_NAMES[@]} -eq 0 ]]; then
  echo "Error: At least one --param required" >&2
  echo "Example: $0 --param min_edge 0.03,0.05,0.08" >&2
  exit 1
fi

cd "$DIR"

TIMESTAMP=$(date -u '+%Y%m%d-%H%M%S')
OUTPUT_DIR="${OUTPUT_DIR:-state/tuning/$TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "=== AutoPredict Parameter Tuning ==="
echo "Time: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "Base config: $BASE_CONFIG"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Parameters to sweep:"
for i in "${!PARAM_NAMES[@]}"; do
  echo "  ${PARAM_NAMES[$i]}: ${PARAM_VALUES[$i]}"
done
echo ""

# Generate parameter combinations using Python
python3 - "$BASE_CONFIG" "$OUTPUT_DIR" "${PARAM_NAMES[@]}" -- "${PARAM_VALUES[@]}" << 'PYEOF'
import itertools
import json
import sys
from pathlib import Path

args = sys.argv[1:]
base_config_path = args[0]
output_dir = Path(args[1])

# Split at '--' separator
sep_idx = args.index('--')
param_names = args[2:sep_idx]
param_values_raw = args[sep_idx + 1:]

# Parse values
param_values = []
for raw in param_values_raw:
    vals = [float(v) for v in raw.split(',')]
    param_values.append(vals)

# Load base config
with open(base_config_path) as f:
    base = json.load(f)

# Generate grid
combos = list(itertools.product(*param_values))
print(f"Total combinations: {len(combos)}")

results = []
for i, combo in enumerate(combos):
    config = dict(base)
    label_parts = []
    for name, val in zip(param_names, combo):
        config[name] = val
        label_parts.append(f"{name}={val}")

    label = "__".join(label_parts)
    config_path = output_dir / f"config_{i:03d}_{label}.json"
    config["name"] = f"tune_{label}"

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"[{i+1}/{len(combos)}] {label}")

    # Run backtest
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "autopredict.cli", "backtest", "--config", str(config_path)],
        capture_output=True, text=True
    )

    # Score
    score_result = subprocess.run(
        [sys.executable, "-m", "autopredict.cli", "score-latest"],
        capture_output=True, text=True
    )

    metrics_path = output_dir / f"metrics_{i:03d}_{label}.json"
    if score_result.returncode == 0:
        try:
            metrics = json.loads(score_result.stdout)
            metrics["_config"] = config
            metrics["_label"] = label
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            results.append(metrics)
            pnl = metrics.get("total_pnl", "?")
            sharpe = metrics.get("sharpe_ratio", "?")
            print(f"  → PnL: {pnl}, Sharpe: {sharpe}")
        except json.JSONDecodeError:
            print(f"  → Score parse error")
    else:
        print(f"  → Backtest failed: {result.stderr[:100]}")

# Summary
if results:
    print(f"\n=== Summary ({len(results)} successful runs) ===")
    # Sort by Sharpe ratio
    sorted_results = sorted(results, key=lambda r: r.get("sharpe_ratio", float("-inf")), reverse=True)
    for i, r in enumerate(sorted_results[:5]):
        print(f"  #{i+1}: {r['_label']}")
        print(f"      PnL: {r.get('total_pnl', '?')}, Sharpe: {r.get('sharpe_ratio', '?')}, Win Rate: {r.get('win_rate', '?')}")

    # Save summary
    summary_path = output_dir / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(sorted_results, f, indent=2)
    print(f"\nFull results saved to: {summary_path}")
PYEOF

echo ""
echo "Tuning complete. Results in: $OUTPUT_DIR"
