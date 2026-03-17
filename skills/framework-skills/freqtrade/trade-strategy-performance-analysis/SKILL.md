---
name: trade-strategy-performance-analysis
description: Analyze Freqtrade strategy performance to find signal quality issues, blocked trades, slippage sensitivity, and failure modes. Use when reviewing generated reports or diagnosing where a strategy makes or loses money.
---

# Trade Strategy Performance Analysis Skill

Audit strategy performance and identify edge cases.

## Framework Standards

- **Tooling**: Use the host repository's standard Freqtrade performance analysis command or wrapper.
- **Artifacts**: Review the generated report files, charts, and debug outputs produced by the host workflow.

## Required Work

- Analyze **Signal Win Rate vs Trade Win Rate**: Identify if exit logic is cutting winners or losers early.
- Review **Gate Filter Funnel**: Check if any `dbg_` filters are blocking profitable trades (false positives).
- Check **Slippage Sensitivity**: Ensure the strategy is still profitable with 0.1% slippage.
- Document "Pain Points" for the next iteration.

## Code Reference

| Purpose | Path |
|---------|------|
| Generate HTML analysis report | `lib/strategy/analytics/analyze_backtest_result.py` |
| Backtest result artifacts | `freqtrade/user_data/backtest_results/` |
| Generated HTML reports | `freqtrade/reports/` |
| Strategy-local reports | `strategies/<family>/reports/` |
