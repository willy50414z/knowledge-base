# Trade Strategy Development Skill (Project Master)

Shared development standards for the `binance` repository, ensuring consistent file placement, coding style, and versioning across the trading bot lifecycle.

## 1. Directory Structure Standards

Always place files according to these package boundaries:

- **Core Bot Logic**: `com/willy/trade_bot/`
    - **Freqtrade**: `com/willy/trade_bot/freqtrade/` (Strategies, executors, and analysis tools)
    - **ML Research**: `com/willy/trade_bot/ml/<StrategyName>/` (Each strategy family has its own sub-folder)
    - **Services**: `com/willy/trade_bot/service/` (LLM, data, and exchange services)
    - **Data/DTO**: `com/willy/trade_bot/dto/` and `com/willy/trade_bot/data/`
- **Legacy/Binance Shared**: `com/willy/binance/` (General binance utilities; avoid adding new trading logic here)
- **Knowledge Base**: `knowledge-base/` (Workflow docs and skills)

## 2. Strategy Versioning & Naming

To manage multiple strategies and iterations, follow the `Major_Minor` scheme:

- **Naming Format**: `<StrategyName>_V<Major>_<Minor>_Strategy.py`
    - **Major (大版本)**: Core logic changes (e.g., new indicators, different timeframe, change from Long to Short).
    - **Minor (小版本)**: Parameter optimization (e.g., tweaking MA periods, changing threshold values).
- **Strategy Families**: Group related iterations in the same folder under `trade_bot/freqtrade/strategy/<StrategyName>/`.
- **Class Names**: Must match the filename (e.g., `class AMRS_V4_1_Strategy`).

## 3. Coding Conventions (Code Style)

### Imports
- **Absolute Imports**: Always use `from com.willy.trade_bot...`.
- **No Circulars**: Keep DTOs and Utils independent of Services.

### Path Management (Critical for Containerization)
- **NO Hardcoded Paths**: Never use `E:\code\...` or `C:\Users\...`.
- **Dynamic Roots**: Reference the repo root dynamically:
  ```python
  REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
  ```
- **Config Util**: Use `config_util("project.path").get("root_dir")` for global directory lookups.

### Freqtrade Specifics
- **Auditability**: Include `dbg_` prefixed columns in the strategy dataframe for every intermediate calculation.
- **Self-Contained**: Ensure the strategy can run with only the `config.json` and its local strategy file.

## 4. Workflow Integrity

- **Validation**: Every version bump (Minor or Major) requires a backtest run via `freqtrade_executor.py` and a report via `analyze_backtest_result.py`.
- **Migration Policy**: `com/willy/binance/freqtrade/` is deprecated. Move all active logic to `com/willy/trade_bot/freqtrade/`.
