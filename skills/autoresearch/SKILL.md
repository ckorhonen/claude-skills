---
name: autoresearch
description: Run a rigorous autonomous experiment loop for any optimization target using explicit hypotheses, repeated trials, structured experiment logs, and local HTML reports. Use when asked to "run autoresearch", "optimize X in a loop", "start experiments", or "improve this with benchmark-driven iteration".
compatibility: Requires python3, git for the safest workflow, and a POSIX shell. The bundled scripts use only the Python standard library.
---

# Autoresearch

Autonomous optimization is only useful when it behaves like disciplined research, not benchmark gambling.

This skill runs a strict experiment loop:
- clarify the target before changing code
- write down hypotheses before testing them
- measure with repeated trials, not one-off wins
- record every experiment, including failures
- generate local reports and graphs that are not checked in

## Core Principles

1. **No silent scope inference**

If the request is vague, stop and ask a short up-front Q&A before starting. Do not silently invent the target workload, correctness bar, or tradeoffs.

2. **One experiment = one hypothesis**

State the proposed change and why it should help before making it. Avoid bundles of unrelated tweaks.

3. **All experiments are logged**

Every experiment must be enumerated in a machine-readable ledger, including discarded ideas, crashes, and failed checks.

4. **Repeated measures beat noisy anecdotes**

Do not keep a change because of one fast run. Use warmups, repeated measurements, and an explicit decision rule.

5. **Artifacts stay local**

Reports, CSVs, JSONL ledgers, and graphs belong in a local `.autoresearch/` directory and should not be committed.

## Available scripts

- **`scripts/init_experiment.py`** — initialize `.autoresearch/session.json`, ensure `.autoresearch/` stays untracked, and scaffold `autoresearch.md` when needed.
- **`scripts/run_experiment.py`** — run warmups and measured trials, parse `METRIC` lines, run optional checks, and emit a JSON experiment record.
- **`scripts/log_experiment.py`** — append an experiment to `.autoresearch/results.jsonl`, decide `keep` vs `discard`, and refresh CSV and HTML artifacts.
- **`scripts/render_report.py`** — regenerate `.autoresearch/results.csv` and `.autoresearch/report.html` from the JSONL ledger.

All scripts are non-interactive, expose `--help`, emit structured JSON on stdout, and keep diagnostics on stderr.

## Default workflow

1. Initialize the session after the up-front Q&A:

   ```bash
   python3 scripts/init_experiment.py \
     --goal "Reduce latency in hot path" \
     --metric-name latency_ms \
     --unit ms \
     --direction lower \
     --command ./autoresearch.sh \
     --checks-command ./autoresearch.checks.sh \
     --scope src/hot_path.ts
   ```

2. Record the baseline:

   ```bash
   # Option A: save to file first, then log
   python3 scripts/run_experiment.py \
     --id baseline \
     --hypothesis "Control run" \
     --change-summary "No code changes" \
     --baseline \
     --output .autoresearch/baseline.json
   python3 scripts/log_experiment.py --input .autoresearch/baseline.json

   # Option B: pipe directly
   python3 scripts/run_experiment.py \
     --id baseline \
     --hypothesis "Control run" \
     --change-summary "No code changes" \
     --baseline \
     | python3 scripts/log_experiment.py
   ```

3. Record each candidate experiment:

   ```bash
   python3 scripts/run_experiment.py \
     --id exp-001 \
     --hypothesis "Inlining removes allocation churn" \
     --change-summary "Inline helper and pre-size buffer" \
     --output .autoresearch/exp-001.json
   python3 scripts/log_experiment.py --input .autoresearch/exp-001.json
   ```

4. Re-render artifacts on demand:

   ```bash
   python3 scripts/render_report.py
   ```

## Up-Front Q&A

Before starting, gather or confirm all of the following. If any item is vague or missing, ask focused questions first.

1. **Objective** — what are we optimizing?
2. **Primary metric** — exact name, unit, and whether lower or higher is better
3. **Minimum meaningful improvement** — default to `1%` if the user does not specify
4. **Workload command** — the exact command or script that represents reality
5. **Correctness gates** — tests, typecheck, lint, eval set, accuracy floor, or any other non-negotiables
6. **Scope** — which files may be changed, and which are off-limits
7. **Budget** — time budget, compute budget, or stop criteria if the user has them

