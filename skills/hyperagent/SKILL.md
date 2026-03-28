---
name: hyperagent
description: Run a self-referential self-improving agent loop where a meta-agent iteratively modifies a task-agent's code to optimize for any measurable target. Based on Facebook Research's Hyperagents paper (arXiv:2603.19461). Use when asked to "run hyperagent", "self-improve this", "optimize with self-modification", or "evolve this agent/script".
compatibility: Requires python3, git. The bundled scripts use only the Python standard library.
---

# Hyperagent

Self-referential self-improvement: a meta-agent that modifies a task-agent (and itself) to optimize any measurable objective.

Inspired by Facebook Research's *Hyperagents* paper (arXiv:2603.19461), which demonstrated that agents combining a task-solver and a self-modifying meta-level into a single editable program can achieve open-ended, compounding improvements that transfer across domains.

## How It Works

A hyperagent is a system with two components in a single editable codebase:

1. **Task Agent** — solves the target task (benchmark, code generation, data processing, etc.)
2. **Meta Agent** — analyzes task performance history and proposes modifications to the task agent's code (and optionally its own code)

The key insight from the paper: when the meta-level modification procedure is itself editable, the system can improve not just task performance but also the mechanism that generates future improvements — enabling compounding, transferable gains.

## Core Principles

1. **Self-referential modification**

   The meta-agent can modify the task-agent's code AND its own strategy. Both live in the same editable workspace. This enables metacognitive self-improvement: improving how you improve.

2. **Population-based exploration (archive)**

   Don't just keep the best variant — maintain an archive of all successful variants as stepping stones. Parent selection favors high performers with unexplored potential.

3. **Empirical evaluation gates everything**

   No change is accepted without measurement. Every candidate is evaluated against the task benchmark with repeated trials.

4. **Persistent memory and performance tracking**

   The system maintains a structured history of all experiments, hypotheses, and outcomes. Later generations build on earlier insights — no rediscovering dead ends.

5. **Transfer across domains**

   Meta-level improvements (performance tracking, evaluation strategies, hypothesis generation patterns) are domain-agnostic and can be transferred to new tasks.

## Available Scripts

- **`scripts/common.py`** — shared utilities (archive management, metrics, reporting)
- **`scripts/init_session.py`** — initialize a hyperagent session, scaffold the workspace
- **`scripts/run_task.py`** — evaluate a task-agent variant and record metrics
- **`scripts/generate_variant.py`** — run the meta-agent to propose a new variant from a parent
- **`scripts/log_variant.py`** — evaluate, decide disposition, add to archive
- **`scripts/render_report.py`** — generate HTML report of the full evolutionary history
- **`scripts/select_parent.py`** — select a parent from the archive for the next generation

All scripts are non-interactive, expose `--help`, emit structured JSON on stdout, and keep diagnostics on stderr.

## Default Workflow

1. **Initialize** the session after defining the optimization target:

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

2. **Evaluate the baseline** (generation 0):

   ```bash
   python3 scripts/run_task.py \
     --id gen-000 \
     --hypothesis "Control: unmodified task agent" \
     --change-summary "No modifications" \
     --baseline \
     --output .hyperagent/gen-000.json

   python3 scripts/log_variant.py --input .hyperagent/gen-000.json
   ```

3. **Selection → Modification → Evaluation loop**:

   ```bash
   # Select a parent from the archive
   python3 scripts/select_parent.py --output .hyperagent/parent.json

   # Generate a variant (meta-agent proposes modifications)
   # This is where YOU (the LLM agent) act as the meta-agent:
   # - Read the parent's code and performance history
   # - Hypothesize an improvement
   # - Apply code modifications
   # - Record what you changed and why

   # Evaluate the variant
   python3 scripts/run_task.py \
     --id gen-001 \
     --hypothesis "Add chain-of-thought prompting to improve reasoning" \
     --change-summary "Wrap task prompt in step-by-step reasoning template" \
     --parent gen-000 \
     --output .hyperagent/gen-001.json

   python3 scripts/log_variant.py --input .hyperagent/gen-001.json
   ```

4. **Render reports** at any time:

   ```bash
   python3 scripts/render_report.py
   ```

## Up-Front Q&A

Before starting, gather or confirm:

1. **Objective** — what are we optimizing?
2. **Primary metric** — exact name, unit, direction (lower/higher)
3. **Task command** — the script that runs the task agent and emits `METRIC name=value` lines
4. **Correctness gates** — tests or checks that must pass for a variant to be kept
5. **Scope** — which files can the meta-agent modify?
6. **Meta-scope** — can the meta-agent modify its own strategy? (default: yes)
7. **Generation budget** — max generations before stopping
8. **Minimum improvement threshold** — default 1%

## Workspace Setup

1. Prefer a **dedicated worktree** on a fresh branch:

   ```bash
   git worktree add ../hyperagent-<goal>-<date> -b hyperagent/<goal>-<date>
   ```

2. Create:
   - `hyperagent.md` — checked in, durable session brief with full evolutionary history
   - `task.sh` — checked in, benchmark runner (emits `METRIC name=value`)
   - `checks.sh` — checked in, correctness gates
   - `.hyperagent/` — local artifact directory, NOT checked in

3. Ensure artifacts stay untracked:

   ```bash
   rg -qxF '.hyperagent/' .git/info/exclude || printf '\n.hyperagent/\n' >> .git/info/exclude
   ```

## The Meta-Agent Role

**You (the LLM) are the meta-agent.** Your job each generation is:

