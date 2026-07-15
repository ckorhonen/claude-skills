#!/usr/bin/env bash
# run_scenario.sh — Run a single breadcrumb eval scenario and emit a result JSON.
#
# Usage:
#   ./scripts/run_scenario.sh scenarios/A_resume_accuracy/scenario_01_with_breadcrumbs.json
#   ./scripts/run_scenario.sh scenarios/A_resume_accuracy/scenario_01_with_breadcrumbs.json --runs 5
#
# Environment:
#   ANTHROPIC_API_KEY  — required
#   MODEL              — optional, defaults to claude-opus-4
#   EVAL_DIR           — optional, defaults to directory containing this script's parent

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVAL_DIR="${EVAL_DIR:-$(dirname "$SCRIPT_DIR")}"
RESULTS_DIR="$EVAL_DIR/results"
mkdir -p "$RESULTS_DIR"

SCENARIO_FILE="${1:-}"
RUNS="${2:---runs}"
RUNS_VAL="${3:-3}"

if [[ -z "$SCENARIO_FILE" ]]; then
    echo "Usage: $0 <scenario.json> [--runs N]" >&2
    exit 1
fi

if [[ ! -f "$SCENARIO_FILE" ]]; then
    echo "ERROR: Scenario file not found: $SCENARIO_FILE" >&2
    exit 1
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "ERROR: ANTHROPIC_API_KEY not set" >&2
    exit 1
fi

MODEL="${MODEL:-claude-opus-4}"
SCENARIO_ID=$(python3 -c "import json,sys; print(json.load(open('$SCENARIO_FILE'))['id'])")
DIMENSION=$(python3 -c "import json,sys; print(json.load(open('$SCENARIO_FILE'))['dimension'])")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RESULT_FILE="$RESULTS_DIR/result_${SCENARIO_ID}_${TIMESTAMP//:/}.json"

echo "=== Running scenario: $SCENARIO_ID (dimension $DIMENSION) ===" >&2
echo "Scenario: $SCENARIO_FILE" >&2
echo "Model: $MODEL | Runs: $RUNS_VAL" >&2
echo "Result: $RESULT_FILE" >&2

# Build workspace for this scenario
WORKSPACE=$(mktemp -d)
trap "rm -rf $WORKSPACE" EXIT

python3 "$EVAL_DIR/scripts/build_workspace.py" \
    --scenario "$SCENARIO_FILE" \
    --eval-dir "$EVAL_DIR" \
    --workspace "$WORKSPACE"

echo "Workspace built at $WORKSPACE" >&2

# Run the agent against the scenario
AGENT_RESPONSE_FILE="$WORKSPACE/agent_response.txt"

python3 "$EVAL_DIR/scripts/call_agent.py" \
    --scenario "$SCENARIO_FILE" \
    --workspace "$WORKSPACE" \
    --model "$MODEL" \
    --output "$AGENT_RESPONSE_FILE"

echo "Agent response saved to $AGENT_RESPONSE_FILE" >&2

# Extract proposed hypotheses from agent response
HYPOTHESES_FILE="$WORKSPACE/proposed_hypotheses.json"
python3 "$EVAL_DIR/scripts/extract_hypotheses.py" \
    --response "$AGENT_RESPONSE_FILE" \
    --output "$HYPOTHESES_FILE"

echo "Extracted hypotheses: $(cat "$HYPOTHESES_FILE" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))') proposals" >&2

# Run judges based on scenario config
JUDGE_RESULTS="$WORKSPACE/judge_results.json"
python3 - <<EOF
import json
import subprocess
import sys

scenario = json.load(open("$SCENARIO_FILE"))
eval_dir = "$EVAL_DIR"
workspace = "$WORKSPACE"
hypotheses = json.load(open("$HYPOTHESES_FILE"))
results_fixture = scenario.get("setup", {}).get("results_fixture", "")
ledger_path = f"{eval_dir}/{results_fixture}" if results_fixture else None

judge_results = {}

# Novelty judge
if ledger_path:
    cmd = [
        "python3", f"{eval_dir}/judges/novelty_judge.py",
        "--ledger", ledger_path,
        "--runs", "$RUNS_VAL",
        "--model", "$MODEL"
    ]
    proc = subprocess.run(cmd, input=json.dumps(hypotheses), capture_output=True, text=True)
    if proc.returncode == 0:
        judge_results["novelty"] = json.loads(proc.stdout)
    else:
        print(f"Novelty judge error: {proc.stderr}", file=sys.stderr)
        judge_results["novelty"] = {"error": proc.stderr}

# Regression judge
    cmd = [
        "python3", f"{eval_dir}/judges/regression_judge.py",
        "--ledger", ledger_path,
        "--runs", "$RUNS_VAL",
        "--model", "$MODEL"
    ]
    proc = subprocess.run(cmd, input=json.dumps(hypotheses), capture_output=True, text=True)
    if proc.returncode == 0:
        judge_results["regression"] = json.loads(proc.stdout)
    else:
        print(f"Regression judge error: {proc.stderr}", file=sys.stderr)
        judge_results["regression"] = {"error": proc.stderr}

json.dump(judge_results, open("$JUDGE_RESULTS", "w"), indent=2)
print("Judge results saved.", file=sys.stderr)
EOF

# Compute pass/fail
python3 - <<EOF
import json
import sys

scenario = json.load(open("$SCENARIO_FILE"))
judge_results = json.load(open("$JUDGE_RESULTS"))
agent_response = open("$AGENT_RESPONSE_FILE").read()

pass_criteria = scenario.get("pass_criteria", {})

# Extract metrics
hns = judge_results.get("novelty", {}).get("mean_hns", None)
rr = judge_results.get("regression", {}).get("regression_rate", None)

checks = {}
passed = True

if "HNS_min" in pass_criteria and hns is not None:
    checks["HNS"] = {"value": hns, "threshold": pass_criteria["HNS_min"],
                     "pass": hns >= pass_criteria["HNS_min"]}
    if not checks["HNS"]["pass"]:
        passed = False

if "RR_max" in pass_criteria and rr is not None:
    checks["RR"] = {"value": rr, "threshold": pass_criteria["RR_max"],
                    "pass": rr <= pass_criteria["RR_max"]}
    if not checks["RR"]["pass"]:
        passed = False

result = {
    "scenario_id": scenario["id"],
    "dimension": scenario["dimension"],
    "name": scenario["name"],
    "condition": scenario.get("condition", "unknown"),
    "timestamp": "$TIMESTAMP",
    "model": "$MODEL",
    "passed": passed,
    "checks": checks,
    "metrics": {
        "HNS": hns,
        "RR": rr,
    },
    "judge_results": judge_results,
    "agent_response_preview": agent_response[:500] + "..." if len(agent_response) > 500 else agent_response
}

json.dump(result, open("$RESULT_FILE", "w"), indent=2)
print(json.dumps(result, indent=2))

status = "PASS ✅" if passed else "FAIL ❌"
print(f"\n{status} — Scenario {scenario['id']}", file=sys.stderr)
if hns is not None:
    print(f"  HNS: {hns:.3f} (threshold: {pass_criteria.get('HNS_min', 'N/A')})", file=sys.stderr)
if rr is not None:
    print(f"  RR:  {rr:.3f} (threshold: {pass_criteria.get('RR_max', 'N/A')})", file=sys.stderr)
EOF

echo "Result saved: $RESULT_FILE" >&2
