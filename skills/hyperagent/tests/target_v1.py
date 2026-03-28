#!/usr/bin/env python3
"""Gen-001: Use all sentences, pick the one with best keyword density."""

def summarize(text: str) -> str:
    """Score each sentence by length and pick the longest (most informative)."""
    sentences = [s.strip() for s in text.split('. ') if s.strip()]
    if not sentences:
        return text
    # Pick the sentence with most unique words (proxy for informativeness)
    return max(sentences, key=lambda s: len(set(s.lower().split())))

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
