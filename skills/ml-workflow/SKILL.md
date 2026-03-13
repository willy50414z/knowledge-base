# ML Workflow Skill

Treat every model change as both an engineering change and a research change.

## Correctness & Data Integrity

- Check data leakage risk first:
    - target construction
    - lagging
    - normalization fit scope
    - multi-timeframe joins
    - validation split boundaries
- Prefer time-series split or walk-forward style validation over random split.

## Decision Making

- Do not judge model quality by classification metrics alone; check trading impact assumptions.
- When editing `binance_tech_idx_model_trainer.py`, also review:
    - target labeling logic
    - calibration logic
    - threshold selection logic
    - artifact output names
