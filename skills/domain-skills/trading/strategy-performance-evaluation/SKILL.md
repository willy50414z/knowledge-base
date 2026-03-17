---
name: strategy-performance-evaluation
description: Professional-grade evaluation framework for crypto perpetual futures backtests (Freqtrade / Binance Futures). Produces a deterministic REJECT/BORDERLINE/PROMISING tier verdict and a KEEP/REVERT/NEED MORE DATA decision from raw backtest metrics. Use when an agent must score a strategy after a backtest or OOS run, or when deciding whether to promote or discard a strategy iteration.
---

# Strategy Performance Evaluation Framework

Applies objective, numeric standards to crypto perpetual futures backtest results (Freqtrade engine, Binance Futures). Every threshold is a specific number — not a range or qualitative descriptor. When the user or a calling skill refers to a KEEP/REVERT decision, this is the authoritative source for that decision logic.

---

## Quick Reference — 3-Tier Verdict Table

Evaluate top-down. Assign the first tier whose conditions are satisfied. Do not skip tiers.

| Tier | Agent action | Condition logic |
|------|-------------|-----------------|
| **REJECT** | REVERT — return to implementation | Any single REJECT trigger (R-codes) fires |
| **BORDERLINE** | NEED MORE DATA — fix listed items and re-backtest | No REJECT triggers; any single BORDERLINE trigger (B-codes) fires |
| **PROMISING** | KEEP — proceed to planning phase | All PROMISING floors met; zero REJECT or BORDERLINE triggers |

---

## Section 1 — REJECT Triggers

Any one of the following fires → Tier = REJECT. Record the trigger code in the verdict output.

| Code | Condition | Notes |
|------|-----------|-------|
| R1 | OOS Profit Factor < 1.0 | Strategy loses money on unseen data |
| R2 | IS Profit Factor < 1.1 | No detectable edge even in-sample |
| R3 | Max Drawdown > 40% | Capital-destruction risk |
| R4 | Sharpe Ratio (annualised) < 0.5 | Return per unit of risk is sub-institutional |
| R5 | Total IS trades < 100 | Statistical basis does not exist |
| R6 | Strategy unprofitable after 0.1% slippage per side | Edge does not survive minimum production cost |
| R7 | Look-ahead bias detected (structural) | Result is invalid — not a performance question |
| R8 | Win Rate < 35% AND Profit Factor < 1.3 simultaneously | Thin edge combined with poor hit rate — not survivable live |
| R9 | IS PF > 5.0 with fewer than 300 IS trades | Near-certain curve fit; block regardless of OOS appearance |
| R10 | Win Rate > 80% | Almost always exit logic reading same-candle close (look-ahead) |
| R11 | Top 1 trade accounts for > 20% of total profit | Single-event dependency, not a systematic edge |
| R12 | OOS period < 60 calendar days | Too short to cover even one market sub-phase |
| R13 | Backtest uses 0% slippage AND 0% fees | Results are not production-representative; re-run required |

---

## Section 2 — BORDERLINE Triggers

No REJECT present and any one fires → Tier = BORDERLINE. List ALL triggered codes in verdict; each has a required fix.

| Code | Condition | Required fix |
|------|-----------|-------------|
| B1 | OOS trade count < 30 | Extend backtest period before re-evaluating |
| B2 | OOS/IS Profit Factor ratio < 0.5 | Reduce parameter count; rerun hyperopt with fewer free parameters |
| B3 | Max Drawdown 25–40% | Improve position sizing or add drawdown guard; re-backtest |
| B4 | IS Profit Factor 1.1–1.3 | Signal quality is thin; investigate entry signal before tuning |
| B5 | Sharpe (annualised) 0.5–0.8 | Risk-adjusted return is marginal; not yet deployable |
| B6 | Equity curve R² < 0.85 | Non-linear growth pattern detected; see Section 6 |
| B7 | Total backtest period < 18 months | Extend data coverage; single regime is insufficient |
| B8 | Longest drawdown duration > 60 calendar days | Recovery too slow for any reasonable capital allocation |
| B9 | > 60% of profit from one calendar quarter | Regime concentration; extend or decompose by regime |
| B10 | OOS/IS ratio 0.5–0.7 | Moderate degradation; iteration plan must address overfitting |
| B11 | Parameter at or near search-space boundary | Optimizer hit a wall; re-run with extended search space |
| B12 | Losing in exactly one regime without documented exclusion | Add regime filter or document the exclusion in strategy spec |
| B13 | Weekend Sharpe < weekday Sharpe by > 30% | Strategy has weekend liquidity sensitivity; validate or restrict hours |
| B14 | Top 5% of trades account for > 50% of total profit | Profit concentrated in outlier events; not a repeatable edge |
| B15 | Best single calendar month removed drops PF below 1.0 | Edge depends on one period; not durable |

