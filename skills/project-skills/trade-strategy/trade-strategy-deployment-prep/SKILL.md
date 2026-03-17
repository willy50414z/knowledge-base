---
name: trade-strategy-deployment-prep
description: Prepare repository strategies for deployment by checking container parity, dependency completeness, runtime safety, and production config hygiene. Use when a strategy is being promoted from research/backtest into deployable execution.
---

# Trade Strategy Deployment Prep Skill

Prepare the strategy for live trading in a containerized environment (Docker).

## Project Standards

- **Relative Paths**: No hardcoded paths allowed. Use `REPO_ROOT` derived from `__file__` or environment variables.
- **Environment Parity**: Every strategy version MUST pass a **Container Dry Run** before going live.
- **Dockerfile**: `build/Dockerfile` is the canonical container definition. Update it when dependencies change.

## Required Work

### 1. Container Dry Run

Build and run the image using the default dry-run command. This verifies imports, path resolution, and dependency completeness.

```bash
# From repo root
docker build -t trade_strategy -f build/Dockerfile .
docker run --rm trade_strategy
```

Expected output:
```
Import check OK
REPO_ROOT: /trade_strategy
strategy_dir: /trade_strategy/freqtrade/strategies
userdir: /trade_strategy/freqtrade/user_data
```

If you see `ModuleNotFoundError` or `FileNotFoundError`, fix the import or path before proceeding.

### 2. Backtest Run in Container

Verify a full backtest completes inside the container:

```bash
docker run --rm \
  -v "$(pwd)/strategies:/trade_strategy/strategies:ro" \
  -v "$(pwd)/data:/trade_strategy/data" \
  -v "$(pwd)/freqtrade/user_data:/trade_strategy/freqtrade/user_data" \
  trade_strategy \
  python -m lib.endpoints.freqtrade <strategy_family> <StrategyClass> <timerange>
```

### 3. Dependency Audit

- All dependencies must be pinned in `requirements.txt` at the repo root.
- The base image (`freqtradeorg/freqtrade:stable`) provides freqtrade, pandas, numpy, TA-Lib.
- Any additional packages must be explicitly listed in `requirements.txt`.
- Verify: `pip install -r requirements.txt` succeeds inside the container without conflicts.

### 4. Risk & API Security

- **Risk Circuit Breaker**: Confirm `stoploss` and `max_open_trades` in `strategies/<family>/engine/freqtrade/config.json` match the live account risk profile.
- **Timezone**: Verify the strategy handles UTC correctly — the container runs in UTC.
- **Log Verification**: Ensure logs do not contain API keys or sensitive balance info.
- **API Permissions**: The production API key must have `Withdrawal` permissions **DISABLED**.
- **Secrets**: `lib/utils/config.ini` must be mounted at runtime, never baked into the image.

## Code Reference

| Purpose | Path |
|---------|------|
| Dockerfile | `build/Dockerfile` |
| Build README | `build/README.md` |
| Freqtrade CLI endpoint | `lib/endpoints/freqtrade.py` |
| Execution adapter | `lib/strategy/execution/freqtrade_executor.py` |
| Root dependencies | `requirements.txt` |
| Strategy-local config | `strategies/<family>/engine/freqtrade/config.json` |

## Output Checklist

- [ ] `docker build` succeeds without errors
- [ ] Container dry run passes (all imports OK, paths correct)
- [ ] Backtest run completes in container
- [ ] `requirements.txt` is up to date and pinned
- [ ] Production config.json reviewed (stoploss, max_open_trades, withdrawal=DISABLED)
- [ ] config.ini not baked into image
