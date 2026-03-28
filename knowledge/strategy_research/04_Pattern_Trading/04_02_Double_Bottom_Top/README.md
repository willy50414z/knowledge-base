# 04-02 Double Bottom / Top（W底 / M頭）

## 策略類型
**04 — Pattern Trading（型態學 / 反轉型態）**

---

## 概述

雙重底（Double Bottom / W底）和雙重頂（Double Top / M頭）是技術分析中最廣為人知的**反轉型態**之一，因其形狀分別像英文字母 W 和 M 而得名。這兩種型態的核心邏輯是：**市場在關鍵價格位置「測試」了兩次，均未能突破，反映出強大的買賣力量均衡後的轉向。**

這種型態最早由 **Richard Schabacker**（現代技術分析先驅之一）在 1930 年代系統化記錄，後由 **John Murphy**、**Thomas Bulkowski** 等人進一步量化研究。

---

## 核心邏輯

### W底（雙重底）
> **「兩次測試支撐不破，說明該位置有強大承接力量，突破頸線即確認反轉。」**

```
       頸線
  _____|_____
 /    |    \
/     |     \
底 1  |    底 2
      ↑
   (相近價位)
```

### M頭（雙重頂）
```
頂 1        頂 2
  \   頸線  /
   \___|___/
       |
      壓力
```

---

## 關鍵識別標準 (量化嚴謹版)

| 特徵 | W底 要求 | 量化定義 (標籤: `Param_W`) |
|------|---------|---------|
| **兩個低點價差** | < 3% | `abs(Low1 - Low2) / Low1 < Threshold` (Threshold 可優化: 1%-5%) |
| **兩個低點間距** | 至少 20 根 K 線 | `Distance(Low1, Low2) > 20 bars` |
| **頸線斜率** | 趨於水平 | `abs(Neckline_Left - Neckline_Right) / Price < 2%` |
| **成交量趨勢** | 第二底量縮 | `Avg_Vol(Bottom2) < Avg_Vol(Bottom1) * 0.8` |
| **突破確認** | 帶量突破 | `Close > Neckline` 且 `Volume > MA(Volume, 20) * 1.5` |

---

## 交易規則 (標籤: `Pattern_Execution`)

### 進場策略
- **觸發條件**：`Close` 站上 `Neckline`。
- **防止假突破**：增加一個 `Buffer`，例如 `Close > Neckline * 1.01`。
- **二次進場**：若價格回測 `Neckline` 且不跌破（`Low > Neckline`），則為第二買點。

### 停損與目標
- **停損 (SL)**：`min(Low1, Low2)` 或 `Neckline - 1.5 * ATR`。
- **量度目標 (TP)**：`Neckline + (Neckline - min(Low1, Low2))`。

---

## 量化優化方向 (Optimization Hooks)

1. **參數掃描 (Grid Search)**：
   - **Tolerance (價差門檻)**：[0.01, 0.02, 0.03, 0.05]。
   - **Separation (間距)**：[20, 40, 60] (決定型態的時間維度)。
2. **PCA 分析點**：
   - 分析 **第二個底部的成交量萎縮程度** 是否為後續漲幅的正向預測因子。
   - **RSI 底背離**：將「是否有 RSI 底背離」作為 W 底型態的附加權重，透過 PCA 評估其特徵貢獻。
3. **實作建議**：
   - 利用 `argrelextrema` 的 `order` 參數來捕捉不同週期的 W 底。大 `order` 捕捉大 W，小 `order` 捕捉微型 W。建議進行多週期併行檢測。

---

## 關鍵指標

| 指標 | 用途 |
|------|------|
| **支撐與壓力線（頸線）** | 定義 W/M 的關鍵突破位 |
| **成交量** | 確認兩個底/頂的量能關係 |
| **RSI** | 底背離（W底時 RSI 底背離）增強訊號可信度 |
| **均線** | 突破頸線時站上均線增強確認 |

---

## 交易規則

