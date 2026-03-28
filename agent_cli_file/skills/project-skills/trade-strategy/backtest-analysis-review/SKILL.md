---
name: backtest-analysis-review
description: Structured checklist for analyzing backtest results and forming an improvement hypothesis before writing the iteration plan. Covers quantitative diagnostics, root cause classification, single-variable change selection, and multi-model review (Claude / Gemini / Codex). Use during the TAO Analysis phase, after session-close has run and before writing iteration-plan.md.
---

# Backtest Analysis Review Skill

Used in the **Analysis phase** of the TAO cycle — after `session-close` updates STATUS.md and before writing `iteration-plan.md`.

The goal is to derive a single, evidence-backed improvement hypothesis from the backtest data. This skill prevents premature hypothesis formation and ensures each change is driven by diagnostic evidence, not intuition.

---

## Step 1 — Establish the Loss Driver (R:R Math)

Before reading any chart or trade list, compute the payoff structure:

```
avg_win    = mean profit of winning trades (%)
avg_loss   = mean loss of losing trades (%)   [absolute value]
R:R        = avg_win / avg_loss
breakeven_WR = 1 / (1 + R:R)
actual_WR    = win_count / total_trades
gap          = breakeven_WR − actual_WR
```

**Interpret the gap**:

| Gap | Diagnosis | Primary lever |
|-----|-----------|---------------|
| gap ≤ 5pp | Close to breakeven — entry quality is the marginal issue | Improve entry filter precision |
| gap 5–15pp | Moderate — WR is structurally too low | Review entry pattern validity |
| gap > 15pp | Severe — strategy lacks edge | Reconsider core hypothesis |

> **Do not** jump to adding filters until you know which dimension to fix. If R:R is low (< 1.5), filters alone will not help — the exit or SL structure needs redesign.

Read these values from: `freqtrade/reports/<stem>_<strategy>.zip` → `summary.json`
Fields: `winrate_pct`, `avg_profit_pct`, `tail_best_1pct_avg_pct`, `tail_worst_1pct_avg_pct`

---

## Step 2 — MAE/MFE Histogram (Entry Timing Quality)

From `deep_diagnostics.json` → `mae_mfe`:

```
avg_MAE = average adverse excursion (how far against us before exit)
avg_MFE = average favorable excursion (how far in our favor)
mfe_hist = distribution of maximum favorable moves
```

**Key question**: What % of trades have MFE < 0.5%?

| MFE Distribution | Diagnosis |
|-----------------|-----------|
| > 50% have MFE < 0.5% | Entry pattern lacks short-term directional prediction |
| Most trades reach ≥ 1% MFE | Entry is directionally sound — problem is WR (wrong setups) or exit timing |

> If most trades never go in your direction, adding more entry filters helps only if they eliminate the trades that immediately reverse. If winners and losers look similar at entry, you have a structural edge problem.

---

## Step 3 — Market Regime Segmentation

From `deep_diagnostics.json` → `market_condition.rows` or `trades.csv` joined with `trade_regime.csv`:

Compute for each regime (rally / range / downtrend):
- trade count and % of total
- win rate
- avg profit

**Key question**: Is the strategy trading in the right conditions?

| Finding | Diagnosis |
|---------|-----------|
| > 70% of trades in range regime | Trend filter is too weak — regime admission is the primary problem |
| Rally WR >> range WR (> 10pp gap) | Regime distinction exists — tighten the trend filter |
| Rally WR ≈ range WR | Regime is not the issue — entry pattern is fundamentally weak |

> A momentum-trend strategy with 90% of trades in ranging markets has a broken regime filter, regardless of entry pattern quality.

---

## Step 4 — Exit Reason Decomposition

From `trades.csv` → `exit_reason` column:

Classify exits by type and profitability:

| Exit Type | Expected behaviour |
|-----------|-------------------|
| `exit_signal` | Most wins AND most losses — signal should be directionally selective |
| `stop_loss` | All losses — check if SL is appropriately sized |
| `trailing_stop_loss` | Mix — check if trailing is locking in enough gain |
| `roi` | Wins only — if absent, ROI is not binding |

**Red flags**:
- High `stop_loss` rate (> 20%) with small avg loss → SL too tight, random noise triggers exits
- High `exit_signal` losses → signal fires while trade is underwater; entry had no valid MFE
- `trailing_stop_loss` losses → trailing kicks in too early, before position matures

---

## Step 5 — Gate Filter Funnel (Signal Precision)

From `gate_filter_funnel.csv`:

> **Note**: This funnel records only trades that entered. `trigger_rate_pct = 100%` for all filters means all entered trades passed all filters — this is expected. The funnel does NOT show how many signals were rejected.

To understand rejection rates, you need a secondary analysis:
- Read `signals_path` (signals feather from backtest zip) and count rows where each `dbg_*` column = 1 vs 0
- Or: compare total `dbg_pullback` fires vs total entered trades across the timerange

**What to look for**:
- If `dbg_1h_bull` rarely blocks entries, the 1H filter may be set too permissively
- If a proposed new filter (e.g., `1h_adx > 25`) would eliminate trades that are predominantly losers, it is high-leverage
- Verify this hypothesis by running a quick ratio: trades with 1H ADX < 25 vs > 25 in the `signal_context.csv`

---

## Step 6 — Root Cause Classification

After completing Steps 1–5, classify the root cause into one of three types:

### Type A — Entry Pattern Lacks Predictive Power
- Evidence: MFE < 0.5% on > 70% of trades, winners and losers similar at entry
- Fix direction: Change or replace the entry pattern (e.g., require a stronger reclaim signal)
- Do NOT fix by tightening parameters of a broken signal

