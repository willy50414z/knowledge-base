---
name: trade-strategy-deployment-prep
description: Prepare repository strategies for deployment by checking container parity, dependency completeness, runtime safety, and production config hygiene. Use when a strategy is being promoted from research/backtest into deployable execution.
---

# Trade Strategy Deployment Prep Skill

Prepare the strategy for live trading in a containerized environment (AWS Lambda / Docker).

## Project Standards

- **Relative Paths**: No hardcoded paths allowed (e.g., `E:\code...`). Use `REPO_ROOT` or `os.path.join`.
- **Environment Parity**: Every strategy version MUST pass a **Container Dry Run** before going live.
- **Dockerfile Update**: Ensure `build/Dockerfile` reflects the latest `trade_bot` package structure.

## Required Work

### 1. Container Pre-flight Check (容器預演測試)
- **Dependency Isolation**: Use `pip install -r requirements.txt` inside a clean container to ensure no local libraries are missing.
- **Path Parity**: Run a minimal script in Docker that loads the strategy file. If it fails with `ModuleNotFoundError` or `FileNotFoundError`, it means hardcoded paths or missing imports exist.
- **Timezone Sync**: Verify the strategy handles UTC vs UTC+8 correctly within the container.

### 2. Dependency Audit
- Check `build/requirements.txt` for all custom ML libraries (`xgboost`, `joblib`, `pyecharts`, etc.).
- Ensure version pinning (e.g., `xgboost==2.0.0`) to avoid breaking changes during auto-deployment.

### 3. Risk & API Security
- **Risk Circuit Breaker**: Confirm `stoploss` and `max_open_trades` match the live account risk profile.
- **Log Verification**: Ensure logs do not contain API Keys or sensitive balance info.
- **API Permissions**: Double-check that the API Key in the production `config.json` has `Withdrawal` permissions **DISABLED**.

## Output

- Container test log (success/failure).
- Finalized `requirements.txt`.
- Production-ready `config.json`.
