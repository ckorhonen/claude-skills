#!/usr/bin/env python3
"""
regression_judge.py — Measures Regression Rate (RR) for proposed experiments.

Checks whether a proposed change would undo or negate an optimization that was
already marked 'keep' in the results.jsonl ledger.

Usage:
    python3 regression_judge.py \
        --proposed "Replace the walrus operator with a traditional for loop for readability" \
        --ledger .autoresearch/results.jsonl \
        [--runs 3] \
        [--model claude-opus-4]

    # Or pipe a JSON array of proposed changes from stdin

Outputs JSON: {"regressions": [...], "regression_rate": 0.33}
"""

import argparse
import json
import os
import sys
from pathlib import Path
from statistics import median

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


REGRESSION_PROMPT = """You are evaluating whether a proposed code change would undo or negate an optimization that was previously kept.

PREVIOUSLY KEPT OPTIMIZATION:
- Experiment: {exp_id}
- Change made: {change_summary}
- Reason kept: {reason}
- Metric improvement: {improvement}

PROPOSED CHANGE:
{proposed_change}

Your task: Determine if the proposed change would REVERT, NEGATE, or UNDO the kept optimization.

Consider:
- Would the proposed change remove or replace the code that was added/modified in the kept experiment?
- Would the proposed change change a constant or setting that the kept optimization depends on?
- Would the proposed change return to a pre-optimization state (even partially)?

If the proposed change is UNRELATED to the kept optimization, answer false.

Reply with ONLY a JSON object, no other text:
{{"regresses": true/false, "confidence": <float 0.0-1.0>, "reason": "<one sentence>"}}"""


def load_kept_experiments(ledger_path: str) -> list[dict]:
    """Load all 'keep' experiments from results.jsonl."""
    kept = []
    try:
        with open(ledger_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if record.get("disposition") == "keep":
                        kept.append(record)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"WARNING: Ledger not found at {ledger_path}", file=sys.stderr)
    return kept


def compute_improvement_str(record: dict) -> str:
    """Extract improvement description from record."""
    baseline_median = None
    summary = record.get("summary", {})
    if not summary:
        return "unknown"
    candidate_median = summary.get("median")
    reason = record.get("reason", "")
    # Try to extract percentage from reason
    import re
    pct_match = re.search(r'(\d+\.?\d*)\s*%', reason)
    if pct_match:
        return f"{pct_match.group(0)} improvement"
    return f"median {record.get('metric_name', 'metric')} = {candidate_median}"


def check_regression(proposed: str, kept_exp: dict, client, model: str, runs: int = 3) -> dict:
    """Check if proposed change regresses a specific kept experiment."""
    votes = []
    reasons = []

    for _ in range(runs):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=200,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": REGRESSION_PROMPT.format(
                        exp_id=kept_exp.get("id", "?"),
                        change_summary=kept_exp.get("change_summary", "Unknown change"),
                        reason=kept_exp.get("reason", "No reason recorded"),
                        improvement=compute_improvement_str(kept_exp),
                        proposed_change=proposed
                    )
                }]
            )
            result = json.loads(response.content[0].text.strip())
            votes.append(result.get("regresses", False))
            reasons.append(result.get("reason", ""))
        except Exception as e:
            print(f"WARNING: Regression judge run failed: {e}", file=sys.stderr)
            continue

    if not votes:
        return {"regresses": False, "confidence": 0.0, "reason": "Judge failed"}

    # Majority vote
    regresses = sum(1 for v in votes if v) > len(votes) / 2
    confidence = sum(1 for v in votes if v == regresses) / len(votes)
    return {
        "regresses": regresses,
        "confidence": confidence,
        "reason": reasons[len(reasons) // 2] if reasons else "",
        "against_experiment": kept_exp.get("id"),
        "against_change": kept_exp.get("change_summary")
    }


def main():
    parser = argparse.ArgumentParser(description="Judge regression risk (RR)")
    parser.add_argument("--proposed", help="Single proposed change string")
    parser.add_argument("--ledger", required=True, help="Path to results.jsonl")
    parser.add_argument("--runs", type=int, default=3, help="Number of judge runs per check")
    parser.add_argument("--model", default="claude-opus-4", help="Anthropic model to use")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    kept_experiments = load_kept_experiments(args.ledger)

    if not kept_experiments:
        print(json.dumps({"regressions": [], "regression_rate": 0.0, "note": "No kept experiments in ledger"}))
        return

    if args.proposed:
        proposals = [args.proposed]
    elif not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        try:
            proposals = json.loads(raw)
            if isinstance(proposals, str):
                proposals = [proposals]
        except json.JSONDecodeError:
            proposals = [raw]
    else:
        parser.print_help()
        sys.exit(1)

    all_regressions = []
    for proposal in proposals:
        proposal_regressions = []
        for kept in kept_experiments:
            result = check_regression(proposal, kept, client, args.model, args.runs)
            if result["regresses"]:
                proposal_regressions.append({
                    "proposal": proposal,
                    **result
                })
        all_regressions.extend(proposal_regressions)

    total_checks = len(proposals) * len(kept_experiments)
    regression_rate = len(all_regressions) / len(proposals) if proposals else 0.0

    output = {
        "regressions": all_regressions,
        "regression_rate": regression_rate,
        "proposals_checked": len(proposals),
        "kept_experiments_checked": len(kept_experiments),
        "total_checks": total_checks
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
