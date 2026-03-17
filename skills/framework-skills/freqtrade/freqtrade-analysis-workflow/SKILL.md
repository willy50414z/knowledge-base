---
name: freqtrade-analysis-workflow
description: Run, validate, analyze, and tune Freqtrade backtest results in one workflow. Covers backtest execution, OOS validation, performance diagnosis, and hyperopt. Use this instead of the individual backtest-validation, performance-analysis, and parameter-tuning skills.
---

# Freqtrade Analysis Workflow Skill

Covers the full post-implementation loop: backtest → validate → analyze → tune.

## Pre-flight (before starting any phase)

- `strategies/<family>/README.md` is the single source of truth for strategy spec. All work traces back to it.
- `strategies/<family>/STATUS.md` shows the current phase and last backtest stem. Read it first.

---

## Phase 1 — Run Backtest

```bash
python -m lib.endpoints.freqtrade <strategy_family> <StrategyName> <timerange> --mode backtest
```

**Gate — confirm before running:**
- [ ] `strategies/<family>/engine/freqtrade/config.json` is generated (not a template placeholder)
- [ ] `freqtrade/strategies/<StrategyName>.py` exists with no TODO markers
- [ ] `python -m lib.endpoints.freqtrade` does not raise an import error

**After running:**
- Update `STATUS.md`: phase → `analysis`, fill in Last Backtest stem and key metrics.

---

## Phase 2 — Validate Results

| Check | Threshold | Action if breached |
|-------|-----------|-------------------|
| Win Rate > 70% with high trade frequency | Mandatory | Run look-ahead bias check before proceeding |
| OOS profit < 50% of IS profit | Unstable | Do not proceed to hyperopt; revise strategy logic |
| Drawdown recovery > 30 days | Unstable | Revise risk controls |
| Slippage 0.1% makes strategy unprofitable | Fragile | Fix edge quality before proceeding |

---

## Phase 3 — Analyze Performance

```bash
python -m lib.strategy.analytics.analyze_backtest_result
```

Diagnose in this order:
1. **Signal Win Rate vs Trade Win Rate** — if trade WR ≪ signal WR, exit logic is cutting winners early
2. **Gate Filter Funnel** (`dbg_` columns) — check if any filter blocks profitable trades (false positives)
3. **Slippage Sensitivity** — strategy must remain profitable at 0.1% slippage per side

**Gate — required before next iteration:**
Write the analysis summary at: `strategies/<family>/sessions/<YYYYMMDD>-analysis-summary.md`

```markdown
# Analysis Summary — <stem> — <YYYY-MM-DD>

## Key Metrics
- Profit Factor: X.XX
- Max Drawdown: XX%
- Win Rate: XX%
- Sharpe: X.XX
- Slippage 0.1% impact: -X.XX PF

## Top Failure Modes
1. <regime/condition>: <metric impact>
2. <regime/condition>: <metric impact>

## Recommended Focus for Next Iteration
<一到兩句具體建議，指向 README.md 裡的哪個 spec 部分需要更新>
```

Update `STATUS.md`: phase → `planning`.

---

## Phase 4 — Parameter Tuning (Hyperopt)

**Only proceed if:**
- Stable baseline exists (Profit Factor > 1.0 on OOS)
- OOS validation path is defined before tuning begins

```bash
python -m lib.endpoints.freqtrade <family> <StrategyName> <timerange> --mode hyperopt --epochs 200
```

Tuning rules:
- Target **Sortino Ratio** or **Sharpe Ratio** — not raw Total Profit
- Inspect the "Best 10" results: if parameter sets are too diverse, strategy logic is unstable — stop and fix logic first
- Stop tuning if improvements only appear in isolated parameter pockets with no nearby stability zone
- Record tuning results in `strategies/<family>/experiments/<YYYYMMDD>-hyperopt-<topic>.md`
- Re-test final parameters on a clean OOS dataset before accepting

**After tuning:**
Update `STATUS.md`: phase → `planning` (if done) or back to `backtest` (if re-running).

---

## Phase Gate Summary

| Phase | Done when |
|-------|-----------|
| Backtest | `freqtrade/user_data/backtest_results/<stem>.json` exists; STATUS.md updated |
| Validate | All threshold checks passed or documented as accepted risks |
| Analyze | `sessions/<date>-analysis-summary.md` written; STATUS.md → `planning` |
| Hyperopt | Final params OOS-validated; experiment record written |

---

## Code Reference

| Purpose | Path |
|---------|------|
| Run backtest / hyperopt | `lib/endpoints/freqtrade.py` |
| Freqtrade execution adapter | `lib/strategy/execution/freqtrade_executor.py` |
| Backtest result artifacts | `freqtrade/user_data/backtest_results/` |
| Hyperopt results | `freqtrade/user_data/hyperopt_results/` |
| Analysis script | `lib/strategy/analytics/analyze_backtest_result.py` |
| Generated analysis reports | `freqtrade/reports/` |
| Strategy-local experiment records | `strategies/<family>/experiments/` |
| Cross-strategy knowledge | `knowledge-base/knowledge/backtest-records/` |
