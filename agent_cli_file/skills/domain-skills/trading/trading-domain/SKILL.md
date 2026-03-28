---
name: trading-domain
description: Apply conservative trading-domain assumptions around costs, slippage, regime shift, and inflated performance claims. Use when reviewing trading logic, backtests, or strategy conclusions that may ignore market realism.
---

# Trading Domain Skill

Assume transaction cost, slippage, and regime shift matter unless explicitly excluded.

## Domain Constraints

- Be conservative about claims of model edge.
- Flag anything that can inflate backtest or validation results.
