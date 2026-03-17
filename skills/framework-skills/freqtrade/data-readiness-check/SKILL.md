---
name: data-readiness-check
description: Verify that Freqtrade feature data exists and covers the full requested timerange before running a backtest. Use as the first gate in the backtest preflight to prevent silent data truncation or cryptic Freqtrade errors.
---

# Data Readiness Check Skill

## Quick Reference

```bash
python -m lib.endpoints.check_data_readiness <pair> <timeframe> <timerange> [--exchange BINANCE] [--market-type FUTURE]
```

Exit codes:
- `0` — READY: proceed with backtest
- `1` — MISSING: data file not found; fetch data first
- `2` — TRUNCATED: data exists but doesn't cover full range; fetch more data
- `3` — ERROR: file corrupt or unreadable

---

## When to Use

Always run before `python -m lib.endpoints.freqtrade ... --mode backtest`.

This check catches two silent failure modes:
1. **MISSING**: Freqtrade will fail with a cryptic error or no trades
2. **TRUNCATED**: Freqtrade will silently backtest a shorter period than requested, making results misleading

## Workflow

### Step 1 — Identify parameters

From `strategies/<family>/README.md` or `STATUS.md`:
- `pair`: product identifier (e.g. `BTCUSDT`)
- `timeframe`: candle period (e.g. `1h`)
- `timerange`: backtest period in YYYYMMDD-YYYYMMDD format

### Step 2 — Run check

```bash
python -m lib.endpoints.check_data_readiness BTCUSDT 1h 20250101-20260101
```

### Step 3 — Handle result

| Status | Action |
|--------|--------|
| `READY` | Proceed to backtest |
| `MISSING` | Fetch data with `data-pipeline` skill, then re-check |
| `TRUNCATED` | Fetch missing date range with `data-pipeline` skill, then re-check |
| `ERROR` | Inspect the feature file manually; re-download if corrupted |

### Step 4 — On MISSING or TRUNCATED

Load the `data-pipeline` skill for fetch commands:
- `knowledge-base/skills/domain-skills/trading/data-pipeline/SKILL.md`

After fetching, re-run the check to confirm READY before proceeding.

## Code Reference

| Purpose | Path |
|---------|------|
| CLI endpoint | `lib/endpoints/check_data_readiness.py` |
| Feature file storage | `data/features/<EXCHANGE>/<MARKET_TYPE>/<PRODUCT>_<TIMEFRAME>.feature` |
| FeatureStore | `lib/storage/feature_store.py` |