1. **Select parent** — use `scripts/select_parent.py` or choose based on the archive
2. **Analyze** — read the parent's code, performance history, and past experiment outcomes
3. **Hypothesize** — propose a specific, testable modification with a causal theory for why it should help
4. **Modify** — apply code changes to the task agent (and optionally to your own strategy notes in `hyperagent.md`)
5. **Evaluate** — run `scripts/run_task.py` to measure the variant
6. **Log** — use `scripts/log_variant.py` to record the result and update the archive
7. **Reflect** — update `hyperagent.md` with what you learned

### Meta-Level Self-Modification

The meta-agent can improve its own process by updating:
- **Strategy notes** in `hyperagent.md` (hypothesis generation patterns, evaluation heuristics)
- **Memory entries** in `.hyperagent/memory.jsonl` (qualitative insights, correction plans)
- **The task evaluation protocol** (adding secondary metrics, changing trial counts)

These meta-improvements compound across generations and transfer to new tasks.

## Required Files

### `hyperagent.md`

The durable contract and evolutionary history. A fresh agent can resume from this.

```markdown
# Hyperagent: <goal>

## Objective
<What is being optimized and why.>

## Configuration
- Primary metric:
- Unit:
- Direction:
- Minimum improvement: X%
- Task command:
- Correctness gates:
- Generation budget:

## Scope
- Task agent files:
- Meta-agent can self-modify: yes/no

## Archive
`.hyperagent/archive.jsonl`

## Lineage
<Tree showing parent→child relationships and which variants were kept>

## Meta-Strategy
<Current approach to hypothesis generation — updated as the meta-agent learns>

## What We've Learned
<Key wins, dead ends, transferable insights>

## Performance Tracking
<Best variant, improvement trajectory, current plateau status>
```

### `task.sh`

Bash script that runs the task agent and emits `METRIC name=value` lines:

```bash
#!/bin/bash
set -euo pipefail
# Run the task agent
python3 src/agent.py --input data/test.json 2>/dev/null
# The agent script should emit: METRIC accuracy=0.85
```

## Archive Structure

The archive (`.hyperagent/archive.jsonl`) stores every variant ever evaluated:

```json
{
  "id": "gen-007",
  "generation": 7,
  "parent_id": "gen-003",
  "timestamp": "2026-03-27T20:00:00Z",
  "hypothesis": "Add few-shot examples to improve pattern recognition",
  "change_summary": "Inserted 3 domain-specific examples into the task prompt",
  "files_touched": ["src/agent.py"],
  "metric_name": "accuracy",
  "direction": "higher",
  "warmup_trials": [0.82, 0.83],
  "measured_trials": [0.85, 0.86, 0.84, 0.85, 0.87],
  "summary": {"median": 0.85, "mean": 0.854, "min": 0.84, "max": 0.87},
  "checks": "passed",
  "disposition": "keep",
  "children_count": 0,
  "meta_modifications": ["Updated strategy notes with few-shot pattern"],
  "reason": "Improved by 3.2% over parent gen-003 (0.824). Checks passed."
}
```

## Parent Selection

Selection probability for a parent is proportional to:
- **Performance score** (higher is better for archive diversity)
- **Inverse of children count** (favor unexplored high-performers)

This balances exploitation (good variants) with exploration (understudied variants).

```bash
python3 scripts/select_parent.py
# Output: {"selected_parent": "gen-003", "score": 0.824, "children": 1, "reason": "High performer with few children"}
```

## Decision Rules

- **`keep`** — variant beats current best by ≥ threshold, checks pass
- **`discard`** — variant is worse, equal, or improvement below threshold
- **`checks_failed`** — metric improved but correctness gates failed
- **`crash`** — variant could not be evaluated

## Plateau Detection

Track improvement velocity. Stop or pivot when:
- 3+ consecutive generations with no improvement
- Hypothesis diversity drops (recycling ideas)
- Improvement velocity < 0.1% per generation over last 5

## Loop Behavior

Run autonomously until:
- Generation budget exhausted
- Plateau detected (3 consecutive non-improvements)
- All promising hypotheses explored
- User interrupts

During the loop:
- One hypothesis per generation
- Record dead ends explicitly
- Keep the worktree clean between variants (revert discarded changes)
- Update `hyperagent.md` after every generation

## Common Pitfalls

### 1. Meta-Agent Overfitting Its Own Strategy
**Symptom:** Meta-strategy becomes over-specialized to early successes
**Fix:** Periodically review and broaden the strategy; try categorically different approaches

### 2. Archive Bloat
**Symptom:** Archive grows large, selection becomes slow
**Fix:** Archive old generations after 50 variants; maintain a compact summary

### 3. Self-Modification Destabilizing the Loop
**Symptom:** Meta-agent modifies evaluation or logging in ways that break the loop
**Fix:** Keep outer-loop scripts (init, run, log, select) immutable. Only modify task code and strategy notes.

### 4. Hypothesis Recycling
**Symptom:** Later generations retry earlier failed ideas
**Fix:** Always read `.hyperagent/memory.jsonl` before proposing. Explicitly check against dead ends.

## Transfer Protocol

To transfer meta-improvements to a new domain:

1. Extract meta-strategy from `hyperagent.md` "What We've Learned" section
2. Copy `.hyperagent/memory.jsonl` as starting knowledge
3. Initialize new session with transferred strategy as initial context
4. The meta-agent starts with accumulated wisdom instead of from scratch

## Report Generation

```bash
python3 scripts/render_report.py
```

Generates `.hyperagent/report.html` with:
- Lineage tree visualization
- Performance over generations
- Best-so-far trend
- Disposition breakdown
- Per-variant trial distributions
- Meta-strategy evolution timeline
