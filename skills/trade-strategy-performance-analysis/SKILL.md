# Trade Strategy Performance Analysis Skill

Audit strategy performance and identify edge cases.

## Project Standards

- **Tooling**: MUST run `com/willy/trade_bot/freqtrade/analyze_backtest_result.py`.
- **Artifacts**: Review the generated `report_<stem>_<strategy>.md` and charts in `user_data/backtest_results/reports/`.

## Required Work

- Analyze **Signal Win Rate vs Trade Win Rate**: Identify if exit logic is cutting winners or losers early.
- Review **Gate Filter Funnel**: Check if any `dbg_` filters are blocking profitable trades (false positives).
- Check **Slippage Sensitivity**: Ensure the strategy is still profitable with 0.1% slippage.
- Document "Pain Points" for the next iteration.
