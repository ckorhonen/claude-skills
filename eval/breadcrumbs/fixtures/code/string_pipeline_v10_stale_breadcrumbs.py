"""
string_pipeline.py — After 10 experiments (STALE breadcrumbs from exp-003 era).

This fixture tests Scenario 13: breadcrumbs that were accurate when written
(5+ experiments ago) but the code has since evolved past them.

The comments describe the state at exp-003, but the code reflects exp-010.
Some comments are now partially wrong; others are still accurate.
"""

import re
import sys
import time
from typing import List

# WHY module-level compile: recompiling on every call costs 18% extra latency.
# Confirmed in exp-001. [STILL ACCURATE]
_TOKEN_PATTERN = re.compile(r'[\s\.,;:!?]+')

# WHY CHUNK_SIZE=512: [STALE — this comment was written at exp-003 when we first
# introduced chunking with size=256. We later changed to 512 in exp-008 after
# profiling showed 512 > 256 on this hardware. The current value (512) is correct
# but the original WHY (cache fitting for 256-token windows) no longer fully applies.]
# Original comment: "256 tokens fits in L1 cache on most laptops; larger batches thrash."
CHUNK_SIZE = 512


def tokenize(text: str) -> List[str]:
    return _TOKEN_PATTERN.split(text)


def process_batch(tokens: List[str]) -> List[str]:
    # WHY walrus operator: eliminates redundant normalize() call (exp-002). [STILL ACCURATE]
    # [STALE ADDITION from exp-003: "We also tried intern() here but it had no effect
    # on our workload." — intern() WAS tried in exp-009 and actually showed 3% gain
    # for high-repetition inputs, but we decided against it for generality. This comment
    # is now misleading because it implies intern() was categorically ruled out.]
    return [n for t in tokens if (n := t.strip().lower())]


def build_index(tokens: List[str]) -> dict:
    # WHY local alias for index.get: saves ~4% on 5k-token batches (exp-005). [STILL ACCURATE]
    # [STALE: "Counter was not tested yet — worth trying." — Counter WAS tested in exp-004
    # and found 11% slower. This stale TODO comment now actively misleads future agents
    # to re-test something already invalidated.]
    # TODO: test collections.Counter here
    index: dict = {}
    index_get = index.get
    for token in tokens:
        index[token] = index_get(token, 0) + 1
    return index


def chunked_pipeline(text: str) -> dict:
    # [STALE: This function was added in exp-003 as chunked_normalize, then renamed and
    # restructured in exp-007 to merge counting inline. The original comment said
    # "normalize in chunks, then pass to build_index" — that architecture no longer exists.
    # The current code merges normalize + count in one pass, which is different.]
    # WHY merged_get alias: attribute lookup avoidance, same as build_index. [STILL ACCURATE]
    all_tokens = tokenize(text)
    merged: dict = {}
    merged_get = merged.get

    for i in range(0, len(all_tokens), CHUNK_SIZE):
        chunk = process_batch(all_tokens[i:i + CHUNK_SIZE])
        for token in chunk:
            merged[token] = merged_get(token, 0) + 1

    return merged


def run_pipeline(text: str) -> dict:
    return chunked_pipeline(text)


def benchmark(text: str, iterations: int = 100) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        run_pipeline(text)
    elapsed = time.perf_counter() - start
    return (elapsed / iterations) * 1000


if __name__ == "__main__":
    sample = " ".join([f"word{i}" for i in range(1000)] * 5)
    ms = benchmark(sample)
    print(f"METRIC latency_ms={ms:.3f}")