If the user says "just run with it," write the assumptions explicitly into `autoresearch.md` before the first experiment, then encode them via `python3 scripts/init_experiment.py ...`.

## Workspace Setup

1. Prefer a **dedicated worktree** on a fresh branch:

   ```bash
   git worktree add ../autoresearch-<goal>-<date> -b autoresearch/<goal>-<date>
   ```

   If a worktree is not practical, use a new branch in a clean working tree. Do not run this skill in a dirty tree with unrelated user changes.

2. Create:
   - `autoresearch.md` — checked in, durable session brief
   - `autoresearch.sh` — checked in, benchmark runner
   - `autoresearch.checks.sh` — checked in only when correctness gates are required
   - `.autoresearch/` — local artifact directory, not checked in

3. Ensure local artifacts stay untracked:

   ```bash
   rg -qxF '.autoresearch/' .git/info/exclude || printf '\n.autoresearch/\n' >> .git/info/exclude
   ```

4. Run `python3 scripts/init_experiment.py --help` if you need the exact interface, then initialize the session, collect a baseline with `python3 scripts/run_experiment.py ...`, and log it with `python3 scripts/log_experiment.py ...` before making any code changes.

## Required Files

### `autoresearch.md`

This is the durable contract for the session. A fresh agent should be able to resume from it without guessing.

```markdown
# Autoresearch: <goal>

## Objective
<What is being optimized and why it matters.>

## Up-Front Answers
- Primary metric:
- Unit:
- Direction:
- Minimum meaningful improvement:
- Workload command:
- Correctness gates:
- Budget / stop criteria:

## Scope
- In scope:
- Off limits:

## Decision Rule
<How many warmups, how many measured trials, how "keep" is decided.>

## Experiment Ledger
`.autoresearch/results.jsonl`

## Report Outputs
- `.autoresearch/report.html`
- `.autoresearch/results.csv`
- `.autoresearch/plots/`

## Current Best Result
<Best known baseline or kept variant.>

## What We've Learned
<Key wins, dead ends, confounders, and structural insights.>
```

Update `autoresearch.md` whenever assumptions change, a new best result is found, or a pattern becomes clear.

### `autoresearch.sh`

Bash script with `set -euo pipefail` that:
- performs only very fast pre-checks
- runs the real benchmark workload
- emits parseable `METRIC name=value` lines
- stays stable across experiments so runs remain comparable

Keep it as small and deterministic as possible. If you change the benchmark protocol, record that in `autoresearch.md` and establish a new baseline.

### `autoresearch.checks.sh`

Create this when the session has correctness gates. It must:
- validate correctness after a candidate benchmark passes
- not affect the primary metric timing
- keep output short and error-focused
- fail hard when the candidate is not safe to keep

If checks fail, the experiment disposition is `checks_failed`, not `keep`. The default script workflow handles this automatically.

## Local Artifact Contract

Everything below lives in `.autoresearch/` and should remain untracked.

### `.autoresearch/results.jsonl`

Append one JSON object per experiment. This is the source of truth for enumerating all experiments.

Required fields:

```json
{
  "id": "exp-007",
  "timestamp": "2026-03-14T13:00:00Z",
  "hypothesis": "Inlining X removes allocation churn in hot path Y.",
  "change_summary": "Inline helper and pre-size buffer.",
  "files_touched": ["src/hot_path.ts"],
  "baseline_commit": "abc1234",
  "candidate_ref": "def5678",
  "metric_name": "latency_ms",
  "direction": "lower",
  "warmup_trials": [12.8, 12.7],
  "measured_trials": [11.9, 12.0, 11.8, 11.9, 12.1],
  "summary": {
    "median": 11.9,
    "mean": 11.94,
    "min": 11.8,
    "max": 12.1
  },
  "secondary_metrics": {
    "memory_mb": 84.1
  },
  "checks": "passed",
  "disposition": "keep",
  "reason": "Median improved by 5.2%, checks passed, complexity acceptable."
}
```

### `.autoresearch/results.csv`

Flatten the JSONL into a spreadsheet-friendly summary after each experiment or at regular intervals.

### `.autoresearch/report.html`

