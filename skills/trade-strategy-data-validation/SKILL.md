# Trade Strategy Data Validation Skill

Collect and validate historical data while preventing leakage.

## Project Standards

- **Data Path**: Use `com/willy/trade_bot/data/` for raw data storage.
- **Leakage Prevention**: Mandatory check for Look-ahead bias in OHLCV alignment.

## Required Work

- Ensure timerange covers at least one full bull and one full bear cycle.
- **Point-in-time check**: Verify that signals at time `T` do not use information from `T+1` (e.g., future close prices).
- **Split Strategy**: Define Train/Validation/OOS (Out-of-Sample) boundaries.
- **Integrity**: Check for missing candles; if > 0.1% are missing, perform interpolation or data re-fetch.