### W底做多
```
1. 識別：找到兩個相近低點（價差 < 3%），中間有明顯反彈
2. 頸線：連接兩個低點之間的最高反彈點
3. 等待：價格向上突破頸線
4. 確認：突破當日或次日成交量放大 > 均量 1.5 倍
5. 進場：突破確認後即時進場，或等待回測頸線後進場
6. 停損：第二個低點（P2）下方（型態被破壞）
7. 目標：頸線 + (頸線 - 底部) 的距離（量度推算）
```

**量度目標計算：**
```
W底目標 = 頸線 + (頸線 - 底部低點)
例：底部 = 100，頸線 = 115
    目標 = 115 + (115 - 100) = 130
```

### M頭做空（對稱邏輯）
```
1. 識別：兩個相近高點，中間有明顯回調
2. 等待跌破頸線（兩個高點中間的低點）
3. 進場做空，停損在第二個高點之上
4. 目標 = 頸線 - (高點 - 頸線)
```

---

## 量化實作

```python
def detect_double_bottom(df, tolerance=0.03, min_separation=20, max_separation=120):
    """
    尋找雙重底型態
    tolerance: 兩個低點的最大價差比例
    min/max_separation: 兩個低點的最小/最大間距（K線數）
    """
    from scipy.signal import argrelextrema
    import numpy as np

    close = df['close']
    low = df['low']

    # 找局部低點
    local_lows = argrelextrema(low.values, np.less, order=5)[0]

    patterns = []

    for i in range(1, len(local_lows)):
        idx1, idx2 = local_lows[i-1], local_lows[i]
        separation = idx2 - idx1

        if not (min_separation <= separation <= max_separation):
            continue

        p1, p2 = low.iloc[idx1], low.iloc[idx2]

        # 兩個低點價格接近
        price_diff = abs(p1 - p2) / p1
        if price_diff > tolerance:
            continue

        # 找頸線（兩個低點之間的最高點）
        neckline = close.iloc[idx1:idx2].max()

        # 確認：第二個低點後的突破
        future_close = close.iloc[idx2:]
        breakout_idx = future_close[future_close > neckline].index

        if len(breakout_idx) > 0:
            patterns.append({
                'bottom1_idx': idx1,
                'bottom2_idx': idx2,
                'bottom1_price': p1,
                'bottom2_price': p2,
                'neckline': neckline,
                'breakout_idx': breakout_idx[0],
                'target': neckline + (neckline - min(p1, p2))
            })

    return patterns
```

---

## Thomas Bulkowski 的統計數據

根據 *Encyclopedia of Chart Patterns*（Thomas Bulkowski）的大量回測：

| 指標 | W底 | M頭 |
|------|-----|-----|
| **突破後 5% 以上的達成率** | 約 73% | 約 68% |
| **平均漲幅/跌幅** | +35% | -22% |
| **失敗率（突破後反轉）** | 約 11% | 約 14% |
| **量能放大突破的成功率** | 顯著更高 | 顯著更高 |

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：兩個谷底或峰頂必須用一致的 pivot window 定義，並加入最短間隔，避免把噪音雙測試誤判成型態。
- 必要條件：頸線突破建議以收盤或 next-bar 突破確認，不能直接使用型態形成中的最高點偷看未來。
- 必要條件：回測需計入手續費與滑點，W/M 型態常需要等待回測頸線，成交價差異很大。
- 可選條件：將雙底間距、價差百分比、頸線斜率、量能收縮與突破量比做成 feature。
- 可選條件：加入大盤 regime filter，逆勢反轉型態在強趨勢市場失效率通常更高。
- 可選條件：測試 neckline retest 成交與直接 breakout 成交的風報差異。

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 訊號明確，進場停損目標清晰 | 等待型態完成時間長，錯過部分漲幅 |
| 量度目標提供客觀的利潤預期 | 頸線突破後容易出現「假突破回測」 |
| 在任何時間框架均有效 | 程式化識別需要滾動視窗和容錯設計 |

---

## 延伸閱讀

- *Encyclopedia of Chart Patterns* — Thomas Bulkowski（含詳細統計）
- *Technical Analysis of the Financial Markets* — John Murphy
- TradingView 的 Pattern Recognition 工具
