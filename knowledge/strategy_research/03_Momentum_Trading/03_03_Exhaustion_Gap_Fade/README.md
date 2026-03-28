# 03-03 Exhaustion Gap Fade（竭盡缺口回補）

## 策略類型
**03 — Momentum Trading（價格行為 / 動能反轉）**

---

## 概述

竭盡缺口回補策略（Exhaustion Gap Fade）是一種**逆勢（Contrarian）**策略，專門針對趨勢末段出現的**竭盡缺口（Exhaustion Gap）**進行反向交易。當市場在一段持續上漲（或下跌）後，突然出現一個大型跳空缺口，這往往是**最後的瘋狂（Last Gasp）**——代表情緒達到頂點、追高/殺低的群眾完全進場後，動能即將耗盡。

---

## 缺口的四種類型（Edward & Magee 分類）

| 類型 | 英文 | 出現位置 | 含義 | 是否填補 |
|------|------|---------|------|---------|
| **普通缺口** | Common Gap | 震盪整理中 | 無特殊含義，流動性低 | 通常快速填補 |
| **突破缺口** | Breakout Gap | 型態突破時 | 強烈方向性訊號 | 不易填補 |
| **持續缺口** | Runaway / Measuring Gap | 趨勢中段 | 趨勢加速延伸 | 不易填補 |
| **竭盡缺口** | **Exhaustion Gap** | 趨勢末段 | 動能耗盡，即將反轉 | **幾乎必然填補** |

---

## 核心邏輯

> **「趨勢末段的跳空不是機會，是陷阱。被情緒驅動的最後一波買盤進場後，主力開始出貨。」**

**竭盡缺口的識別特徵：**
1. 在一段較長的單邊趨勢（如上漲 5 週以上）之後出現
2. 缺口的跳空幅度**大於**趨勢中段的缺口
3. 缺口出現後，**成交量異常放大**（代表情緒達到頂峰）
4. 缺口後**1-3 根 K 線**就出現反向收盤（填補缺口嘗試）

---

## 關鍵指標

| 指標 | 用途 |
|------|------|
| **缺口大小（Gap Size）** | 相對於 ATR 的倍數，衡量極端性 |
| **RSI** | > 80 代表超買（空頭竭盡缺口），< 20 代表超賣 |
| **ATR (14)** | 定義缺口的「大小是否極端」 |
| **成交量** | 竭盡缺口通常伴隨量能爆炸 |
| **K 線型態** | 缺口後出現孕線、流星線等反轉 K 線 |

---

## 交易規則 (量化嚴謹版)

### 空頭竭盡缺口 (做空) (標籤: `Gap_Fade_Short`)
1. **背景確認 (Uptrend)**：
   - `ROC(Close, 20) > 1.5 * StdDev(ROC, 100)` (漲幅處於近期極端值)。
   - `RSI(14) > 75`。
2. **缺口識別 (Gap)**：
   - `Open > High[昨日] + 1.5 * ATR(14)`。
3. **反轉確認 (Trigger)**：
   - ~~在缺口被反向填補的過程中做空~~
   - **量化做法**：當前價 `Current_Price < High[昨日]` (即缺口上緣被跌破)。
4. **停損 (SL)**：`High[今日]` + `0.2 * ATR`。

---

## 量化優化方向 (Optimization Hooks)

1. **參數掃描**：
   - **Trend_Lookback**: [20, 40, 60] (判斷趨勢多長算「長」)。
   - **Gap_ATR_Multiplier**: [1.0, 1.5, 2.0] (定義何謂「大」缺口)。
2. **過濾器 (Filters)**：
   - **成交量峰值**：`Volume[今日] > Max(Volume[前 10 日])`。竭盡缺口通常伴隨換手量。
   - **缺口位置**：使用 PCA 分析「缺口距離最近一個月高點的百分比」對勝率的影響。
3. **出場策略**：
   - 竭盡缺口回補通常是快速的。建議設為 `Timed_Exit`（例如 3-5 根 K 線後不論盈虧平倉）或目標為回測 `EMA(20)`。

### 多頭竭盡缺口（趨勢末段跳空低開，準備做多）
```
對稱邏輯，在下跌趨勢末段的跳空低開後反向做多
RSI < 25，且缺口後出現錘頭 K 線或吞噬型態
```

---

## 量化實作

```python
def exhaustion_gap_signal(df, trend_period=20, gap_atr_mult=1.5, trend_min_return=0.15):
    """
    df: OHLCV DataFrame (至少包含 open, high, low, close, volume)
    """
    # 計算趨勢漲幅
    trend_return = df['close'].pct_change(trend_period)

    # 計算 ATR
    atr = compute_atr(df, 14)

    # 計算缺口大小
    gap = df['open'] - df['close'].shift(1)

    # 計算 RSI
    rsi = compute_rsi(df['close'], 14)

    # 空頭竭盡缺口訊號
    strong_uptrend = trend_return > trend_min_return       # 之前漲了超過15%
    gap_up = gap > gap_atr_mult * atr                      # 跳空幅度超過1.5ATR
    overbought = rsi > 75                                  # RSI 超買
    bearish_candle = df['close'] < df['open']              # 缺口當日收黑

    bearish_exhaustion = strong_uptrend & gap_up & overbought & bearish_candle

    return bearish_exhaustion

# 進階：缺口填補條件確認
gap_filled = df['low'] < df['close'].shift(1)  # 當日低點回落至昨日收盤以下
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：需先區分普通缺口、突破缺口、測量缺口與竭盡缺口，不能只因 gap 大就直接逆勢。
- 必要條件：缺口策略對成本與滑點高度敏感，必須以可成交價格而非理想缺口邊界回測。
- 必要條件：建議加入過熱條件，例如 `Gap_ZScore`、`RSI percentile`、連續單邊天數，避免在趨勢早期反做。
- 可選條件：把缺口大小、回補速度、首小時成交量、前波報酬率納入 feature set。
- 可選條件：加入市場狀態分類，僅在極端情緒與高波動反轉 regime 啟動。
- 可選條件：把「當日回補」與「數日回補」分成不同子策略獨立優化。

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 在趨勢末段提供絕佳的風報比 | 竭盡缺口和持續缺口難以即時區分 |
| 明確的進場、停損點 | 強勢趨勢中可能多次出現「假竭盡缺口」 |
| 逆勢策略，捕捉大幅反轉 | 需要等待確認，可能錯過部分反轉幅度 |

---

## 延伸閱讀

- *Technical Analysis of Stock Trends* — Robert Edwards & John Magee（缺口四分類的原始來源）
- *Encyclopedia of Chart Patterns* — Thomas Bulkowski（各類缺口的統計勝率）
- Bulkowski 的研究：竭盡缺口在 21 天內被填補的機率約 **72%**
