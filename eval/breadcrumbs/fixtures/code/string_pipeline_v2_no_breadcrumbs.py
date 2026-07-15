"""
string_pipeline.py — After 2 optimization experiments (no breadcrumbs).

Optimizations applied: exp-001 (compiled regex), exp-002 (list comprehension in normalize batch).
"""

import re
import time
from typing import Iterator, List

_TOKEN_PATTERN = re.compile(r'[\s\.,;:!?]+')


def tokenize(text: str) -> List[str]:
    return _TOKEN_PATTERN.split(text)


def normalize(token: str) -> str:
    return token.strip().lower()


def process_batch(tokens: List[str]) -> List[str]:
    return [n for t in tokens if (n := t.strip().lower())]


def build_index(tokens: List[str]) -> dict:
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
