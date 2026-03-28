---
name: autopredict
description: Wrap the howdymary/autopredict Polymarket trading-agent repo. Use when you need to scan live Polymarket markets, inspect structural event mispricing, evaluate a market with your own fair probability, run reproducible backtests against a JSON dataset, tune strategy parameters safely, or review the repo's paper/live trading scaffolds and failure modes.
---

# AutoPredict

## Quick Start — Simple Examples

New to AutoPredict? Start here before reading the full docs.

**1. Scan what's trending on Polymarket right now**
```bash
python3 predict.py --top 10
```
Shows the 10 most active markets with spreads, depth, and overround signals.

**2. Show me the 5 most liquid markets**
```bash
python3 predict.py --top 5 --verbose
```
Lists markets sorted by liquidity with full execution details.

**3. Browse multi-outcome events for structural mispricing**
```bash
python3 predict.py --events --top 10
```
Checks whether event probabilities sum to more or less than 100%.

**4. What does the order book look like for a specific market?**
```bash
python3 predict.py --fair 0.55 <condition_id>
```
Replace `<condition_id>` with the Polymarket ID. Provide your own fair probability estimate and AutoPredict evaluates the trade.

> Run `python3 predict.py --help` for all flags. No credentials required for live reads.

---

AutoPredict is an execution framework for prediction-market trading. It is **not** a forecasting model.

- You provide `fair_prob`.
- The repo evaluates execution quality: side, order type, size, spread, depth, slippage, and risk.
- Live market reads require internet but no credentials.
- Real trading is scaffolded, not production-ready.

This skill was audited against the upstream repository layout and command surface, not just the README.

## What Is Real vs Scaffold

**Reliable entry points**

- `python3 predict.py` scans live Polymarket markets.
- `python3 predict.py --events` inspects multi-outcome event overround / underround.
- `python3 predict.py --fair 0.60 <condition_id>` evaluates one market using your explicit probability.
- `python3 -m autopredict.cli backtest --dataset ...` runs an offline backtest.
- `python3 -m autopredict.cli score-latest` prints the most recent saved metrics JSON.

**Partially implemented or scaffold-only**

- `python3 -m autopredict.cli learn analyze` only works if you already have JSONL trade logs. Plain CLI backtests do **not** create those logs.
- `python3 -m autopredict.cli learn tune` and `learn improve` are placeholders that point to a nonexistent `scripts/learn_and_improve.py`.
- `python3 -m autopredict.cli trade-live` is intentionally disabled by config.
- `scripts/run_paper.py` and `scripts/run_live.py` are deployment scaffolds. `run_live.py` uses a `MockVenueAdapter`, so it is not a real exchange adapter.

## Repo Map

- `predict.py`: live Polymarket scanner and one-off evaluation path.
- `autopredict/cli.py`: packaged CLI used for backtest, score-latest, and learning commands.
- `run_experiment.py`: simple offline backtest harness used by `autopredict.cli backtest`.
- `strategy_configs/*.json`: strategy knobs for offline experiments.
- `autopredict/_defaults/datasets/sample_markets.json`: bundled sample dataset. Use this when you need a known-good backtest input.
- `autopredict/learning/tuner.py`: reusable grid-search API. Better than the stub CLI.
- `scripts/run_paper.py`, `scripts/run_live.py`: paper/live monitoring templates.

## Decision Tree

### 1. Choose the workflow

If the user wants to:

- **Find liquid live markets or structural event mispricing**: use `predict.py` via `scripts/scan_markets.sh`.
- **Evaluate one market with a known fair probability**: use `predict.py --fair ...`.
- **Compare strategy configs or produce reproducible metrics**: use `python3 -m autopredict.cli backtest --dataset ...` via `scripts/run_backtest.sh`.
- **Sweep parameters safely**: use `scripts/tune_params.sh`. Do **not** use `python3 -m autopredict.cli learn tune`.
- **Inspect trade logs**: use `python3 -m autopredict.cli learn analyze --log-dir ...` only if JSONL logs already exist.
- **Discuss paper/live deployment scaffolds**: read `docs/DEPLOYMENT.md`, `configs/*.yaml`, and the Python runners before claiming the repo can trade live.

