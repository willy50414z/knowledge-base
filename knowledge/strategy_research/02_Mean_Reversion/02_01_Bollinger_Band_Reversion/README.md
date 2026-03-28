# 02-01 Bollinger Band Reversion（布林通道回歸）

## 策略類型
**02 — Mean Reversion（均值回歸）**

---

## 概述

布林通道回歸策略基於統計學中的**均值回歸（Mean Reversion）**原理：市場價格短期內可能偏離均值，但長期存在回歸平均水平的傾向。**John Bollinger** 於 1980 年代發展出布林通道（Bollinger Bands），並於 2001 年出版《Bollinger on Bollinger Bands》系統化記錄此方法。

策略假設：**大多數收盤價落在通道內（統計上約 95% 的時間）**，當價格觸及通道邊緣時，代表極端偏離，回彈機率高。

---

## 核心邏輯

> **「市場在常態分佈中震盪，觸及極端值後必然均值回歸。」**

布林通道是基於統計學的動態區間：
```
中軌 = 20 期簡單移動平均（SMA）
上軌 = SMA + 2 × 標準差（σ）
下軌 = SMA - 2 × 標準差（σ）
```

- 約 **68%** 的收盤價落在 ±1σ 範圍內
- 約 **95%** 的收盤價落在 ±2σ 範圍內
- 約 **99.7%** 的收盤價落在 ±3σ 範圍內

---

## 關鍵指標

| 指標 | 參數 | 用途 |
|------|------|------|
| **布林通道 (Bollinger Bands)** | 20 期 SMA，±2σ | 定義超買超賣邊界 |
| **RSI** | 14 期 | 確認動能方向，避免逆勢強勢趨勢 |
| **成交量** | 20 期均量 | 確認反彈量能是否充足 |
| **布林帶寬（%B）** | — | 衡量相對位置（0 = 下軌，1 = 上軌） |

---

## 交易規則 (量化嚴謹版)

### 做多進場 (標籤: `Mean_Reversion_Long`)
| 條件 | 量化定義 | 說明 |
|------|------|------|
| **觸及邊界** | `Close < Lower_Band` | ~~跌破下軌~~ 建議使用收盤價確認，減少穿刺假訊號 |
| **超賣過濾** | `RSI(14) < 35` | 容許範圍優化為 30-40 |
| **趨勢過濾** | `ADX(14) < 25` | **必要條件**：避免在強勢下降趨勢中接刀 |
| **反轉確認** | `Close > Open` | (可選) 出現陽線確認反彈 |

### 做空進場 (標籤: `Mean_Reversion_Short`)
| 條件 | 量化定義 | 說明 |
|------|------|------|
| **觸及邊界** | `Close > Upper_Band` | 突破上軌 |
| **超買過濾** | `RSI(14) > 65` | 容許範圍優化為 60-70 |
| **趨勢過濾** | `ADX(14) < 25` | 避免在強勢上升趨勢中做空 |

### 出場與停損
- **獲利目標 (TP)**：價格回歸 **中軌 (SMA 20)**。
- **動態獲利**：若動能極強，可分批在「中軌」與「對側 1σ」平倉。
- **強硬停損 (SL)**：~~收盤再次突破同方向的 2.5σ~~ `Close < Lower_Band - 0.5 * ATR`。

---

## 量化優化方向 (Optimization Hooks)

1. **參數空間分析**：
   - **Period**: [10, 20, 30, 50] (影響回歸的平均週期)
   - **StdDev**: [1.5, 2.0, 2.5] (影響進場頻率與勝率)
   - **ADX Threshold**: [20, 25, 30] (決定策略在何種強度下失效)
2. **PCA 優化建議**：
   - 使用 PCA 分析 **RSI** 與 **%B** 指標的線性相關性，若重疊過高，可考慮移除其一。
   - **Bandwidth (帶寬)**：`(Upper - Lower) / Middle`，當帶寬過窄（擠壓）時，回歸策略通常失效，應停止交易。

---

## 量化實作

```python
import pandas as pd
import numpy as np

def bollinger_bands(close, period=20, std_dev=2):
    sma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = sma + std_dev * std
    lower = sma - std_dev * std
    return sma, upper, lower

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

sma, upper, lower = bollinger_bands(close)
rsi_values = rsi(close)

# 買入訊號
buy_signal = (close < lower) & (rsi_values < 30)
# 賣出訊號
sell_signal = (close > upper) & (rsi_values > 70)
# 平倉
exit_long = close > sma
exit_short = close < sma
```

---

## 進階變形：網格交易版本

布林通道回歸非常適合改造為**自動化網格交易機器人**：

```
下軌附近掛多單：下軌 × 1.0, 下軌 × 0.99, 下軌 × 0.98
目標全部設在中軌附近
停損設在下軌 × 0.95（突破 3σ）
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：策略必須先確認處於非趨勢市，除 `ADX` 外也可加入 `Hurst exponent`、`Bandwidth percentile` 或均線斜率。
- 必要條件：回測需計入雙邊手續費與滑點，均值回歸常靠小利累積，成本足以吃掉表面 alpha。
- 必要條件：需明確設定時間停損，若價格長時間貼著外軌不回中軌，應視為 regime 失效。
- 可選條件：把 `%B`、`Bandwidth`、`Distance_to_VWAP`、`RSI` 組成 feature matrix 做 PCA。
- 可選條件：加入事件黑名單，避開財報、宏觀數據、公鏈升級等會破壞常態波動假設的時段。
- 可選條件：分開測試「觸軌即進」與「回到帶內才進」兩種進場定義的差異。

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 邏輯直覺、數學基礎清晰 | 強趨勢行情中連續觸及通道邊緣，逆勢持續虧損 |
| 參數少，容易實作 | 需判斷市場是否處於震盪而非趨勢 |
| 適合震盪市場，勝率相對較高 | 標準差計算對極端值敏感 |
| 可輕易改造為自動化機器人 | 20 期 SMA 的滯後性 |

---

## 進階過濾：趨勢過濾器

**關鍵改善**：在強趨勢市場中，均值回歸策略會持續虧損。建議加入趨勢過濾：

```python
# 只在非強趨勢市場中使用均值回歸
adx = average_directional_index(period=14)
is_ranging = adx < 25  # ADX < 25 代表震盪市場

if is_ranging and buy_signal:
    enter_long()
```

---

## 延伸閱讀

- *Bollinger on Bollinger Bands* — John Bollinger（2001）
- John Bollinger 官網：BollingerBands.com
- %B 與 Bandwidth 指標的詳細說明
- Keltner Channel（類似但用 ATR 替代標準差）作為比較
