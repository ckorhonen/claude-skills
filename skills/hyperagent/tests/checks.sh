#!/bin/bash
# Correctness gate: ensure summarizer outputs a valid METRIC line
result=$(python3 "$(dirname "$0")/target.py" 2>&1)
if echo "$result" | grep -q "METRIC score="; then
    echo "Checks passed"
    exit 0
else
    echo "Checks failed: no METRIC line found"
    exit 1
fi
