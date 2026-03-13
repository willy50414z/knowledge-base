# Trade Strategy Improvement Planning Skill

Refine trading strategies based on historical audit results.

## Project Standards

- **Folder Path**: Document improvements in `com/willy/trade_bot/ml/<StrategyName>/improvement_V<Major>.md`.
- **Versioning**: Decide whether to bump the `Major` or `Minor` version based on the planned change.

## Required Work

- Identify the specific regime (e.g., Sideways, High Vol) where the strategy underperforms.
- Formulate a new hypothesis to fix the identified "Pain Point."
- Update the Prototype Design spec before re-implementing.

## General Decision Rules

- Do not propose changes that are not linked to a specific observed weakness or failure mode.
- Do not batch unrelated improvements into one iteration if that would make validation attribution unclear.
- Do not re-implement before the revised hypothesis and prototype changes are written down clearly enough to test.