### 2. Choose the command surface

- Use `predict.py` for live reads and one-off agent evaluation.
- Use `python3 -m autopredict.cli ...` for reproducible offline backtests.
- Avoid `python3 -m autopredict.backtest.cli ...`; that submodule has brittle import behavior in the current repo state.

### 3. Choose the data source

- For a quick smoke test: use `autopredict/_defaults/datasets/sample_markets.json`.
- For real research: require a user-supplied dataset of historical snapshots.
- If the user has no dataset and wants strategy performance claims, stop and say the repo cannot produce a valid backtest without one.

## Setup

Preferred helper:

```bash
bash skills/autopredict/scripts/setup.sh --dir /tmp/autopredict
```

Manual setup:

```bash
git clone https://github.com/howdymary/autopredict.git /tmp/autopredict
cd /tmp/autopredict
python3 -m pip install -e .
python3 predict.py --help
python3 -m autopredict.cli --help
```

After setup, keep work inside the cloned repo when invoking upstream commands.

## Opinionated Workflows

### Workflow A: Fast live market triage

Use this when the user wants ideas, not a PnL claim.

```bash
cd /tmp/autopredict
python3 predict.py --top 10 --verbose
python3 predict.py --events --top 10
```

Interpretation:

- Prefer markets with tight spreads and visible depth.
- Treat event underround as a structural clue, not automatic free money.
- Only move to trade evaluation once you can justify a `fair_prob`.

### Workflow B: Evaluate a single conviction

Use this when the user already has a thesis on one market.

```bash
cd /tmp/autopredict
python3 predict.py --fair 0.60 <condition_id>
```

Important caveat:

- `predict.py --fair` constructs `AutoPredictAgent(AgentConfig())` directly.
- That means it uses default agent parameters, not `strategy_configs/baseline.json` or your edited JSON config.
- Use it as a default-policy sanity check, not as proof that a tuned config behaves the same way.

### Workflow C: Backtest a strategy config

Use this when the user wants reproducible metrics or config comparisons.

```bash
cd /tmp/autopredict
python3 -m autopredict.cli backtest \
  --config strategy_configs/baseline.json \
  --dataset autopredict/_defaults/datasets/sample_markets.json

python3 -m autopredict.cli score-latest
```

Opinionated rule:

- Always pass `--dataset`.
- The repo default `config.json` sets `"default_dataset": null`.
- Running `python3 -m autopredict.cli backtest` with no dataset currently throws a `TypeError`.

### Workflow D: Tune parameters

Use the bundled helper instead of the stub CLI:

```bash
bash skills/autopredict/scripts/tune_params.sh \
  --dir /tmp/autopredict \
  --dataset autopredict/_defaults/datasets/sample_markets.json \
  --param min_edge 0.03,0.05,0.08 \
  --param aggressive_edge 0.10,0.12,0.15
```

Opinionated tuning rules:

- Start with 1-2 parameters, not 6.
- Prefer `sharpe` or `total_pnl` only after sample size is reasonable.
- Reject “best” configs with too few trades.
- Save every run; do not trust memory or terminal output.

### Workflow E: Review learning / deployment scaffolds

Use this when the user asks about self-improvement, paper trading, or live trading.

- `autopredict.learning.tuner.GridSearchTuner` is real and reusable.
- `python3 -m autopredict.cli learn tune` is just a message, not a tuning engine.
- `scripts/run_paper.py` is a monitoring loop template; it does not fetch real markets or execute the full agent logic.
- `scripts/run_live.py` requires confirmation and safety flags, but still uses `MockVenueAdapter`, so it cannot trade a real venue out of the box.

