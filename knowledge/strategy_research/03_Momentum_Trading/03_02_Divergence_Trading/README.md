# 03-02 Divergence Trading（指標背離策略）

## 策略類型
**03 — Momentum Trading（動能交易 / 反轉）**

---

## 概述

指標背離策略是技術分析中最經典的反轉（或趨勢減弱）訊號識別方法之一。**背離（Divergence）**是指價格走勢與動能指標走勢出現方向不一致的現象，反映**趨勢背後的推動力正在衰竭**，即將發生轉折或至少是顯著的調整。

背離的概念由 **Gerald Appel**（MACD 發明者）和 **J. Welles Wilder**（RSI 發明者）在其著作中廣泛討論。

---

## 核心邏輯

> **「價格創新高（低），但動能指標沒有跟上，說明趨勢的『燃料』正在耗盡。」**

類比：一輛車在油門越踩越少的情況下仍在前進，速度遲早會下降。

---

## 背離的四種類型

### 1. 頂背離（Bearish Regular Divergence）
```
價格：Higher High（新高）
指標：Lower High（未創新高）
→ 上漲動能衰竭，可能即將下跌
```

### 2. 底背離（Bullish Regular Divergence）
```
價格：Lower Low（新低）
指標：Higher Low（未創新低）
→ 下跌動能衰竭，可能即將反彈
```

### 3. 隱性頂背離（Bearish Hidden Divergence）
```
價格：Lower High（回調未到前高）
指標：Higher High（指標創新高）
→ 空頭趨勢延續訊號，反彈後繼續下跌
```

### 4. 隱性底背離（Bullish Hidden Divergence）
```
價格：Higher Low（回調高於前低）
指標：Lower Low（指標創新低）
→ 多頭趨勢延續訊號，回調後繼續上漲
```

---

## 關鍵指標

| 指標 | 特點 |
|------|------|
| **RSI (14)** | 最常用，反應靈敏，適合短中線 |
| **MACD 柱狀圖** | 適合趨勢轉折，長線效果較佳 |
| **隨機指標 KD (9,3,3)** | 較靈敏，適合短線和震盪市場 |
| **OBV (能量潮)** | 透過成交量確認，更為可靠 |

---
## 交易規則 (量化嚴謹版)

### 底背離做多邏輯 (標籤: `Divergence_Trigger`)
1. **結構識別 (Pattern)**：
   - 價格低點：`P2 < P1`。
   - 指標低點：`R2 > R1`。
   - **間隔約束**：`5 < Distance(P1, P2) < 50` 根 K 線 (避免背離時間過長失效)。
2. **即時確認 (Confirmation - 關鍵)**：
   - ~~在第二個低點 (P2) 附近進場~~
   - **量化做法**：由於 `P2` 是局部極值，需等待 `N` 根 K 線確認轉折（如 `Close > High[P2]` 或 `RSI > RSI[P2]` 且已勾頭向上）。
3. **過濾條件**：
   - `R1` 必須處於超賣區 (`RSI < 30`)，`R2` 可以不進入超賣區，代表動能減弱。

### 停損與獲利
- **停損 (SL)**：`P2 - 0.5 * ATR`。
- **目標 (TP)**：回歸至前波高點或利用 `MACD 死亡交叉` 出場。

---

## 量化實作要點 (標籤: `Anti_Future_Function`)

1. **避免未來函數**：
   在回測中，不可在 `P2` 當下進場，因為當時還不知道那是最低點。
   ```python
   # 正確做法：右側確認
   if is_local_min(price, index-2, window=2): # 延後兩根 K 線確認
       if current_price > price[index-2]:
           enter_trade()
   ```
2. **優化空間 (Optimization Hooks)**：
   - **指標選擇**：PCA 分析 RSI vs MACD vs Stochastic 在背離訊號上的勝率差異。
   - **窗口大小 (Order)**：[3, 5, 10] 影響訊號頻率與準確性。
3. **隱性背離 (Hidden Divergence)**：
   將隱性背離加入策略作為「趨勢延續」的加碼訊號，與常規背離構成完整系統。
    # 找局部低點
    price_lows = argrelextrema(price.values, np.less, order=order)[0]
    ind_lows = argrelextrema(indicator.values, np.less, order=order)[0]

    divergence_signals = []

    for i in range(1, len(price_lows)):
        p_idx1, p_idx2 = price_lows[i-1], price_lows[i]

        # 找對應的指標低點
        ind_idx = ind_lows[(ind_lows >= p_idx1) & (ind_lows <= p_idx2)]
        if len(ind_idx) < 2:
            continue

        p1, p2 = price.iloc[p_idx1], price.iloc[p_idx2]
        r1, r2 = indicator.iloc[ind_idx[0]], indicator.iloc[ind_idx[-1]]

        # 底背離：價格創新低但指標未創新低
        if p2 < p1 and r2 > r1:
            divergence_signals.append({
                'type': 'bullish_divergence',
                'index': p_idx2,
                'price_low': p2,
                'rsi_low': r2
            })

    return divergence_signals
```

---

## 實作注意事項

1. **背離不等於立即反轉**：背離可能持續多根 K 線後才真正反轉，需要等待觸發確認
2. **時間框架一致性**：比較的兩個高/低點必須在同一時間框架
3. **滾動視窗大小**：窗口太小 → 噪音太多；窗口太大 → 訊號太少
4. **趨勢過濾**：底背離更適合在整體空頭市場的局部反彈，非牛市中追求頂部
5. **量能確認**：背離的第二個低點若伴隨縮量，反轉可信度更高

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：價格與指標的局部極值需用同一套 pivot confirmation 規則產生，避免人眼背離與程式背離定義不一致。
- 必要條件：回測需納入交易成本，背離策略進出頻率不低，且常在波動放大時成交。
- 必要條件：建議加主趨勢濾網，區分逆勢 regular divergence 與順勢 hidden divergence 的適用 regime。
- 可選條件：將 `pivot_distance`、`indicator_slope`、`price_slope`、`divergence_age` 做成特徵供 PCA。
- 可選條件：加入多指標共振分數，測試 RSI、MACD Histogram、Stoch 的加權方式。
- 可選條件：建立失效標籤，例如背離後 `N` 根內再創新低/高，供後續分類模型學習。

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 提早識別趨勢衰竭，可以「左側建倉」 | 假背離頻繁，在強趨勢中可能提前進場 |
| 風報比好（進場位置接近支撐/壓力） | 程式化判斷局部極值有技術難度 |
| 可搭配任何動能指標使用 | 背離存在主觀性，不同人識別可能不同 |

---

## 延伸閱讀

- *Technical Analysis of the Financial Markets* — John Murphy（背離章節）
- *New Concepts in Technical Trading Systems* — J. Welles Wilder（RSI 原著）
- Andrew Cardwell：RSI 的進階應用，重新詮釋背離的意義
