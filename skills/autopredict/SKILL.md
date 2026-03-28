---
name: autopredict
description: Run the AutoPredict prediction market trading agent framework. Scan live Polymarket markets, evaluate trade opportunities with execution-aware metrics, backtest strategies, and iteratively tune agent parameters. Use when asked to "scan markets", "find prediction market edges", "backtest trading strategy", "tune autopredict", or "run autopredict".
compatibility: Requires python3 (3.10+), pip, and internet access for live Polymarket data. No API keys needed for read-only market scanning. CLOB API credentials required only for live trading (disabled by default).
---

# AutoPredict

A framework for prediction market trading agents. It connects to live Polymarket data, lets you supply your own probability estimates, and evaluates trade opportunities with execution-aware metrics.

**The agent does NOT generate predictions.** It optimizes execution given your forecast. The forecasting is your job. The execution is the agent's job.

## Core Capabilities

1. **Live market scanning** — Fetch active markets and real order books from Polymarket (no auth needed for reads)
2. **Event-level analysis** — Find multi-outcome events where sibling prices don't sum to 1.0 (structural mispricing)
3. **Execution-aware agent** — Given your `fair_prob`, evaluates edge, spread, liquidity, and book depth before recommending a trade
4. **Configurable strategy** — All agent parameters are JSON-tunable (edge thresholds, risk limits, sizing)
5. **Backtesting engine** — Test strategy changes against market data with slippage and fill rate simulation
6. **Self-learning loop** — Analyze trade logs, identify failure patterns, and auto-tune parameters

## Architecture

```
CLI Layer (predict.py / cli.py)
  │
  ├─ Live scanning: predict.py (default entry point)
  └─ Backtesting:   cli.py backtest / score-latest / learn-analyze
  │
  ▼
Agent Layer (agent.py)                Market Environment (market_env.py)
├─ AutoPredictAgent                   ├─ OrderBook (depth-aware)
│  ├─ evaluate_market()               │  ├─ walk_book()
│  ├─ analyze_performance()           │  ├─ mid_price / spread
│  └─ propose_improvement()           │  └─ market_impact_estimate
├─ ExecutionStrategy                  ├─ ExecutionEngine
│  ├─ decide_order_type()             │  ├─ market_order simulation
│  ├─ calculate_trade_size()          │  └─ limit_order simulation
│  └─ split_order()                   └─ Metrics (epistemic/financial/execution)
└─ AgentConfig (JSON-driven knobs)
  │
  ▼
Configuration
├─ strategy_configs/{name}.json       (AgentConfig parameters)
├─ strategy.md                        (human guidance for agent focus)
└─ config.json                        (experiment paths, bankroll, flags)
```

### Key Separation

- **Agent** (mutable): Decision logic — when/how to trade. You change this.
- **Environment** (fixed): Order book simulation, execution mechanics, metrics. You don't change this.
- **Config** (tunable): JSON knobs that control agent behavior without code changes.

## Setup

### Clone and install

```bash
git clone https://github.com/howdymary/autopredict.git
cd autopredict
python3 -m pip install -e .
```

### Verify installation

```bash
python3 predict.py --help
```

## Available Scripts

This skill bundles helper scripts for common workflows:

- **`scripts/setup.sh`** — Clone repo, install deps, verify setup
- **`scripts/scan_markets.sh`** — Scan live markets with configurable filters
- **`scripts/run_backtest.sh`** — Run a backtest with a given strategy config
- **`scripts/tune_params.sh`** — Grid search over parameter space

## Workflows

### 1. Scan Live Markets

The primary entry point for market discovery:

```bash
cd autopredict
python3 predict.py                              # scan top markets by volume
python3 predict.py --top 10 --verbose           # detailed view of top 10
python3 predict.py --category politics           # filter by category
python3 predict.py --min-liquidity 5000          # only liquid markets
python3 predict.py --events                      # find multi-outcome mispricing
```

**What to look for:**
- Markets with tight spreads (<4%) and deep books
- Event groups where sibling probabilities don't sum to ~1.0
- Markets where you have domain expertise to form a `fair_prob`

### 2. Evaluate a Specific Market

When you have an opinion on a market's true probability:

```bash
python3 predict.py --fair 0.60 <condition_id>
```

This will:
1. Fetch real market data + order book
2. Compute edge (your `fair_prob` vs market price)
3. Run the AutoPredict agent to recommend: side, size, order type, limit price
4. Show execution-quality metrics (spread, depth, slippage estimate)

### 3. Run a Backtest

Test strategy changes against historical data:

```bash
# Default backtest with baseline config
python3 -m autopredict.cli backtest

# Custom config
python3 -m autopredict.cli backtest --config strategy_configs/optimized.json

# Score the latest run
python3 -m autopredict.cli score-latest
```

### 4. Iterative Strategy Tuning

The core improvement loop:

```bash
# 1. Establish baseline
python3 -m autopredict.cli backtest --config strategy_configs/baseline.json
python3 -m autopredict.cli score-latest

# 2. Modify one parameter
# Edit strategy_configs/candidate.json — change ONE knob

# 3. Run candidate
python3 -m autopredict.cli backtest --config strategy_configs/candidate.json
python3 -m autopredict.cli score-latest

# 4. Compare metrics — keep or discard
# 5. Repeat
```

### 5. Analyze Trade Performance

After backtesting or live monitoring:

```bash
python3 -m autopredict.cli learn-analyze
python3 -m autopredict.cli learn-analyze --log-dir state/trades --last 50
```

Identifies:
- Win rate by category/market type
- Systematic failure patterns (e.g., wide-spread markets losing)
- Calibration error between your forecasts and outcomes
- Parameter adjustment recommendations

### 6. Parameter Grid Search

Automated tuning over parameter space:

```bash
python3 -m autopredict.cli learn-tune \
  --param min_edge 0.03 0.05 0.08 \
  --param aggressive_edge 0.10 0.12 0.15 \
  --param max_risk_fraction 0.01 0.02 0.03
```

## Strategy Configuration

### AgentConfig Parameters

All tunable via `strategy_configs/{name}.json`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_edge` | 0.05 | Minimum edge (probability units) to consider a trade |
| `aggressive_edge` | 0.12 | Edge threshold for market orders (vs limit) |
| `max_risk_fraction` | 0.02 | Max loss per trade as % of bankroll |
| `max_position_notional` | 25.0 | Hard cap on position size ($) |
| `min_book_liquidity` | 60.0 | Minimum visible depth to trade |
| `max_spread_pct` | 0.04 | Max spread before rejecting |
| `max_depth_fraction` | 0.15 | Max trade as fraction of visible depth |
| `split_threshold_fraction` | 0.25 | Threshold for splitting orders |
| `passive_requote_fraction` | 0.25 | Reserved for passive order re-quoting |

### Tuning Guidelines

**Start conservative, loosen one knob at a time:**

1. **More trades?** Lower `min_edge` (0.05 → 0.03). Risk: worse average quality.
2. **More aggressive execution?** Lower `aggressive_edge` (0.12 → 0.08). Risk: more slippage.
3. **Larger positions?** Raise `max_risk_fraction` (0.02 → 0.03). Risk: bigger drawdowns.
4. **Thinner markets?** Lower `min_book_liquidity` (60 → 30). Risk: poor fills.
5. **Wider spreads?** Raise `max_spread_pct` (0.04 → 0.06). Risk: execution drag.

**Never change more than one parameter per experiment.** Measure the effect, then decide.

## Metrics

Three groups of metrics, all computed via `evaluate_all()`:

### Epistemic Metrics
- **Brier Score** — Mean squared error of probability forecasts (lower is better, target <0.20)
- **Calibration by bucket** — Accuracy within probability bins (0.0-0.1, 0.1-0.2, etc.)

### Financial Metrics
- **Total PnL** — Sum of realized gains/losses
- **Sharpe Ratio** — Risk-adjusted returns (target >1.0)
- **Max Drawdown** — Largest peak-to-trough decline (target <50%)
- **Win Rate** — Fraction of profitable trades (target >50%)

### Execution Metrics
- **Avg Slippage (bps)** — How much worse than mid price (target <10 bps limit, <30 bps market)
- **Fill Rate** — Fraction of requested size filled (market: 0.8-1.0, limit: 0.15-0.75)
- **Spread Capture (bps)** — Profit from passive order placement (target >0)
- **Market Impact (bps)** — Price movement caused by trade (target <50 bps)
- **Implementation Shortfall (bps)** — Total cost: slippage + fees (target <30 bps)
- **Adverse Selection Rate** — Fraction of limit orders that moved against you (target <20%)

## Strategy Guidance File

`strategy.md` provides human-readable context for the agent's focus areas:

```markdown
# AutoPredict Strategy Guidance

