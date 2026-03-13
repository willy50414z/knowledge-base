# Trade Strategy Prototype Design Skill

Formalize trading logic specify before implementation.

## Project Standards

- **Doc Path**: Save the design spec as `com/willy/trade_bot/ml/<StrategyName>/spec_V<Major>.md`.
- **Constraint**: Must explicitly list all `dbg_` columns that will be used for later performance analysis.

## Required Work

- Define Entry/Exit conditions precisely.
- Define **Risk Circuit Breaker**: When should the strategy stop trading?
- Define Regime Filters: (e.g., only trade when ADX > 25).
- List all hyper-parameters to be tuned later.

## General Decision Rules

- Do not implement if the entry, exit, and stop conditions are still ambiguous in plain language.
- Do not proceed if the prototype has no explicit rule for stopping or reducing risk during abnormal behavior.
- Do not mark a parameter as tunable unless its trading meaning is understood well enough to justify why it exists.
