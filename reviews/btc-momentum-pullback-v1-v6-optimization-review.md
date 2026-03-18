# BTC Momentum Pullback — v1 到 v6 完整優化歷程

**策略家族**: btc-momentum-pullback
**回測區間**: IS 2023-01-01 ~ 2025-01-01 / OOS 2025-01-01 ~ 2026-01-01
**整理日期**: 2026-03-18
**結論**: 6 輪優化，最佳 OOS PF 0.8011（v6），尚未達到投入實戰標準（目標 OOS PF ≥ 1.0）

---

## 目錄

1. [策略基本設計](#策略基本設計)
2. [優化方法論](#優化方法論)
3. [版本總表](#版本總表)
4. [v1 — 基礎版本](#v1--基礎版本)
5. [v2 — 1H ADX 制度濾波](#v2--1h-adx-制度濾波)
6. [v3 — 成交量確認](#v3--成交量確認)
7. [v4 — ATR 追蹤止損](#v4--atr-追蹤止損)
8. [v5 — 移除 EMA25 出場](#v5--移除-ema25-出場)
9. [v6 — EMA25 雙 K 確認](#v6--ema25-雙-k-確認)
10. [跨版本學習總結](#跨版本學習總結)
11. [下一步：v7 假設](#下一步v7-假設)

---

## 策略基本設計

**核心概念**: BTC 永續合約 15m，在 1H 多頭趨勢確認下，等待 15m EMA7 回踩後出現陽線收回（bullish reclaim），視為動能重啟訊號入場。

### 固定架構（v1–v6 不變）

**時框**: 15m 進場 + 1H 趨勢過濾

**出場邏輯**（v1 基礎）:
- 道氏理論：收盤低於前 5 根 K 線的最低點（swing low）
- 趨勢終止：收盤低於 15m EMA25

**止損**:
- 主要：entry_price − ATR(14) × 2.0（固定於進場當根）
- Hard fallback: −15%

**目標指標**（全程不變）:

| Metric | 目標 |
|--------|------|
| Win Rate | ≥ 35% |
| Profit Factor (IS) | ≥ 1.3 |
| Profit Factor (OOS) | ≥ 1.0 |
| Max Drawdown | ≤ 25% |
| Trades/day | ≤ 0.5 |

---

## 優化方法論

### TAO 循環（每輪必走）

```
Analysis → Planning → Implementation → Backtest → Analysis → ...
```

每輪：
1. **Codex 雙輪 review** — 將假設寫進 MD，Claude 審閱後決策
2. **single-variable 原則** — 每輪只改一件事，否則無法歸因
3. **check-gate 強制** — hypothesis-log.md 須記錄 IS stem + OOS stem + Verdict 才能進入下一輪
4. **Pipeline 自動化** — `run_backtest_suite` 串接：data check → IS backtest → OOS backtest → reports → session_close → check-gate

### Root Cause 分類框架

| 類型 | 定義 |
|------|------|
| Type A | 進場品質問題（訊號本身方向性弱，avg MFE 低）|
| Type B | 制度選擇問題（在錯誤的市場狀態下進場）|
| Type C | 出場/止損結構問題（進場方向對，但出場設計破壞 R:R）|

---

## 版本總表

| 版本 | 單一變更 | IS PF | OOS PF | OOS WR | OOS MDD | Verdict | 根因類型 |
|------|---------|-------|--------|--------|---------|---------|---------|
| v1 | 基礎版本 | 0.80 | 0.71 | 24.6% | 30.8% | FAIL | Type A + B |
| v2 | +1H ADX(14) > 25 | 0.88 | 0.64 | 23.2% | 23.6% | REVERT | B（ADX 不可靠）|
| v3 | +volume > vol_ma20 | 0.83 | 0.80 | 32.6% | 14.9% | INCONCLUSIVE | Type C（exit）|
| v4 | ATR trailing stop | 0.27 | 0.32 | 29.0% | 42.8% | REVERT | 設計錯誤（churn）|
| v5 | 移除 EMA25 exit | 0.85 | 0.75 | 32.1% | 19.3% | FAIL | Type C（stop 太寬）|
| **v6** | EMA25 2-bar confirm | **0.86** | **0.80** | **32.2%** | **15.5%** | **INCONCLUSIVE** | **Type C（ATR×2 太寬）**|

---

## v1 — 基礎版本

### 設計

| 條件 | 說明 |
|------|------|
| 1H EMA7 > EMA25 | 多頭趨勢確認 |
| 15m ADX(14) > 25 | 排除本地橫盤 |
| 15m RSI(14) 50–70 | 動能帶確認 |
| 15m low < EMA7, close > EMA7, close > open | EMA7 回踩收回（bullish reclaim）|
| volume > 0 | 合理性確認 |

**IS stem**: backtest-result-2026-03-18_15-01-30
**OOS stem**: backtest-result-2026-03-18_15-01-52

### 回測結果

| Metric | IS | OOS |
|--------|-----|-----|
| Trades | 1015 (1.39/d) | 472 (1.29/d) |
| Win Rate | 21.8% | 24.6% |
| Profit Factor | 0.80 | 0.71 |
| Max Drawdown | 55.1% | 30.8% |
| Sharpe | -1.51 | -2.91 |
| R:R (calc) | 2.90× | ~2.90× |
| Breakeven WR | 25.6% | 25.6% |
| WR gap | -3.8pp | -1.0pp |

### 診斷

**Verdict: FAIL**

1. **Type B（市場制度）**: 90% 的交易發生在橫盤 regime（1H EMA7>EMA25 太寬鬆，實際多頭結構要求更高）
2. **Type A（進場品質）**: 96% 的交易 MFE < 0.47%（入場後短期方向性極弱，avg MFE = 0.13–0.17%）
3. OOS PF < 1.0 → 無正期望值，但 IS vs OOS 差距小，非過擬合問題

### 決策理由

R:R 2.90× 結構尚可，問題在 WR 太低（21.8%）。根因分析指向 Type A（個別交易進場品質）與 Type B（regime 選擇）兩個方向。優先測試 Type B（更容易量化），選擇 1H ADX 作為 regime filter。

---

## v2 — 1H ADX 制度濾波

### 變更

**單一改變**: 加入 `1H ADX(14) > 25` 到進場條件

**假設**: 1H ADX > 25 代表 1H 真正有動能趨勢，排除低動能橫盤期

**IS stem**: backtest-result-2026-03-18_18-06-15
**OOS stem**: backtest-result-2026-03-18_18-06-32

### 回測結果

| Metric | v1 IS | v2 IS | v1 OOS | v2 OOS |
|--------|-------|-------|--------|--------|
| Trades | 1015 (1.39/d) | 598 (0.82/d) | 472 | 250 |
| Win Rate | 21.8% | 23.1% | 24.6% | 23.2% |
| PF | 0.80 | 0.88 | 0.71 | **0.64** ↓ |
| MDD | 55.1% | 35.2% | 30.8% | 23.6% |
| R:R | ~2.90× | ~2.95× | ~2.90× | **2.13×** ↓ |

### Codex Review 關鍵發現

Codex（實作 feasibility review）提出：
1. **[HIGH]** 原分析提出 4 個改變同時實施（ADX + Volume + RSI + ADX threshold），違反 single-variable 原則
2. **[HIGH]** Exit/SL 結構問題（Loser hold 1h26m vs Winner 5h36m）被忽略
3. **[MEDIUM]** 1H ADX > 25 是否能排除 range regime 未有數據支撐

Claude 決策：採用 Codex 建議，本輪只測 1H ADX（最直接的單一 regime 變數）。

### 診斷

**Verdict: REVERT**

1. **1H ADX > 25 不是 range regime 的可靠代理**: IS range regime 90% → 84%，OOS 維持 91%——幾乎沒有改善
2. **OOS R:R 從 2.9× 降至 2.13×**: filter 在 2025 年（OOS）移除了比例較高的獲利交易
3. **IS 改善是過擬合**: IS PF 0.80 → 0.88 但 OOS PF 0.71 → 0.64，IS 改善反映 2023–2024 ADX 特性，不能推廣到 OOS

### 決策理由

REVERT。ADX 衡量的是當下價格運動的方向強度，不是整體市場是否趨勢。橫盤市場中的個別 K 線完全可能有高 ADX。Type B 的 regime filter 策略失敗。轉向 Type A（個別交易進場品質）：Codex 建議的 Volume confirmation。

---

## v3 — 成交量確認

### 變更

**單一改變**: 移除 v2 的 1H ADX（REVERT），加入 `volume > volume.rolling(20).mean()`

**假設**: 在 EMA7 reclaim 時要求成交量高於 20 根移動均量，過濾無量反彈（dead-cat bounce），提升個別交易的短期方向性

**Codex Review (2-round)**:
- Round 1 找到：語法錯誤（`mean(20)` → `mean()`），缺少 `dbg_vol_ok` debug column，volume 非穩態性
- Verdict: **MODIFY** — 修正語法，加入 debug column，接受 IS/OOS volume 分布差異風險

**IS stem**: backtest-result-2026-03-18_18-49-52
**OOS stem**: backtest-result-2026-03-18_18-50-04

### 回測結果

| Metric | v1 IS | v3 IS | v1 OOS | v3 OOS |
|--------|-------|-------|--------|--------|
| Trades | 1015 (1.39/d) | 465 (0.64/d) | 472 | 242 |
| Win Rate | 21.8% | 25.4% | 24.6% | **32.6%** ↑ |
| PF | 0.80 | 0.83 | 0.71 | **0.80** ↑ |
| MDD | 55.1% | 37.5% | 30.8% | **14.9%** ↓ |
| Sharpe | -1.51 | -0.65 | -2.91 | **-1.04** ↑ |
| avg MFE | 0.13–0.17% | **0.95%** | — | **0.73%** |
| Profit giveback | — | 64.4% | — | 63.0% |
| OOS R:R | — | — | ~2.90× | **1.645×** ↓ |

### 診斷

**Verdict: INCONCLUSIVE**

**Volume filter 機械驗證成功**:
- avg MFE 從 0.13% → 0.73% OOS（Codex 門檻 > 0.30% 達成）
- OOS WR +8pp，MDD -16pp，Sharpe +1.87
- Type A 問題已修正：進場品質確認改善

**新的根因浮現（Type C）**:
- Profit giveback 63%：交易到達 MFE 後，出場吐還 63% 的利潤
- OOS R:R 壓縮到 1.645×（v1: 2.9×）
- OOS breakeven WR = 37.8% > actual 32.6% → gap -5.2pp（惡化）
- 出場結構成為新瓶頸：5-bar swing low + EMA25 在橫盤環境過早觸發

### 決策理由

INCONCLUSIVE（不 REVERT）：明顯改善趨勢，根因已從 Type A+B 轉移到 Type C（exit structure）。下一步：測試 ATR trailing stop 來降低 profit giveback。

---

## v4 — ATR 追蹤止損

### 變更

**單一改變**: custom_stoploss 改為兩段式（v3 固定止損不動，疊加 trailing logic）

- Phase 1（profit < +0.3%）: 固定止損 entry − ATR×2.0（同 v3）
- Phase 2（profit ≥ +0.3%）: 追蹤止損 current_rate − ATR_current×1.5

**假設**: 在累積獲利 +0.3% 後啟動追蹤止損，鎖住利潤，降低 profit giveback

**Codex Review (2-round)**:
- **[HIGH]** v3 custom_stoploss 使用 entry-candle ATR，Phase 2 須改為 current-bar ATR
- **[HIGH]** activation +0.5% 太高（OOS avg MFE 0.73%），建議降至 +0.3%
- Verdict: **MODIFY** — 接受修正

**IS stem**: backtest-result-2026-03-18_19-01-04
**OOS stem**: backtest-result-2026-03-18_19-01-14

### 回測結果

| Metric | v3 OOS | v4 OOS |
|--------|--------|--------|
| Trades | 242 | **589** ↑↑ |
| PF | 0.80 | **0.32** ↓↓ |
| MDD | 14.9% | **42.8%** ↑↑ |
| Sharpe | -1.04 | **-6.64** ↓↓ |

### Exit 分解（OOS）

| Exit type | Count | Avg PnL |
|-----------|-------|---------|
| trailing_stop_loss | 159 | **+0.16%** |
| exit_signal (EMA25) | 107 | **-2.64%** |
| stop_loss (Phase 1) | 34 | -4.84% |

### 診斷

**Verdict: REVERT**

**Trailing stop 本身是有效的**（OOS avg +0.16%），但造成了「快速換手」問題：
1. Trail 在 +0.3% activation 後，ATR×1.5 trail 距離幾乎吃掉整個 gain → 以接近零獲利快速出場
2. 快速出場 → 釋放資本 → 立刻再入場 → 新進場被 EMA25 割在 -2.64% avg
3. 交易數從 465 → 589 (+27%) → churn 效應

Root cause：trail activation threshold（+0.3%）與 trail 寬度（1.5 ATR）過於接近，幾乎所有 Phase 2 都在接近零獲利時出場。

### 決策理由

REVERT 回 v3 baseline（保留 volume filter）。Churn 問題不是 trailing stop 方向錯誤，是參數組合失敗。但 EMA25 exit 造成的 -2.64% 損失現在更加顯眼——決定直接移除 EMA25 exit（v5）。

---

## v5 — 移除 EMA25 出場

### 變更

**單一改變（從 v3 baseline）**: 移除 `| close < EMA25` exit 條件，只保留 5-bar swing low

**假設**: EMA25 在 89-95% range regime 中震盪，造成平均 -2.23% IS / -2.64% OOS 的提前出場損失；移除後讓 swing low 決定所有出場

**Codex Review (2-round)**:
- **[HIGH]** exit_signal attribution 不清楚（EMA25 vs swing_low 混在同一 bucket）— 需加 exit_tag
- **[HIGH]** 移除 EMA25 後在下趨勢中 MAE 尾部可能顯著擴大
- Verdict: **APPROVE with monitoring**（需確認 v4 trailing code 已完全移除）

**IS stem**: backtest-result-2026-03-18_19-08-08
**OOS stem**: backtest-result-2026-03-18_19-08-19

### 回測結果（含 exit_tag 分解）

**OOS Exit Breakdown（首次有完整 attribution）**:

| Exit type | OOS count | OOS avg PnL | OOS avg MFE |
|-----------|-----------|-------------|-------------|
| swing_low | 167 | **+1.54%** | +0.98% |
| stop_loss | 52 | **-6.02%** | +0.27% |
| trailing_stop_loss* | 21 | -5.75% | +0.24% |

*custom_stoploss ratio 動態變化，Freqtrade 分類為 trailing

| Metric | v3 OOS | v5 OOS |
|--------|--------|--------|
| PF | 0.80 | **0.75** ↓ |
| WR | 32.6% | 32.1% |
| MDD | 14.9% | 19.3% |
| avg hold | ~160 min | 172 min |

### 診斷

**Verdict: FAIL**

**Swing_low exits 優秀**（+1.54% avg OOS）— 確認 swing_low 是好的出場機制

**EMA25 是不可缺少的快速虧損保護**：
- 移除 EMA25 後，losers 一路跌至 ATR×2 stop（avg -6.02% OOS）
- 原本 EMA25 會在 -1～-2% 範圍切掉這些交易，現在全部跌到 -6%
- stop_loss OOS count = 52（Codex 診斷閾值 < 30 → 未達）

**結論：問題不是 EMA25「存在」，而是 EMA25 的「1-bar 觸發機制」在 range 環境中過於敏感**

### 決策理由

FAIL。但本輪提供了重要訊息：swing_low exits 是好的，stop_loss（ATR×2）太寬是問題。修正方向：把 EMA25 加回來，但改為 2-bar confirmation（v6），保留 loss protection 同時過濾單根震盪誤觸。

---

## v6 — EMA25 雙 K 確認

### 變更

**單一改變（從 v3 baseline）**: EMA25 exit 改為需要連續 2 根收盤低於 EMA25 才觸發，並加入 `exit_tag="ema25_2bar"` 區分出場原因

```python
# v6 exit logic
dataframe.loc[
    (dataframe["close"] < dataframe["swing_low_5"]),
    ["exit_long", "exit_tag"],
] = [1, "swing_low"]

dataframe.loc[
    (
        (dataframe["close"] < dataframe["ema25"])
        & (dataframe["close"].shift(1) < dataframe["ema25"].shift(1))
    ),
    ["exit_long", "exit_tag"],
] = [1, "ema25_2bar"]
```

**假設**: Range 震盪通常 1 根就恢復，2 根連續低於 EMA25 才代表真正的趨勢終止

**Codex Review (2-round)**:
- **[HIGH]** v5 的 `trailing_stop_loss` 分類是 Freqtrade 行為特性（custom_stoploss ratio 動態變化），v4 code 已清楚移除 ✓
- **[HIGH]** 2-bar delay 在真實下跌時增加約 -0.5～-1.0% 額外損失（30 min）
- **[MEDIUM]** OOS PF ≥ 1.0 機率估計 40–55%
- Verdict: **APPROVE with exit_tag instrumentation**

**IS stem**: backtest-result-2026-03-18_19-18-25
**OOS stem**: backtest-result-2026-03-18_19-18-37

### 回測結果（完整 exit_tag 分解）

**OOS Exit Breakdown**:

| Exit type | OOS count | OOS avg PnL | OOS avg MFE | Codex threshold |
|-----------|-----------|-------------|-------------|-----------------|
| swing_low | 151 | **+1.99%** | +1.02% | — |
| ema25_2bar | 28 | -3.08% | +0.49% | avg > -1.5% → ❌ |
| stop_loss | 43 | **-5.71%** | +0.27% | count < 30 → ❌ |
| trailing_stop_loss* | 17 | -6.13% | +0.24% | — |

| Metric | v3 OOS | v6 OOS | 變化 |
|--------|--------|--------|------|
| PF | 0.7959 | **0.8011** | +0.005 ↑ |
| WR | 32.6% | 32.2% | -0.4pp |
| MDD | 14.9% | 15.5% | +0.6pp |
| Sharpe | -1.04 | -1.01 | +0.03 ↑ |
| R:R | 1.645× | **1.685×** | +0.04× ↑ |
| avg hold | ~160 min | 170 min | +10 min ↑ |

### 診斷

**Verdict: INCONCLUSIVE（6 輪最佳 OOS PF）**

**2-bar EMA25 有效**：
- swing_low exits 改善：OOS avg +1.99%（v5: +1.54%）
- hold time +10 min → winners 撐更久
- ema25_2bar exits 只有 28（vs v3 大量 EMA25 premature fires）

**剩餘問題：ATR×2 止損太寬**：
- stop_loss OOS count = 43（目標 < 30，未達）
- stop_loss OOS avg = -5.71%（仍然災難性）
- 這些是「假突破」進場：volume reclaim 確認，但之後反轉幅度超過 ATR×2

### 決策理由

INCONCLUSIVE。v6 是 6 輪中 OOS PF 最高（0.8011），但仍未過 1.0 gate。根因已非常清楚：ATR×2 止損允許的虧損空間太大，43 筆交易平均 -5.71% 是唯一的主要障礙。

---

## 跨版本學習總結

### 進場品質演進

| 版本 | avg MFE (IS) | avg MFE (OOS) | 意義 |
|------|-------------|--------------|------|
| v1 | 0.13–0.17% | 0.13–0.17% | 進場後無短期方向性 |
| v3+ | 0.95% | 0.73% | Volume filter 成功提升進場品質 |

**結論**: Volume filter（v3）是整個優化歷程中最有效的單一改變，MFE 改善 4–5 倍。

### 出場結構演進

| 版本 | 主要出場問題 | 解法嘗試 | 結果 |
|------|------------|---------|------|
| v1–v3 | profit giveback 63%（EMA25 過早觸發）| — | — |
| v4 | ATR trail churn | trailing stop 設計 | REVERT（參數錯誤）|
| v5 | ATR stop 太寬（-6% avg） | 完全移除 EMA25 | FAIL（失去 loss protection）|
| v6 | ATR stop 仍太寬（-5.71% avg） | 2-bar EMA25 confirmation | INCONCLUSIVE（最佳）|

**結論**: EMA25 是必要的虧損保護機制，但 1-bar 觸發過於敏感。2-bar confirmation 是正確方向，但 ATR×2 止損寬度仍是最後一個阻礙。

### 優化歷程的市場制度觀察

| 指標 | v1 IS | v1 OOS | v6 IS | v6 OOS |
|------|-------|--------|-------|--------|
| Range regime | 90% | 91% | ~89% | ~95% |
| Rally regime | ~9% | ~9% | ~10% | ~5% |

**Range regime 在 OOS（2025–2026）甚至比 IS（2023–2025）更高（91% → 95%）**。這說明：
- 2025 年 BTC 市場整體震盪特性比 2023–2024 更明顯
- 所有基於「趨勢」假設的 entry filter（1H ADX、EMA7>EMA25）都無法有效排除 range
- **策略的核心限制可能是結構性的**：在 95% range 環境中，任何追趨勢入場的策略都面臨天然劣勢

### Codex 多輪審查的價值

每輪 Codex 雙輪 review（寫入 MD，Claude 審閱）提前攔截：
- v3：語法錯誤（`mean(20)` → `mean()`），缺少 debug column
- v4：activation threshold 太高（+0.5% → +0.3%），ATR lookup 必須改為 current-bar
- v5：stop_loss -6% 是 EMA25 移除的直接後果（提前預測）
- v6：2-bar delay 在真實下跌時的額外成本（30min，-0.5～-1.0%）

---

## 下一步：v7 假設

### 假設

**單一改變（從 v6 baseline）**: ATR stop multiplier 2.0 → 1.5

**估算依據**（v6 OOS 數據）：

若 stop_loss avg 從 -5.71% 降至 -3.0%（tighter stop）且 count 降至 30（部分由 ema25_2bar 攔截）：

```
OOS gross_profit (swing_low) = +301
OOS ema25_2bar damage        = -86
OOS stop_loss damage         = 30 × -3.0% = -90 (from -246)
OOS trailing_stop damage     = -104 (unchanged)
──────────────────────────────────────
Estimated OOS net = 301 - 86 - 90 - 104 = +21
Estimated OOS PF  = 301 / (86 + 90 + 104) ≈ 1.07 → 超過 1.0 gate ✓
```

**風險**：ATR×1.5 可能讓部分本來能回復的交易更早被止損，降低 WR。若 WR 從 32.2% 降至 < 28%，R:R 改善可能不足以補償。

### 接受標準

| 條件 | 結果 |
|------|------|
| OOS PF ≥ 1.0 AND IS PF ≥ 1.3 | **KEEP** — 投入 paper trading 驗證 |
| OOS PF ≥ 1.0 但 IS PF < 1.3 | **INCONCLUSIVE** |
| OOS PF < 1.0 且 OOS WR < 28% | **REVERT** — 退回 v6，重新評估方向 |

---

*文件自動從 hypothesis-log.md、analysis-summary、Codex review MD 及回測報告整合*
*所有回測 stem 均已記錄在 hypothesis-log.md 可重現*
