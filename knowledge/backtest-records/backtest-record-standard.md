# Backtest Record Standard

Guidelines for accumulating backtest results as reusable knowledge.
Follow this whenever a backtest completes — pass or fail.

---

## Why Record?

A backtest that isn't recorded is knowledge that evaporates. Even failed experiments contain
signal: they narrow the hypothesis space and prevent repeating the same mistakes.

---

## Where to Store

| Record type | Location |
|------------|----------|
| Strategy-level backtest summary | `strategies/<family>/reports/<YYYYMMDD>-<description>.md` |
| Experiment notes (parameter variants) | `strategies/<family>/experiments/<YYYYMMDD>-<description>.md` |
| Long-term lessons (cross-strategy) | `knowledge-base/knowledge/backtest-records/<topic>.md` |
| Raw Freqtrade HTML report | `freqtrade/reports/` (auto-generated, not hand-written) |

---

## Backtest Report Template

Save to `strategies/<family>/reports/<YYYYMMDD>-<run-name>.md`.

```markdown
# Backtest Report — <Strategy Name> — <Date>

## Run Config
- Timerange: YYYYMMDD-YYYYMMDD
- Strategy class: <ClassName>
- Config: strategies/<family>/engine/freqtrade/config.json
- Export: signals / trades

## Key Metrics
| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| Total Profit % | | > 0% | |
| Profit Factor | | > 1.5 | |
| Win Rate | | > 45% | |
| Max Drawdown | | < 20% | |
| Sharpe Ratio | | > 1.0 | |
| Avg Trade Duration | | | |

## OOS Check
- Training period profit: X%
- OOS period profit: Y%
- OOS / Training ratio: Z% (must be > 50%)
- Result: PASS / FAIL

## Signal Quality
- Total signals generated: N
- Signals entering trades: N (X%)
- Blocked by gate filters: N (X%)
- Notable blocked filters: <list dbg_ columns>

## Verdict
PASS / FAIL / CONDITIONAL

Reason: <one sentence>

## Pain Points
- <List specific failure modes observed>

## Next Actions
- [ ] <action 1>
- [ ] <action 2>
```

---

## Experiment Notes Template

Save to `strategies/<family>/experiments/<YYYYMMDD>-<experiment-name>.md`.

```markdown
# Experiment — <Name> — <Date>

## Hypothesis
What change was tested and why.

## Change vs Baseline
- Parameter / logic changed: <describe>
- Previous value: X
- New value: Y

## Result
| Metric | Baseline | This Run | Delta |
|--------|----------|----------|-------|
| Profit Factor | | | |
| Win Rate | | | |
| Max Drawdown | | | |

## Conclusion
BETTER / WORSE / NEUTRAL

Why: <one sentence>

## Decision
Keep / Revert / Investigate further
```

---

## Cross-Strategy Knowledge Accumulation

When a lesson applies beyond one strategy family, record it here in
`knowledge-base/knowledge/backtest-records/`.

Format: `<topic>.md` — free-form, but must include:

1. **Observation** — what was seen across multiple runs
2. **Hypothesis** — why it might be happening
3. **Evidence** — which strategies / runs exhibited this
4. **Rule derived** — the actionable rule going forward

Example file: `knowledge-base/knowledge/backtest-records/high-winrate-bias-pattern.md`

---

## Retention Policy

- Keep all reports in `strategies/<family>/reports/` — they are the audit trail.
- Experiments older than 6 months with a clear REVERT decision can be archived to `strategies/<family>/experiments/archive/`.
- Cross-strategy knowledge files in `knowledge-base/knowledge/backtest-records/` are permanent.
