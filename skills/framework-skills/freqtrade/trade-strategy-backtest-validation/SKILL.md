---
name: trade-strategy-backtest-validation
description: Validate Freqtrade backtests with checks for OOS degradation, suspicious win rates, and unstable drawdown behavior. Use when running, reviewing, or judging Freqtrade backtest results.
---

# Trade Strategy Backtest Validation Skill

Standardize backtesting and validation processes using project tools.

## Framework Standards

- **Tooling**: Use the host repository's standard Freqtrade backtest command or wrapper.
- **Verification**: If `Win Rate > 70%` with high frequency, a mandatory Look-ahead bias check is required.

## Required Work

- Run standard backtest for the specified `timerange`.
- Verify **OOS (Out-of-Sample) Performance**: If OOS profit is < 50% of the training period profit, mark the strategy as unstable.
- Check `Drawdown Duration`: Ensure recovery time is within project constraints (e.g., < 30 days).

## Code Reference

| Purpose | Path |
|---------|------|
| Run backtest via CLI | `lib/endpoints/freqtrade.py` |
| Execution adapter | `lib/strategy/execution/freqtrade_executor.py` |
| Backtest result artifacts | `freqtrade/user_data/backtest_results/` |
| Record results as knowledge | `knowledge-base/knowledge/backtest-records/` (see backtest-record-standard.md) |