Generate an HTML report that visualizes the session. At minimum include:
- a table enumerating every experiment and disposition
- primary metric over time
- best-so-far trend
- per-experiment measured-trial distribution
- checks pass/fail/crash counts
- summary of kept improvements vs. discarded ideas

### `.autoresearch/plots/`

Store generated charts or exported images here when the report uses external assets.

## Experiment Card

Before each experiment, write a short experiment card into `autoresearch.md` or a temporary note:

- `id`
- `hypothesis`
- `planned change`
- `why this should affect the metric`
- `files expected to change`
- `predicted direction and rough magnitude`
- `rollback plan`

If you cannot explain why the change should help, do not run the experiment yet.

## Measurement Protocol

Use this default unless the user specifies something stricter:

1. **Warm up first**
   - Run at least `2` warmup trials that are not used for the decision.

2. **Measure repeatedly**
   - Run at least `5` measured trials for the baseline and for each serious candidate.
   - If noise is high or the win is marginal, increase the sample size. Do not accept ambiguous results.

3. **Summarize robustly**
   - Use the **median** as the primary decision statistic.
   - Also record mean, min, and max so variance is visible.

4. **Apply a pre-declared threshold**
   - Keep a change only when it beats the current best by at least the minimum meaningful improvement threshold and passes all correctness checks.

5. **Reset baseline when needed**
   - If the workload, machine conditions, dataset, or benchmark harness changes materially, establish a fresh baseline and note why.

## Decision Rules

- **`keep`**
  - candidate beats the current best according to the declared metric direction
  - improvement clears the minimum meaningful improvement threshold
  - correctness checks pass
  - no unacceptable regression appears in a required secondary metric

- **`discard`**
  - candidate is worse
  - candidate is effectively equal
  - result is too noisy to justify confidence
  - complexity cost is not worth the gain

- **`checks_failed`**
  - benchmark may have improved, but required correctness gates failed

- **`crash`**
  - candidate broke the workload or could not be measured reliably

Never upgrade an ambiguous result to `keep` because it feels promising.

## Loop Behavior

Run autonomously, but do not run forever without learning. Continue until one of these is true:
- time or compute budget is exhausted
- no meaningful improvement has been found after several distinct hypotheses
- all promising ideas are exhausted
- the user interrupts or redirects the work

During the loop:
- prefer one meaningful change at a time
- avoid retrying the same failed idea with superficial variation
- write down dead ends so future agents do not repeat them
- keep the worktree clean between experiments

When discarding a candidate, restore back to the last committed good state in the isolated worktree before starting the next idea.

## Common Pitfalls

Autoresearch is disciplined empiricism, but several failure modes emerge in long-running optimization loops. Knowing these patterns helps prevent wasted experiments and broken workflows.

### 1. Experiment Loop Doesn't Terminate When Optimization Plateaus

**Symptom:**
- Agent continues running new experiments for many cycles after the last improvement
- No clear stopping point; loop feels directionless after 10-15 experiments
- Time/compute budget consumed without discovering new insights

**Root Cause:**
- Missing exit conditions beyond budget exhaustion
- Agent assumes "more experiments = more knowledge" without checking for learning curve saturation
- No systematic detection of repeated hypothesis patterns or diminishing returns

**Mitigation:**
- Set a **plateau threshold** in `autoresearch.md`: stop after N consecutive experiments with no improvement, e.g., "Stop if 3 experiments in a row show <0.5% gain"
- Track **hypothesis diversity** — if new hypotheses are rewording old ideas, stop and document learnings
- Implement a **moving-window heuristic**: calculate improvement velocity over the last 5 experiments; stop when velocity < 0.1% per experiment
- Record stopping reason explicitly in `autoresearch.md` when exiting early

### 2. Hypothesis Generation Becomes Repetitive After 5–10 Iterations

**Symptom:**
- Later experiments are minor variations on earlier ideas (e.g., "buffer size 16 vs. 32 vs. 24")
- Hypotheses lack distinct causal theories; just tweaking constants
- Diminishing variance in results, but no clear winner emerges

**Root Cause:**
- Agent defaults to local gradient descent without pausing to reflect on root causes
- No explicit hypothesis inventory or cross-check for novelty
- Hypothesis space is not well-explored before drilling into micro-optimizations

