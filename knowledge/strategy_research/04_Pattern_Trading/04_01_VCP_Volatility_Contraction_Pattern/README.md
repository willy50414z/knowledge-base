# 04-01 VCP — Volatility Contraction Pattern（波動率收縮型態）

## 策略類型
**04 — Pattern Trading（型態突破）**

---

## 概述

波動率收縮型態（VCP）由美國超級交易員 **Mark Minervini** 在其著作《Trade Like a Stock Market Wizard》（2013）中系統性提出，並作為其 SEPA（Specific Entry Point Analysis）交易系統的核心進場型態。Minervini 是 1997 年美國投資錦標賽（USIC）冠軍，5 年年化報酬率超過 220%。

VCP 描述的是強勢股在大幅突破前，必然經歷的「浮額清洗（Shakeout）」過程：價格修正的幅度一次比一次小，成交量逐漸萎縮，代表籌碼越來越集中，浮動籌碼不斷被消化，最終彈簧壓縮到極限後爆發。

---

## 核心邏輯

> **「偉大的突破不會從震盪的高點直接突破，它需要先完成洗盤，讓弱勢籌碼出清。」**

VCP 的本質是：
1. 大資金在蓄積籌碼（壓低股價）
2. 弱勢散戶被「洗出場」
3. 籌碼集中到強勢持有者手中
4. 最後以極小的修正完成最後一次洗盤
5. 放量突破，啟動新一輪漲勢

---

## VCP 的識別標準 (量化嚴謹版)

### 核心特徵：收縮與狹窄度 (Tightness)
1. **收縮次數 (T 數)**：
   - `Volatility[n] < Volatility[n-1] * 0.7`。
   - 每次修正波段的幅度（高點到低點）必須呈遞減趨勢。
2. **狹窄度 (Tightness)**：
   - 最後一次收縮的幅度應小於當前股價的 `3%` 或是 `ATR(14) * 0.5`。
3. **成交量乾涸 (Volume Dry-out)**：
   - 在最後一次收縮區間，平均成交量應小於 `MA(Volume, 50) * 0.6`。

### 交易規則 (標籤: `VCP_Entry`)
- **進場 (Pivot)**：`Close > Max(Last_Contraction_High)` 且 `Volume > MA(Volume, 50) * 1.5`。
- **停損 (SL)**：`Last_Contraction_Low` 之下，或 `Entry_Price - 1.5 * ATR`。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化**：
   - **T-Count**: [2, 3, 4] (測試不同收縮次數的穩定度)。
   - **Lookback_Period**: [60, 120, 250] (型態醞釀的總長度)。
2. **PCA 分析點**：
   - **波動率衰減率**：分析從第一波到最後一波的衰減速度是否與後續漲幅正相關。
   - **相對強度 (RS)**：Minervini 非常強調 RS。在量化中需加入 `RS_Index > 80` 作為權重過濾。
3. **實作細節**：
   - 型態識別可利用 `ZigZag` 的極值來計算波段寬度，但須注意 `Order` 參數的選取會顯著改變 VCP 的檢測結果。建議對 `Order` 進行參數掃描。

---

## 關鍵指標

| 指標 | 用途 |
|------|------|
| **SMA (10/30/40 週)** | 確認多頭排列（大趨勢） |
| **ATR (14)** | 量化每次收縮的幅度（ATR 逐漸下降） |
| **成交量萎縮特徵** | 各次修正期間量能縮減 |
| **距前高的距離** | 突破時距離前高越近，型態越強 |

---

## 交易規則

### 進場
- **觸發**：在最後一次收縮的低點之上，出現**帶量收盤突破頸線（Pivot Point）**
- **頸線定義**：最近整理區間的最高點（通常是右側的小平台高點）
- **最佳進場**：突破頸線當日，或隔日確認成交量後

### 停損
- **絕對停損**：最後一次修正的低點下方（結構被破壞）
- **ATR 停損**：頸線突破點 - 1.5 × ATR(14)

### 目標
- 最少目標：突破高度 = 修正深度（整理箱高度的 1:1）
- 合理目標：前高之上；或以帶柄杯（Cup with Handle）的量度方法估算

---

## 量化實作

```python
def detect_vcp(df, window=60, min_contractions=2):
    """
    df: OHLCV DataFrame
    檢測最近 window 根 K 線內是否存在 VCP 型態
    """
    recent = df.tail(window).copy()

    # 計算 ATR 趨勢（應逐漸下降）
    recent['atr'] = compute_atr(recent, 14)
    atr_declining = recent['atr'].iloc[-1] < recent['atr'].iloc[-window//2]

    # 計算成交量趨勢（應逐漸萎縮）
    vol_ma20 = recent['volume'].rolling(20).mean()
    vol_contracting = recent['volume'].iloc[-5:].mean() < vol_ma20.iloc[-5:].mean()

    # 均線多頭排列
    sma10w = df['close'].rolling(50).mean()   # 近似10週
    sma30w = df['close'].rolling(150).mean()  # 近似30週
    bullish_ma = sma10w.iloc[-1] > sma30w.iloc[-1]
    price_above_ma = df['close'].iloc[-1] > sma10w.iloc[-1]

    # 近期高點（頸線）
    pivot = recent['high'].max()
    near_pivot = df['close'].iloc[-1] > pivot * 0.97  # 距頸線 3% 以內

    is_vcp = atr_declining and vol_contracting and bullish_ma and price_above_ma

    return {
        'is_vcp': is_vcp,
        'pivot': pivot,
        'atr_declining': atr_declining,
        'vol_contracting': vol_contracting
    }
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：每次收縮波需等右側結束後才確認，否則很容易把尚未完成的整理錯判成 VCP。
- 必要條件：需加入市場狀態與大盤趨勢過濾，VCP 在領漲族群與多頭環境中才較有優勢。
- 必要條件：回測需納入流動性、成交量與交易成本，因突破點常伴隨滑價。
- 可選條件：將收縮次數、ATR 壓縮率、量縮斜率、base 長度、接近前高程度做成 quality score。
- 可選條件：加入相對強弱排名，只在領先板塊中尋找 VCP。
- 可選條件：測試 breakout 後回踩 pivot 再進場的保守版本。

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 進場位置精確，風報比極佳 | 完整 VCP 型態需要數週或數月醞釀 |
| 籌碼乾淨，突破後持倉穩定 | 純量化定義困難，通常需要結合人工判斷 |
| Minervini 的歷史驗證極強 | 多數平庸股也會形成類似形狀但無效 |
| 停損點明確 | 市場整體環境差時，即使 VCP 也容易失敗 |

---

## 延伸閱讀

- *Trade Like a Stock Market Wizard* — Mark Minervini（2013）
- *Think and Trade Like a Champion* — Mark Minervini（2017）
- SEPA 系統：[minervini.com](https://www.minervini.com)
- 相關型態：Stage 2 Analysis（Stan Weinstein）、Cup with Handle（William O'Neil）
