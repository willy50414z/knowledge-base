---
name: trade-strategy-freqtrade-implementation
description: Implement trading strategies in Freqtrade with auditable signals, reproducible config, and traceable mapping from prototype to code. Use when building or reviewing a Freqtrade strategy implementation.
---

# Trade Strategy Freqtrade Implementation Skill

Implement strategies in Freqtrade with auditable, reproducible behavior.

## Framework Standards

- Keep strategy files, config, and dependencies organized so the strategy can be run reproducibly in the target repo.
- Use the host repository's naming and import conventions instead of assuming a fixed package layout.

## Required Work

- Implement `populate_indicators`, `populate_entry_trend`, and `populate_exit_trend`.
- Include `dbg_` columns for all internal indicators to support `analyze_backtest_result.py`.
- Manage `informative_pairs` if required for multi-timeframe analysis.
- Update the strategy-local Freqtrade config with appropriate whitelist, stake amount, and dry-run wallet settings.

## General Decision Rules

- Do not mark the implementation as complete if the Freqtrade logic cannot be traced back to the approved prototype or research hypothesis.
- Do not proceed if entry, exit, or risk-control behavior depends on hidden state that cannot be audited from the dataframe or strategy code.
- Do not proceed if informative timeframe handling, config assumptions, or runtime dependencies differ materially from the intended live setup.
- Do not proceed if the strategy cannot be executed reproducibly with the documented strategy file, config, and required artifacts.

## Code Reference

| Purpose | Path |
|---------|------|
| Run backtesting / hyperopt | `lib/endpoints/freqtrade.py` |
| Freqtrade execution adapter | `lib/strategy/execution/freqtrade_executor.py` |
| Generate strategy config | `lib/endpoints/generate_freqtrade_config.py` |
| Base Freqtrade config template | `freqtrade/configs/base.json` |
| Strategy .py file location | `freqtrade/strategies/<StrategyClass>.py` |
| Strategy-local config | `strategies/<family>/engine/freqtrade/config.json` |
| Technical indicators (TA-Lib wrapper) | `lib/ohlcv_data_handler/tech_idx_svc.py` |
