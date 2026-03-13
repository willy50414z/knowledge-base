---
name: trade-strategy-data-validation
description: Collect and validate the historical dataset needed for trading strategy research, backtesting, and later deployment.
---

# Trade Strategy Data Validation Skill

Use this skill when the task starts from data collection, data cleanup, or dataset approval.

## Goal

Produce a trustworthy dataset that is suitable for research and validation.

## Required Work

- collect required OHLCV and supporting data
- confirm timeframe and market-type consistency
- inspect missing candles, duplicates, and time continuity
- ensure the dataset spans enough market regimes
- define train, validation, test, and OOS periods

## Output

- approved dataset
- data quality summary
- documented date ranges and splits
