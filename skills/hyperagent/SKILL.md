---
name: hyperagent
description: "Run a self-improving optimization loop inspired by the Hyperagents/Darwin Gödel Machine framework. Unlike linear autoresearch, this skill explores a TREE of solutions where the agent can modify both its task-solving code AND its own improvement strategy. Use when asked to 'run hyperagent', 'self-improving optimization', 'evolve this', or when optimization requires exploring fundamentally different approaches rather than incremental tuning."
compatibility: Requires python3, git, and a POSIX shell. Bundled scripts use only the Python standard library.
---

# Hyperagent

A self-improving optimization framework that goes beyond linear experiment loops. Based on the Darwin Gödel Machine (DGM-H) pattern from Meta AI research (arxiv:2603.19461), combined with the disciplined measurement infrastructure of autoresearch.

**Key difference from autoresearch:** Autoresearch runs a linear sequence of experiments with a fixed improvement strategy. Hyperagent explores a *tree* of solutions where each node can modify not just the task code but also *how it searches for improvements*. The meta-logic itself evolves.

## Core Concepts

### The Hyperagent Structure

A hyperagent is a unified program with two editable components:

1. **Task Agent** — the code that solves the target problem (benchmark runner, feature implementation, prompt template, etc.)
2. **Meta Agent** — the strategy for generating improvements. Unlike autoresearch's fixed loop, this is *part of the editable code*. The agent can change how it searches.

Both components live in the same editable workspace. When the meta agent generates a child variant, it can modify the task code, the meta strategy, or both.

### Archive of Stepping Stones

Instead of a single linear "best so far," hyperagent maintains a *population archive* — a tree of scored variants. Each variant is a potential parent for the next generation. This prevents getting stuck in local optima by preserving diverse approaches.

### Metacognitive Self-Modification

The agent doesn't just look for better solutions. It looks for *better ways of looking for better solutions*. If it detects that its current improvement strategy is plateauing, it can rewrite the strategy itself.

## When to Use Hyperagent vs. Autoresearch

| Situation | Use |
|-----------|-----|
| Optimizing a known metric with incremental changes | Autoresearch |
| Tuning hyperparameters or config values | Autoresearch |
| Exploring fundamentally different algorithmic approaches | **Hyperagent** |
| The search space is large with many local optima | **Hyperagent** |
| You want the system to discover novel strategies | **Hyperagent** |
| Prompt engineering with structural variation | **Hyperagent** |
| Evolving reward functions or evaluation criteria | **Hyperagent** |
| Budget is tight and you need efficiency | Autoresearch |

## Up-Front Q&A

Before starting, gather or confirm:

1. **Objective** — what are we optimizing?
2. **Primary metric** — name, unit, direction (higher/lower is better)
3. **Evaluation command** — how to score a variant
4. **Correctness gates** — non-negotiable constraints
5. **Scope** — what files may be modified
6. **Budget** — max iterations, max time, max cost (tokens/API calls)
7. **Exploration breadth** — how many children per parent? (default: 2-3)
8. **Archive size limit** — max stepping stones to maintain (default: 20)

## Workspace Setup

1. Create a dedicated worktree:

   ```bash
   git worktree add ../hyperagent-<goal>-<date> -b hyperagent/<goal>-<date>
   ```

2. Initialize the workspace:

   ```
   .hyperagent/
   ├── archive.jsonl          # All variants (the stepping stone archive)
   ├── tree.json              # Parent-child relationships
   ├── meta_strategy.md       # Current meta-agent strategy (editable by the agent)
   ├── improvements.md        # Agent's diary of insights
   ├── report.html            # Visual report
   └── plots/                 # Charts
   ```

3. Create required files:
   - `hyperagent.md` — session contract (like autoresearch.md)
   - `hyperagent.sh` — evaluation script
   - `hyperagent.checks.sh` — correctness gates (if needed)
   - `.hyperagent/meta_strategy.md` — the meta-agent's improvement strategy

4. Ensure `.hyperagent/` stays untracked:

   ```bash
   rg -qxF '.hyperagent/' .git/info/exclude || printf '\n.hyperagent/\n' >> .git/info/exclude
   ```

## Required Files

### `hyperagent.md`

The durable session contract. A fresh agent should be able to resume from this.