---

## Section 3 — PROMISING Floors

ALL conditions must hold simultaneously. Any failure triggers BORDERLINE or REJECT as appropriate.

| Metric | Minimum floor | Strong signal |
|--------|--------------|---------------|
| IS Profit Factor | ≥ 1.4 | ≥ 1.8 |
| OOS Profit Factor | ≥ 1.1 | ≥ 1.4 |
| OOS/IS PF ratio | ≥ 0.5 | ≥ 0.7 |
| Sharpe Ratio (annualised, OOS) | ≥ 0.8 | ≥ 1.5 |
| Sortino Ratio (annualised, OOS) | ≥ 1.0 | ≥ 2.0 |
| Calmar Ratio (OOS) | ≥ 0.5 | ≥ 1.0 |
| Max Drawdown | ≤ 25% | ≤ 15% |
| Win Rate | ≥ 40% | ≥ 52% |
| Total IS trades | ≥ 150 | ≥ 300 |
| OOS trade count | ≥ 30 | ≥ 60 |
| Total backtest period | ≥ 18 months | ≥ 30 months |
| Equity curve R² | ≥ 0.85 | ≥ 0.93 |
| Regime coverage | 3 of 4 regimes profitable | 4 of 4 profitable |

---

## Section 4 — Primary Metrics Detail

### 4.1 Profit Factor

Gross profit divided by gross loss. Primary gating metric. Evaluate IS and OOS separately.

| Level | IS | OOS |
|-------|----|-----|
| REJECT | < 1.1 | < 1.0 |
| BORDERLINE | 1.1–1.3 | 1.0–1.1 |
| Minimum viable (PROMISING floor) | 1.4 | 1.1 |
| Strong signal | ≥ 1.8 | ≥ 1.4 |
| Suspiciously high — flag overfitting | > 5.0 (< 300 trades) | > 2.5 with OOS < 1.3 |

A PF above 3.0 in IS with fewer than 200 trades is near-certain curve fit. Flag R9 regardless of OOS appearance.

### 4.2 Sharpe Ratio (annualised)

Annualise using 365-day base (crypto trades 24/7). Freqtrade uses 365 by default — confirm before comparing to external benchmarks using 252.

| Level | OOS threshold |
|-------|---------------|
| REJECT | < 0.5 |
| BORDERLINE | 0.5–0.8 |
| Minimum viable | 0.8 |
| Strong | ≥ 1.5 |
| Suspiciously high | > 3.0 on < 200 OOS trades |

A crypto Sharpe of 0.9 is roughly equivalent to an equity Sharpe of 1.2 given the 3–5x volatility differential. Do not compare directly to equity benchmarks.

### 4.3 Sortino Ratio (annualised)

Penalises downside deviation only. Preferred primary risk metric for momentum and breakout strategies with asymmetric return distributions.

| Level | OOS threshold |
|-------|---------------|
| REJECT (implicit via Sharpe gate) | — |
| Minimum viable | ≥ 1.0 |
| Strong | ≥ 2.0 |

Sortino should always exceed Sharpe by at least 10%. If Sortino < Sharpe, the strategy has more upside than downside volatility — verify trade-level P&L distribution for data integrity issues.

### 4.4 Calmar Ratio

Annualised return divided by max drawdown. Measures return per unit of drawdown risk.

| Level | OOS threshold |
|-------|---------------|
| Minimum viable | ≥ 0.5 |
| Strong | ≥ 1.0 |

Crypto Calmar of 0.5 is approximately equivalent to equities Calmar of 1.0 given vol differential.

### 4.5 Max Drawdown

Peak-to-trough equity decline as reported by Freqtrade (closed-trade equity basis).

