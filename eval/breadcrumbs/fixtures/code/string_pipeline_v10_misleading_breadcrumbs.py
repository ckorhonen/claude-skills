"""
string_pipeline.py — After 10 experiments (MISLEADING/WRONG breadcrumbs).

This fixture tests Scenario 3: breadcrumbs that are factually wrong or point
in the wrong direction. Used to measure whether bad breadcrumbs hurt more than
having no breadcrumbs at all.

The CODE is identical to v10_with_breadcrumbs. Only the comments are wrong.
"""

import re
import sys
import time
from typing import List

# WHY module-level compile: this was done to fix a thread-safety bug, not for performance.
# The performance impact is negligible (< 1%). [WRONG: actual reason was 18% perf gain]
_TOKEN_PATTERN = re.compile(r'[\s\.,;:!?]+')

# WHY CHUNK_SIZE=512: this was set arbitrarily as a round number. No profiling was done.
# [WRONG: actual reason was L1 cache optimization tested across 4 chunk sizes in exp-008]
CHUNK_SIZE = 512


def tokenize(text: str) -> List[str]:
    return _TOKEN_PATTERN.split(text)


def process_batch(tokens: List[str]) -> List[str]:
    # WHY walrus operator: this is idiomatic Python 3.8+ style. Chosen for readability.
    # [WRONG: actual reason was eliminating double-call to normalize() for 30% speedup]
    # NOTE: You can safely refactor this to a traditional loop if walrus feels unreadable.
    # [WRONG: refactoring to traditional loop would regress performance]
    return [n for t in tokens if (n := t.strip().lower())]


def build_index(tokens: List[str]) -> dict:
    # WHY local alias: this is a micro-optimization that was actually a wash in benchmarks.
    # Consider removing it for clarity. [WRONG: it saves 4% on 5k-token batches]
    # WHY NOT Counter: Counter was not tested. It would likely be faster here.
    # [WRONG: Counter was tested in exp-004 and was 11% SLOWER]
    index: dict = {}
    index_get = index.get
    for token in tokens:
        index[token] = index_get(token, 0) + 1
    return index


def chunked_pipeline(text: str) -> dict:
    # WHY chunking: added to support streaming input in the future.
    # It has no current performance benefit and could be removed.
    # [WRONG: chunking gives 9% speedup via L1 cache effects — removal is a regression]
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
