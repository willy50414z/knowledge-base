---
name: experiment-compare
description: Compare two Freqtrade backtest stems and emit a KEEP / REVERT / NEED MORE DATA verdict. Use when evaluating whether a strategy change improved performance vs the baseline.
---

# Experiment Compare Skill

Structured comparison of two backtest runs to produce an evidence-based verdict.

## Quick Reference

| Input | Description |
|-------|-------------|
| `baseline_stem` | The stem of the reference run (usually the previous iteration) |
| `candidate_stem` | The stem of the changed run (after the change) |
| `anchor_stem` | The anchor baseline from `hypothesis-log.md` (best OOS-validated version) |
| `family` | Strategy family folder name |

**Always compare against two references**: previous iteration AND anchor baseline.
If candidate beats anchor → update anchor after KEEP verdict.

Output: comparison record at `strategies/<family>/experiments/<YYYYMMDD>-compare-<topic>.md`

---

## Workflow

### Step 1 — Load both run summaries

For each stem, read from `freqtrade/user_data/backtest_results/`:
- `<stem>.meta.json` — strategy name, timerange, config hash
- `<stem>.json` — trade-level results

If the full JSON is too large, use the report zip at `freqtrade/reports/<stem>_<strategy>.zip` instead.
Load summary metrics only — do not load trade-level detail unless diagnosing a specific anomaly.

### Step 2 — Extract key metrics for both runs

| Metric | Baseline | Candidate | Delta |
|--------|---------|-----------|-------|
| Profit Factor | | | |
| Max Drawdown % | | | |
| Win Rate % | | | |
| Sharpe Ratio | | | |
| Sortino Ratio | | | |
| Total Trades | | | |
| Avg Trade Duration | | | |
| OOS Profit Factor (if available) | | | |

### Step 3 — Compute deltas and classify change

For each metric delta:
- **Improvement**: delta is in the desired direction by > 5%
- **Regression**: delta is in the undesired direction by > 5%
- **Neutral**: delta < 5% in either direction

Classify the overall change:
- `CLEAR_WIN`: all primary metrics improved, no regressions
- `TRADE_OFF`: some metrics improved, some regressed — requires explicit acceptance
- `CLEAR_LOSS`: primary metrics regressed
- `NOISE`: no significant delta in either direction

### Step 4 — Verdict

| Verdict | Condition |
|---------|-----------|
| `KEEP` | Classification is CLEAR_WIN, or TRADE_OFF where accepted trade-offs are documented |
| `REVERT` | Classification is CLEAR_LOSS |
| `NEED MORE DATA` | Classification is NOISE (insufficient trades or too short a period to distinguish signal from variance) |
| `REVERT` | OOS Profit Factor dropped below 1.0 regardless of IS results |

### Step 5 — Write comparison record

Write to: `strategies/<family>/experiments/<YYYYMMDD>-compare-<topic>.md`

```markdown
# Experiment Comparison — <topic> — <YYYY-MM-DD>

## Stems
- Baseline: <stem>
- Candidate: <stem>

## Change Tested
<one sentence describing what changed>

## Metrics

| Metric | Baseline | Candidate | Delta | Direction |
|--------|---------|-----------|-------|-----------|
| Profit Factor | | | | |
| Max Drawdown % | | | | |
| Win Rate % | | | | |
| Sharpe | | | | |
| Total Trades | | | | |

## Classification
<CLEAR_WIN | TRADE_OFF | CLEAR_LOSS | NOISE>

## Verdict
**KEEP / REVERT / NEED MORE DATA**

## Rationale
<one paragraph: what the data shows and why this verdict was chosen>

## Accepted Trade-offs (if KEEP with TRADE_OFF)
- <metric> regressed by <X%> — accepted because <reason>

## Next Action
<what to do after this result>
```

### Step 6 — Update hypothesis-log.md

Update the entry for the current hypothesis version with the verdict and link to this comparison record.