| Level | Threshold |
|-------|-----------|
| REJECT | > 40% |
| BORDERLINE | 25–40% |
| Minimum viable | ≤ 25% |
| Strong | ≤ 15% |

Apply a 1.5x live stress multiplier for deployment sizing: a 20% OOS drawdown should be budgeted as 30% in live. Also check **drawdown duration**: max acceptable time from peak to full recovery is 60 calendar days. Flag B8 if exceeded.

### 4.6 Win Rate

Evaluate in context of average Risk:Reward ratio. Win rate alone is not a gating condition.

| Avg R:R | Minimum Win Rate | Promising |
|---------|-----------------|-----------|
| 0.5:1 | 70% | > 75% |
| 1.0:1 | 40% | > 50% |
| 1.5:1 | 35% | > 45% |
| 2.0:1 | 30% | > 40% |
| 3.0:1 | 25% | > 35% |

A win rate below 30% is flagged for any R:R — losing streaks become psychologically unsurvivable and execution variance has outsized impact. Apply R8 when WR < 35% AND PF < 1.3 simultaneously.

### 4.7 Average Risk:Reward Ratio

Average win size divided by average loss size per trade.

| Level | Threshold |
|-------|-----------|
| REJECT-adjacent | < 0.5 |
| Marginal | 0.5–0.8 |
| Acceptable | 0.8–1.2 |
| Promising | 1.2–2.0 |
| Strong | > 2.0 |

An R:R above 3.0 with Win Rate above 55% at > 200 trades is statistically implausible — flag as potential look-ahead bias.

### 4.8 Recovery Factor

Total net profit divided by max drawdown (same units). Measures how many times the strategy earns back its worst loss.

| Level | OOS threshold |
|-------|---------------|
| Minimum viable | ≥ 1.0 |
| Promising | ≥ 2.0 |
| Strong | > 4.0 |

---

## Section 5 — Risk-Adjusted vs Absolute Return Priority

In crypto, raw return % is not a reliable evaluation signal because bull markets inflate returns independent of edge, leverage amplifies noise as much as signal, and drawdowns can be catastrophic with aggressive sizing.

**Priority order for all gating decisions:**

1. OOS Profit Factor — primary gate (R1). Measures edge persistence on unseen data.
2. Sortino Ratio — primary risk-adjusted metric. Penalises downside volatility specifically.
3. Max Drawdown — capital preservation hard ceiling.
4. Sharpe Ratio — secondary risk-adjusted metric. Tiebreaker between similar candidates.
5. Calmar Ratio — supplementary context for deployment sizing.
6. Total Return % — informational only. Never used as a gating condition.
7. CAGR — informational only. Useful for sizing context but not pass/fail.

Do not optimise hyperopt for Total Profit or CAGR. Use Sortino or Sharpe as the hyperopt objective (see `freqtrade-analysis-workflow` skill).

---

## Section 6 — OOS Validation Standards

### 6.1 IS/OOS Split Requirements

| Parameter | Standard | Notes |
|-----------|---------|-------|
| Minimum IS period | 12 months | Must include at least one Bull and one Bear quarter |
| Minimum OOS period | 6 months | Must be strictly later in time than IS (walk-forward) |
| OOS as % of total period | 25–33% | Random splits are invalid for time-series strategies |
| OOS must be defined | Before any hyperopt run | Post-hoc OOS designation is treated as IS |

### 6.2 Acceptable IS-to-OOS Degradation

| OOS/IS PF ratio | Verdict |
|----------------|---------|
| > 0.90 | Excellent generalisation — proceed |
| 0.70–0.90 | Acceptable degradation — proceed |
| 0.50–0.70 | BORDERLINE (B10) — iteration plan must explicitly address overfitting |
| 0.30–0.50 | BORDERLINE (B2) — reduce parameter count before next run |
| < 0.30 | REJECT — rebuild signal logic |

Apply the same ratio to Sharpe: OOS Sharpe / IS Sharpe must be > 0.4. Below 0.4 is a second independent overfitting signal (flag B2 if present).

### 6.3 Minimum OOS Trade Count and Confidence

| OOS trade count | Confidence | Action |
|-----------------|-----------|--------|
| > 200 | PF reliable to ± 0.05 | Full confidence |
| 100–200 | PF reliable to ± 0.1 | Full confidence |
| 50–100 | PF reliable to ± 0.2 | Acceptable |
| 30–49 | PF reliable to ± 0.3 | Acceptable; note limited confidence |
| < 30 | PF unreliable | BORDERLINE B1 — extend period |

