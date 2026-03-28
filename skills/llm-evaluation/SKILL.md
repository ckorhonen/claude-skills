---
name: llm-evaluation
description: Implement comprehensive evaluation strategies for LLM applications using automated metrics, LLM-as-judge, human feedback, and benchmarking. Use when testing LLM performance, measuring AI application quality, comparing prompts/models, or establishing evaluation frameworks. Covers RAGAS for RAG pipelines, evals-as-code CI/CD integration, and modern 2025/2026 practices including structured output evaluation and agentic task success measurement.
---

# LLM Evaluation

Master comprehensive evaluation strategies for LLM applications, from automated metrics to human evaluation and A/B testing.

## When to Use This Skill

- Measuring LLM application performance systematically
- Comparing different models or prompts
- Detecting performance regressions before deployment
- Validating improvements from prompt changes
- Building confidence in production systems
- Establishing baselines and tracking progress over time
- Debugging unexpected model behavior
- Evaluating RAG pipeline quality (retrieval + generation)
- Measuring agentic task success rates
- Testing structured output schema compliance

## Core Evaluation Types

### 1. Automated Metrics
Fast, repeatable, scalable evaluation using computed scores.

**Text Generation:**
- **BLEU**: N-gram overlap (translation)
- **ROUGE**: Recall-oriented (summarization)
- **METEOR**: Semantic similarity
- **BERTScore**: Embedding-based similarity
- **Perplexity**: Language model confidence

**Classification:**
- **Accuracy**: Percentage correct
- **Precision/Recall/F1**: Class-specific performance
- **Confusion Matrix**: Error patterns
- **AUC-ROC**: Ranking quality

**Retrieval (RAG):**
- **MRR**: Mean Reciprocal Rank
- **NDCG**: Normalized Discounted Cumulative Gain
- **Precision@K**: Relevant in top K
- **Recall@K**: Coverage in top K

### 2. Human Evaluation
Manual assessment for quality aspects difficult to automate.

**Dimensions:**
- **Accuracy**: Factual correctness
- **Coherence**: Logical flow
- **Relevance**: Answers the question
- **Fluency**: Natural language quality
- **Safety**: No harmful content
- **Helpfulness**: Useful to the user

### 3. LLM-as-Judge
Use stronger LLMs to evaluate weaker model outputs. This is the dominant approach in 2025/2026 for open-ended tasks.

**Approaches:**
- **Pointwise**: Score individual responses (0-10 Likert scales)
- **Pairwise**: Compare two responses (preferred by MT-Bench, Chatbot Arena)
- **Reference-based**: Compare to gold standard answer
- **Reference-free**: Judge without ground truth (good for creative/open-ended tasks)
- **Rubric-based**: Judge against explicit criteria (best for consistency)
- **Constitutional**: Check against a set of principles or rules

**Key challenges:**
- Position bias: judge models prefer whichever response appears first
- Verbosity bias: longer responses often rated higher regardless of quality
- Self-preference bias: a model may favor its own outputs
- Mitigation: swap order and average; use structured rubrics; use 3rd-party judges

### 4. RAG-Specific Evaluation (RAGAS)

For Retrieval-Augmented Generation pipelines, use RAGAS metrics:

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,        # Is answer grounded in retrieved context?
    answer_relevancy,   # Does answer address the question?
    context_precision,  # Is retrieved context relevant?
    context_recall,     # Is all necessary info retrieved?
)
from datasets import Dataset

# Prepare evaluation dataset
data = {
    "question": ["What is the capital of France?"],
    "answer": ["Paris is the capital of France."],
    "contexts": [["Paris is a city in France. It is the capital."]],
    "ground_truth": ["Paris"]
}

