# Eval: Breadcrumbs Hypothesis

## Hypothesis

> Leaving breadcrumbs (inline code comments, DECISION.md files, etc.) explaining **why** optimization patterns were chosen helps future agents perform better in subsequent autoresearch sessions, versus having no such breadcrumbs.

## Background

The autoresearch skill already provides agents with:
- `autoresearch.md` — a "What We've Learned" narrative section
- `.autoresearch/results.jsonl` — a machine-readable ledger with `hypothesis` and `reason` fields
- Git history with change summaries

This eval tests whether **additional** breadcrumbs *inside the code itself* — inline comments, `DECISION.md` files, architecture decision records — add value **on top of** the existing ledger.

## Why This Matters

When optimization sessions grow complex (10+ experiments), a fresh agent resuming work must quickly grasp:
1. What was tried and discarded (prevents regressions)
2. Why the current patterns were kept (prevents re-testing known dead ends)
3. Which patterns are interdependent (prevents breaking coupled optimizations)

The ledger captures (1) at a high level, but breadcrumbs *in the code* can anchor (2) and (3) precisely at the decision site.

## Evaluation Dimensions

| Dimension | Scenarios | Core Question |
|-----------|-----------|---------------|
| A — Resume Accuracy | 1–3 | Can a fresh agent propose genuinely novel hypotheses? |
| B — Regression Prevention | 4–5 | Does seeing past-decision rationale stop the agent from undoing wins? |
| C — Complexity Scaling | 6–8 | Do breadcrumbs matter more as experiment depth increases? |
| D — Format Comparison | 9–12 | Inline vs. DECISION.md vs. both vs. autoresearch.md only |
| E — Knowledge Decay | 13–14 | Do stale or wrong breadcrumbs hurt more than help? |
| F — Token Budget | 15–16 | Does breadcrumb density eat context to the point of regressing quality? |

## Structure

```
eval/breadcrumbs/
├── README.md                        # This file
├── METHODOLOGY.md                   # Scoring rubric, statistical approach
├── fixtures/
│   ├── code/                        # Versioned code snapshots (with/without breadcrumbs)
│   ├── autoresearch_states/         # Canned session states (autoresearch.md + results.jsonl)
│   └── decisions/                   # DECISION.md variants
├── scenarios/
│   ├── A_resume_accuracy/           # Scenarios 1–3
│   ├── B_regression_prevention/     # Scenarios 4–5
│   ├── C_complexity_scaling/        # Scenarios 6–8
│   ├── D_format_tests/              # Scenarios 9–12
│   ├── E_knowledge_decay/           # Scenarios 13–14
│   └── F_token_budget/              # Scenarios 15–16
├── judges/
│   ├── novelty_judge.py             # LLM-based judge: is this hypothesis novel?
│   ├── regression_judge.py          # Does the proposed change undo a prior win?
│   ├── coherence_judge.py           # Is the reasoning coherent with the breadcrumbs?
│   └── token_counter.py             # Counts tokens in a scenario prompt
├── scripts/
│   ├── run_scenario.sh              # Run a single scenario and emit a result JSON
│   ├── run_all.sh                   # Run the full suite
│   ├── build_fixtures.sh            # Regenerate fixtures from templates
│   └── compare_conditions.py        # Aggregate results and compute effect sizes
└── results/                         # Auto-generated; not committed
```

## Running the Eval

### Prerequisites

```bash
pip install anthropic tiktoken scipy numpy
export ANTHROPIC_API_KEY=...
```

### Run a single scenario

```bash
./scripts/run_scenario.sh scenarios/A_resume_accuracy/scenario_01_with_breadcrumbs.json
```

### Run a full dimension

```bash
./scripts/run_all.sh --dimension A
```

### Run the complete suite

```bash
./scripts/run_all.sh --all
```

### Compare conditions

```bash
python scripts/compare_conditions.py results/
```

## Meta-Eval Design

Several scenarios are designed to be run **with the autoresearch skill itself** — the skill is pointed at a fixture codebase, and we observe whether the *type* and *quality* of experiments it proposes differs based on breadcrumb presence.

This creates a self-referential loop: the autoresearch skill is the subject *and* the tool for studying itself.

## Scoring

See `METHODOLOGY.md` for the full rubric. Key metrics:

- **Hypothesis Novelty Score (HNS)** — 0–1, how different are proposed hypotheses from already-tried ones?
- **Regression Rate (RR)** — fraction of proposals that would undo a prior win
- **Dead-End Repeat Rate (DERR)** — fraction of proposals that re-test something already discarded
- **Session Bootstrap Time (SBT)** — how many tokens the agent consumes before its first experiment proposal
- **Token Overhead Ratio (TOR)** — breadcrumb tokens / total context tokens

## Caveats

- LLM judges are themselves LLMs; they introduce variance. Use multiple judge runs and report median.
- Fixture code is synthetic (a string processing pipeline). Real-world generalization requires testing on production codebases.
- Agent behavior varies with temperature and model. Fix both across conditions for valid comparisons.
- Some scenarios require a human rater for the final "did the agent do something smart?" judgment. The automated judges are approximations.