## Strategy Knobs That Matter

Main JSON parameters in `strategy_configs/*.json`:

- `min_edge`: minimum edge before any trade is considered.
- `aggressive_edge`: threshold for using market orders more aggressively.
- `max_risk_fraction`: position sizing as fraction of bankroll.
- `max_position_notional`: hard dollar cap per order.
- `min_book_liquidity`: minimum visible depth required.
- `max_spread_pct`: spread filter.
- `max_depth_fraction`: cap as fraction of visible depth.
- `split_threshold_fraction`: start slicing when order is too large relative to depth.

Opinionated tuning guidance:

- Lower `min_edge` only if trade count is too low.
- Raise `aggressive_edge` if slippage is the dominant problem.
- Lower `max_depth_fraction` before touching risk caps when market impact is the problem.
- Do not loosen spread and liquidity filters at the same time; you will not know which one caused the regression.

## Failure Modes and Edge Cases

### Backtest failures

- **`TypeError` before the backtest starts**: almost always because no `--dataset` was passed and `default_dataset` is `null`.
- **`No metrics.json found under state directory`**: `score-latest` was run before a successful backtest.
- **Malformed JSON errors**: invalid strategy config or dataset schema.

### Learning workflow failures

- **`learn analyze` reports no logs**: expected unless you created JSONL logs with `TradeLogger` or a scaffold that writes them.
- **`learn tune` / `learn improve` prints advice only**: expected. Those subcommands are placeholders.
- **Docs mention `scripts/learn_and_improve.py`**: that script does not exist in the audited upstream repo.

### Live / paper trading confusion

- **Paper trading is not the same as live market scanning**: `run_paper.py` is a loop scaffold, not an end-to-end paper execution engine over Polymarket.
- **Live trading docs sound complete, but adapter is mock**: `run_live.py` cannot place real venue orders without extra implementation.
- **`trade-live` CLI is disabled**: `config.json` defaults `live_trading_enabled` to `false`.

### Command-path gotchas

- **Do not use `python3 -m autopredict.backtest.cli`** in this repo state unless you are ready to debug import-path issues.
- **Do not assume root docs and packaged CLI are fully synchronized**. The package path under `autopredict/` is the safer source of truth.
- **Do not claim config changes affect `predict.py --fair`** unless you verified the code path. It currently ignores `strategy_configs/*.json`.

## Helper Scripts Bundled With This Skill

- `scripts/setup.sh`: clone, install, verify, and smoke-test the repo.
- `scripts/scan_markets.sh`: wrapper around `predict.py` for live scan / `--events` / `--fair` paths.
- `scripts/run_backtest.sh`: safe backtest wrapper that always provides a dataset or fails with a useful error.
- `scripts/tune_params.sh`: grid-search wrapper that bypasses the upstream stub tuning CLI.

## Recommended Agent Behavior

When using this skill:

- Lead with the limitation that AutoPredict optimizes execution, not prediction.
- Ask where `fair_prob` comes from before discussing edges as if they were alpha.
- Require a dataset for any serious backtest claim.
- Separate “works in the repo” from “documented in the repo”.
- Treat paper/live trading as architecture review unless the user is explicitly asking to extend the scaffold.

## Autoresearch Pairing

Use this skill with `autoresearch` when the user wants disciplined tuning.

Recommended setup:

1. Define the target metric, usually `sharpe`, `total_pnl`, or `avg_slippage_bps`.
2. Use `scripts/run_backtest.sh` or `scripts/tune_params.sh` as the experiment workload.
3. Keep one hypothesis per run.
4. Store configs and metrics under a dated output directory.

Good autoresearch prompt framing:

- “Optimize `aggressive_edge` and `max_depth_fraction` for lower slippage without collapsing trade count.”
- “Improve Sharpe on this dataset while keeping max drawdown below 35%.”

Bad framing:

- “Make it profitable” with no dataset.
- “Tune everything” with no metric priority.
