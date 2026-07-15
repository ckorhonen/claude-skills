#!/usr/bin/env python3
"""
call_agent.py — Call the Anthropic API with a scenario's prompt and workspace files.

Assembles the full prompt from workspace files and scenario stimulus,
calls the model, and saves the response.

Usage:
    python3 call_agent.py \
        --scenario scenario.json \
        --workspace /tmp/eval-workspace-XXX \
        --model claude-opus-4 \
        --output agent_response.txt
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


def build_file_context(workspace: Path, context_files: list[str]) -> str:
    """Read workspace files and format them as context."""
    parts = []
    for pattern in context_files:
        if "*" in pattern:
            files = sorted(workspace.glob(pattern))
        else:
            files = [workspace / pattern]

        for fpath in files:
            if fpath.exists():
                content = fpath.read_text()
                parts.append(f"--- {fpath.name} ---\n{content}")
            else:
                print(f"  WARNING: Context file not found: {fpath}", file=sys.stderr)

    return "\n\n".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--model", default="claude-opus-4")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-tokens", type=int, default=4096)
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    workspace = Path(args.workspace)
    scenario = json.loads(Path(args.scenario).read_text())

    stimulus = scenario.get("stimulus", {})
    system_prompt = stimulus.get("system_prompt", "You are an optimization research assistant.")
    user_prompt = stimulus.get("user_prompt", "")
    context_files = stimulus.get("context_files", [])

    # Build file context
    file_context = build_file_context(workspace, context_files)

    # Full user message = file context + prompt
    full_user_message = f"{file_context}\n\n{user_prompt}" if file_context else user_prompt

    print(f"Calling {args.model} (max_tokens={args.max_tokens})...", file=sys.stderr)
    print(f"Prompt size: ~{len(full_user_message)//4} tokens (estimated)", file=sys.stderr)

    response = client.messages.create(
        model=args.model,
        max_tokens=args.max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": full_user_message}]
    )

    response_text = response.content[0].text
    Path(args.output).write_text(response_text)

    print(f"Response saved: {args.output} ({len(response_text)} chars)", file=sys.stderr)
    print(f"Usage: {response.usage}", file=sys.stderr)


if __name__ == "__main__":
    main()
