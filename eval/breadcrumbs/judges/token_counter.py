#!/usr/bin/env python3
"""
token_counter.py — Count tokens in scenario prompts to compute TOR (Token Overhead Ratio).

Usage:
    python3 token_counter.py \
        --code fixtures/code/string_pipeline_v10_with_breadcrumbs.py \
        --autoresearch fixtures/autoresearch_states/session_10exp.md \
        --results fixtures/autoresearch_states/results_10exp.jsonl \
        [--decision fixtures/decisions/DECISION_v10.md] \
        [--baseline-code fixtures/code/string_pipeline_v10_no_breadcrumbs.py]

    # Run all conditions at once:
    python3 token_counter.py --all-conditions

Outputs JSON with token counts and TOR.
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import tiktoken
    ENCODER = tiktoken.encoding_for_model("gpt-4")
    def count_tokens(text: str) -> int:
        return len(ENCODER.encode(text))
except ImportError:
    # Fallback: rough approximation (4 chars per token)
    print("WARNING: tiktoken not installed, using char/4 approximation", file=sys.stderr)
    def count_tokens(text: str) -> int:
        return len(text) // 4


SYSTEM_PROMPT = """You are resuming an autoresearch session to optimize string_pipeline.py for minimum latency. You have access to the autoresearch.md session notes, the results.jsonl experiment ledger, and the current code. Your task is to propose the next 3 experiments."""

USER_PROMPT_TEMPLATE = """Resume the autoresearch session. Read autoresearch.md and .autoresearch/results.jsonl to understand what has been tried. Then read string_pipeline.py carefully, including all comments. Propose the next 3 experiments as experiment cards (each with: id, hypothesis, planned change, why it should help, predicted improvement, rollback plan). Do NOT propose anything that was already tried. Do NOT propose changes that would undo an existing optimization."""


def read_file(path: str) -> str:
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        print(f"WARNING: File not found: {path}", file=sys.stderr)
        return ""


def measure_condition(code_path: str, autoresearch_path: str, results_path: str,
                      decision_path: str = None, baseline_code_path: str = None) -> dict:
    """Measure token counts for a single condition."""
    code_content = read_file(code_path)
    autoresearch_content = read_file(autoresearch_path)
    results_content = read_file(results_path)
    decision_content = read_file(decision_path) if decision_path else ""
    baseline_content = read_file(baseline_code_path) if baseline_code_path else ""

    # Assemble full prompt as it would be sent to LLM
    prompt_parts = [
        f"--- string_pipeline.py ---\n{code_content}",
        f"--- autoresearch.md ---\n{autoresearch_content}",
        f"--- .autoresearch/results.jsonl ---\n{results_content}",
    ]
    if decision_content:
        prompt_parts.append(f"--- DECISION.md ---\n{decision_content}")
    prompt_parts.append(USER_PROMPT_TEMPLATE)

    full_prompt = "\n\n".join(prompt_parts)

    code_tokens = count_tokens(code_content)
    autoresearch_tokens = count_tokens(autoresearch_content)
    results_tokens = count_tokens(results_content)
    decision_tokens = count_tokens(decision_content) if decision_content else 0
    system_tokens = count_tokens(SYSTEM_PROMPT)
    user_prompt_tokens = count_tokens(USER_PROMPT_TEMPLATE)

    total_tokens = code_tokens + autoresearch_tokens + results_tokens + decision_tokens + system_tokens + user_prompt_tokens

    # Compute breadcrumb overhead vs. baseline
    breadcrumb_tokens = 0
    if baseline_content:
        baseline_tokens = count_tokens(baseline_content)
        breadcrumb_tokens = max(0, code_tokens - baseline_tokens)

    # Include DECISION.md as breadcrumb tokens too
    breadcrumb_tokens += decision_tokens

    tor = breadcrumb_tokens / total_tokens if total_tokens > 0 else 0.0

    return {
        "code_tokens": code_tokens,
        "autoresearch_tokens": autoresearch_tokens,
        "results_jsonl_tokens": results_tokens,
        "decision_tokens": decision_tokens,
        "system_tokens": system_tokens,
        "user_prompt_tokens": user_prompt_tokens,
        "total_tokens": total_tokens,
        "breadcrumb_tokens": breadcrumb_tokens,
        "TOR": round(tor, 4)
    }


def main():
    parser = argparse.ArgumentParser(description="Count tokens for breadcrumb eval scenarios")
    parser.add_argument("--code", help="Path to code file")
    parser.add_argument("--autoresearch", help="Path to autoresearch.md")
    parser.add_argument("--results", help="Path to results.jsonl")
    parser.add_argument("--decision", help="Optional path to DECISION.md")
    parser.add_argument("--baseline-code", help="Baseline code file (without breadcrumbs) to compute overhead")
    parser.add_argument("--all-conditions", action="store_true", help="Measure all fixture conditions")
    parser.add_argument("--fixtures-dir", default=".", help="Base directory for fixtures")
    args = parser.parse_args()

    base = Path(args.fixtures_dir)

    if args.all_conditions:
        conditions = [
            {
                "name": "no_breadcrumbs_2exp",
                "code": base / "fixtures/code/string_pipeline_v2_no_breadcrumbs.py",
                "autoresearch": base / "fixtures/autoresearch_states/session_2exp.md",
                "results": base / "fixtures/autoresearch_states/results_2exp.jsonl",
                "decision": None,
                "baseline_code": None
            },
            {
                "name": "inline_only_2exp",
                "code": base / "fixtures/code/string_pipeline_v2_with_breadcrumbs.py",
                "autoresearch": base / "fixtures/autoresearch_states/session_2exp.md",
                "results": base / "fixtures/autoresearch_states/results_2exp.jsonl",
                "decision": None,
                "baseline_code": base / "fixtures/code/string_pipeline_v2_no_breadcrumbs.py"
            },
            {
                "name": "no_breadcrumbs_10exp",
                "code": base / "fixtures/code/string_pipeline_v10_no_breadcrumbs.py",
                "autoresearch": base / "fixtures/autoresearch_states/session_10exp.md",
                "results": base / "fixtures/autoresearch_states/results_10exp.jsonl",
                "decision": None,
                "baseline_code": None
            },
            {
                "name": "inline_only_10exp",
                "code": base / "fixtures/code/string_pipeline_v10_with_breadcrumbs.py",
                "autoresearch": base / "fixtures/autoresearch_states/session_10exp.md",
                "results": base / "fixtures/autoresearch_states/results_10exp.jsonl",
                "decision": None,
                "baseline_code": base / "fixtures/code/string_pipeline_v10_no_breadcrumbs.py"
            },
            {
                "name": "decision_md_only_10exp",
                "code": base / "fixtures/code/string_pipeline_v10_no_breadcrumbs.py",
                "autoresearch": base / "fixtures/autoresearch_states/session_10exp.md",
                "results": base / "fixtures/autoresearch_states/results_10exp.jsonl",
                "decision": base / "fixtures/decisions/DECISION_v10.md",
                "baseline_code": base / "fixtures/code/string_pipeline_v10_no_breadcrumbs.py"
            },
            {
                "name": "inline_and_decision_10exp",
                "code": base / "fixtures/code/string_pipeline_v10_with_breadcrumbs.py",
                "autoresearch": base / "fixtures/autoresearch_states/session_10exp.md",
                "results": base / "fixtures/autoresearch_states/results_10exp.jsonl",
                "decision": base / "fixtures/decisions/DECISION_v10.md",
                "baseline_code": base / "fixtures/code/string_pipeline_v10_no_breadcrumbs.py"
            },
        ]

        results = []
        for cond in conditions:
            metrics = measure_condition(
                str(cond["code"]),
                str(cond["autoresearch"]),
                str(cond["results"]),
                str(cond["decision"]) if cond["decision"] else None,
                str(cond["baseline_code"]) if cond["baseline_code"] else None
            )
            results.append({"condition": cond["name"], **metrics})

        print(json.dumps(results, indent=2))

        # Also print a simple table
        print("\n--- Token Overhead Summary ---", file=sys.stderr)
        print(f"{'Condition':<35} {'Total':>8} {'Breadcrumb':>12} {'TOR':>6}", file=sys.stderr)
        print("-" * 65, file=sys.stderr)
        for r in results:
            print(f"{r['condition']:<35} {r['total_tokens']:>8} {r['breadcrumb_tokens']:>12} {r['TOR']:>6.3f}", file=sys.stderr)

    elif args.code and args.autoresearch and args.results:
        metrics = measure_condition(
            args.code, args.autoresearch, args.results,
            args.decision, args.baseline_code
        )
        print(json.dumps(metrics, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