### Type B — Regime Filter Too Weak
- Evidence: > 60% of trades in ranging markets, WR gap between rally and range > 10pp
- Fix direction: Add or tighten the regime admission condition (e.g., 1H ADX, ADR threshold)
- Fix Type B before Type A — if wrong markets are being traded, entry pattern results are contaminated

### Type C — Exit / SL Structure Misaligned
- Evidence: High SL rate with small per-SL loss (too tight), or large average loss with low SL rate (too wide)
- Fix direction: Adjust SL multiplier, add trailing, or revise exit signal threshold
- Fix Type C independently only when R:R is the primary lever (gap analysis in Step 1 shows low R:R)

**Priority order**: Fix B → A → C. Rarely all three at once.

---

## Step 7 — Form the Improvement Hypothesis

State the hypothesis as a single sentence following this template:

> "Adding [specific condition] to [entry/regime/exit] will [expected metric change] because [evidence from steps 1–5]."

Checklist before committing:
- [ ] Hypothesis targets the root cause identified in Step 6 (not a symptom)
- [ ] Only ONE variable changes vs baseline (single-variable principle)
- [ ] Prior art check: `hypothesis-log.md` reviewed — this change not previously tried with FAIL verdict
- [ ] Expected impact estimated (e.g., "should reduce trades by ~40%, raise WR from 22% to 28%")
- [ ] Change is testable: there is a clear before/after metric to compare

If changing more than one variable is unavoidable, document which variable is primary and which is secondary, and set up separate experiment branches where possible.

---

## Step 8 — Multi-Model Review

**Trigger review when**:
- Hypothesis involves a major direction change (new regime filter, replacing entry pattern)
- R:R gap > 15pp (strategy may need core redesign)
- Analysis conclusions are conflicting or ambiguous

**Skip review when**:
- Hypothesis is a single parameter tightening (ADX 25 → 30, RSI band shift)
- Evidence from Steps 1–5 is unambiguous and convergent

### Review Workflow

Build a review packet from the analysis summary written in the previous step:

```
Review packet contents:
1. Strategy spec (entry/exit/SL logic summary)
2. Key metrics: IS PF, OOS PF, WR, R:R, Sharpe, trades/day
3. Root cause diagnosis (one paragraph per type A/B/C)
4. Proposed hypothesis (the one sentence from Step 7)
5. Data evidence (MAE/MFE summary, regime breakdown table)
```

Submit to each model with these scopes:

| Model | Review scope | Prompt anchor |
|-------|-------------|---------------|
| **Gemini** | Market logic and domain validity — does the diagnosis match known BTC behaviour? Is the proposed change directionally sound for futures momentum? | "Review this backtest analysis for market logic correctness and domain validity. Flag any conclusion that contradicts known BTC futures behaviour." |
| **Codex** | Implementation feasibility — can this change be coded without look-ahead bias, excessive complexity, or indicator lag? | "Review this improvement hypothesis for implementation feasibility. Flag look-ahead bias risks, indicator lag concerns, and any edge cases in the proposed code change." |
| **Claude** | Synthesize both reviews and write the iteration plan. Claude has final authority. | Reads Gemini + Codex outputs and writes the DECISION section. |

Use the `multi-agent-consensus` skill for the parallel call pattern:
→ [multi-agent-consensus/SKILL.md](../multi-agent-consensus/SKILL.md)

Save the review at:
```
strategies/<family>/sessions/<YYYYMMDD>-consensus-analysis-<topic>.md
```

### Synthesis Rules for Claude

When resolving Gemini vs Codex disagreements:
- **Gemini flags domain risk, Codex says feasible**: accept the domain concern — market logic overrides implementation convenience
- **Codex flags look-ahead bias, Gemini silent**: always fix the bias — correctness is non-negotiable
- **Both raise different concerns**: address both; if addressing both requires > 2 code changes, split into separate iterations
- **Both approve**: proceed; note the approval in the iteration plan

---

## Step 9 — Output Artifacts

After completing Steps 1–8, produce:

1. **`sessions/<YYYYMMDD>-analysis-summary.md`** (already written in Analysis phase)
   - Must include: R:R math, MAE/MFE interpretation, regime table, root cause type, proposed hypothesis

2. **`sessions/<YYYYMMDD>-consensus-analysis-<topic>.md`** (only if multi-model review was triggered)
   - Each model's output pasted in, Claude decision written last

3. **`sessions/<YYYYMMDD>-iteration-plan.md`** (written at end of Analysis / start of Planning phase)
   - One change, one hypothesis, clear acceptance criteria

Then run:
```bash
python -m lib.endpoints.session_close <family> \
  --is-stem <stem> \
  --oos-stem <oos_stem> \
  --phase analysis \
  --analysis-summary <YYYYMMDD>-analysis-summary.md
```

And verify gate:
```bash
python -m lib.endpoints.strategy_cycle check-gate <family>
```

---

## Anti-Patterns to Avoid

| Anti-pattern | Why it fails |
|-------------|--------------|
| Adding 3+ filters at once | Cannot isolate which change helped or hurt |
| Tightening parameters without root cause diagnosis | Reduces trades without fixing the underlying edge problem |
| Proposing a change because "it should work" | Must be backed by evidence from Steps 1–5 |
| Skipping prior art check | Risk of circular exploration — repeating a previously failed hypothesis |
| Proceeding without multi-model review after a major hypothesis change | Single-model blind spots compound across iterations |
| Writing iteration plan before analysis summary is complete | Analysis summary IS the evidence base for the plan |
