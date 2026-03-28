#!/usr/bin/env python3
"""Gen-003: TF-IDF style sentence scoring - pick top-2 sentences by keyword density."""

def summarize(text: str) -> str:
    """Score sentences by keyword density (non-stopword ratio) and combine top 2."""
    stopwords = {'the', 'a', 'an', 'is', 'it', 'in', 'for', 'and', 'or',
                 'but', 'with', 'over', 'by', 'are', 'was', 'were', 'its',
                 'be', 'been', 'have', 'has', 'had', 'to', 'of', 'at', 'on',
                 'from', 'that', 'this', 'which', 'who', 'more', 'most'}
    sentences = [s.strip() for s in text.split('. ') if s.strip()]
    if not sentences:
        return text

    def keyword_density(s):
        words = s.lower().split()
        if not words:
            return 0
        kws = [w.strip('.,!?') for w in words if w.strip('.,!?') not in stopwords]
        return len(kws) / len(words)

    ranked = sorted(sentences, key=keyword_density, reverse=True)
    top2 = ranked[:min(2, len(ranked))]
    return ' '.join(top2)

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
