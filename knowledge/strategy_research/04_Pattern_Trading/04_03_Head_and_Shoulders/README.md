# 04-03 Head and Shoulders（頭肩底 / 頭肩頂）

## 策略類型
**04 — Pattern Trading（型態學 / 反轉型態）**

---

## 概述

頭肩型態（Head and Shoulders）是技術分析中**最可靠的趨勢反轉型態之一**，被學術研究和實務交易者廣泛驗證。**頭肩頂（Head and Shoulders Top）**出現在上升趨勢末端，預示下跌；**頭肩底（Inverse Head and Shoulders / Head and Shoulders Bottom）**出現在下跌趨勢末端，預示上漲。

此型態由三個峰值（谷值）組成：中間的「頭部」最極端，兩側的「肩部」較為對稱。**頸線（Neckline）**是連接兩個肩部之間谷點（峰點）的關鍵支撐壓力線，突破頸線即為進場訊號。

---

## 型態結構

### 頭肩頂（做空型態）
```
    頭
   /  \
左肩    右肩
  \    /
   頸線
    ↓
  突破做空
```

| 組件 | 說明 |
|------|------|
| **左肩（Left Shoulder）** | 上漲趨勢中的一個高點，隨後回調 |
| **頭部（Head）** | 比左肩更高的新高點，之後下跌 |
| **右肩（Right Shoulder）** | 反彈但未能超過頭部，高度接近左肩 |
| **頸線（Neckline）** | 連接左肩和頭部之間的谷底、以及頭部和右肩之間的谷底 |

### 頭肩底（做多型態）
```
  頸線
    ↑
   /  \
左肩    右肩
  \    /
    頭
```

---

## 關鍵識別標準 (量化嚴謹版)

| 標準 | 理想條件 | 量化定義 (標籤: `Param_HS`) |
|------|---------|---------|
| **左右肩對稱性** | 價差 < 5% | `abs(LS_Price - RS_Price) / LS_Price < 0.05` |
| **頭部高度** | 高於肩部 | `Head_Price > Max(LS_Price, RS_Price) + ATR * 1.5` |
| **頸線斜率** | 角度平緩 | `abs(Neck_Left - Neck_Right) / Distance < 0.02` (防止過斜導致失效) |
| **成交量特徵** | 右肩縮量 | `Vol_RS < Vol_LS * 0.7` |
| **突破確認** | 帶量突破頸線 | `Close < Neckline` (頂) 或 `Close > Neckline` (底) 且 `Vol > MA*1.5` |

---

## 交易規則 (標籤: `HS_Execution`)

### 進場
- **觸發點**：收盤確認突破頸線。
- **過濾條件**：若頸線向下傾斜（做多型態），突破更具看漲意義；反之亦然。
- **回測進場**：在 `Close` 突破後，掛 `Limit Order` 於 `Neckline` 價位等待回測。

### 停損與目標
- **停損 (SL)**：`RS_Price` 之外（結構破壞）。
- **目標 (TP)**：`Neckline ± (Head - Neckline)` 的 100% 或 161.8% 投射。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化**：
   - **Symmetry_Tolerance**: [0.03, 0.05, 0.10]。
   - **Neckline_Slope_Max**: [0.01, 0.02, 0.05]。
2. **PCA 與降維建議**：
   - 使用 **MACD 背離** 作為頭肩型態的數值化指標（Feature Engineering）。
   - 分析 **頭部與肩部的「寬度比」**。實務上，頭部與肩部的持續時間比例接近 1:1 時最為穩定。
3. **數據同步**：
   - 在量化實作中，頭肩型態常被視為 `W底` 或 `M頭` 的變體，可將這三類型態彙整為一套「支撐壓力測試」系統。

---

## 交易規則

### 頭肩底做多
```
1. 識別三個低點：左肩(LS) < 頭(H) > 右肩(RS)，且 LS 和 RS 接近
2. 畫頸線：連接 LS 後的高點和 H 後的高點
3. 等待：收盤帶量突破頸線
4. 進場：
   (a) 激進：突破頸線當日進場
   (b) 保守：等待突破後回測頸線不破再進場
5. 停損：右肩低點下方
6. 目標：頸線 + (頸線 - 頭部低點的距離)
```