## Current focus
- Improve execution quality before chasing more raw PnL
- Prefer smaller orders in thin books
- Use passive orders when edge is real but not urgent

## Hard constraints
- Never risk more than 2% of bankroll on one market snapshot
- Avoid markets with visible depth below the configured minimum

## Research questions
- Are weak-edge market orders causing slippage drag?
- Does time-to-expiry justify more aggressive execution?
```

Update this file as your understanding evolves. The agent reads it for context.

## Integration with Autoresearch

AutoPredict pairs naturally with the **autoresearch** skill for disciplined optimization:

1. Use autoresearch to define the optimization target (e.g., Sharpe ratio, slippage)
2. Use autopredict's backtest as the `autoresearch.sh` workload
3. Let autoresearch manage the experiment loop, hypothesis tracking, and reporting
4. AutoPredict provides the domain-specific metrics

Example `autoresearch.sh` for AutoPredict optimization:

```bash
#!/bin/bash
set -euo pipefail
cd /path/to/autopredict
python3 -m autopredict.cli backtest --config strategy_configs/candidate.json 2>/dev/null
METRICS=$(python3 -m autopredict.cli score-latest 2>/dev/null)
SHARPE=$(echo "$METRICS" | python3 -c "import json,sys; print(json.load(sys.stdin).get('sharpe_ratio', 0))")
echo "METRIC sharpe=$SHARPE"
```

## Environment Variables

For read-only scanning (default), no credentials needed.

For authenticated CLOB access (future live trading):

```bash
export POLYMARKET_API_KEY="..."
export POLYMARKET_API_SECRET="..."
export POLYMARKET_PASSPHRASE="..."
export POLYMARKET_PK="..."           # wallet private key (optional)
export POLYMARKET_FUNDER="..."       # funder address (optional)
```

**Live trading is disabled by default** (`live_trading_enabled: false` in config.json).

## File Reference

| File | Purpose |
|------|---------|
| `predict.py` | Live market scanner — main entry point |
| `agent.py` | Mutable trading agent with tunable knobs |
| `market_env.py` | Fixed order book simulation and execution |
| `cli.py` | CLI for backtest, scoring, analysis |
| `config.json` | Experiment harness configuration |
| `strategy.md` | Human guidance for agent focus |
| `strategy_configs/` | JSON parameter configs (baseline, optimized, etc.) |
| `autopredict/markets/polymarket.py` | Polymarket API adapter (Gamma + CLOB) |
| `autopredict/strategies/` | Strategy implementations |
| `autopredict/backtest/` | Backtest engine and metrics |
| `autopredict/learning/` | Performance analysis and auto-tuning |
| `autopredict/live/` | Live monitoring and risk management |
| `autopredict/config/` | Config loading and validation |

## Common Pitfalls

### 1. Confusing market artifacts with real arbitrage

Multi-outcome events (e.g., "Who wins the Masters?") have sibling probabilities that sum to >1.0 by design. This is a grouping artifact, not arbitrage. Real binary arbitrage requires exactly two outcomes where one MUST happen.

### 2. Overfitting to backtest data

Strategy configs tuned on one dataset may not generalize. Use walk-forward testing (`enable_walk_forward: true`) and out-of-sample validation.

### 3. Ignoring execution costs

A strategy that looks good on mid-price fills may be unprofitable after slippage, spread, and market impact. Always evaluate execution metrics alongside PnL.

### 4. Changing multiple parameters at once

One change per experiment. If you change `min_edge` and `aggressive_edge` simultaneously, you can't attribute the result to either change.

### 5. Treating the agent as a forecaster

AutoPredict does not predict outcomes. It takes your `fair_prob` and decides whether/how to trade. Bad forecasts in → bad trades out, regardless of how good the execution engine is.
