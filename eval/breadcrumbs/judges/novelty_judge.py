#!/usr/bin/env python3
"""
novelty_judge.py — Measures Hypothesis Novelty Score (HNS) for proposed experiments.

Usage:
    python3 novelty_judge.py \
        --proposed "Use a C extension for the inner loop to eliminate interpreter overhead" \
        --ledger .autoresearch/results.jsonl \
        [--runs 3] \
        [--model claude-opus-4]

    # Or pipe multiple proposals via stdin (JSON array of strings)
    echo '["hyp1", "hyp2"]' | python3 novelty_judge.py --ledger results.jsonl

Outputs JSON: {"scores": [{"hypothesis": "...", "score": 0.85, "reason": "..."}], "mean_hns": 0.85}
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


JUDGE_PROMPT = """You are evaluating whether a proposed experiment hypothesis is novel relative to a set of hypotheses already tried in an autoresearch session.

PAST HYPOTHESES (already tried — including both kept and discarded experiments):
{past_hypotheses}

PROPOSED HYPOTHESIS:
{proposed_hypothesis}

Your task: Score the proposed hypothesis for novelty from 0.0 to 1.0.

Scoring guide:
- 0.0 = Essentially the SAME hypothesis. Same mechanism, same prediction, same change.
  Example: Past: "Compile regex at module level" / Proposed: "Pre-compile the regex pattern" → 0.0
- 0.3 = Very similar. Minor variation on same mechanism (e.g., different parameter value for same idea).
  Example: Past: "CHUNK_SIZE=512 for cache efficiency" / Proposed: "CHUNK_SIZE=256 for cache efficiency" → 0.3
- 0.5 = Related but meaningfully different. Same general category but different mechanism or prediction.
  Example: Past: "Use Counter for frequency counting" / Proposed: "Use sorted+groupby for frequency" → 0.5
- 0.7 = Different approach. Different category or layer of optimization.
  Example: Past: "Pre-compile regex" / Proposed: "Use Cython extension" → 0.7
- 1.0 = Completely novel. No connection to any past hypothesis in mechanism or prediction.

Reply with ONLY a JSON object, no other text:
{{"score": <float 0.0-1.0>, "reason": "<one sentence explaining the score>"}}"""


def load_past_hypotheses(ledger_path: str) -> list[str]:
    """Load all hypotheses from results.jsonl."""
    hypotheses = []
    try:
        with open(ledger_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    h = record.get("hypothesis", "")
                    if h and record.get("id") != "baseline":
                        hypotheses.append(h)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"WARNING: Ledger not found at {ledger_path}", file=sys.stderr)
    return hypotheses


def judge_novelty(proposed: str, past_hypotheses: list[str], client, model: str, runs: int = 3) -> dict:
    """Judge novelty of a single proposed hypothesis. Returns averaged score over multiple runs."""
    if not past_hypotheses:
        return {"hypothesis": proposed, "score": 1.0, "reason": "No past hypotheses to compare against."}

    past_text = "\n".join(f"{i+1}. {h}" for i, h in enumerate(past_hypotheses))

    scores = []
    reasons = []
    for _ in range(runs):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=200,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": JUDGE_PROMPT.format(
                        past_hypotheses=past_text,
                        proposed_hypothesis=proposed
                    )
                }]
            )
            result = json.loads(response.content[0].text.strip())
            scores.append(float(result["score"]))
            reasons.append(result.get("reason", ""))
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"WARNING: Judge run failed: {e}", file=sys.stderr)
            continue

    if not scores:
        return {"hypothesis": proposed, "score": 0.5, "reason": "Judge failed to produce results."}

    return {
        "hypothesis": proposed,
        "score": median(scores),
        "score_runs": scores,
        "reason": reasons[len(reasons) // 2] if reasons else ""
    }


def main():
    parser = argparse.ArgumentParser(description="Judge hypothesis novelty (HNS)")
    parser.add_argument("--proposed", help="Single proposed hypothesis string")
    parser.add_argument("--ledger", required=True, help="Path to results.jsonl")
    parser.add_argument("--runs", type=int, default=3, help="Number of judge runs per hypothesis")
    parser.add_argument("--model", default="claude-opus-4", help="Anthropic model to use")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    past_hypotheses = load_past_hypotheses(args.ledger)

    # Read proposed hypotheses: either from --proposed flag or stdin (JSON array)
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

    results = []
    for proposal in proposals:
        result = judge_novelty(proposal, past_hypotheses, client, args.model, args.runs)
        results.append(result)

    all_scores = [r["score"] for r in results]
    output = {
        "scores": results,
        "mean_hns": sum(all_scores) / len(all_scores) if all_scores else 0.0,
        "median_hns": median(all_scores) if all_scores else 0.0,
        "past_hypothesis_count": len(past_hypotheses)
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