When evaluating results near the PROMISING floor, use the lower bound of the confidence interval: a PF of 1.2 with 35 OOS trades should be treated as PF 0.9 (1.2 − 0.3).

### 6.4 Walk-Forward Validation (Recommended After Hyperopt)

If the strategy has been hyperopt-tuned, run a rolling walk-forward: 12-month IS window, 3-month OOS step, minimum 4 folds. Accept only if ≥ 3 of 4 folds show OOS PF ≥ 1.0. Fewer than 3 profitable folds → flag B2.

### 6.5 Secondary Overfitting Signals

Flag all of the following as independent overfitting indicators regardless of OOS/IS ratio:

- **Parameter density**: more than 1 free parameter per 50 IS trades is over-parameterized (8 parameters on 150 trades = disqualifying; 8 on 400 trades = borderline).
- **Hyperopt stability**: run hyperopt twice with different random seeds. If top-1 PF differs by > 15%, the optimization surface is too rough — flag B2.
- **Parameter cliff**: vary any single parameter ±10% from optimal. If PF drops below 1.0 with any single move, the strategy is curve-fit to that value — flag B11.
- **Profit concentration**: top 5% of trades accounting for > 50% of profit → flag B14.
- **Best-period dependency**: removing the best calendar month drops PF below 1.0 → flag B15.

---

## Section 7 — Backtest Period and Time-Weighting

### 7.1 Minimum Period Requirements

| Parameter | Minimum | Strong |
|-----------|---------|--------|
| Total backtest period | 18 months | 30 months |
| IS period | 12 months | 24 months |
| OOS period | 6 months | 12 months |
| Regime coverage required | Bull + Bear + at least one Crab | All four regime types |

A backtest covering only a bull market is not PROMISING regardless of metrics. The regime coverage check is mandatory.

### 7.2 Regime Classification (Four-Regime Model)

Evaluate separately across all four regimes using BTC as the market proxy.

| Regime | Definition |
|--------|-----------|
| Bull trending | BTC price > 20-week SMA, ADX > 25, net monthly direction positive over 2+ months |
| Bear trending | BTC price < 20-week SMA, ADX > 25, net monthly direction negative over 2+ months |
| Sideways low-vol | ADX < 20, ATR% below 30-day median |
| Sideways high-vol | ADX < 25, ATR% above 30-day median (choppy with wide swings) |

### 7.3 Per-Regime Thresholds

| Regime | Min trades | Minimum PF to be "covered" | Notes |
|--------|-----------|--------------------------|-------|
| Bull trending | 20 | 1.0 | Modest loss acceptable if strategy is documented short-only |
| Bear trending | 20 | 1.0 | Modest loss acceptable if strategy is documented long-only |
| Sideways low-vol | 15 | 1.0 | |
| Sideways high-vol | 15 | 1.0 | |

Losing in 2 or more regimes → REJECT regardless of aggregate metrics. Losing in exactly 1 regime without a documented exclusion → BORDERLINE B12.

A strategy may explicitly exclude one regime. The exclusion must appear in the strategy spec. An excluded regime must show near-zero trade count, not a losing trade sequence.

### 7.4 Recent Performance Weighting

When sub-dividing IS performance for recency checks, apply:

```
Weighted_PF = (PF_last_6_months × 2 + PF_prior_period × 1) / 3
```

If Weighted_PF < 1.2 while full-IS PF ≥ 1.4, the strategy may be decaying. Flag B9 and investigate recent regime shift before proceeding.

---

## Section 8 — Equity Curve Quality

### 8.1 Linearity (R² of equity curve)

Fit a linear regression to the cumulative equity curve (equity value vs calendar day index).

| R² | Interpretation |
|----|---------------|
| ≥ 0.93 | Highly linear — consistent edge across regimes (strong signal) |
| 0.85–0.92 | Acceptable linearity — minor inconsistency |
| < 0.85 | Non-linear — regime-dependent or curve-fit → BORDERLINE B6 |

Qualitative override of R²: if R² > 0.95 but the curve shows 2–3 very steep climbs separated by flat or declining periods, the strategy is episodically profitable rather than consistently edged. This is a curve-fit pattern regardless of the R² number.