**Mitigation:**
- **Before each experiment**, write the hypothesis in a form that answers "why should this improve the metric?" If the answer is "because I'm turning a knob," pause and sketch a new direction first
- **Document dead ends** — when discarding an experiment, explicitly note why it failed so future hypotheses don't retread that ground
- **Rotate hypothesis types** every 3–4 experiments:
  - algorithmic changes (e.g., trade hash table for skiplist)
  - data structure changes (e.g., pre-allocation, layout)
  - control flow changes (e.g., branch prediction, loop unrolling)
  - external factors (e.g., compiler flags, sampling rate)
- **Checkpoint & reflect**: after 5 experiments, re-read `autoresearch.md` and explicitly write a "What We've Learned" section with 2–3 key insights. If that section is empty, you're spinning

### 3. Log Files Grow Unbounded on Long Runs

**Symptom:**
- `.autoresearch/` directory balloons to 10s or 100s of MB after 50+ experiments
- Runtime of `python3 scripts/render_report.py` slows down measurably over time
- Disk usage becomes an operational concern on resource-constrained machines

**Root Cause:**
- Each experiment produces a full JSON record, and records are never pruned
- If measurements include verbose debug output or traces, they accumulate in the JSONL
- HTML reports may embed all raw data inline, leading to multi-MB HTML files

**Mitigation:**
- **Archive periodically**: every 20 experiments, archive old results to `.autoresearch/archive/YYYYMMDD-run-N.jsonl` and restart with a fresh `results.jsonl`
- **Limit measurement output**: ensure `autoresearch.sh` does not emit verbose logs; capture only `METRIC` lines
- **Store summaries, not raw traces**: in `results.jsonl`, record `{"summary": {...}, "median": X}` instead of all raw trial values if space is critical
- **Document archival in `autoresearch.md`**: note when the ledger was archived and how to access previous runs
- **Monitor artifact size**: add a check in the loop: `du -sh .autoresearch/ | grep -qE '[0-9]+M' && echo "WARNING: artifact directory >100MB"`

### 4. HTML Reports Don't Render Properly When Experiments > 100

**Symptom:**
- Browser lags or hangs when opening `.autoresearch/report.html` after many experiments
- Charts fail to render or display only partial data
- Page size balloons to 50+ MB, making it impractical to share or version-control

**Root Cause:**
- `render_report.py` generates a single monolithic HTML file with all data inlined
- JavaScript charting library chokes on 100+ data points without pagination or lazy loading
- No truncation or summary mode for large result sets

**Mitigation:**
- **Paginate results**: split the experiment ledger into chunks of 50 and generate separate report pages (`report-01.html`, `report-02.html`, etc.) with navigation links
- **Use summary mode for large runs**: if `len(results) > 100`, render a condensed report that includes:
  - table of kept experiments only (discard, crash, checks_failed filtered out)
  - best-so-far trend line (not all individual points)
  - per-phase statistical summary instead of per-experiment distributions
- **Offload heavy data to JSON**: embed a `.autoresearch/data.json` with the full result set and reference it from the HTML with client-side rendering, so the HTML itself stays under 1 MB
- **Auto-detect and warn**: in `render_report.py`, if result count > 100, log: `"WARNING: report contains >100 experiments; consider archiving old runs or using --summary-mode"`

---

## Report Generation

Generate or refresh `.autoresearch/report.html` periodically and always at the end of the session:

```bash
python3 scripts/render_report.py
```

The report should answer:
- what experiments were tried
- which ones won, failed, or crashed
- how the best metric evolved over time
- what tradeoffs appeared in secondary metrics
- what the final recommended change is and why

If rich charting is cumbersome, generate a simple static HTML file with inline SVG charts or lightweight local assets. The report matters more than polish.

## Resume Behavior

When resuming:
1. read `autoresearch.md`
2. inspect `.autoresearch/results.jsonl`
3. inspect `.autoresearch/report.html` if present
4. review git history for kept commits
5. continue from the best known state, not from stale assumptions

## User Messages During Experiments

If the user sends a message while an experiment is running, finish the current measurement cycle if it is short and safe to do so, then respond. If the run is long or risky, stop at the nearest safe checkpoint and reply.
