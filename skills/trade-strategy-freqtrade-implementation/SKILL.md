# Trade Strategy Freqtrade Implementation Skill

Implement strategies in Freqtrade following project versioning and path standards.

## Project Standards

- **Strategy Path**: `com/willy/trade_bot/freqtrade/strategy/<StrategyName>/`
- **Versioning Rule**: `<StrategyName>_V<Major>_<Minor>_Strategy.py`
    - **Major**: Core logic change (e.g., new indicators).
    - **Minor**: Parameter change (e.g., tweaking thresholds).
- **Imports**: Always use `from com.willy.trade_bot...` for utilities.

## Required Work

- Implement `populate_indicators`, `populate_entry_trend`, and `populate_exit_trend`.
- Include `dbg_` columns for all internal indicators to support `analyze_backtest_result.py`.
- Manage `informative_pairs` if required for multi-timeframe analysis.
- Update `config.json` with appropriate `whitelist`, `stake_amount`, and `dry_run_wallet`.

## General Decision Rules

- Do not mark the implementation as complete if the Freqtrade logic cannot be traced back to the approved prototype or research hypothesis.
- Do not proceed if entry, exit, or risk-control behavior depends on hidden state that cannot be audited from the dataframe or strategy code.
- Do not proceed if informative timeframe handling, config assumptions, or runtime dependencies differ materially from the intended live setup.
- Do not proceed if the strategy cannot be executed reproducibly with the documented strategy file, config, and required artifacts.
