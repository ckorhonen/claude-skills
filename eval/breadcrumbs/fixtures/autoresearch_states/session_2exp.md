# Autoresearch: Reduce latency in string_pipeline.py

## Objective
Minimize `latency_ms` (wall-clock time per call, median of 5 trials) in `string_pipeline.py`.
Target workload: 5,000-token input document processed 100 times.

## Up-Front Answers
- Primary metric: `latency_ms`
- Unit: ms
- Direction: lower
- Minimum meaningful improvement: 1%
- Workload command: `python3 string_pipeline.py`
- Correctness gates: `python3 -m pytest tests/`
- Budget: 20 experiments or plateau after 3 consecutive non-improvements

## Scope
- In scope: `string_pipeline.py`
- Off limits: `tests/`, benchmark harness

## Decision Rule
2 warmup trials, 5 measured trials. Keep if median improves ≥ 1% and tests pass.

## Experiment Ledger
`.autoresearch/results.jsonl`

## Current Best Result
Baseline: 12.4 ms → After exp-002: 9.8 ms (21% improvement)

## What We've Learned
- Compiling the regex at module level (not per-call) gave a clean 18% speedup with no downsides.
- Replacing the explicit normalize() loop with a walrus-operator list comprehension eliminated
  a redundant function call per token and cut another 6% of latency.
- `dict.get()` and `defaultdict` were both tried informally (no full experiment) and appeared
  slower than the explicit key-check for our workload's token distribution.
