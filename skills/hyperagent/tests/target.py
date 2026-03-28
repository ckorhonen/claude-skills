#!/usr/bin/env python3
"""Target: a text summarizer that scores itself via word overlap (ROUGE-like)."""

def summarize(text: str) -> str:
    """Baseline summarizer: just take the first sentence."""
    sentences = text.split('. ')
    return sentences[0] if sentences else text

def score(summary: str, reference: str) -> float:
    """Word overlap score (like ROUGE-1 recall)."""
    ref_words = set(reference.lower().split())
    sum_words = set(summary.lower().split())
    if not ref_words:
        return 0.0
    return len(sum_words & ref_words) / len(ref_words)

SAMPLES = [
    {
        "text": "The quick brown fox jumps over the lazy dog. It ran across the field. The dog barked loudly.",
        "reference": "fox dog field barked"
    },
    {
        "text": "Python is a programming language. It is widely used in data science. Many developers prefer Python for its readability.",
        "reference": "python programming data science developers readability"
    },
    {
        "text": "Climate change affects global weather patterns. Rising temperatures cause more extreme events. Scientists urge immediate action.",
        "reference": "climate temperature extreme events scientists action"
    },
]

if __name__ == "__main__":
    scores = []
    for sample in SAMPLES:
        s = summarize(sample["text"])
        sc = score(s, sample["reference"])
        scores.append(sc)

    avg_score = sum(scores) / len(scores)
    print(f"METRIC score={avg_score:.4f}")
