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
- Strategy status file: `strategies/<family>/STATUS.md`
- Feature data: `data/features/<EXCHANGE>/<MARKET_TYPE>/`

For record placement rules (reports/, experiments/, sessions/, reviews/), see:
→ `knowledge-base/skills/project-skills/trade-strategy/strategy-workflow/SKILL.md`

---

## Agent Session Start Protocol

Before loading any skill, an agent MUST:

1. Read `strategies/<family>/_context_digest.md` if it exists (one read replaces the full cold-start chain).
2. If no digest exists, read `strategies/<family>/STATUS.md` frontmatter to get current phase.
3. Use the phase-gated table below to identify valid skills for this phase.
4. Only then load the relevant skill file(s).

This protocol prevents loading skills that are invalid for the current phase and minimizes cold-start token cost.

---

## Phase-Gated Skill Routing

Read `STATUS.md` phase first. Then load only skills valid for that phase.

| Current phase | Valid primary skills |
|--------------|---------------------|
| `implementation` | `trade-strategy-freqtrade-implementation`, `trade-strategy-data-validation` |
| `backtest` | `freqtrade-analysis-workflow` (Phase 1 only), `data-readiness-check` |
| `analysis` | `freqtrade-analysis-workflow` (Phase 3), `trade-strategy-improvement-planning` |
| `planning` | `trade-strategy-improvement-planning`, `trade-strategy-prototype-design` |
| `new` (no phase yet) | `strategy-bootstrap`, `trade-strategy-scope`, `trade-strategy-hypothesis-baseline` |

When a user request maps to a skill not valid for the current phase, surface the conflict explicitly before acting.

---

## Task → Skill Mapping

Load only the skill(s) that match the current task.

| Task type | Primary skill | Secondary skill |
|-----------|--------------|--------------------|
| New strategy from scratch | `strategy-bootstrap` | `trade-strategy-scope` |
| Strategy hypothesis & baseline | `trade-strategy-hypothesis-baseline` | `trading-domain` |
| Prototype entry/exit/risk spec | `trade-strategy-prototype-design` | `trade-strategy-scope` |
| Freqtrade strategy implementation | `trade-strategy-freqtrade-implementation` | `trade-strategy-data-validation` |
| Running backtest, analyzing results, or hyperopt | `freqtrade-analysis-workflow` | `trade-strategy-improvement-planning` |
| Planning next iteration | `trade-strategy-improvement-planning` | `trade-strategy-prototype-design` |
| ML strategy | `ml-trading-strategy` | `ml-workflow` |
| Fetching or validating market data | `data-pipeline` | `trade-strategy-data-validation` |
| Check data before backtest | `data-readiness-check` | — |
| Inspect strategy code for look-ahead bias | `look-ahead-bias-check` | — |
| Validate OOS results before Planning phase | `oos-validation-gate` | — |
| Validate regime filter calibration | `regime-filter-validation` | — |
| Determine what to do next (any phase) | `strategy-cycle-orchestrator` | — |
| Compare two experiment results | `experiment-compare` | — |
| Extract lessons after iteration | `knowledge-extraction` | — |
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
- [Strategy Workflow](./trade-strategy/strategy-workflow/SKILL.md) — record placement, phase gates (single source of truth)
- [Strategy Cycle Orchestrator](./trade-strategy/strategy-cycle-orchestrator/SKILL.md) — determine current phase and next action; use when unclear what to do next
- [Strategy Bootstrap](./trade-strategy/strategy-bootstrap/SKILL.md) — initialize new strategy family workspace from a raw idea
- [Artifact Triage](./trade-strategy/artifact-triage/SKILL.md) — load minimal context before escalating to large files; reduces cold-start token cost
- [Experiment Compare](./trade-strategy/experiment-compare/SKILL.md) — compare two backtest stems and emit KEEP/REVERT verdict
- [Knowledge Extraction](./trade-strategy/knowledge-extraction/SKILL.md) — distill cross-strategy lessons to knowledge-base after an iteration
- [LLM Orchestration](./trade-strategy/llm-orchestration/SKILL.md) — agent routing, capability table, fallback chain
- [Multi-Agent Consensus](./trade-strategy/multi-agent-consensus/SKILL.md) — structured multi-LLM planning decisions
- [Code Review MD Export](./trade-strategy/code-review-md-export/SKILL.md) — structured multi-LLM review session
- [Trade Strategy Deployment Prep](./trade-strategy/trade-strategy-deployment-prep/SKILL.md) — Docker dry run & deployment checklist

### Framework (Freqtrade — quality gates)
- [Data Readiness Check](../framework-skills/freqtrade/data-readiness-check/SKILL.md) — verify feature data exists and covers a requested timerange before backtest
- [Look-Ahead Bias Check](../framework-skills/freqtrade/look-ahead-bias-check/SKILL.md) — mandatory structural inspection of strategy code for look-ahead bias patterns
- [OOS Validation Gate](../framework-skills/freqtrade/oos-validation-gate/SKILL.md) — hard gate: OOS PF must be ≥ 1.0 before Planning phase is allowed

### Domain
- [Trade Strategy Scope](../domain-skills/trading/trade-strategy-scope/SKILL.md)
- [Trade Strategy Hypothesis Baseline](../domain-skills/trading/trade-strategy-hypothesis-baseline/SKILL.md)
- [Trade Strategy Prototype Design](../domain-skills/trading/trade-strategy-prototype-design/SKILL.md)
- [Trade Strategy Data Validation](../domain-skills/trading/trade-strategy-data-validation/SKILL.md)
- [Trade Strategy Improvement Planning](../domain-skills/trading/trade-strategy-improvement-planning/SKILL.md)
- [Trading Domain](../domain-skills/trading/trading-domain/SKILL.md)
- [Data Pipeline](../domain-skills/trading/data-pipeline/SKILL.md) — fetch / validate / cache
- [Regime Filter Validation](../domain-skills/trading/regime-filter-validation/SKILL.md) — validate regime filter calibration after backtest

### ML
- [ML Workflow](../domain-skills/ml/ml-workflow/SKILL.md)
- [ML Trading Strategy](../domain-skills/ml/ml-trading-strategy/SKILL.md)

### Framework (Freqtrade)
- [Freqtrade Implementation](../framework-skills/freqtrade/trade-strategy-freqtrade-implementation/SKILL.md)
- [Freqtrade Analysis Workflow](../framework-skills/freqtrade/freqtrade-analysis-workflow/SKILL.md) — backtest, validation, analysis, hyperopt

### General
- [Documentation Workflow](../general-skills/docs/documentation-workflow/SKILL.md)
- [Markdown Review](../general-skills/docs/markdown-review/SKILL.md)
