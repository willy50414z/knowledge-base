# Trade Strategy Parameter Tuning Skill

Optimize strategy parameters without over-fitting.

## Project Standards

- **Tooling**: Use `freqtrade_executor.py` in `hyperopt` mode.
- **Validation**: Tuned parameters must be re-tested on a clean OOS dataset.

## Required Work

- Define searchable spaces for indicators and risk parameters.
- Target **Sortino Ratio** or **Sharpe Ratio** instead of just Total Profit.
- Inspect the "Best 10" results: If they are too diverse, the logic may be unstable.

## General Decision Rules

- Do not start tuning until there is a stable baseline implementation and an approved OOS validation path.
- Stop tuning if improvements appear only in isolated parameter pockets with no nearby stability.
- Treat large variation among top-ranked parameter sets as a sign to re-check strategy logic before expanding the search.
