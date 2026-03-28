#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Grid-search AutoPredict strategy parameters using the working backtest CLI.

Usage:
  bash skills/autopredict/scripts/tune_params.sh [OPTIONS]

Options:
  --dir DIR              AutoPredict repo directory (default: ./autopredict)
  --python BIN           Python executable to use (default: python3)
  --base-config FILE     Base config JSON (default: strategy_configs/baseline.json)
  --dataset FILE         Dataset JSON. If omitted, uses the bundled sample dataset when available.
  --param NAME VALUES    Parameter sweep, repeatable. VALUES is comma-separated and parsed as JSON when possible.
  --scoring METRIC       Ranking metric: sharpe, total_pnl, ending_bankroll, win_rate,
                         num_trades, avg_slippage_bps, or implementation_shortfall_bps
                         (default: sharpe)
  --top N                Number of ranked results to print (default: 5)
  --output DIR           Output directory (default: state/tuning/<timestamp>)
  --help, -h             Show this help text

Example:
  bash skills/autopredict/scripts/tune_params.sh \
    --dataset autopredict/_defaults/datasets/sample_markets.json \
    --param min_edge 0.03,0.05,0.08 \
    --param aggressive_edge 0.10,0.12,0.15
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
BASE_CONFIG="strategy_configs/baseline.json"
DATASET=""
OUTPUT_DIR=""
SCORING="sharpe"
TOP_N=5
declare -a PARAM_NAMES=()
declare -a PARAM_VALUES=()

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
    --base-config)
      [[ $# -ge 2 ]] || die "--base-config requires a value"
      BASE_CONFIG="$2"
      shift 2
      ;;
    --dataset)
      [[ $# -ge 2 ]] || die "--dataset requires a value"
      DATASET="$2"
      shift 2
      ;;
    --param)
      [[ $# -ge 3 ]] || die "--param requires NAME and comma-separated VALUES"
      PARAM_NAMES+=("$2")
      PARAM_VALUES+=("$3")
      shift 3
      ;;
    --scoring)
      [[ $# -ge 2 ]] || die "--scoring requires a value"
      SCORING="$2"
      shift 2
      ;;
    --top)
      [[ $# -ge 2 ]] || die "--top requires a value"
      TOP_N="$2"
      shift 2
      ;;
    --output)
      [[ $# -ge 2 ]] || die "--output requires a value"
      OUTPUT_DIR="$2"
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
[[ "$TOP_N" =~ ^[0-9]+$ ]] || die "--top must be an integer"
[[ ${#PARAM_NAMES[@]} -gt 0 ]] || die "At least one --param is required"
[[ -d "$DIR" ]] || die "Repo directory not found: $DIR"
[[ -f "$DIR/autopredict/cli.py" ]] || die "$DIR is not an AutoPredict checkout (missing autopredict/cli.py)"

cd "$DIR"

[[ -f "$BASE_CONFIG" ]] || die "Base config not found: $BASE_CONFIG"

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

timestamp="$(date -u '+%Y%m%d-%H%M%S')"
OUTPUT_DIR="${OUTPUT_DIR:-state/tuning/$timestamp}"
mkdir -p "$OUTPUT_DIR"

echo "=== AutoPredict Parameter Tuning ==="
echo "Repo: $(pwd)"
echo "Time: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "Base config: $BASE_CONFIG"
echo "Dataset: $DATASET"
echo "Scoring: $SCORING"
echo "Output: $OUTPUT_DIR"
echo

args=("$BASE_CONFIG" "$DATASET" "$OUTPUT_DIR" "$SCORING" "$TOP_N")
args+=("${PARAM_NAMES[@]}")
args+=("--")
args+=("${PARAM_VALUES[@]}")

"$PYTHON_BIN" - "${args[@]}" <<'PYEOF'
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path


def parse_value(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def sanitize_label(parts: list[str]) -> str:
    label = "__".join(parts)
    label = re.sub(r"[^A-Za-z0-9._=-]+", "_", label)
    return label[:180] or "run"


def metric_score(metrics: dict, scoring: str) -> float:
    if scoring == "sharpe":
        value = metrics.get("sharpe")
    elif scoring == "total_pnl":
        value = metrics.get("total_pnl")
    elif scoring == "ending_bankroll":
        value = metrics.get("ending_bankroll")
    elif scoring == "win_rate":
        value = metrics.get("win_rate")
    elif scoring == "num_trades":
        value = metrics.get("num_trades")
    elif scoring == "avg_slippage_bps":
        value = metrics.get("avg_slippage_bps")
        return float("-inf") if value is None else -float(value)
    elif scoring == "implementation_shortfall_bps":
        value = metrics.get("implementation_shortfall_bps")
        return float("-inf") if value is None else -float(value)
    else:
        raise ValueError(
            "Unsupported scoring metric. Use one of: sharpe, total_pnl, "
            "ending_bankroll, win_rate, num_trades, avg_slippage_bps, "
            "implementation_shortfall_bps"
        )

    return float("-inf") if value is None else float(value)


argv = sys.argv[1:]
base_config_path = Path(argv[0])
dataset_path = Path(argv[1])
output_dir = Path(argv[2])
scoring = argv[3]
top_n = int(argv[4])

separator = argv.index("--")
param_names = argv[5:separator]
param_values_raw = argv[separator + 1 :]

if len(param_names) != len(param_values_raw):
    raise SystemExit("Parameter names and values are mismatched")

with base_config_path.open("r", encoding="utf-8") as handle:
    base_config = json.load(handle)

param_values = []
for raw in param_values_raw:
    values = [parse_value(chunk) for chunk in raw.split(",") if chunk]
    if not values:
      raise SystemExit(f"Empty value list in --param specification: {raw!r}")
    param_values.append(values)

combinations = list(itertools.product(*param_values))
print(f"Total combinations: {len(combinations)}")
print()

results: list[dict] = []
failures: list[dict] = []

for index, combo in enumerate(combinations, start=1):
    params = dict(zip(param_names, combo))
    label_parts = [f"{name}={params[name]!r}" for name in param_names]
    label = sanitize_label(label_parts)
    config_payload = dict(base_config)
    config_payload.update(params)
    config_payload["name"] = f"skill_tune_{index:03d}"

    config_path = output_dir / f"config_{index:03d}_{label}.json"
    metrics_path = output_dir / f"metrics_{index:03d}_{label}.json"
    stderr_path = output_dir / f"stderr_{index:03d}_{label}.log"

    config_path.write_text(json.dumps(config_payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[{index}/{len(combinations)}] {params}")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "autopredict.cli",
            "backtest",
            "--config",
            str(config_path),
            "--dataset",
            str(dataset_path),
        ],
        capture_output=True,
        text=True,
    )

    if completed.stderr:
        stderr_path.write_text(completed.stderr, encoding="utf-8")

    if completed.returncode != 0:
        failures.append(
            {
                "params": params,
                "label": label,
                "returncode": completed.returncode,
                "stderr_log": str(stderr_path) if completed.stderr else None,
            }
        )
        print(f"  FAILED (exit {completed.returncode})")
        continue

    try:
        metrics = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        failures.append(
            {
                "params": params,
                "label": label,
                "returncode": completed.returncode,
                "stderr_log": str(stderr_path) if completed.stderr else None,
                "error": f"stdout was not valid JSON: {exc}",
            }
        )
        print("  FAILED (stdout was not valid JSON)")
        continue

    score = metric_score(metrics, scoring)
    record = {
        "params": params,
        "label": label,
        "score_metric": scoring,
        "score": score,
        "metrics": metrics,
        "config_path": str(config_path),
    }
    metrics_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    results.append(record)

    sharpe = metrics.get("sharpe")
    pnl = metrics.get("total_pnl")
    trades = metrics.get("num_trades")
    print(f"  score={score:.6g} sharpe={sharpe} pnl={pnl} trades={trades}")

summary = {
    "score_metric": scoring,
    "dataset": str(dataset_path),
    "base_config": str(base_config_path),
    "total_combinations": len(combinations),
    "successful_runs": len(results),
    "failed_runs": len(failures),
}

summary_path = output_dir / "summary.json"
failures_path = output_dir / "failures.json"

ranked = sorted(results, key=lambda item: item["score"], reverse=True)
summary["top_results"] = ranked[:top_n]
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
failures_path.write_text(json.dumps(failures, indent=2, sort_keys=True), encoding="utf-8")

print()
if ranked:
    print(f"Top {min(top_n, len(ranked))} results by {scoring}:")
    for rank, item in enumerate(ranked[:top_n], start=1):
        metrics = item["metrics"]
        print(
            f"  #{rank}: {item['params']} | score={item['score']:.6g} "
            f"| sharpe={metrics.get('sharpe')} | pnl={metrics.get('total_pnl')} "
            f"| trades={metrics.get('num_trades')}"
        )
else:
    print("No successful runs.")

print()
print(f"Summary saved to: {summary_path}")
print(f"Failures saved to: {failures_path}")

if not ranked:
    raise SystemExit(1)
PYEOF

echo
echo "Tuning complete. Results in: $OUTPUT_DIR"
echo "Upstream note: autopredict.cli learn tune is a stub; this helper bypasses it by calling the working backtest CLI directly."
