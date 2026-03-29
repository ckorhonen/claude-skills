#!/usr/bin/env bash
# build_fixtures.sh — Regenerate or extend eval fixtures.
#
# Usage:
#   ./scripts/build_fixtures.sh              # Validate all existing fixtures
#   ./scripts/build_fixtures.sh --large-session  # Generate large-session fixtures for scenario_16

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVAL_DIR="$(dirname "$SCRIPT_DIR")"
FIXTURES_DIR="$EVAL_DIR/fixtures"

validate_fixtures() {
    echo "Validating fixtures..."
    local errors=0

    # Check code fixtures
    for f in "$FIXTURES_DIR/code"/*.py; do
        if python3 -m py_compile "$f" 2>/dev/null; then
            echo "  ✅ $f"
        else
            echo "  ❌ Syntax error: $f"
            ((errors++))
        fi
    done

    # Check JSONL fixtures
    for f in "$FIXTURES_DIR/autoresearch_states"/*.jsonl; do
        local lines=0
        local errors_in_file=0
        while IFS= read -r line; do
            ((lines++))
            python3 -c "import json; json.loads('$line')" 2>/dev/null || ((errors_in_file++))
        done < "$f"
        if [[ $errors_in_file -eq 0 ]]; then
            echo "  ✅ $f ($lines records)"
        else
            echo "  ❌ JSON errors in $f ($errors_in_file/$lines invalid)"
            ((errors++))
        fi
    done

    # Check scenario JSON files
    for f in "$EVAL_DIR/scenarios"/**/*.json; do
        if python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
            echo "  ✅ $f"
        else
            echo "  ❌ JSON error: $f"
            ((errors++))
        fi
    done

    if [[ $errors -eq 0 ]]; then
        echo "All fixtures valid."
    else
        echo "ERRORS: $errors fixture validation failures."
        exit 1
    fi
}

build_large_session() {
    echo "Generating large-session fixtures for scenario_16..."
    local output_dir="$FIXTURES_DIR/large_session"
    mkdir -p "$output_dir"

    # Generate a multi-file pipeline with varying breadcrumb densities
    python3 - <<'EOF'
import os
import json
from pathlib import Path

output_dir = Path(os.environ.get("FIXTURES_DIR", "fixtures")) / "large_session"
output_dir.mkdir(parents=True, exist_ok=True)

# Generate synthetic experiment history (20 experiments)
experiments = [{"id": "baseline", "timestamp": "2026-03-01T09:00:00Z",
                "hypothesis": "Control run", "change_summary": "No changes",
                "files_touched": [], "baseline_commit": "abc0000",
                "candidate_ref": "abc0000", "metric_name": "latency_ms",
                "direction": "lower", "warmup_trials": [50.0, 49.8],
                "measured_trials": [50.0, 49.9, 50.1, 49.8, 50.2],
                "summary": {"median": 50.0, "mean": 50.0, "min": 49.8, "max": 50.2},
                "secondary_metrics": {}, "checks": "passed", "disposition": "baseline",
                "reason": "Baseline established."}]

keeps = 0
for i in range(1, 21):
    disposition = "keep" if i % 3 == 0 else "discard"
    if disposition == "keep":
        keeps += 1
    improvement = 1.5 if disposition == "keep" else 0.0
    baseline_median = experiments[-1]["summary"]["median"] if disposition == "keep" else experiments[0]["summary"]["median"]
    candidate_median = baseline_median * (1 - improvement/100) if disposition == "keep" else baseline_median * 1.02

    experiments.append({
        "id": f"exp-{i:03d}",
        "timestamp": f"2026-03-{(i//10)+1:02d}T{9+(i%8):02d}:00:00Z",
        "hypothesis": f"Optimization hypothesis #{i}: try technique {['caching', 'batching', 'vectorization', 'parallelism', 'pre-allocation', 'loop unrolling', 'data locality', 'branch prediction'][i % 8]} to reduce overhead",
        "change_summary": f"Apply optimization {i} to module_{(i%3)+1}.py",
        "files_touched": [f"module_{(i%3)+1}.py"],
        "baseline_commit": f"abc{i:04d}",
        "candidate_ref": f"abc{i+1:04d}",
        "metric_name": "latency_ms",
        "direction": "lower",
        "warmup_trials": [candidate_median + 0.1, candidate_median],
        "measured_trials": [candidate_median] * 5,
        "summary": {"median": candidate_median, "mean": candidate_median,
                    "min": candidate_median - 0.1, "max": candidate_median + 0.1},
        "secondary_metrics": {},
        "checks": "passed",
        "disposition": disposition,
        "reason": f"{'Improvement of 1.5%. Tests pass.' if disposition == 'keep' else 'No improvement observed.'}"
    })

jsonl_path = output_dir / "results_20exp.jsonl"
with open(jsonl_path, "w") as f:
    for exp in experiments:
        f.write(json.dumps(exp) + "\n")
print(f"Generated {jsonl_path} ({len(experiments)} records)")
EOF

    echo "Large session fixtures generated at $output_dir"
}

case "${1:---validate}" in
    --validate) validate_fixtures ;;
    --large-session) build_large_session ;;
    *)
        echo "Usage: $0 [--validate | --large-session]"
        exit 1
        ;;
esac
