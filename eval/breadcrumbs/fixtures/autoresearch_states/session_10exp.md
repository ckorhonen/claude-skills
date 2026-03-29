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
Baseline: 12.4 ms → After exp-010: 7.1 ms (43% total improvement over baseline)

## What We've Learned

### Wins
- **Compiled regex (exp-001):** Module-level `re.compile()` removed per-call pattern recompilation. 18% gain.
- **Walrus list comprehension (exp-002):** Eliminated redundant normalize() call per token. 4% gain.
- **Local `dict.get` alias (exp-005):** `index_get = index.get` before the loop avoids repeated attribute lookup. 4% gain.
- **Chunked processing with CHUNK_SIZE=512 (exp-008):** Processes tokens in 512-token windows so the working set fits in CPU L1 cache. 9% gain. Profiling showed 512 outperformed 128, 256, 1024.

### Dead Ends (do not re-test)
- **collections.Counter (exp-004):** Counter was 11% SLOWER for our workload. Our token distribution has high unique-token rate and low repetition, which is Counter's worst case. This is fundamental to our data, not an implementation artifact.
- **sys.intern() for token deduplication (exp-003):** No measurable gain on our workload. intern() helps when tokens are used as dict keys repeatedly across many calls, but our pipeline is stateless per-call.
- **Multiprocessing (exp-006):** Process spawn overhead (>50 ms) dominated the 7 ms we were trying to save. Only viable if batches are much larger (>50k tokens).
- **numpy array operations for counting (exp-007):** Conversion overhead to/from numpy exceeded the vectorized counting benefit for our token sizes. Only potentially useful at 100k+ unique tokens.
- **Pre-allocated dict with estimated size (exp-009):** Python dicts don't support pre-allocation; the CPython implementation grows amortized. This experiment confirmed no gain from hinting size.
- **defaultdict(int) (exp-010 side-test):** Slightly slower than explicit key-check due to __missing__ call overhead. Tested as sanity check after exp-005 finding.

### Structural Insights
- The pipeline is CPU-bound on the `build_index` loop, not on regex or string operations.
- Token uniqueness rate in our workload is ~60% (3k unique tokens from 5k total). This makes frequency-counting approaches like numpy less competitive.
- L1 cache effects are real and significant for this workload. The 512-chunk size discovery suggests further cache-aware restructuring may be worth exploring.
