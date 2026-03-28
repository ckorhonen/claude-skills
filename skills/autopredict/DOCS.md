# AutoPredict Skill Companion

This skill wraps the upstream [`howdymary/autopredict`](https://github.com/howdymary/autopredict) repository and adds safer helper scripts plus repo-specific guidance.

Use it when you want to:

- scan live Polymarket markets
- inspect event-level overround / underround
- evaluate one market with your own `fair_prob`
- run reproducible backtests against a JSON dataset
- sweep strategy parameters without relying on the repo's stub tuning CLI
- understand what the paper/live trading scaffolds can and cannot do

## Quick Start

Clone and verify the upstream repo:

```bash
bash skills/autopredict/scripts/setup.sh --dir /tmp/autopredict
```

Scan live markets:

```bash
bash skills/autopredict/scripts/scan_markets.sh \
  --dir /tmp/autopredict \
  --top 10 \
  --verbose
```

Inspect structural event mispricing:

```bash
bash skills/autopredict/scripts/scan_markets.sh \
  --dir /tmp/autopredict \
  --events \
  --top 10
```

Evaluate a specific market with your own fair probability:

```bash
bash skills/autopredict/scripts/scan_markets.sh \
  --dir /tmp/autopredict \
  --fair 0.60 \
  <condition_id>
```

Run a safe sample backtest:

```bash
bash skills/autopredict/scripts/run_backtest.sh \
  --dir /tmp/autopredict \
  --score
```

Tune a couple of parameters:

```bash
bash skills/autopredict/scripts/tune_params.sh \
  --dir /tmp/autopredict \
  --param min_edge 0.03,0.05,0.08 \
  --param aggressive_edge 0.10,0.12,0.15
```

## What To Use For What

### I want markets worth researching

Start with `scan_markets.sh` and keep it read-only.

```bash
bash skills/autopredict/scripts/scan_markets.sh \
  --dir /tmp/autopredict \
  --category politics \
  --min-liquidity 5000 \
  --top 15
```

Then look for:

- tight spreads
- visible book depth on both sides
- events where sibling prices obviously disagree with each other
- markets where you can produce an external probability estimate

### I already have a forecast and want an execution recommendation

Use `predict.py --fair` through `scan_markets.sh`.

```bash
bash skills/autopredict/scripts/scan_markets.sh \
  --dir /tmp/autopredict \
  --fair 0.57 \
  <condition_id>
```

Important caveat:

- this path uses the repo's default `AgentConfig()`
- it does **not** load `strategy_configs/baseline.json`
- treat it as a default-policy sanity check, not config validation

### I want a reproducible backtest before changing parameters

Use `run_backtest.sh`, not ad-hoc notebook output.

```bash
bash skills/autopredict/scripts/run_backtest.sh \
  --dir /tmp/autopredict \
  --config strategy_configs/baseline.json \
  --dataset autopredict/_defaults/datasets/sample_markets.json \
  --score \
  --output /tmp/autopredict-baseline.json
```

For real research, replace the sample dataset with your own snapshot file.

### I want to compare configs, not just eyeball one run

Use `tune_params.sh`.

```bash
bash skills/autopredict/scripts/tune_params.sh \
  --dir /tmp/autopredict \
  --dataset /path/to/markets.json \
  --scoring sharpe \
  --param min_edge 0.03,0.05,0.08 \
  --param max_depth_fraction 0.10,0.15,0.20
```

The helper writes:

- generated config JSON files
- per-run metrics JSON files
- `summary.json`
- `failures.json`

## Tips

- Always pass a dataset for serious backtests. Upstream `config.json` sets `default_dataset` to `null`, so `python3 -m autopredict.cli backtest` with no dataset crashes.
- Prefer `python3 -m autopredict.cli backtest` over `python3 -m autopredict.backtest.cli`; the backtest submodule has brittle imports in the current repo state.
- `python3 -m autopredict.cli learn analyze` only makes sense if JSONL trade logs already exist. Plain backtests do not generate them.
- `python3 -m autopredict.cli learn tune` and `learn improve` are placeholders that point to a missing script.
- `scripts/run_paper.py` and `scripts/run_live.py` are scaffolds. `run_live.py` still uses `MockVenueAdapter`.

## Failure Modes To Expect

### `TypeError` before a backtest even starts

Cause:

- no dataset was passed and upstream tried to resolve `null` as a path

Fix:

```bash
bash skills/autopredict/scripts/run_backtest.sh \
  --dir /tmp/autopredict \
  --dataset autopredict/_defaults/datasets/sample_markets.json
```

### `score-latest` says no metrics file exists

Cause:

- the previous backtest failed or never ran

Fix:

- rerun the backtest with a valid dataset
- only call `score-latest` after success

### `learn analyze` finds no logs

Cause:

- there are no JSONL trade logs in `state/trades`

Fix:

- use a workflow that writes `TradeLogger` logs
- do not assume plain CLI backtests create them

### Live trading sounds implemented but nothing can trade

Cause:

- `scripts/run_live.py` is a template with `MockVenueAdapter`

Fix:

- treat live trading as an extension project unless you are adding a real venue adapter

## Autoresearch Integration

AutoPredict pairs well with the `autoresearch` skill if you keep the objective narrow.

Recommended pattern:

1. choose one target metric
2. pick one small hypothesis
3. run backtests or parameter sweeps
4. keep artifacts and compare objectively

Good targets:

- maximize `sharpe`
- improve `total_pnl` without increasing drawdown too much
- reduce `avg_slippage_bps`
- increase trade count without collapsing edge quality

Good autoresearch workload ideas:

```bash
bash skills/autopredict/scripts/run_backtest.sh \
  --dir /tmp/autopredict \
  --config strategy_configs/baseline.json \
  --dataset /path/to/markets.json \
  --output /tmp/run.json
```

```bash
bash skills/autopredict/scripts/tune_params.sh \
  --dir /tmp/autopredict \
  --dataset /path/to/markets.json \
  --scoring sharpe \
  --param aggressive_edge 0.10,0.12,0.15 \
  --param max_depth_fraction 0.10,0.15,0.20 \
  --output /tmp/autopredict-tuning
```

Recommended autoresearch prompts:

- “Optimize `aggressive_edge` and `max_depth_fraction` for lower slippage while keeping trade count above 20.”
- “Find whether lowering `min_edge` improves Sharpe on this dataset or just adds noisy trades.”

Bad autoresearch prompts:

- “Make it profitable.”
- “Tune every parameter.”
- “Use live trading results” when the adapter is still a scaffold.
