#!/usr/bin/env python3
"""
extract_hypotheses.py — Extract proposed experiment hypotheses from agent response text.

Uses a simple LLM call to reliably parse the agent's proposals out of freeform text.

Usage:
    python3 extract_hypotheses.py \
        --response agent_response.txt \
        --output proposed_hypotheses.json \
        [--model claude-haiku-3]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed.", file=sys.stderr)
    sys.exit(1)


EXTRACTION_PROMPT = """Extract the experiment hypotheses from this agent response. 
An experiment hypothesis is a statement of WHAT will be changed and WHY it should improve performance.
Return ONLY a JSON array of strings, where each string is one hypothesis statement.
If the agent proposed 3 experiments, return 3 strings. No other text.

AGENT RESPONSE:
{response}

Reply with ONLY a JSON array of hypothesis strings:"""


def extract_with_regex(text: str) -> list[str]:
    """Fallback: simple regex extraction for numbered list items."""
    # Look for patterns like "1. ...", "**Experiment 1**", "exp-011: ..."
    patterns = [
        r'\d+\.\s+\*\*[Hh]ypothesis[^:]*:\*\*\s*(.+?)(?=\n\d+\.|\Z)',
        r'[Hh]ypothesis:\s*(.+?)(?=\n(?:[A-Z]|\d+\.)|\Z)',
        r'exp-\d+.*?[Hh]ypothesis.*?:\s*(.+?)(?=\nexp-|\Z)',
    ]
    results = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            results = [m.strip()[:500] for m in matches[:5]]
            break

    # Last resort: split on numbered items
    if not results:
        items = re.split(r'\n\d+\.\s+', text)
        results = [item.split('\n')[0].strip() for item in items[1:4] if item.strip()]

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--response", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="claude-haiku-3-5")
    args = parser.parse_args()

    response_text = Path(args.response).read_text()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback to regex
        hypotheses = extract_with_regex(response_text)
        print(f"WARNING: No API key — used regex extraction, got {len(hypotheses)} hypotheses", file=sys.stderr)
    else:
        client = anthropic.Anthropic(api_key=api_key)
        try:
            resp = client.messages.create(
                model=args.model,
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": EXTRACTION_PROMPT.format(response=response_text[:8000])
                }]
            )
            hypotheses = json.loads(resp.content[0].text.strip())
            if not isinstance(hypotheses, list):
                raise ValueError("Response is not a list")
        except Exception as e:
            print(f"WARNING: LLM extraction failed ({e}), falling back to regex", file=sys.stderr)
            hypotheses = extract_with_regex(response_text)

    print(f"Extracted {len(hypotheses)} hypotheses", file=sys.stderr)
    for i, h in enumerate(hypotheses, 1):
        print(f"  {i}. {h[:100]}...", file=sys.stderr)

    Path(args.output).write_text(json.dumps(hypotheses, indent=2))


if __name__ == "__main__":
    main()
