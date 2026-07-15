"""
string_pipeline.py — Baseline version (no optimizations applied).

Processes a stream of text tokens: split, normalize, batch, emit.
This is the pre-optimization state that all autoresearch sessions start from.
"""

import re
import time
from typing import Iterator, List


def tokenize(text: str) -> List[str]:
    """Split text into tokens on whitespace and punctuation."""
    return re.split(r'[\s\.,;:!?]+', text)


def normalize(token: str) -> str:
    """Normalize a single token to lowercase stripped form."""
    return token.strip().lower()


def process_batch(tokens: List[str]) -> List[str]:
    """Process a batch of tokens through normalization."""
    result = []
    for token in tokens:
        normalized = normalize(token)
        if normalized:
            result.append(normalized)
    return result


def build_index(tokens: List[str]) -> dict:
    """Build a frequency index from a list of tokens."""
    index = {}
    for token in tokens:
        if token in index:
            index[token] += 1
        else:
            index[token] = 1
    return index


def run_pipeline(text: str) -> dict:
    """Run the full pipeline: tokenize → normalize → index."""
    raw_tokens = tokenize(text)
    processed = process_batch(raw_tokens)
    index = build_index(processed)
    return index


def benchmark(text: str, iterations: int = 100) -> float:
    """Time the pipeline over multiple iterations."""
    start = time.perf_counter()
    for _ in range(iterations):
        run_pipeline(text)
    elapsed = time.perf_counter() - start
    return (elapsed / iterations) * 1000  # ms per call


if __name__ == "__main__":
    sample = " ".join([f"word{i}" for i in range(1000)] * 5)
    ms = benchmark(sample)
    print(f"METRIC latency_ms={ms:.3f}")