```markdown
# Hyperagent: <goal>

## Objective
<What is being optimized and why.>

## Configuration
- Primary metric:
- Unit:
- Direction:
- Evaluation command:
- Correctness gates:
- Budget: <max iterations> iterations, <max time>
- Exploration breadth: <children per parent>
- Archive size limit: <max stepping stones>

## Scope
- In scope:
- Off limits:

## Archive Summary
Total variants: <N>
Best score: <score> (variant <id>)
Tree depth: <max depth>

## What We've Learned
<Key wins, dead ends, structural insights, meta-strategy changes.>

## Meta-Strategy Evolution Log
<Track when and why the meta strategy was modified.>
```

### `.hyperagent/meta_strategy.md`

This is the *editable* improvement strategy. The agent reads this before generating each child variant. **The agent can and should modify this file when it discovers better ways to search.**

Initial template:

```markdown
# Meta Strategy

## Current Approach
Generate improvements by:
1. Analyze the parent's code and score
2. Identify the most likely bottleneck or weakness
3. Propose a single targeted change with a clear hypothesis
4. Prefer structural changes over parameter tweaks when score is plateauing

## Exploration Heuristics
- If last 3 children from same parent all failed: try a fundamentally different parent
- If score plateau detected (variance < 1% over 5 variants): switch to exploratory mode
  - In exploratory mode: make larger structural changes, try unconventional approaches
- If a new best is found: generate 2-3 children from it (exploit the breakthrough)

## Self-Modification Triggers
Modify this strategy when:
- 5+ consecutive children show no improvement regardless of parent
- A child that was expected to fail succeeds (the model of what works is wrong)
- The agent detects it's repeating hypothesis patterns

## Hypothesis Generation Rules
- Each hypothesis must explain WHY the change should help
- No "try X and see" without a causal theory
- Maintain a hypothesis inventory to avoid repetition
```

### `.hyperagent/improvements.md`

The agent's diary. Written by the agent, for the agent. Track insights, patterns, dead ends, and meta-observations about the search process itself.

```markdown
# Improvements Diary

## Iteration 1
- Parent: node-0 (baseline)
- Observation: <what I noticed>
- Hypothesis: <what I think will work>
- Result: <what happened>
- Insight: <what I learned>

## Meta-Observations
- <Patterns about the search process itself>
```

## The Algorithm

### 1. Initialize

```
Create baseline variant (node-0)
Evaluate baseline → score
Add to archive: {id: "node-0", score: <score>, parent: null, depth: 0}
Initialize meta_strategy.md with default strategy
```

### 2. Select Parent

Use a selection mechanism that balances exploitation and exploration:

```python
def select_parent(archive):
    """
    Score-weighted selection with fertility penalty.
    High-performing variants are more likely to be selected.
    Variants that have already produced many children are penalized.
    """
    for variant in archive:
        # Base weight from performance (normalize scores to 0-1)
        weight = normalize(variant.score)
        
        # Fertility penalty: reduce weight for over-bred parents
        children_count = count_children(variant.id)
        fertility_penalty = 1.0 / (1.0 + children_count)
        
        variant.selection_weight = weight * fertility_penalty
    
    # Probabilistic selection weighted by adjusted scores
    return weighted_random_choice(archive)
```

### 3. Generate Child (Metacognitive Self-Modification)

```
Read meta_strategy.md
Read parent's code and score
Read improvements.md for context
Read archive summary for landscape awareness

Generate child by:
  1. Analyze parent's weaknesses
  2. Form hypothesis (per meta_strategy rules)
  3. Apply code changes to task agent
  4. Optionally: modify meta_strategy.md if triggers are met
  5. Record changes in improvements.md
```

### 4. Evaluate Child

```
Run hyperagent.sh → collect METRIC lines
Run hyperagent.checks.sh → verify correctness
Score the child
```

### 5. Update Archive

```
Add child to archive regardless of score (diversity matters)
Update tree.json with parent-child relationship
If archive exceeds size limit:
  Prune lowest-scoring variants that are NOT ancestors of the current best
  Never prune the baseline or the current best
```

### 6. Loop or Terminate

Continue until:
- Budget exhausted (iterations, time, or cost)
- Convergence detected (no improvement in N iterations across all branches)
- User interrupts
- All promising branches exhausted

### 7. Report

Generate `.hyperagent/report.html` with:
- Tree visualization of all variants
- Score evolution across the tree
- Best path from root to best variant
- Meta-strategy evolution timeline
- Key insights from improvements.md

## Archive Record Format

Each variant in `.hyperagent/archive.jsonl`:

```json
{
  "id": "node-007",
  "parent_id": "node-003",
  "depth": 3,
  "timestamp": "2026-03-27T22:00:00Z",
  "hypothesis": "Restructuring the prompt template to use chain-of-thought will improve accuracy",
  "change_summary": "Rewrote prompt template with explicit reasoning steps",
  "files_touched": ["prompts/evaluate.txt"],
  "meta_strategy_modified": false,
  "metric_name": "accuracy",
  "direction": "higher",
  "warmup_trials": [0.82, 0.83],
  "measured_trials": [0.87, 0.86, 0.88, 0.87, 0.86],
  "summary": {
    "median": 0.87,
    "mean": 0.868,
    "min": 0.86,
    "max": 0.88
  },
  "checks": "passed",
  "disposition": "keep",
  "children_count": 0,
  "selection_weight": null
}
```

## Tree Record Format

`.hyperagent/tree.json`:

```json
{
  "nodes": {
    "node-0": {"score": 0.72, "depth": 0, "children": ["node-1", "node-2"]},
    "node-1": {"score": 0.78, "depth": 1, "children": ["node-3", "node-4"]},
    "node-2": {"score": 0.69, "depth": 1, "children": []},
    "node-3": {"score": 0.87, "depth": 2, "children": ["node-5"]},
    "node-4": {"score": 0.75, "depth": 2, "children": []},
    "node-5": {"score": 0.91, "depth": 3, "children": []}
  },
  "best": "node-5",
  "best_path": ["node-0", "node-1", "node-3", "node-5"]
}
```

## Measurement Protocol

Same as autoresearch — discipline matters even in exploratory search:

1. **Warm up**: 2+ warmup trials (discarded)
2. **Measure**: 5+ measured trials
3. **Summarize**: Use median as primary decision statistic
4. **Threshold**: Pre-declare minimum meaningful improvement (default 1%)

## Meta-Strategy Self-Modification

This is what makes hyperagent different from autoresearch. The agent should modify `.hyperagent/meta_strategy.md` when:

### Trigger: Plateau Detection
If the last 5 variants across all branches show <1% variance in scores:
- Switch from exploitation to exploration mode
- Try larger structural changes
- Consider completely different algorithmic approaches
- Record the strategy change in improvements.md

### Trigger: Surprise Success
If a child scores significantly better than predicted:
- Analyze WHY it worked when the model predicted otherwise
- Update the hypothesis generation rules
- Generate 2-3 children from this variant to exploit the breakthrough

### Trigger: Hypothesis Repetition
If the agent is generating similar hypotheses to earlier ones:
- Stop and review improvements.md
- Identify which hypothesis TYPES have been tried
- Force the next N hypotheses to be from an untried category
- Categories: algorithmic, structural, data, prompt, parameter, architectural

### Trigger: Dead Branch
If a parent has produced 3+ children all scoring worse:
- Mark the branch as exhausted
- Reduce the parent's selection weight to near-zero
- Select a different parent from the archive, preferring under-explored ones

## Common Pitfalls

### 1. Archive Explosion
The tree can grow fast. Prune aggressively:
- Archive older than 20 variants: prune bottom 25% by score (preserving ancestors of best)
- Never let archive exceed 50 variants

### 2. Meta-Strategy Drift
The agent may modify its meta strategy in ways that are counterproductive:
- Keep a log of ALL meta strategy changes in improvements.md
- If performance degrades after a meta-strategy change, revert it
- Never allow meta-strategy changes more than once per 5 iterations

### 3. Exploration Without Exploitation
Diverse exploration is good, but not at the cost of never deepening a promising branch:
- After finding a new best, always generate at least 2 children before exploring elsewhere
- Track "exploitation ratio" — at least 40% of iterations should be children of top-3 variants

### 4. Cost Control
Hyperagent uses more tokens than linear autoresearch:
- Track cumulative token/API cost
- Set hard budget limits in hyperagent.md
- Default: 50 iterations max, 20 archive slots

## Resume Behavior

When resuming:
1. Read `hyperagent.md`
2. Read `.hyperagent/archive.jsonl` and `.hyperagent/tree.json`
3. Read `.hyperagent/meta_strategy.md` (may have been modified by previous runs)
4. Read `.hyperagent/improvements.md` for context
5. Identify the current best and under-explored branches
6. Continue from the most promising frontier

## Output

At the end of a session, produce:

1. **Best variant** — the code state with the highest score
2. **Best path** — the chain of changes from baseline to best
3. **Tree report** — visual HTML report of the exploration tree
4. **Learnings** — key insights from improvements.md
5. **Meta-strategy final state** — how the improvement strategy evolved
6. **Recommendation** — whether to continue exploring or ship the current best
