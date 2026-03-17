# Trade Strategy Project Skills

> **Quick context** — This is a strategy-centric trading research repo.
> Active engine: Freqtrade (backtest). Data source: Binance (futures & spot).
> Strategy artifacts live in `strategies/<family>/`. Code lives in `lib/`. Engine integration in `freqtrade/`.

---

## Implemented Code — Load Before Modifying

| Module | Path |
|--------|------|
| Freqtrade executor | `lib/strategy/execution/freqtrade_executor.py` |
| Backtest analysis | `lib/strategy/analytics/analyze_backtest_result.py` |
| Freqtrade CLI endpoint | `lib/endpoints/freqtrade.py` |
| Freqtrade config generator | `lib/endpoints/generate_freqtrade_config.py` |
| Binance market data | `lib/client/crypto_exchange/binance_svc.py` |
| Feature file persistence | `lib/storage/feature_store.py` |
| Technical indicators | `lib/ohlcv_data_handler/tech_idx_svc.py` |
| ML utilities | `lib/ml/ml_svc.py` |
| Telegram notification | `lib/client/notification/telegram_svc.py` |
| LLM routing | `lib/llm_agent/llm_svc.py` |

Key config paths:
- Shared Freqtrade base config: `freqtrade/configs/base.json`
- Strategy-local Freqtrade config: `strategies/<family>/engine/freqtrade/config.json`
- Feature data: `data/features/<EXCHANGE>/<MARKET_TYPE>/`

For record placement rules (reports/, experiments/, sessions/, reviews/), see:
→ `knowledge-base/skills/project-skills/trade-strategy/strategy-workflow/SKILL.md`

---

## Task → Skill Mapping

Load only the skill(s) that match the current task.

| Task type | Primary skill | Secondary skill |
|-----------|--------------|-----------------|
| New strategy from scratch | `trade-strategy-scope` | `trade-strategy-hypothesis-baseline` |
| Strategy hypothesis & baseline | `trade-strategy-hypothesis-baseline` | `trading-domain` |
| Prototype entry/exit/risk spec | `trade-strategy-prototype-design` | `trade-strategy-scope` |
| Freqtrade strategy implementation | `trade-strategy-freqtrade-implementation` | `trade-strategy-data-validation` |
| Running backtest or hyperopt | `trade-strategy-backtest-validation` | `trade-strategy-parameter-tuning` |
| Analyzing backtest HTML report | `trade-strategy-performance-analysis` | `trade-strategy-improvement-planning` |
| Planning next iteration | `trade-strategy-improvement-planning` | `trade-strategy-prototype-design` |
| ML strategy | `ml-trading-strategy` | `ml-workflow` |
| Fetching or validating market data | `data-pipeline` | `trade-strategy-data-validation` |
| Multi-agent / LLM task routing | `llm-orchestration` | — |
| Major strategy decision needing multi-LLM input | `multi-agent-consensus` | `llm-orchestration` |
| Multi-LLM code / spec review session | `code-review-md-export` | — |
| Repo structure / file placement | `trade-strategy-development` | — |
| Strategy markdown artifacts | `strategy-workflow` | — |
| Deployment checklist | `trade-strategy-deployment-prep` | — |
| Code review export to markdown | `code-review-md-export` | — |

---

## Skill Index

### Project
- [Trade Strategy Development](./trade-strategy/trade-strategy-development/SKILL.md) — folder/naming rules
- [Strategy Workflow](./trade-strategy/strategy-workflow/SKILL.md) — record placement (single source of truth)
- [LLM Orchestration](./trade-strategy/llm-orchestration/SKILL.md) — agent routing, capability table, fallback chain
- [Multi-Agent Consensus](./trade-strategy/multi-agent-consensus/SKILL.md) — structured multi-LLM planning decisions
- [Code Review MD Export](./trade-strategy/code-review-md-export/SKILL.md) — structured multi-LLM review session
- [Trade Strategy Deployment Prep](./trade-strategy/trade-strategy-deployment-prep/SKILL.md) — Docker dry run & deployment checklist

### Domain
- [Trade Strategy Scope](../domain-skills/trading/trade-strategy-scope/SKILL.md)
- [Trade Strategy Hypothesis Baseline](../domain-skills/trading/trade-strategy-hypothesis-baseline/SKILL.md)
- [Trade Strategy Prototype Design](../domain-skills/trading/trade-strategy-prototype-design/SKILL.md)
- [Trade Strategy Data Validation](../domain-skills/trading/trade-strategy-data-validation/SKILL.md)
- [Trade Strategy Improvement Planning](../domain-skills/trading/trade-strategy-improvement-planning/SKILL.md)
- [Trading Domain](../domain-skills/trading/trading-domain/SKILL.md)
- [Data Pipeline](../domain-skills/trading/data-pipeline/SKILL.md) — fetch / validate / cache
- [ML Workflow](../domain-skills/ml/ml-workflow/SKILL.md)
- [ML Trading Strategy](../domain-skills/ml/ml-trading-strategy/SKILL.md)

### Framework (Freqtrade)
- [Freqtrade Implementation](../framework-skills/freqtrade/trade-strategy-freqtrade-implementation/SKILL.md)
- [Backtest Validation](../framework-skills/freqtrade/trade-strategy-backtest-validation/SKILL.md)
- [Parameter Tuning](../framework-skills/freqtrade/trade-strategy-parameter-tuning/SKILL.md)
- [Performance Analysis](../framework-skills/freqtrade/trade-strategy-performance-analysis/SKILL.md)

### General
- [Documentation Workflow](../general-skills/docs/documentation-workflow/SKILL.md)
- [Markdown Review](../general-skills/docs/markdown-review/SKILL.md)
