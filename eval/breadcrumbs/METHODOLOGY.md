# Methodology

## Experimental Design

This eval uses a **between-conditions** design: each scenario exists in a `with_breadcrumbs` and `without_breadcrumbs` variant that differ *only* in whether code comments and/or DECISION.md files are present.

All other variables are held constant:
- Same underlying code logic and performance characteristics
- Same `autoresearch.md` narrative ("What We've Learned" section)
- Same `.autoresearch/results.jsonl` ledger entries
- Same prompt template
- Same model (default: `claude-opus-4`) and temperature (default: `1.0`)

## Scenario Structure

Each scenario is a JSON file with the following schema:

```json
{
  "id": "scenario_01",
  "dimension": "A",
  "name": "Resume accuracy — with breadcrumbs",
  "condition": "with_breadcrumbs",
  "hypothesis": "Agents given breadcrumbs will propose more novel hypotheses",
  "setup": {
    "code_fixture": "fixtures/code/string_pipeline_v5_with_breadcrumbs.py",
    "autoresearch_fixture": "fixtures/autoresearch_states/session_10exp.md",
    "results_fixture": "fixtures/autoresearch_states/results_10exp.jsonl",
    "decision_fixture": null
  },
  "stimulus": {
    "system_prompt": "You are running the autoresearch skill...",
    "user_prompt": "Resume the autoresearch session. Propose the next 3 experiments."
  },
  "measurement": {
    "extract": "proposed_hypotheses",
    "judge": "judges/novelty_judge.py",
    "metrics": ["HNS", "DERR"]
  },
  "pass_criteria": {
    "HNS_min": 0.7,
    "DERR_max": 0.15
  }
}
```

## Metrics

### Hypothesis Novelty Score (HNS)

Measures how semantically distinct proposed hypotheses are from the set of already-tried hypotheses in the ledger.

**Computation:**
1. Embed each proposed hypothesis and each past hypothesis with a text embedding model.
2. For each proposed hypothesis, compute cosine distance to its nearest neighbor in the past-hypothesis set.
3. HNS = mean of these distances across all proposals.

**Range:** 0 (identical to past work) → 1 (maximally novel)

**Threshold:** HNS ≥ 0.70 = PASS (proposals are meaningfully different from past work)

### Dead-End Repeat Rate (DERR)

Fraction of proposed hypotheses that correspond to experiments already tried and **discarded** in the ledger.

**Computation:**
1. For each proposed hypothesis, check if a semantically similar hypothesis (cosine similarity > 0.85) exists in the ledger with `disposition: "discard"` or `disposition: "crash"`.
2. DERR = count of matches / total proposals.

**Range:** 0 (no repeats) → 1 (all proposals are rehashed discards)

**Threshold:** DERR ≤ 0.10 = PASS

### Regression Rate (RR)

Fraction of proposed code changes that would undo an optimization already marked `keep` in the ledger.

**Computation:**
1. Extract the proposed code change from the agent output (diff or description).
2. For each `keep` experiment in the ledger, check if the proposed change would revert that optimization (LLM judge).
3. RR = count of reversions / total proposals.

**Range:** 0 (no regressions) → 1 (all proposals undo prior wins)

**Threshold:** RR ≤ 0.05 = PASS

### Session Bootstrap Time (SBT)

Total input tokens consumed before the agent emits its first experiment proposal.

**Computation:** Count tokens in all messages up to (but not including) the first `exp-` or `experiment` reference in the output.

**Purpose:** Measures how much "orienting" the agent does before acting. Breadcrumbs may reduce SBT by providing clear context, or increase it by adding tokens the agent must read.

### Token Overhead Ratio (TOR)

Breadcrumb tokens as a fraction of total context tokens.

```
TOR = breadcrumb_tokens / (code_tokens + context_tokens + breadcrumb_tokens)
```

**Purpose:** Identifies at what TOR value quality metrics start to degrade (context pressure).

## Statistical Approach

For each metric, we run each scenario **N=10 times** (to account for LLM variance) and report:
- Mean ± standard deviation
- Median
- Effect size (Cohen's d) between with/without breadcrumbs conditions
- p-value from a two-tailed Welch's t-test

**Minimum detectable effect size:** d=0.5 (medium) with N=10 per condition gives ~50% power at α=0.05. For stronger confidence, increase N.

## Judge Prompts

### Novelty Judge

```
You are evaluating whether a proposed experiment hypothesis is novel relative to a set of past hypotheses.

PAST HYPOTHESES (already tried):
{past_hypotheses}

PROPOSED HYPOTHESIS:
{proposed_hypothesis}

Score from 0.0 to 1.0:
- 0.0 = This is essentially the same hypothesis as a past one (same mechanism, same prediction)
- 0.5 = This is related but meaningfully different (different mechanism or different prediction)
- 1.0 = This is completely novel (no clear connection to past hypotheses)

Reply with only a JSON object: {"score": 0.0, "reason": "one sentence"}
```

### Regression Judge

```
You are evaluating whether a proposed code change would undo an optimization that was previously kept.

KEPT OPTIMIZATION:
Change: {kept_change_summary}
Reason: {kept_reason}
Code after optimization: {kept_code_snippet}

PROPOSED CHANGE:
{proposed_change}

Would the proposed change revert or negate the kept optimization?
Reply with only a JSON object: {"regresses": true/false, "confidence": 0.0-1.0, "reason": "one sentence"}
```

## Fixture Construction

Fixtures represent a string processing pipeline (`string_pipeline.py`) that has been through varying depths of autoresearch optimization. The pipeline includes:
- Token splitting
- Normalization
- Buffer management  
- Batch processing
- Cache utilization

Each optimization depth (2 experiments, 5 experiments, 10 experiments) has:
- A "with breadcrumbs" variant: inline comments explaining WHY each pattern was chosen
- A "without breadcrumbs" variant: same code, no explanatory comments
- A matching `results.jsonl` with the corresponding experiment history

## Confounders to Watch For

1. **Comment length signal**: Commented code is longer. Longer code = more tokens. Control: count baseline tokens with neutral comments (e.g., `# TODO`) vs. explanatory comments.

2. **Comment as documentation**: Some comments describe WHAT, not WHY. Only WHY-explaining comments count as "breadcrumbs" for this eval.

3. **autoresearch.md bleed**: The `autoresearch.md` "What We've Learned" section may partially replicate breadcrumb information. Ensure ledger fixtures are identical across conditions.

4. **Order effects in multi-experiment runs**: If the agent runs multiple experiments, later ones benefit from earlier ones' outputs regardless of breadcrumbs. Measure only the *first* proposed experiment to isolate the effect.

5. **Model capability**: A more capable model may reconstruct the missing WHY from the code structure alone. Test across model tiers.
