#!/usr/bin/env python3
"""
coherence_judge.py — Measures whether agent reasoning is coherent with available breadcrumbs.

Specifically: does the agent's explanation for WHY a proposal is novel or safe reference
the breadcrumb information (comments, DECISION.md) when it's present?

This measures whether breadcrumbs are USED, not just whether the agent succeeds.
A high coherence score means the agent's reasoning is anchored to the breadcrumbs.

Usage:
    python3 coherence_judge.py \
        --agent-response response.txt \
        --breadcrumbs fixtures/code/string_pipeline_v10_with_breadcrumbs.py \
        [--decision-md fixtures/decisions/DECISION_v10.md] \
        [--runs 3] \
        [--model claude-opus-4]

Outputs JSON: {"coherence_score": 0.8, "anchoring_examples": [...], "missed_anchors": [...]}
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


COHERENCE_PROMPT = """You are evaluating whether an agent's response makes proper use of breadcrumb information available in the codebase.

BREADCRUMBS AVAILABLE (WHY comments from the code):
{breadcrumbs}

AGENT RESPONSE:
{agent_response}

Your task: Evaluate whether the agent's reasoning references or builds on the breadcrumb information.

Score 0.0 to 1.0:
- 0.0 = Agent completely ignores all breadcrumbs; no reference to WHY comments
- 0.3 = Agent vaguely acknowledges some patterns but doesn't cite specific reasons
- 0.5 = Agent references some breadcrumbs but misses important ones
- 0.7 = Agent clearly builds on the breadcrumb information in its reasoning
- 1.0 = Agent explicitly cites breadcrumb reasoning and uses it to justify novel proposals or avoid dead ends

Also identify:
1. Up to 3 examples where the agent DID anchor to a breadcrumb
2. Up to 3 important breadcrumbs the agent MISSED (if any)

Reply with ONLY a JSON object:
{{
  "coherence_score": <float 0.0-1.0>,
  "anchoring_examples": ["example1", "example2"],
  "missed_anchors": ["missed1", "missed2"],
  "reason": "<one sentence summary>"
}}"""


def extract_breadcrumb_comments(code_path: str) -> str:
    """Extract WHY comments from code file."""
    comments = []
    try:
        with open(code_path) as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if "WHY" in stripped or "DO NOT" in stripped or "REJECTED" in stripped or "tested in exp-" in stripped.lower():
                    comments.append(f"Line {i}: {stripped}")
    except FileNotFoundError:
        pass
    return "\n".join(comments) if comments else "No WHY comments found in code."


def main():
    parser = argparse.ArgumentParser(description="Judge coherence between agent response and breadcrumbs")
    parser.add_argument("--agent-response", required=True, help="Path to agent response text file")
    parser.add_argument("--breadcrumbs", required=True, help="Path to code file with breadcrumb comments")
    parser.add_argument("--decision-md", help="Optional path to DECISION.md")
    parser.add_argument("--runs", type=int, default=3, help="Number of judge runs")
    parser.add_argument("--model", default="claude-opus-4", help="Anthropic model")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    try:
        with open(args.agent_response) as f:
            agent_response = f.read()
    except FileNotFoundError:
        print(f"ERROR: Agent response file not found: {args.agent_response}", file=sys.stderr)
        sys.exit(1)

    breadcrumbs = extract_breadcrumb_comments(args.breadcrumbs)
    if args.decision_md:
        try:
            with open(args.decision_md) as f:
                breadcrumbs += "\n\n--- DECISION.md ---\n" + f.read()
        except FileNotFoundError:
            pass

    scores = []
    anchoring_examples = []
    missed_anchors = []
    reasons = []

    for _ in range(args.runs):
        try:
            response = client.messages.create(
                model=args.model,
                max_tokens=500,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": COHERENCE_PROMPT.format(
                        breadcrumbs=breadcrumbs,
                        agent_response=agent_response
                    )
                }]
            )
            result = json.loads(response.content[0].text.strip())
            scores.append(float(result["coherence_score"]))
            anchoring_examples.extend(result.get("anchoring_examples", []))
            missed_anchors.extend(result.get("missed_anchors", []))
            reasons.append(result.get("reason", ""))
        except Exception as e:
            print(f"WARNING: Coherence judge run failed: {e}", file=sys.stderr)
            continue

    output = {
        "coherence_score": median(scores) if scores else 0.5,
        "score_runs": scores,
        "anchoring_examples": list(set(anchoring_examples))[:5],
        "missed_anchors": list(set(missed_anchors))[:5],
        "reason": reasons[len(reasons) // 2] if reasons else ""
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
