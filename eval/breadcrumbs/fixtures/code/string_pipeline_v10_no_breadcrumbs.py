"""
string_pipeline.py — After 10 optimization experiments (no breadcrumbs).

Accumulated optimizations: compiled regex, list comprehension, pre-sized index,
Counter replacement rejected, intern() for repeated tokens, CHUNK_SIZE=512.
"""

import re
import sys
import time
from typing import List

_TOKEN_PATTERN = re.compile(r'[\s\.,;:!?]+')

CHUNK_SIZE = 512


def tokenize(text: str) -> List[str]:
    return _TOKEN_PATTERN.split(text)


def process_batch(tokens: List[str]) -> List[str]:
    return [n for t in tokens if (n := t.strip().lower())]


def build_index(tokens: List[str]) -> dict:
    index: dict = {}
    index_get = index.get
    for token in tokens:
        index[token] = index_get(token, 0) + 1
    return index


def chunked_pipeline(text: str) -> dict:
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
