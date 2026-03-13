# Trade Strategy Backtest Validation Skill

Standardize backtesting and validation processes using project tools.

## Project Standards

- **Tooling**: MUST use `com/willy/trade_bot/freqtrade/freqtrade_executor.py` for running backtests.
- **Verification**: If `Win Rate > 70%` with high frequency, a mandatory Look-ahead bias check is required.

## Required Work

- Run standard backtest for the specified `timerange`.
- Verify **OOS (Out-of-Sample) Performance**: If OOS profit is < 50% of the training period profit, mark the strategy as unstable.
- Check `Drawdown Duration`: Ensure recovery time is within project constraints (e.g., < 30 days).
