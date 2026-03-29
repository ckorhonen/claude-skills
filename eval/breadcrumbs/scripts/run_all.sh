#!/usr/bin/env bash
# run_all.sh — Run the full breadcrumb eval suite or a single dimension.
#
# Usage:
#   ./scripts/run_all.sh --all              # All scenarios
#   ./scripts/run_all.sh --dimension A      # Just dimension A
#   ./scripts/run_all.sh --dimension B C    # Dimensions B and C
#   ./scripts/run_all.sh --scenario scenario_01  # Single scenario by ID prefix
#
# Environment:
#   ANTHROPIC_API_KEY  — required
#   MODEL              — optional, defaults to claude-opus-4
#   RUNS               — optional, judge runs per scenario, defaults to 3
#   PARALLEL           — optional, number of parallel scenario runs (default 1)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVAL_DIR="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$EVAL_DIR/results"
mkdir -p "$RESULTS_DIR"

MODEL="${MODEL:-claude-opus-4}"
RUNS="${RUNS:-3}"
PARALLEL="${PARALLEL:-1}"
TIMESTAMP=$(date -u +"%Y%m%d-%H%M%S")
SUMMARY_FILE="$RESULTS_DIR/summary_${TIMESTAMP}.json"

# Parse arguments
DIMENSIONS=()
SCENARIO_FILTER=""
RUN_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all) RUN_ALL=true; shift ;;
        --dimension) shift; DIMENSIONS+=("$1"); shift ;;
        --scenario) shift; SCENARIO_FILTER="$1"; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

if [[ "$RUN_ALL" == false && ${#DIMENSIONS[@]} -eq 0 && -z "$SCENARIO_FILTER" ]]; then
    echo "Usage: $0 --all | --dimension A [B C ...] | --scenario <id>" >&2
    exit 1
fi

# Collect scenario files to run
SCENARIOS=()

if [[ "$RUN_ALL" == true ]]; then
    while IFS= read -r f; do SCENARIOS+=("$f"); done < <(find "$EVAL_DIR/scenarios" -name "*.json" | sort)
elif [[ ${#DIMENSIONS[@]} -gt 0 ]]; then
    for dim in "${DIMENSIONS[@]}"; do
        # Map dimension letter to directory
        case $dim in
            A) dir="A_resume_accuracy" ;;
            B) dir="B_regression_prevention" ;;
            C) dir="C_complexity_scaling" ;;
            D) dir="D_format_tests" ;;
            E) dir="E_knowledge_decay" ;;
            F) dir="F_token_budget" ;;
            *) dir="*${dim}*" ;;
        esac
        while IFS= read -r f; do SCENARIOS+=("$f"); done < <(find "$EVAL_DIR/scenarios/${dir}" -name "*.json" 2>/dev/null | sort)
    done
elif [[ -n "$SCENARIO_FILTER" ]]; then
    while IFS= read -r f; do SCENARIOS+=("$f"); done < <(find "$EVAL_DIR/scenarios" -name "*${SCENARIO_FILTER}*.json" | sort)
fi