dataset = Dataset.from_dict(data)
result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
print(result)
```

**RAGAS metric interpretation:**
- **Faithfulness** (0-1): Low score = hallucination. Critical for factual applications.
- **Answer Relevancy** (0-1): Low = answer is off-topic or evasive.
- **Context Precision** (0-1): Low = retrieval fetching irrelevant chunks.
- **Context Recall** (0-1): Low = missing relevant documents in retrieval.

### 5. Agentic Task Evaluation

For agents that execute multi-step tasks:

```python
class AgentTaskEvaluator:
    """Evaluate agentic task completion."""

    def evaluate_task(self, task, agent_trajectory, expected_result):
        return {
            "task_success": self._check_task_success(agent_trajectory, expected_result),
            "tool_use_accuracy": self._check_tool_selection(agent_trajectory),
            "step_efficiency": self._measure_step_efficiency(agent_trajectory),
            "hallucination_rate": self._check_for_hallucinations(agent_trajectory),
        }

    def _check_task_success(self, trajectory, expected):
        # Did agent achieve the goal? (binary or partial credit)
        final_state = trajectory[-1]["state"]
        return compare_states(final_state, expected)

    def _measure_step_efficiency(self, trajectory):
        # How many extra steps did agent take? (vs. optimal path)
        actual_steps = len(trajectory)
        optimal_steps = self.get_optimal_path_length(trajectory[0]["task"])
        return optimal_steps / actual_steps  # 1.0 = optimal

    def _check_tool_selection(self, trajectory):
        # Did agent use correct tools in correct order?
        correct_tools = sum(1 for step in trajectory if step["tool_correct"])
        return correct_tools / len(trajectory)
```

**Key agentic metrics:**
- **Task completion rate**: % of tasks fully completed
- **Step efficiency**: optimal steps / actual steps taken
- **Tool selection accuracy**: correct tool chosen / total tool calls
- **Error recovery**: did agent recover from mistakes?
- **Hallucinated tool calls**: tools called with made-up parameters

## Quick Start

```python
from llm_eval import EvaluationSuite, Metric

# Define evaluation suite
suite = EvaluationSuite([
    Metric.accuracy(),
    Metric.bleu(),
    Metric.bertscore(),
    Metric.custom(name="groundedness", fn=check_groundedness)
])

# Prepare test cases
test_cases = [
    {
        "input": "What is the capital of France?",
        "expected": "Paris",
        "context": "France is a country in Europe. Paris is its capital."
    },
    # ... more test cases
]

# Run evaluation
results = suite.evaluate(
    model=your_model,
    test_cases=test_cases
)

print(f"Overall Accuracy: {results.metrics['accuracy']}")
print(f"BLEU Score: {results.metrics['bleu']}")
```

## Automated Metrics Implementation

### BLEU Score
```python
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def calculate_bleu(reference, hypothesis):
    """Calculate BLEU score between reference and hypothesis."""
    smoothie = SmoothingFunction().method4

    return sentence_bleu(
        [reference.split()],
        hypothesis.split(),
        smoothing_function=smoothie
    )

# Usage
bleu = calculate_bleu(
    reference="The cat sat on the mat",
    hypothesis="A cat is sitting on the mat"
)
```

### ROUGE Score
```python
from rouge_score import rouge_scorer

def calculate_rouge(reference, hypothesis):
    """Calculate ROUGE scores."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)

    return {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rougeL': scores['rougeL'].fmeasure
    }
```

### BERTScore
```python
from bert_score import score

def calculate_bertscore(references, hypotheses):
    """Calculate BERTScore using pre-trained BERT."""
    P, R, F1 = score(
        hypotheses,
        references,
        lang='en',
        model_type='microsoft/deberta-xlarge-mnli'
    )

    return {
        'precision': P.mean().item(),
        'recall': R.mean().item(),
        'f1': F1.mean().item()
    }
```

### Custom Metrics
```python
def calculate_groundedness(response, context):
    """Check if response is grounded in provided context."""
    # Use NLI model to check entailment
    from transformers import pipeline

    nli = pipeline("text-classification", model="microsoft/deberta-large-mnli")

    result = nli(f"{context} [SEP] {response}")[0]

    # Return confidence that response is entailed by context
    return result['score'] if result['label'] == 'ENTAILMENT' else 0.0

def calculate_toxicity(text):
    """Measure toxicity in generated text."""
    from detoxify import Detoxify

    results = Detoxify('original').predict(text)
    return max(results.values())  # Return highest toxicity score

def calculate_factuality(claim, knowledge_base):
    """Verify factual claims against knowledge base."""
    # Implementation depends on your knowledge base
    # Could use retrieval + NLI, or fact-checking API
    pass
```

## LLM-as-Judge Patterns

### Single Output Evaluation (Rubric-Based)
```python
from openai import OpenAI
import json

client = OpenAI()

def llm_judge_quality(response, question):
    """Use GPT-4.1 to judge response quality with structured output."""
    prompt = f"""You are an impartial evaluator. Rate the following response on a scale of 1-10 for each criterion.

