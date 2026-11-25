"""
string_pipeline.py — After 2 optimization experiments (with breadcrumbs).

Optimizations applied: exp-001 (compiled regex), exp-002 (list comprehension in normalize batch).
"""

import re
import time
from typing import Iterator, List

# WHY module-level compile: re.split() recompiles the pattern on every call.
# Compiling once at module load gave 18% latency reduction (exp-001, 2026-03-10).
# Do NOT move this inside tokenize() — that reverts the gain.
_TOKEN_PATTERN = re.compile(r'[\s\.,;:!?]+')


def tokenize(text: str) -> List[str]:
    return _TOKEN_PATTERN.split(text)


def normalize(token: str) -> str:
    return token.strip().lower()


def process_batch(tokens: List[str]) -> List[str]:
    # WHY walrus + list comprehension: avoids a second pass and a separate normalize() call
    # per token. Profiling showed normalize() overhead was 30% of process_batch time (exp-002).
    # The walrus operator (:=) assigns AND filters in one pass — do not split into two loops.
    return [n for t in tokens if (n := t.strip().lower())]


def build_index(tokens: List[str]) -> dict:
    # NOTE: dict.get() and defaultdict were tested (exp-001 notes) — both slower than
    # explicit key-check for typical token distributions due to function call overhead.
    index = {}
    for token in tokens:
        if token in index:
            index[token] += 1
        else:
            index[token] = 1
    return index


def run_pipeline(text: str) -> dict:
    raw_tokens = tokenize(text)
    processed = process_batch(raw_tokens)
    index = build_index(processed)
    return index


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
