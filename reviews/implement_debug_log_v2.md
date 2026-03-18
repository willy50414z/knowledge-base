# TAO Loop v2 Debug Log

**Strategy**: btc-momentum-pullback
**Loop**: v1 → v2 iteration
**Date**: 2026-03-18
**Objective**: 執行完整的 TAO 第二輪循環，驗證流程工具是否正常運作

---

## Pre-loop State

- Phase: analysis (PASS gate)
- v1 결果: IS PF 0.80, OOS PF 0.71 → FAIL
- Root cause: Type B（90% trades in range regime, 1H EMA filter too permissive）
- R:R 2.90×, WR gap 3.8pp to breakeven

---

## Step 1 — Commit checklist fix

**Action**: 補上 `knowledge-base/` 到 strategy-workflow SKILL.md + README.md 的 commit checklist
**Result**: ...

---

## Step 2 — Multi-agent consensus (Codex review)

**Action**: 呼叫 Codex 對 analysis summary + 改善假設進行 implementation feasibility review

**Codex findings**:

1. **[HIGH] 原 analysis-summary 提出 4 個改變同時實施** — 加 1H ADX、Volume 確認、RSI 55-70、ADX>30，違反 one-variable 原則，改了就無法歸因。需要拆成單一變數。

2. **[HIGH] Exit/SL 結構問題被忽略** — Loser 平均 hold 1h26m vs Winner 5h36m 的不對稱，以及 ATR×2 在不同波動環境的適應性問題尚未解決。只改 entry 可能掩蓋真正的失敗原因。

3. **[MEDIUM] 過濾條件未量化驗證** — 「1H ADX > 25 能排掉哪些壞交易」沒有用數據支撐，只是假設。

4. **[MEDIUM] 流程 gap** — phase 仍在 analysis，_latest.json 尚未有 iteration_plan，README 還是 v1 spec。

**Codex 建議**: 最乾淨的單一實驗是「volume-confirmed EMA7 reclaim」，因為它直接針對 MFE 低的根因（無量反彈），而非加多一層 regime filter。

**Claude synthesis（最終決策）**:

Codex finding #1 完全正確 — 原 analysis-summary 的 Proposed Direction 列了 4 件事，這是 planning 失誤。本輪只做一個改變。

Codex finding #2 我評估為中低優先：R:R 已是 2.90×，exit/SL ratio 本身不差，問題是 WR 太低（21.8%）。MDD 55% 確實需要關注，但那是 WR 低的結果，不是 SL 設計的問題。先修 entry 側。

Codex finding #3 有道理，但退一步看：90% trades 在 range regime 是最直接的數據，1H ADX 是最清楚的量化方式過濾這個 regime。

**v2 決定：單一改變 = 加入 1H ADX(14) > 25 到 entry conditions**

理由優先於 Volume confirmation：
- 90% range regime 是數據已確認的最大問題，ADX 直接過濾這個
- 1H informative frame 已在程式碼中載入，零額外複雜度
- Volume confirmation 可以是 v3（如果 v2 WR 仍未達標）
- 若加了 1H ADX 後 MFE 問題消失 → 說明 MFE 低是 regime 的副作用，不是獨立問題

---

## Step 3 — Planning phase

**Action**: 寫 `sessions/20260318-iteration-plan.md`，更新 hypothesis-log.md v2 entry (PENDING)
**Result**: OK — single change defined: add 1H ADX(14) > 25

---

## Step 4 — session_close --phase planning

**Command**: `python -m lib.endpoints.session_close btc-momentum-pullback --is-stem backtest-result-2026-03-18_15-01-30 --oos-stem backtest-result-2026-03-18_15-01-52 --phase planning --iteration-plan 20260318-iteration-plan.md`
**Gate result**: PASS

---

## Step 5 — Commit (planning phase artifacts)