### 8.2 Drawdown Clustering

A healthy strategy distributes drawdowns across time. Clustering indicates fragility.

Clustering test:
1. Identify all drawdown events > 5% peak-to-trough.
2. Calculate what fraction of all drawdown events fall within any single 90-day window.
3. If > 50% cluster in one 90-day window → flag BORDERLINE B9 (same fix: extend or decompose by regime).

### 8.3 Win/Loss Streak Analysis

| Metric | Acceptable | Flag |
|--------|-----------|------|
| Max consecutive losses | ≤ 10 | > 15 → BORDERLINE |
| Max consecutive wins | — | > 20 → check for data issue or look-ahead bias |
| Average losing streak length | ≤ 5 | > 8 sustained → indicates fragile edge |

### 8.4 Monthly Return Distribution

| Property | Healthy | Flag |
|----------|---------|------|
| Profitable months % | ≥ 60% | < 50% → BORDERLINE |
| Worst single month drawdown | ≤ 15% | > 20% → BORDERLINE |
| Monthly return CV across quarters | Consistent | CV > 1.5 → high instability flag |

### 8.5 Healthy vs Curve-Fit Equity Curve — Diagnostic Checklist

Healthy curve characteristics:
- Roughly linear growth with minor oscillation (R² ≥ 0.85)
- Drawdowns spread across multiple market regimes
- Performance in bull, bear, and crab periods is within a 2× factor of each other
- No single month accounts for > 30% of total profit
- No single trade accounts for > 10% of total profit

Curve-fit curve characteristics:
- Parabolic shape (equity accelerating toward end of IS period)
- One or two "lucky" periods account for > 50% of total profit
- Flat or declining equity in OOS that was not visible in IS period
- Very high IS PF (> 2.5) with OOS PF below 1.3
- Equity curve looks smooth only because trades cluster in one favourable regime

---

## Section 9 — Crypto-Specific Adjustments

### 9.1 Fee Modeling Requirements

Standard Binance Futures fees:
- Maker: 0.02% per side
- Taker: 0.04% per side
- Minimum modeled fee in backtest: 0.05% per side (0.1% total round-trip as conservative floor)

If the backtest uses 0% fees → fire R13. If the backtest uses fees but < 0.05% per side → flag BORDERLINE and rerun.

### 9.2 Slippage Standards

| Position size vs 24h pair volume | Slippage assumption | Gate |
|----------------------------------|---------------------|------|
| < 0.1% of ADV | 0.05% per side | Must be profitable at this level |
| 0.1–1% of ADV | 0.15% per side | Retest; flag BORDERLINE if fails |
| > 1% of ADV | 0.3%+ per side | Strategy is not scalable at this size; document |

Hard gate R6: strategy must remain PF ≥ 1.0 after applying 0.1% slippage per side. This is the minimum production assumption for Binance Futures mid-cap pairs.

Do not backtest on pairs with < $10M average daily volume on Binance Futures. For pairs with ADV $10M–$50M, increase slippage assumption by 0.05% per side.

### 9.3 Funding Rate Drag

Perpetual futures funding is charged every 8 hours. For strategies holding positions longer than 8 hours:

| Avg funding rate | Annual drag | Adjustment |
|-----------------|-------------|-----------|
| 0.01% per 8h (neutral) | ~11% annually | Subtract from expected return |
| 0.03% per 8h (hot bull) | ~33% annually | Subtract; rerun if adjusted PF drops below floor |
| < 0.005% per 8h | ~5.5% annually | Minimal; flag but not blocking |

Standard assumption when funding data unavailable: 0.01% per 8h for long-biased strategies; 0% for market-neutral.

If Freqtrade does not model funding rates, apply post-hoc: subtract estimated annual drag from total return before computing PF. If adjusted PF drops below the PROMISING floor, downgrade tier.

If average trade duration > 24 hours, subtract 0.03%–0.09% per trade from raw PF before evaluation.

### 9.4 Annualisation Base

Use 365 days (not 252). Crypto trades every day including weekends and holidays. Confirm Freqtrade config uses 365 before comparing annualised metrics to any external benchmark using 252.

### 9.5 Regime Shift Risk

