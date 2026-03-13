---
name: trade-strategy-development
description: Develop a BTC futures trading strategy from research idea to deployable execution using a staged workflow, while delegating ML-specific checks to the existing ml-trading-strategy skill.
---

# Trade Strategy Development Skill

Use this skill when the user wants to design, implement, validate, improve, or operationalize a trading strategy from concept to production readiness.

## Goal

Produce a strategy workflow that moves through these stages in order:

1. define research scope
2. collect and validate data
3. form strategy hypothesis and baselines
4. design the strategy prototype
5. implement the strategy in Freqtrade
6. backtest and validate
7. tune parameters carefully
8. analyze performance
9. plan improvements
10. prepare for deployment

## Rule

- Keep this skill focused on end-to-end workflow control.
- Do not duplicate ML leakage, labeling, walk-forward, or baseline validation details that already belong in `knowledge-base/skills/ml-trading-strategy/SKILL.md`.
- When the strategy uses ML, invoke that skill alongside this one.
- If the task starts from a specific stage instead of a full workflow, prefer the matching step-specific skill under `knowledge-base/skills/trade-strategy-*`.

## Referenced Step Skills

- `trade-strategy-scope`
- `trade-strategy-data-validation`
- `trade-strategy-hypothesis-baseline`
- `trade-strategy-prototype-design`
- `trade-strategy-freqtrade-implementation`
- `trade-strategy-backtest-validation`
- `trade-strategy-parameter-tuning`
- `trade-strategy-performance-analysis`
- `trade-strategy-improvement-planning`
- `trade-strategy-deployment-prep`

## Expected Outcome

The strategy should progress from idea to an auditable, testable, and deployable workflow, with clear go/no-go checks at each stage.
