---
name: trade-strategy-freqtrade-implementation
description: Implement trading strategies in Freqtrade with auditable signals, reproducible config, and traceable mapping from prototype to code. Use when building or reviewing a Freqtrade strategy implementation.
---

# Trade Strategy Freqtrade Implementation Skill

Implement strategies in Freqtrade with auditable, reproducible behavior.

## Quick Reference

For common implementation tasks — stop reading after this section if covered.

**Required methods checklist:**
- [ ] `populate_indicators` — all indicators computed; `dbg_` columns included for all filter signals
- [ ] `populate_entry_trend` — uses only lagged signals (no `.shift(0)` on future data)
- [ ] `populate_exit_trend` — traceable to prototype spec

**Common look-ahead bias traps (cross-ref `look-ahead-bias-check`):**

| Pattern | Issue | Fix |
|---------|-------|-----|
| `df['signal'].shift(0)` in entry | Future leak | Use `.shift(1)` |
| `.iloc[-1]` in `custom_exit` | Future leak | Use last-row column values |
| Informative merge without `ffill` | Gap fill issues | Always `ffill` after merge |

**Config generation (run after implementation):**
```bash
python -m lib.endpoints.generate_freqtrade_config <strategy_family>
```
Verify `config.json` has `trading_mode`, `exchange`, and `fee` fields before backtest.

---

## Framework Standards

- Keep strategy files, config, and dependencies organized so the strategy can be run reproducibly in the target repo.
- Use the host repository's naming and import conventions instead of assuming a fixed package layout.

## Required Work

- Implement `populate_indicators`, `populate_entry_trend`, and `populate_exit_trend`.
- Include `dbg_` columns for all internal indicators to support `analyze_backtest_result.py`.
- Manage `informative_pairs` if required for multi-timeframe analysis.
- Update the strategy-local Freqtrade config with appropriate whitelist, stake amount, and dry-run wallet settings.

## Implementation Completion Checklist

Run this before marking implementation as done and advancing to `backtest` phase:

- [ ] `populate_indicators`, `populate_entry_trend`, `populate_exit_trend` all implemented
- [ ] `dbg_` columns included for all filter signals in `populate_indicators`
- [ ] Look-ahead bias self-check passed (cross-ref `look-ahead-bias-check/SKILL.md`)
- [ ] Config generated and verified:
  ```bash
  python -m lib.endpoints.generate_freqtrade_config <strategy_family>
  ```
  Confirm `strategies/<family>/engine/freqtrade/config.json` has `trading_mode`, `exchange`, and `stake_amount` — not a template placeholder.
- [ ] `freqtrade/strategies/<StrategyName>.py` importable: `python -m lib.endpoints.freqtrade` does not raise an import error
- [ ] `STATUS.md` phase updated to `backtest`

---

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
