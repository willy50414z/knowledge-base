# Trade Strategy Project Skills

Use this file as the main entry point for repository-specific skills in `trade_strategy`.

## Architecture Direction

Treat this repository as a strategy-centric trading research and execution workspace.

The repository should support:

- many strategy families
- many markdown artifacts for hypothesis, design, review, run history, and performance analysis
- Freqtrade as the current backtest engine
- future expansion to other exchanges, products, execution engines, and external services

## Recommended Repository Layout

Use this structure as the target layout for future work and gradual migration.

```text
trade_strategy/
  lib/
    endpoints/                  # CLI / agent entry points
    client/
      crypto_exchange/          # Exchange and market-data adapters
      execution_engine/         # Backtest/live engine adapters
      notification/             # Telegram or other notification adapters
      storage/                  # S3, DB, artifact storage adapters
    strategy/
      research/                 # Strategy-domain workflows and orchestration
      execution/                # Strategy-to-engine mapping logic
      analytics/                # Performance analysis and review helpers
      registry/                 # Strategy metadata and discovery
    llm_agent/                  # LLM routing and agent integrations
    utils/                      # Shared utilities
  freqtrade/
    strategies/                # Freqtrade strategy implementations
    configs/                   # Engine-specific config templates / overrides
    reports/                   # Generated backtest analysis outputs
  data/
    market/                    # Raw or normalized OHLCV and market data
    features/                  # Derived feature sets
    snapshots/                 # Reproducible dataset snapshots
  strategies/
    <strategy_family>/
      README.md                # Short strategy index
      scope.md                 # Market, timeframe, constraints, success criteria
      hypothesis.md            # Alpha thesis and baselines
      spec.md                  # Entry/exit/risk logic
      implementation.md        # Mapping from spec to engine implementation
      reviews/                 # Review logs and decision records
      experiments/             # Tuning, validation, comparison notes
      reports/                 # Backtest and performance summaries
      sessions/                # User-managed discussion / execution records
      artifacts/               # Strategy-local generated outputs if needed
  knowledge-base/
    skills/
    knowledge/
```

## Planning Principles

- Keep strategy artifacts grouped by strategy family under `strategies/<strategy_family>/`.
- Keep engine-specific code under engine folders such as `freqtrade/`, not mixed into strategy notes.
- Keep reusable Python code in `lib/`, not inside strategy artifact folders.
- Keep generated outputs separate from hand-written specs and reviews.
- Prefer adding a new adapter folder under `lib/client/` when integrating a new external service.
- Keep strategy hypothesis, scope, and design engine-agnostic unless the decision is truly engine-specific.

## Current-State Guidance

- `lib/` remains the shared application/library layer.
- `freqtrade/` remains the active backtest-engine integration.
- `data/` stores local fetched or derived datasets.
- `knowledge-base/` stores reusable skills and supporting documents.
- New strategy-local markdown records should be organized under `strategies/<strategy_family>/` instead of legacy `com/willy/...` paths.
- Prefer `freqtrade/configs/base.json` as the shared Freqtrade base config.
- Prefer `strategies/<strategy_family>/engine/freqtrade/config.json` for strategy-local Freqtrade config.
- Prefer `data/features/` for feature caches and derived market datasets going forward.

## Current Implemented Capabilities

- `lib/endpoints/send_message.py`
  CLI entry point for Telegram message sending.
- `lib/endpoints/call_llm_cli.py`
  CLI entry point for one-shot LLM calls through `lib/llm_agent/llm_svc.py`.
- `lib/endpoints/get_crypto_exchange_data.py`
  CLI entry point for Binance kline retrieval.
- `lib/endpoints/generate_freqtrade_config.py`
  CLI entry point for generating strategy-local Freqtrade config from `freqtrade/configs/base.json`.
- `lib/client/notification/telegram_svc.py`
  Current notification adapter location.
- `lib/client/crypto_exchange/binance_svc.py`
  Current Binance market-data client and feature-cache integration.
- `freqtrade/analyze_backtest_result.py`
  Current report analysis script, now aligned with `freqtrade/reports` and `freqtrade/strategies`.

## Migration Approach

- The recommended skeleton may coexist with current live paths during migration.
- Prefer creating new work in the recommended folders instead of moving active runtime files unless the task explicitly includes migration.
- Do not break current imports or runtime entry points only to satisfy the target layout.
- Migrate one concern at a time: strategy docs first, then engine-specific configs, then reusable code placement.

## Load Order

- Read [agent-general-skills.md](../agent-general-skills.md) first for cross-project standards.
- Then read the project overview skill:
  [trade-strategy-development/SKILL.md](./trade-strategy/trade-strategy-development/SKILL.md)
- Then load only the specific project, domain, or framework skill that matches the task.

## Project-Specific Skills

### Project Overview

- [Trade Strategy Development](./trade-strategy/trade-strategy-development/SKILL.md)
  Repository-level folder, naming, and migration rules.

### Domain Skills

- [Trade Strategy Scope](../domain-skills/trading/trade-strategy-scope/SKILL.md)
- [Trade Strategy Data Validation](../domain-skills/trading/trade-strategy-data-validation/SKILL.md)
- [Trade Strategy Hypothesis Baseline](../domain-skills/trading/trade-strategy-hypothesis-baseline/SKILL.md)
- [Trade Strategy Prototype Design](../domain-skills/trading/trade-strategy-prototype-design/SKILL.md)
- [Trade Strategy Improvement Planning](../domain-skills/trading/trade-strategy-improvement-planning/SKILL.md)
- [ML Workflow](../domain-skills/ml/ml-workflow/SKILL.md)
- [ML Trading Strategy Development](../domain-skills/ml/ml-trading-strategy/SKILL.md)
- [Trading Domain](../domain-skills/trading/trading-domain/SKILL.md)

### Framework Skills

- [Trade Strategy Freqtrade Implementation](../framework-skills/freqtrade/trade-strategy-freqtrade-implementation/SKILL.md)
- [Trade Strategy Backtest Validation](../framework-skills/freqtrade/trade-strategy-backtest-validation/SKILL.md)
- [Trade Strategy Parameter Tuning](../framework-skills/freqtrade/trade-strategy-parameter-tuning/SKILL.md)
- [Trade Strategy Performance Analysis](../framework-skills/freqtrade/trade-strategy-performance-analysis/SKILL.md)

### Supporting Project Skills

- [Strategy Workflow](./trade-strategy/strategy-workflow/SKILL.md)
  Rules for strategy-local markdown artifacts and review placement.
- [ML Consensus Review](./trade-strategy/ml-consensus-review/SKILL.md)
  Multi-agent review workflow tied to this repository's LLM tooling.
- [Code Review MD Export](./trade-strategy/code-review-md-export/SKILL.md)
  Markdown review export workflow for strategy-related review logs and specs.
- [Trade Strategy Deployment Prep](./trade-strategy/trade-strategy-deployment-prep/SKILL.md)
  Deployment constraints that still depend on this repository's runtime setup.

### Related General Skills

- [Documentation Workflow](../general-skills/docs/documentation-workflow/SKILL.md)
  Use when code and markdown need to stay aligned.
- [Markdown Review](../general-skills/docs/markdown-review/SKILL.md)
  Use when reviewing or revising markdown quality directly.

## Selection Guidance

- If the task is repository-wide architecture, folder placement, or migration, start with Trade Strategy Development.
- If the task is strategy hypothesis, spec, or validation logic, start with the matching domain skill.
- If the task is Freqtrade implementation, backtest, hyperopt, or report analysis, start with the matching framework skill.
- If the task is about updating markdown review artifacts tied to a strategy, use Code Review MD Export.