if [[ ${#SCENARIOS[@]} -eq 0 ]]; then
    echo "ERROR: No scenarios found matching criteria" >&2
    exit 1
fi

echo "=== Breadcrumb Eval Suite ===" >&2
echo "Scenarios: ${#SCENARIOS[@]}" >&2
echo "Model: $MODEL | Runs: $RUNS | Parallel: $PARALLEL" >&2
echo "Results: $RESULTS_DIR" >&2
echo "" >&2

# Run scenarios
PASSED=0
FAILED=0
ERRORS=0
RESULT_FILES=()

run_scenario() {
    local scenario_file="$1"
    local scenario_id
    scenario_id=$(python3 -c "import json; print(json.load(open('$scenario_file'))['id'])" 2>/dev/null || echo "unknown")

    echo "Running: $scenario_id..." >&2

    # Special handling for token-only scenarios
    local measurement_script
    measurement_script=$(python3 -c "
import json
s = json.load(open('$scenario_file'))
script = s.get('stimulus', {}).get('script', '')
print(script)
" 2>/dev/null || echo "")

    if [[ "$measurement_script" == *"token_counter"* ]]; then
        echo "  [Token measurement scenario — running token_counter directly]" >&2
        python3 "$EVAL_DIR/judges/token_counter.py" \
            --all-conditions \
            --fixtures-dir "$EVAL_DIR" \
            > "$RESULTS_DIR/token_counts_${TIMESTAMP}.json"
        echo "  Token counts saved." >&2
        return 0
    fi

    local result_file
    result_file="$RESULTS_DIR/result_${scenario_id}_${TIMESTAMP}.json"

    if bash "$SCRIPT_DIR/run_scenario.sh" "$scenario_file" --runs "$RUNS" > "$result_file" 2>&1; then
        local passed
        passed=$(python3 -c "import json; print(json.load(open('$result_file')).get('passed', False))" 2>/dev/null || echo "false")
        if [[ "$passed" == "True" ]]; then
            echo "  ✅ PASS: $scenario_id" >&2
            RESULT_FILES+=("$result_file:pass")
        else
            echo "  ❌ FAIL: $scenario_id" >&2
            RESULT_FILES+=("$result_file:fail")
        fi
    else
        echo "  ⚠️  ERROR: $scenario_id (exit code $?)" >&2
        RESULT_FILES+=("$result_file:error")
    fi
}

for scenario in "${SCENARIOS[@]}"; do
    run_scenario "$scenario"
done

# Aggregate results
python3 - <<EOF
import json
import glob
import sys
from pathlib import Path

results_dir = "$RESULTS_DIR"
timestamp = "$TIMESTAMP"

result_files = sorted(glob.glob(f"{results_dir}/result_*_{timestamp}.json"))
results = []
for f in result_files:
    try:
        results.append(json.load(open(f)))
    except:
        pass

if not results:
    print("No results to aggregate.", file=sys.stderr)
    sys.exit(0)

# Compute summary stats
passed = sum(1 for r in results if r.get("passed"))
failed = len(results) - passed

# Group by dimension
by_dim = {}
for r in results:
    dim = r.get("dimension", "?")
    if dim not in by_dim:
        by_dim[dim] = {"pass": 0, "fail": 0, "HNS_values": [], "RR_values": []}
    if r.get("passed"):
        by_dim[dim]["pass"] += 1
    else:
        by_dim[dim]["fail"] += 1
    metrics = r.get("metrics", {})
    if metrics.get("HNS") is not None:
        by_dim[dim]["HNS_values"].append(metrics["HNS"])
    if metrics.get("RR") is not None:
        by_dim[dim]["RR_values"].append(metrics["RR"])

# Compute mean metrics per dimension
for dim, data in by_dim.items():
    data["mean_HNS"] = sum(data["HNS_values"]) / len(data["HNS_values"]) if data["HNS_values"] else None
    data["mean_RR"] = sum(data["RR_values"]) / len(data["RR_values"]) if data["RR_values"] else None
    del data["HNS_values"]
    del data["RR_values"]

summary = {
    "timestamp": timestamp,
    "model": "$MODEL",
    "total_scenarios": len(results),
    "passed": passed,
    "failed": failed,
    "pass_rate": passed / len(results) if results else 0,
    "by_dimension": by_dim,
    "individual_results": results
}

summary_file = "$SUMMARY_FILE"
json.dump(summary, open(summary_file, "w"), indent=2)
print(json.dumps(summary, indent=2))

print(f"\n=== Summary ===", file=sys.stderr)
print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Rate: {passed/len(results)*100:.0f}%", file=sys.stderr)
print(f"", file=sys.stderr)
for dim, data in sorted(by_dim.items()):
    hns = f"{data['mean_HNS']:.3f}" if data['mean_HNS'] is not None else "N/A"
    rr = f"{data['mean_RR']:.3f}" if data['mean_RR'] is not None else "N/A"
    print(f"  Dim {dim}: {data['pass']}/{data['pass']+data['fail']} pass | HNS={hns} | RR={rr}", file=sys.stderr)
print(f"\nFull summary: $SUMMARY_FILE", file=sys.stderr)
EOF
