# Hyperagent

A self-referential self-improving agent skill where a meta-agent iteratively modifies a task-agent's code to optimize any measurable objective. Based on Facebook Research's [Hyperagents paper](https://arxiv.org/abs/2603.19461) (arXiv:2603.19461).

## What is a Hyperagent?

A hyperagent combines two components into a single editable codebase:

1. **Task Agent** — the code that solves your target task
2. **Meta Agent** — the intelligence that analyzes performance and proposes modifications to the task agent (and itself)

The key insight: when the modification mechanism is itself modifiable, the system achieves **compounding self-improvement** — it gets better at getting better.

## Quick Start

### 1. Initialize a session

```bash
python3 scripts/init_session.py \
  --goal "Improve prompt accuracy on math benchmark" \
  --metric-name accuracy \
  --unit pct \
  --direction higher \
  --task-command ./task.sh \
  --checks-command ./checks.sh \
  --scope src/agent.py \
  --max-generations 50
```

This creates:
- `hyperagent.md` — session brief and evolutionary history
- `.hyperagent/` — local artifacts directory (gitignored)

### 2. Write your task script

Create `task.sh` that runs your task agent and emits `METRIC` lines:

```bash
#!/bin/bash
set -euo pipefail
python3 src/agent.py --input data/test.json
# Agent should emit lines like:
# METRIC accuracy=0.85
# METRIC latency_ms=120
```

### 3. Evaluate the baseline

```bash
python3 scripts/run_task.py \
  --id gen-000 \
  --hypothesis "Control: unmodified task agent" \
  --change-summary "No modifications" \
  --baseline \
  --generation 0 \
  --output .hyperagent/gen-000.json

python3 scripts/log_variant.py --input .hyperagent/gen-000.json
```

### 4. Run the improvement loop

For each generation:

```bash
# Select a parent variant
python3 scripts/select_parent.py

# (You, the LLM, act as the meta-agent here:)
# - Analyze the parent's code and performance history
# - Hypothesize an improvement with a causal theory
# - Apply code modifications
# - Record what changed and why

# Evaluate the new variant
python3 scripts/run_task.py \
  --id gen-001 \
  --hypothesis "Add few-shot examples to improve pattern recognition" \
  --change-summary "Inserted 3 domain-specific examples into prompt" \
  --parent gen-000 \
  --generation 1 \
  --output .hyperagent/gen-001.json

python3 scripts/log_variant.py --input .hyperagent/gen-001.json
```

### 5. Generate reports

```bash
python3 scripts/render_report.py
open .hyperagent/report.html
```

## Example Usages

### Optimizing an LLM Prompt

```bash
# Goal: improve a summarization prompt's ROUGE score
python3 scripts/init_session.py \
  --goal "Maximize ROUGE-L score for article summarization" \
  --metric-name rouge_l \
  --unit score \
  --direction higher \
  --task-command "./eval_summarizer.sh" \
  --scope prompts/summarize.txt \
  --max-generations 30

# Meta-agent iterations might:
# gen-000: Baseline prompt → ROUGE-L 0.42
# gen-001: Add "be concise" instruction → 0.44 (keep, +4.8%)
# gen-002: Add few-shot examples → 0.48 (keep, +9.1%)
# gen-003: Chain-of-thought extraction → 0.47 (discard)
# gen-004: Structured output format → 0.51 (keep, +6.3%)
```

### Optimizing Code Performance

```bash
# Goal: reduce latency of a hot code path
python3 scripts/init_session.py \
  --goal "Minimize API response latency" \
  --metric-name latency_ms \
  --unit ms \
  --direction lower \
  --task-command "./benchmark.sh" \
  --checks-command "./tests.sh" \
  --scope "src/api/handler.ts" "src/api/cache.ts" \
  --off-limits "src/api/auth.ts" \
  --max-generations 20

# Meta-agent iterations might:
# gen-000: Baseline → 120ms
# gen-001: Add response caching → 85ms (keep, -29.2%)
# gen-002: Batch database queries → 72ms (keep, -15.3%)
# gen-003: Async parallel fetch → 68ms (keep, -5.6%)
# gen-004: Pre-warm cache on startup → 65ms (keep, -4.4%)
```

### Evolving a Reward Function

```bash
# Goal: improve RL reward shaping for a robotics task
python3 scripts/init_session.py \
  --goal "Maximize task completion rate via reward shaping" \
  --metric-name completion_rate \
  --unit pct \
  --direction higher \
  --task-command "./train_and_eval.sh" \
  --checks-command "./safety_checks.sh" \
  --scope "src/reward.py" \
  --max-generations 40

# The meta-agent can modify the reward function,
# observe training outcomes, and iteratively improve
# the reward signal based on completion rate trends.
```

### Self-Improving an Agent's Own Tools

```bash
# Goal: improve an agent's code generation accuracy
python3 scripts/init_session.py \
  --goal "Improve code generation pass@1 on HumanEval" \
  --metric-name pass_at_1 \
  --unit pct \
  --direction higher \
  --task-command "./eval_codegen.sh" \
  --scope "src/agent.py" "src/prompts/" \
  --max-generations 50

# Meta-level self-modification:
# The meta-agent can update its own strategy notes
# in hyperagent.md and memory entries in .hyperagent/memory.jsonl.
# These meta-improvements transfer if you start a new session.
```

## Key Concepts

### Parent Selection

Parents are selected from the archive using performance-weighted, exploration-biased sampling:

```
P(parent) ∝ normalized_score / (1 + children_count)
```

This favors high performers that haven't been explored yet, balancing exploitation with exploration.

### Plateau Detection

The system automatically detects when improvement stalls:
- Monitors consecutive non-improvements (default: 3)
- Tracks improvement velocity over recent kept variants
- Warns when it's time to pivot strategy or stop

### Persistent Memory

The meta-agent maintains qualitative memory (`.hyperagent/memory.jsonl`) of:
- Dead ends and why they failed
- Successful patterns worth repeating
- Strategic insights about the optimization landscape
- Correction plans for future generations

### Transfer Learning

Meta-level improvements transfer across domains. To bootstrap a new task:

1. Copy `hyperagent.md` "What We've Learned" + "Meta-Strategy" sections
2. Copy `.hyperagent/memory.jsonl` as starting knowledge
3. Initialize the new session with accumulated wisdom

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `init_session.py` | Initialize workspace, scaffold `hyperagent.md` and `.hyperagent/` |
| `run_task.py` | Run warmup + measured trials, parse metrics, run checks |
| `log_variant.py` | Decide disposition (keep/discard/crash), update archive and reports |
| `select_parent.py` | Select next parent using performance-weighted exploration sampling |
| `render_report.py` | Generate HTML report with lineage tree, charts, and full history |

All scripts:
- Accept `--help` for full option documentation
- Emit structured JSON on stdout
- Keep diagnostics on stderr
- Are non-interactive

## File Structure

```
project/
├── hyperagent.md              # Session brief + evolutionary history (checked in)
├── task.sh                    # Benchmark runner (checked in)
├── checks.sh                  # Correctness gates (checked in)
├── .hyperagent/               # Local artifacts (NOT checked in)
│   ├── session.json           # Session configuration
│   ├── archive.jsonl          # Full evolutionary archive
│   ├── memory.jsonl           # Meta-agent qualitative memory
│   ├── results.csv            # Spreadsheet-friendly summary
│   ├── report.html            # Visual HTML report
│   └── variants/              # Per-variant JSON records
│       ├── gen-000.json
│       ├── gen-001.json
│       └── ...
```

## Differences from Autoresearch

| Feature | Autoresearch | Hyperagent |
|---------|-------------|------------|
| **Model** | Linear experiment sequence | Population-based evolutionary archive |
| **Selection** | Always improves on current best | Parent selection from archive with exploration bias |
| **Self-modification** | No | Meta-agent can modify its own strategy |
| **Memory** | Experiment log only | Structured qualitative memory + performance tracking |
| **Lineage** | Flat sequence | Tree structure (parent→children) |
| **Plateau handling** | Manual | Automatic detection + velocity tracking |
| **Transfer** | Per-session | Meta-improvements transfer across sessions |

## Paper Reference

Based on: *Hyperagents* (Zhang et al., 2026). [arXiv:2603.19461](https://arxiv.org/abs/2603.19461) | [GitHub](https://github.com/facebookresearch/Hyperagents)

Key ideas adapted:
- Self-referential agents with editable task + meta components
- Population-based archive with parent selection ∝ performance / children
- Persistent memory and performance tracking as emergent meta-improvements
- Cross-domain transfer of meta-level capabilities