| Check | Method | Threshold |
|-------|--------|-----------|
| Bear regime performance | Subset backtest to bear quarters | PF must be ≥ 1.0 |
| Crab regime performance | Subset to sideways quarters | PF must be ≥ 1.0 |
| Bull vs Bear PF ratio | IS Bull PF / IS Bear PF | Ratio > 3.0 → flag B12 (bull-dependent strategy) |

A strategy that only works in a bull regime is levered beta, not a systematic edge. Mark as BORDERLINE unless the strategy explicitly documents itself as bull-regime-only with a calibrated regime filter.

### 9.6 24/7 Market Structure Effects

- No overnight gap risk: strategies that benefit from equity gap dynamics in backtests do not receive that benefit here.
- Weekend liquidity: BTC and altcoin liquidity drops 20–40% on weekends. Flag B13 if weekend Sharpe is more than 30% below weekday Sharpe.
- Funding as regime signal: extreme funding rates (> 0.05% per 8h or < -0.01% per 8h) are market regime signals, not just cost items. A strategy that ignores extreme funding is missing a regime filter opportunity.
- Liquidation cascades: test the strategy across at least one major liquidation event (e.g., May 2021, November 2022). Pure trend-following strategies are vulnerable during cascade reversals.

### 9.7 Leverage Adjustment

Standard evaluation assumes 1× leverage. If the strategy uses leverage:
- Report all drawdown metrics on leveraged equity, not notional.
- Apply leverage multiplier to slippage and funding drag before evaluation.
- Max Drawdown threshold tightens by leverage factor: at 3× leverage, the 25% PROMISING floor becomes 8% on the leveraged equity curve.

### 9.8 Altcoin-Specific Adjustments

If the strategy trades altcoin futures (not BTC/ETH):
- Add 0.02% per side spread premium to modeled fees (altcoin spread is wider than BTC).
- IS period must include at least one BTC-dominant drawdown period (altcoins typically drop 1.5–3× BTC during deleveraging).
- All minimum trade count requirements increase by 50% (altcoin trade distributions are more heavy-tailed).

---

## Section 10 — Evaluation Workflow

Agents must follow this exact sequence:

```
Step 1 — Extract metrics
  IS PF, OOS PF, IS trades, OOS trades, Sharpe, Sortino, Calmar, Max DD, Win Rate,
  Avg R:R, Recovery Factor, equity curve R², monthly return distribution

Step 2 — Check REJECT triggers (R1–R13)
  IF any trigger fires → Tier = REJECT
  Stop; write verdict with the specific R-codes

Step 3 — Check BORDERLINE triggers (B1–B15)
  IF any trigger fires → Tier = BORDERLINE
  List ALL triggered B-codes; each requires its specific fix action

Step 4 — Check PROMISING floors (Section 3)
  ALL floors must be met simultaneously
  IF all met → Tier = PROMISING

Step 5 — Apply crypto-specific adjustments (Section 9)
  Funding drag adjustment applied?
  Slippage retest at 0.1% per side passed?
  Regime subset check (bear + crab must each be PF ≥ 1.0)?
  Annualisation base confirmed as 365?

Step 6 — Emit verdict (use format in Section 10.1)
```

### 10.1 Verdict Output Format