**Files committed**: .gitignore, README.md, lib/endpoints/*.py, analyze_backtest_result.py, strategies/_template/hypothesis-log.md, btc-momentum-pullback STATUS/digest/hypothesis-log/sessions, knowledge-base submodule
**Commit**: 6fc8b70

---

## Step 6 — Implementation phase (v2)

**Changes vs v1**:
- Added `informative_1h["adx"] = ta.ADX(informative_1h, timeperiod=14)`
- Added `dbg_1h_adx_ok = (dataframe["adx_1h"] > 25)` debug column
- Added `& (dataframe["dbg_1h_adx_ok"] == 1)` to entry condition
- `startup_candle_count`: 50 → 75
- Version bump: v1 → v2 in docstring

**Data readiness**: 1H data READY (26446 rows, 2023–2026)
**Look-ahead bias**: 1H ADX uses merge_informative_pair with shift=True — CLEAN

---

## Step 7 — Backtest (v2 IS + OOS)

**IS stem**: backtest-result-2026-03-18_18-06-15
**OOS stem**: backtest-result-2026-03-18_18-06-32

---

## Step 8 — session_close --phase analysis

**IS**:  PF 0.8776 | MDD 35.2% | WR 23.1% | Sharpe -0.5654 | Trades 598
**OOS**: PF 0.6418 | MDD 23.6% | WR 23.2% | Sharpe -2.0362 | Trades 250

---

## Step 9 — Analyze backtest result

IS report generated to `freqtrade/reports/btc-momentum-pullback/`
OOS report generated to `freqtrade/reports/btc-momentum-pullback/`

---

## Step 10 — Analysis (v2)

### Metrics vs v1

| Metric | v1 IS | v2 IS | v1 OOS | v2 OOS |
|--------|-------|-------|--------|--------|
| Trades | 1015 (1.39/d) | 598 (0.82/d) | 472 | 250 |
| Win Rate | 21.8% | 23.1% | 24.6% | 23.2% |
| Profit Factor | 0.80 | 0.88 | 0.71 | **0.64** ← worse |
| MDD | 55.1% | 35.2% | 30.8% | 23.6% |
| Sharpe | -1.51 | -0.57 | -2.91 | -2.04 |
| R:R | 2.90× | 2.95× | ? | **2.13×** ← dropped |
| Breakeven WR | 25.6% | 25.3% | ? | **31.9%** ← harder |

### Key Findings

1. **Trades reduced correctly** — IS 41% fewer, OOS 47% fewer. Filter fires.

2. **Regime distribution barely changed** — IS range regime: 90% → 84%, OOS: still 91%. The 1H ADX > 25 did NOT effectively remove ranging markets. Conclusion: 1H ADX > 25 is not a reliable proxy for "market is trending at daily timeframe."

3. **OOS R:R degraded** — v2 OOS R:R = 2.13× vs IS 2.95×. The 1H ADX filter removed a larger proportion of winning OOS trades. In 2025 (OOS), periods with 1H ADX > 25 coincidentally selected WORSE payoff setups.

4. **OOS PF is WORSE** — 0.71 → 0.64. The change hurt OOS performance. This is a REVERT signal.

5. **IS metrics improved (misleading)** — IS PF 0.80 → 0.88, MDD halved. But the OOS degradation suggests this was IS-period overfitting to 2023-2024 trend characteristics.

### Verdict: REVERT

1H ADX > 25 as a regime filter does not generalize across IS and OOS. The OOS period (2025) has different ADX distribution that penalizes this filter. Change reverted.

### Process Findings

- `session_close --phase analysis` correctly detected check-gate would fail (hypothesis-log stems not filled) → needed to fill stems before gate would pass ← **check confirmed working**
- IS report generation requires manually updating `.last_result.json` → this is a UX friction point for running multiple backtest reports in one session
- `analyze_backtest_result --stem` parameter would be useful to avoid manual JSON editing

---

## Issues Found

<!-- 記錄本輪發現的 bug 或流程問題 -->

---

## Process Observations

<!-- 哪些步驟順暢，哪些需要改善 -->
