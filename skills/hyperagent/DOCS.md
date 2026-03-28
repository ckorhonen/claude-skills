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

**Real output:**
```json
{
  "status": "ok",
  "session_path": "/path/to/project/.hyperagent/session.json",
  "artifacts_dir": "/path/to/project/.hyperagent",
  "scaffolded_hyperagent_md": true,
  "exclude_updated": true
}
```

This creates:
- `hyperagent.md` — session brief and evolutionary history
- `.hyperagent/` — local artifacts directory (gitignored via `.git/info/exclude`)

### 2. Write your task script

Create `task.sh` that runs your task agent and emits `METRIC` lines:

```bash
#!/bin/bash
python3 src/agent.py --input data/test.json
# Script must emit lines like:
# METRIC accuracy=0.85
# METRIC latency_ms=120
#
# JSON format also supported:
# METRIC {"accuracy": 0.85, "latency_ms": 120}
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

**Real output from `log_variant.py`:**
```json
{
  "id": "gen-000",
  "generation": 0,
  "baseline": true,
  "hypothesis": "Control: unmodified task agent",
  "change_summary": "No modifications",
  "metric_name": "score",
  "direction": "higher",
  "measured_trials": [0.3333, 0.3333, 0.3333],
  "summary": {
    "median": 0.3333,
    "mean": 0.3333,
    "min": 0.3333,
    "max": 0.3333
  },
  "checks": "passed",
  "disposition": "keep",
  "reason": "Initial baseline recorded."
}
```

### 4. Run the improvement loop

For each generation:

```bash
# Select a parent variant
python3 scripts/select_parent.py
```

**Real output from `select_parent.py`:**
```json
{
  "selected_parent": "gen-000",
  "score": 0.3333,
  "children_count": 0,
  "generation": 1,
  "plateau_detected": false,
  "improvement_velocity": null,
  "archive_size": 1,
  "kept_count": 1,
  "reason": "Selected gen-000 (score=0.3333, children=0)"
}
```

Then, **you (the LLM) act as the meta-agent:**
- Analyze the parent's code and performance history
- Hypothesize an improvement with a causal theory
- Apply code modifications
- Record what changed and why

```bash
# Evaluate the new variant
python3 scripts/run_task.py \
  --id gen-001 \
  --hypothesis "Keyword extraction captures more reference terms than first-sentence" \
  --change-summary "Changed summarize() to remove stopwords from full text" \
  --parent gen-000 \
  --generation 1 \
  --command "python3 src/agent_v1.py" \
  --output .hyperagent/gen-001.json

python3 scripts/log_variant.py --input .hyperagent/gen-001.json
```

**Real output when variant improves:**
```json
{
  "id": "gen-001",
  "generation": 1,
  "parent_id": "gen-000",
  "summary": {"median": 0.9444, "mean": 0.9444, "min": 0.9444, "max": 0.9444},
  "disposition": "keep",
  "reason": "Improved by 183.35% over best (gen-000). Checks passed.",
  "improvement_pct": 183.34833483348334
}
```

**Real output when variant does NOT improve:**
```json
{
  "id": "gen-003",
  "generation": 2,
  "parent_id": "gen-002",
  "summary": {"median": 0.5278},
  "disposition": "discard",
  "reason": "Variant did not beat the current best.",
  "improvement_pct": -44.11266412537061
}
```

**Real output when variant crashes:**
```json
{
  "id": "gen-crash",
  "status": "crash",
  "summary": {},
  "disposition": "crash",
  "reason": "can't open file '/tmp/nonexistent.py': [Errno 2] No such file or directory"
}
```

### 5. Generate reports

```bash
python3 scripts/render_report.py
```

**Real output:**
```json
{
  "status": "ok",
  "archive_size": 4,
  "csv_path": "/path/to/project/.hyperagent/results.csv",
  "report_path": "/path/to/project/.hyperagent/report.html"
}
```

Open `.hyperagent/report.html` for an HTML report with:
- Summary stats (kept/discarded/failed counts)
- Best variant highlighted
- SVG line charts of metric over generations
- Best-so-far trend chart
- Disposition bar chart
- Lineage tree (parent→child relationships)
- Full variant table with hypotheses and change summaries

## Real Tested Example: Text Summarizer Optimization

This is a real run tested on 2026-03-28. Task: improve a Python text summarizer's
word overlap score (ROUGE-like metric).

### Setup

```python
# target.py (baseline)
def summarize(text: str) -> str:
    """Baseline: just take the first sentence."""
    sentences = text.split('. ')
    return sentences[0] if sentences else text
```

```bash
# task.sh
python3 target.py
# Outputs: METRIC score=0.3333
```

### Init

```bash
python3 scripts/init_session.py \
  --goal "Improve text summarizer word overlap score" \
  --metric-name score \
  --unit "overlap" \
  --direction higher \
  --task-command "bash task.sh" \
  --checks-command "bash checks.sh" \
  --min-improvement 5.0 \
  --warmups 1 --trials 3 \
  --scope target.py \
  --max-generations 10
```

### Run

| ID | Generation | Hypothesis | Score | Disposition | Improvement |
|----|-----------|------------|-------|-------------|-------------|
| gen-000 | 0 | Baseline: first-sentence extraction | 0.3333 | keep | — |
| gen-001 | 1 | Pick sentence with most unique words | 0.3333 | discard | 0.0% |
| gen-002 | 1 | Keyword extraction (remove stopwords) | **0.9444** | **keep** | **+183.3%** |
| gen-003 | 2 | TF-IDF sentence ranking + top-2 | 0.5278 | discard | -44.1% |

### Select parent for gen-001 (fresh archive, only baseline)

```json
{
  "selected_parent": "gen-000",
  "score": 0.3333,
  "children_count": 0,
  "generation": 1
}
```

### Select parent after gen-002 is archived

```json
{
  "selected_parent": "gen-002",
  "score": 0.9444,
  "children_count": 1,
  "generation": 2
}
```

## Example Usages

### Optimizing an LLM Prompt

```bash
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
```

### Evolving a Reward Function

```bash
python3 scripts/init_session.py \
  --goal "Maximize task completion rate via reward shaping" \
  --metric-name completion_rate \
  --unit pct \
  --direction higher \
  --task-command "./train_and_eval.sh" \
  --checks-command "./safety_checks.sh" \
  --scope "src/reward.py" \
  --max-generations 40
```

## METRIC Format

Task scripts must emit `METRIC` lines to stdout:

```
# Key=value format (one or more metrics)
METRIC score=0.8542
METRIC latency_ms=142 throughput=850

# JSON format (multiple metrics in one line)
METRIC {"score": 0.8542, "latency_ms": 142}
```

Rules:
- Lines must start with `METRIC ` (case-sensitive)
- Keys cannot contain spaces in key=value format; use JSON format for multi-word names
- Values must be parseable as floats
- Other stdout output is ignored (safe to print debug info)

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

Add memory entries programmatically or via the `append_memory()` utility in `common.py`.

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
- Are non-interactive (safe to pipe)

> **Note:** There is no `generate_variant.py`. The meta-agent role — hypothesis generation and code modification — is performed by the LLM agent itself.

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
│   └── variants/              # Per-variant JSON records (optional --output)
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
