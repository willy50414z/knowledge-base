---
name: trade-strategy-parameter-tuning
description: Tune strategy parameters carefully while checking robustness instead of maximizing historical fit.
---

# Trade Strategy Parameter Tuning Skill

Use this skill when the task starts from hyperparameter search, threshold tuning, or rule sensitivity analysis.

## Goal

Improve strategy stability without creating fragile historical overfit.

## Required Work

- tune a limited set of important parameters
- avoid changing too many dimensions at once
- re-check OOS behavior after meaningful changes
- prefer stable parameter regions over sharp optima

## Output

- tuned parameter set
- sensitivity notes
- updated validation result