```markdown
## Performance Evaluation Verdict

**Tier**: REJECT | BORDERLINE | PROMISING
**Decision**: KEEP | REVERT | NEED MORE DATA

### Triggered Codes
- <R# or B#>: <metric value> vs threshold <threshold>

### Metric Scorecard

#### Statistical Gate
- IS Trade Count: N → [PASS / INSUFFICIENT]
- OOS Trade Count: N → [PASS / INSUFFICIENT]

#### Core Metrics (OOS unless noted)
| Metric | Value | Floor | Status |
|--------|-------|-------|--------|
| IS Profit Factor | X.XX | ≥ 1.4 | PASS/FAIL |
| OOS Profit Factor | X.XX | ≥ 1.1 | PASS/FAIL |
| OOS/IS PF Ratio | X.XX | ≥ 0.5 | PASS/FAIL |
| Sharpe (annualised) | X.XX | ≥ 0.8 | PASS/FAIL |
| Sortino (annualised) | X.XX | ≥ 1.0 | PASS/FAIL |
| Calmar | X.XX | ≥ 0.5 | PASS/FAIL |
| Max Drawdown | XX% | ≤ 25% | PASS/FAIL |
| Drawdown Duration | N days | ≤ 60 | PASS/FAIL |
| Win Rate | XX% | ≥ 40% | PASS/FAIL |
| Avg R:R | X.XX | ≥ 0.8 | PASS/FAIL |
| Recovery Factor | X.XX | ≥ 1.0 | PASS/FAIL |
| Equity Curve R² | X.XX | ≥ 0.85 | PASS/FAIL |
| Profitable Months % | XX% | ≥ 60% | PASS/FAIL |

#### Overfitting Check
- OOS/IS PF Ratio: X.XX → [PASS / WARN / BLOCK]
- OOS/IS Sharpe Ratio: X.XX → [PASS / WARN / BLOCK]
- Parameter density: N params / N IS trades → [OK / WARN]

#### Regime Coverage
- Bull trending: PF X.XX, N trades → [PASS / FAIL / EXCLUDED]
- Bear trending: PF X.XX, N trades → [PASS / FAIL / EXCLUDED]
- Sideways low-vol: PF X.XX, N trades → [PASS / FAIL / EXCLUDED]
- Sideways high-vol: PF X.XX, N trades → [PASS / FAIL / EXCLUDED]

#### Crypto-Specific Checks
- Fee model: X.XX% per side → [ADEQUATE / INSUFFICIENT]
- Slippage at 0.1%/side: PF = X.XX → [PASS / FAIL]
- Funding drag applied: YES/NO — adjusted PF: X.XX
- Annualisation base: [365 / OTHER]
- Regime coverage: Bull YES/NO | Bear YES/NO | Crab YES/NO

### Rationale
<one paragraph explaining the verdict>

### Required Actions (BORDERLINE only)
1. B#: <specific fix>
2. B#: <specific fix>
```

### 10.2 Decision Mapping

| Tier | Decision | Next step |
|------|----------|-----------|
| PROMISING | KEEP | Proceed to planning phase |
| BORDERLINE | NEED MORE DATA | Fix all listed B-codes; re-backtest before deciding |
| REJECT | REVERT | Return to implementation; do not write an iteration plan |

---

## Section 11 — Integration with Other Skills

| Condition | Skill to use |
|-----------|-------------|
| OOS gate only (quick check) | `oos-validation-gate` — simpler hard gate |
| Full tier verdict (this skill) | `strategy-performance-evaluation` |
| Comparing two experiments | `experiment-compare` — uses this skill's thresholds |
| Regime filter calibration | `regime-filter-validation` |
| Structural look-ahead check | `look-ahead-bias-check` — run before this skill |
| After PROMISING verdict | `trade-strategy-improvement-planning` |
| After REJECT verdict | `trade-strategy-freqtrade-implementation` |
| Full backtest → analyse loop | `freqtrade-analysis-workflow` — orchestrates all steps |

---

## Appendix — Threshold Derivation Rationale

| Threshold | Rationale |
|-----------|-----------|
| IS PF ≥ 1.4 | Below 1.4 the edge does not survive slippage + funding drag in live trading |
| OOS PF ≥ 1.1 | Minimum to remain profitable after live execution costs (0.1% slippage + fees) |
| OOS/IS ≥ 0.5 | Below 50% retention, IS tuning is producing regime-specific artefacts |
| OOS/IS ≥ 0.7 for "strong" | 70% retention indicates genuine generalisation, not lucky OOS period |
| Sharpe ≥ 0.8 | Institutional minimum for systematic strategy allocation consideration in crypto |
| Sortino ≥ 1.0 | Ensures downside risk is managed independently of upside volatility |
| Max DD ≤ 25% | Beyond 25%, strategy requires 33% recovery just to return to breakeven |
| OOS trades ≥ 30 | With < 30 trades, 95% CI on PF spans ± 0.3 — result is noise |
| R² ≥ 0.85 | Below this, equity growth is non-linear and likely regime-dependent |
| Backtest ≥ 18 months | Must span at least one partial crypto cycle with mixed regimes |
| 365-day annualisation | Crypto trades every calendar day; 252 understates annualised vol and return |
| 0.1% slippage gate | Conservative minimum for Binance Futures mid-cap pairs at reasonable size |