### 量度目標
```
頭肩底目標 = 頸線 + (頸線 - 頭部最低點)
頭肩頂目標 = 頸線 - (頭部最高點 - 頸線)
```

---

## 量化實作方法

### 方法一：三波段識別（ZigZag 輔助）
```python
from scipy.signal import argrelextrema
import numpy as np

def detect_head_and_shoulders_bottom(df, order=10, tolerance=0.05):
    """
    識別頭肩底型態
    order: 局部極值確認窗口
    tolerance: 左右肩高度差容忍度
    """
    low = df['low'].values

    # 找局部低點
    local_lows_idx = argrelextrema(low, np.less, order=order)[0]

    patterns = []

    for i in range(2, len(local_lows_idx)):
        rs_idx = local_lows_idx[i]
        head_idx = local_lows_idx[i-1]
        ls_idx = local_lows_idx[i-2]

        ls = low[ls_idx]
        head = low[head_idx]
        rs = low[rs_idx]

        # 頭部必須低於兩肩
        if not (head < ls and head < rs):
            continue

        # 兩肩高度接近
        shoulder_diff = abs(ls - rs) / ls
        if shoulder_diff > tolerance:
            continue

        # 找頸線（兩個肩部間的高點）
        neckline_left = df['high'].iloc[ls_idx:head_idx].max()
        neckline_right = df['high'].iloc[head_idx:rs_idx].max()
        neckline = (neckline_left + neckline_right) / 2

        # 計算目標
        target = neckline + (neckline - head)

        patterns.append({
            'ls_idx': ls_idx, 'head_idx': head_idx, 'rs_idx': rs_idx,
            'ls_price': ls, 'head_price': head, 'rs_price': rs,
            'neckline': neckline,
            'target': target
        })

    return patterns
```

### 方法二：MACD 替代方案（程式化更穩定）
> **實務建議**：純量化交易員常用 **MACD 底背離** 捕捉類似頭肩底的精神，而非死磕 K 線圖形識別：
```python
# MACD 柱狀圖底背離 = 近似頭肩底的量化版本
macd_hist_low1 = ...  # 第一個低點
macd_hist_low2 = ...  # 第二個低點（高於第一個 = 底背離）
price_low1 = ...       # 第一個價格低點
price_low2 = ...       # 第二個價格低點（低於第一個）

bullish_divergence = (price_low2 < price_low1) and (macd_hist_low2 > macd_hist_low1)
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：左右肩與頭部的 pivot 必須在結束後確認，否則頭肩型態最容易產生 look-ahead bias。
- 必要條件：頸線突破需定義為收盤確認或下一根 stop order 觸發，避免盤中穿越即視為成立。
- 必要條件：回測需納入交易成本與型態完成時間成本，因這類型態形成週期長、交易次數少。
- 可選條件：將肩部對稱度、頭部深度/高度、頸線斜率、右肩量縮比率納入 feature engineering。
- 可選條件：加入 trend exhaustion 因子，例如 MACD histogram、RSI divergence 作為附加確認。
- 可選條件：把頭肩底與 W 底視為同一類 reversal family，統一建 quality score。

---

## Thomas Bulkowski 統計數據

| 型態 | 突破成功率 | 平均漲跌幅 | 量度目標達成率 |
|------|-----------|-----------|-------------|
| **頭肩底** | 約 83% | +38% | 約 63% |
| **頭肩頂** | 約 77% | -23% | 約 55% |

*（數據來源：Encyclopedia of Chart Patterns, Thomas Bulkowski）*

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 學術與實務驗證充分，可信度高 | 型態識別程式化難度較高 |
| 量度目標明確 | 頸線突破後常有「回測頸線」的假動作 |
| 兩肩對稱提供明確的停損參考 | 耗時，需要數週至數月才能完成 |

---

## 延伸閱讀

- *Technical Analysis of Stock Trends* — Edwards & Magee（頭肩型態的詳細分析）
- *Encyclopedia of Chart Patterns* — Thomas Bulkowski
- Edwards, Magee & Bassetti: *Technical Analysis of Stock Trends*, 10th Edition
