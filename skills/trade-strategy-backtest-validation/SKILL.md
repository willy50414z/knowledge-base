---
name: trade-strategy-backtest-validation
description: Backtest the strategy, compare it against baselines, and run the required validation checks before further optimization.
---

# Trade Strategy Backtest Validation Skill

Use this skill when the task starts from backtesting, bias checks, or OOS validation.

## Goal

Decide whether the implemented strategy is credible enough to continue.

## Required Work

- run backtests with explicit execution assumptions
- compare results with baselines
- inspect drawdown, trade count, and stability
- run required validation checks
- use `knowledge-base/skills/ml-trading-strategy/SKILL.md` for ML-specific checks

## Output

- backtest summary
- validation result
- go / no-go decision
