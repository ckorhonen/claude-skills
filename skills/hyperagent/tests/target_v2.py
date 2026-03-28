#!/usr/bin/env python3
"""Gen-002: Combine all sentences and use keyword extraction."""

def summarize(text: str) -> str:
    """Extract key nouns/words from all sentences by removing stopwords."""
    stopwords = {'the', 'a', 'an', 'is', 'it', 'in', 'for', 'and', 'or',
                 'but', 'with', 'over', 'by', 'are', 'was', 'were', 'its',
                 'be', 'been', 'have', 'has', 'had', 'to', 'of', 'at', 'on',
                 'from', 'that', 'this', 'which', 'who', 'more', 'most'}
    words = text.lower().split()
    keywords = [w.strip('.,!?') for w in words if w.strip('.,!?') not in stopwords]
    return ' '.join(keywords)

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