**Criteria:**
1. Accuracy (1=many factual errors, 10=completely correct)
2. Helpfulness (1=doesn't address question, 10=fully resolves question)  
3. Clarity (1=confusing/unclear, 10=perfectly clear and well-structured)

**Question:** {question}
**Response:** {response}

Evaluate objectively. Provide ratings in JSON format:
{{
  "accuracy": <1-10>,
  "helpfulness": <1-10>,
  "clarity": <1-10>,
  "reasoning": "<2-3 sentence justification>",
  "overall": <1-10>
}}
"""

    result = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}  # Structured output
    )

    return json.loads(result.choices[0].message.content)


### Pairwise Comparison (with position bias mitigation)
```python
def compare_responses(question, response_a, response_b):
    """Compare two responses using LLM judge with position bias mitigation."""

    def _judge(q, r1, r2, label1, label2):
        prompt = f"""Compare these two responses to the question. Which is better?

Question: {q}

Response {label1}: {r1}

Response {label2}: {r2}

Which response is better and why? Consider accuracy, helpfulness, and clarity.

Answer with JSON:
{{
  "winner": "{label1}" or "{label2}" or "tie",
  "reasoning": "<explanation>",
  "confidence": <1-10>
}}
"""
        result = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        return json.loads(result.choices[0].message.content)

    # Run twice with swapped order to detect position bias
    result_ab = _judge(question, response_a, response_b, "A", "B")
    result_ba = _judge(question, response_b, response_a, "B", "A")  # swapped

    # Normalize result_ba back to A/B labels
    winner_ba_normalized = "A" if result_ba["winner"] == "B" else ("B" if result_ba["winner"] == "A" else "tie")

    # Check for consistency
    consistent = result_ab["winner"] == winner_ba_normalized
    if not consistent:
        final_winner = "tie"  # Disagree = call it a tie
    else:
        final_winner = result_ab["winner"]

    return {
        "winner": final_winner,
        "consistent": consistent,
        "reasoning_ab": result_ab["reasoning"],
        "reasoning_ba": result_ba["reasoning"],
    }
```

## Human Evaluation Frameworks

### Annotation Guidelines
```python
class AnnotationTask:
    """Structure for human annotation task."""

    def __init__(self, response, question, context=None):
        self.response = response
        self.question = question
        self.context = context

    def get_annotation_form(self):
        return {
            "question": self.question,
            "context": self.context,
            "response": self.response,
            "ratings": {
                "accuracy": {
                    "scale": "1-5",
                    "description": "Is the response factually correct?"
                },
                "relevance": {
                    "scale": "1-5",
                    "description": "Does it answer the question?"
                },
                "coherence": {
                    "scale": "1-5",
                    "description": "Is it logically consistent?"
                }
            },
            "issues": {
                "factual_error": False,
                "hallucination": False,
                "off_topic": False,
                "unsafe_content": False
            },
            "feedback": ""
        }
```

### Inter-Rater Agreement
```python
from sklearn.metrics import cohen_kappa_score

def calculate_agreement(rater1_scores, rater2_scores):
    """Calculate inter-rater agreement."""
    kappa = cohen_kappa_score(rater1_scores, rater2_scores)

    interpretation = {
        kappa < 0: "Poor",
        kappa < 0.2: "Slight",
        kappa < 0.4: "Fair",
        kappa < 0.6: "Moderate",
        kappa < 0.8: "Substantial",
        kappa <= 1.0: "Almost Perfect"
    }

    return {
        "kappa": kappa,
        "interpretation": interpretation[True]
    }
```

## A/B Testing

### Statistical Testing Framework
```python
from scipy import stats
import numpy as np

class ABTest:
    def __init__(self, variant_a_name="A", variant_b_name="B"):
        self.variant_a = {"name": variant_a_name, "scores": []}
        self.variant_b = {"name": variant_b_name, "scores": []}

    def add_result(self, variant, score):
        """Add evaluation result for a variant."""
        if variant == "A":
            self.variant_a["scores"].append(score)
        else:
            self.variant_b["scores"].append(score)

    def analyze(self, alpha=0.05):
        """Perform statistical analysis."""
        a_scores = self.variant_a["scores"]
        b_scores = self.variant_b["scores"]

        # T-test
        t_stat, p_value = stats.ttest_ind(a_scores, b_scores)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.std(a_scores)**2 + np.std(b_scores)**2) / 2)
        cohens_d = (np.mean(b_scores) - np.mean(a_scores)) / pooled_std

        return {
            "variant_a_mean": np.mean(a_scores),
            "variant_b_mean": np.mean(b_scores),
            "difference": np.mean(b_scores) - np.mean(a_scores),
            "relative_improvement": (np.mean(b_scores) - np.mean(a_scores)) / np.mean(a_scores),
            "p_value": p_value,
            "statistically_significant": p_value < alpha,
            "cohens_d": cohens_d,
            "effect_size": self.interpret_cohens_d(cohens_d),
            "winner": "B" if np.mean(b_scores) > np.mean(a_scores) else "A"
        }

    @staticmethod
    def interpret_cohens_d(d):
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"
```

## Regression Testing

### Regression Detection
```python
class RegressionDetector:
    def __init__(self, baseline_results, threshold=0.05):
        self.baseline = baseline_results
        self.threshold = threshold

    def check_for_regression(self, new_results):
        """Detect if new results show regression."""
        regressions = []

        for metric in self.baseline.keys():
            baseline_score = self.baseline[metric]
            new_score = new_results.get(metric)

            if new_score is None:
                continue

            # Calculate relative change
            relative_change = (new_score - baseline_score) / baseline_score

            # Flag if significant decrease
            if relative_change < -self.threshold:
                regressions.append({
                    "metric": metric,
                    "baseline": baseline_score,
                    "current": new_score,
                    "change": relative_change
                })

        return {
            "has_regression": len(regressions) > 0,
            "regressions": regressions
        }
```

## Benchmarking

### Running Benchmarks
```python
class BenchmarkRunner:
    def __init__(self, benchmark_dataset):
        self.dataset = benchmark_dataset

    def run_benchmark(self, model, metrics):
        """Run model on benchmark and calculate metrics."""
        results = {metric.name: [] for metric in metrics}

        for example in self.dataset:
            # Generate prediction
            prediction = model.predict(example["input"])

            # Calculate each metric
            for metric in metrics:
                score = metric.calculate(
                    prediction=prediction,
                    reference=example["reference"],
                    context=example.get("context")
                )
                results[metric.name].append(score)

        # Aggregate results
        return {
            metric: {
                "mean": np.mean(scores),
                "std": np.std(scores),
                "min": min(scores),
                "max": max(scores)
            }
            for metric, scores in results.items()
        }
```

## Resources

- **references/metrics.md**: Comprehensive metric guide
- **references/human-evaluation.md**: Annotation best practices
- **references/benchmarking.md**: Standard benchmarks
- **references/a-b-testing.md**: Statistical testing guide
- **references/regression-testing.md**: CI/CD integration
- **assets/evaluation-framework.py**: Complete evaluation harness
- **assets/benchmark-dataset.jsonl**: Example datasets
- **scripts/evaluate-model.py**: Automated evaluation runner

## CI/CD Integration: Evals as Code

Run evaluations automatically in your CI/CD pipeline:

```yaml
# .github/workflows/eval.yml
name: LLM Evaluation
on:
  pull_request:
    paths: ['prompts/**', 'src/llm/**']

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run evaluation suite
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pip install -r requirements-eval.txt
          python scripts/run_evaluations.py --baseline main --compare HEAD
          
      - name: Check for regression
        run: |
          python scripts/check_regression.py \
            --threshold 0.05 \
            --fail-on-regression
```

```python
# scripts/run_evaluations.py
import argparse
import json
from pathlib import Path

def run_eval_suite(model_fn, test_cases, metrics):
    """Run complete evaluation suite and return results."""
    results = []
    for case in test_cases:
        prediction = model_fn(case["input"])
        scores = {m.name: m.calculate(prediction, case["reference"]) for m in metrics}
        results.append({"case": case["id"], "scores": scores})
    
    aggregated = {
        metric: sum(r["scores"][metric] for r in results) / len(results)
        for metric in results[0]["scores"]
    }
    return aggregated

def main():
    # Load test cases
    test_cases = json.loads(Path("evals/test_cases.json").read_text())
    
    # Run evaluation
    results = run_eval_suite(your_model, test_cases, your_metrics)
    
    # Save results with git commit hash
    import subprocess
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    
    output = {"commit": commit, "metrics": results}
    Path(f"eval_results/{commit[:8]}.json").write_text(json.dumps(output, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
```

## Structured Output Evaluation

For applications that require structured outputs (JSON schemas, function calls):

```python
from pydantic import BaseModel, ValidationError

class ExpectedOutput(BaseModel):
    name: str
    age: int
    email: str

def evaluate_structured_output(model_response: str, expected: dict) -> dict:
    """Evaluate whether model output conforms to schema and matches expected values."""
    
    # 1. Schema compliance
    try:
        parsed = ExpectedOutput.model_validate_json(model_response)
        schema_valid = True
    except ValidationError as e:
        return {"schema_valid": False, "error": str(e), "field_accuracy": 0}
    
    # 2. Field accuracy
    expected_obj = ExpectedOutput(**expected)
    fields = ExpectedOutput.model_fields.keys()
    correct = sum(1 for f in fields if getattr(parsed, f) == getattr(expected_obj, f))
    
    return {
        "schema_valid": True,
        "field_accuracy": correct / len(fields),
        "fields_correct": correct,
        "fields_total": len(fields),
    }
```

## Best Practices

1. **Multiple Metrics**: Use diverse metrics for comprehensive view; no single metric tells the whole story
2. **Representative Data**: Test on real-world, diverse examples; adversarial examples too
3. **Baselines**: Always compare against baseline performance (previous prompt version, weaker model)
4. **Statistical Rigor**: Use proper statistical tests; bootstrap confidence intervals when n < 100
5. **Continuous Evaluation**: Integrate into CI/CD pipeline; eval on every prompt change
6. **Human Validation**: Periodically validate LLM-as-judge outputs against human raters
7. **Error Analysis**: Cluster failures to find systematic weaknesses, not just count them
8. **Version Control**: Track evaluation datasets and results in git; treat evals as code
9. **Position Bias Mitigation**: Swap A/B order in pairwise comparisons; average results
10. **Separate Dev/Test Sets**: Don't tune prompts on your test set; maintain held-out data

## Common Pitfalls

- **Single Metric Obsession**: Optimizing for one metric at the expense of others
- **Small Sample Size**: Drawing conclusions from too few examples (need 50+ for statistical power)
- **Data Contamination**: Testing on training data or data that was used to tune the prompt
- **Ignoring Variance**: Not accounting for statistical uncertainty; report confidence intervals
- **Metric Mismatch**: Using BLEU/ROUGE for open-ended tasks (they're correlation-poor for modern LLMs)
- **Judge Model Bias**: Not checking if your LLM judge has systematic biases
- **Benchmark Leakage**: Popular benchmarks may be in training data; prefer private evals
- **Ignoring Latency/Cost**: A metric improvement that triples cost may not be worth it
