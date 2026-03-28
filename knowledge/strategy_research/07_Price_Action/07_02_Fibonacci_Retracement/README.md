# 07-02 Fibonacci Retracement（斐波那契回撤）

## 策略類型
**07 — Price Action（支撐壓力 / 比例分析）**

---

## 概述

斐波那契回撤（Fibonacci Retracement）是技術分析中最廣泛使用的工具之一，基於 13 世紀義大利數學家 **列奧納多·斐波那契（Leonardo Fibonacci）** 發現的斐波那契數列，以及由此衍生的**黃金比例（Golden Ratio）0.618**。

技術分析師將這些比例應用於金融市場，認為**價格在趨勢中的回調（Retracement）往往在特定的黃金比例位置找到支撐或壓力**，反映了市場參與者的群體心理和自然週期規律。

> **Ralph Nelson Elliott** 在其波浪理論（Elliott Wave Theory）中大量使用斐波那契比例來預測波段目標，使其成為主流技術分析工具。

---

## 斐波那契數列與黃金比例

```
斐波那契數列：1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144...
（每一項 = 前兩項之和）

關鍵比例：
  相鄰項比值 → 0.618（黃金比例 φ⁻¹）
  隔一項比值 → 0.382（= 1 - 0.618）
  隔兩項比值 → 0.236

衍生比例：
  0.786 = √0.618（蝙蝠型態的 D 點）
  1.272 = √2（延伸目標）
  1.618 = φ（黃金比例本身）
  2.618 = φ²
```

---

## 核心回撤比例

| 比例 | 來源 | 意義 |
|------|------|------|
| **23.6%** | 斐波那契比例 | 淺回撤（強勢趨勢） |
| **38.2%** | 1 - 0.618 | 中等回撤支撐 |
| **50.0%** | 心理整數 | 非斐氏比例，但廣泛使用 |
| **61.8%** | 黃金比例倒數 | **最重要的回撤位** |
| **78.6%** | √0.618 | 深度回撤（諧波型態使用）|

---

## 如何畫斐波那契回撤

```
步驟：
1. 識別一段明顯的價格波段（高點和低點）
2. 工具起點（0%）= 波段起點
3. 工具終點（100%）= 波段終點
4. 自動計算各回撤比例的絕對價格

上漲趨勢中的回撤支撐：
  回撤支撐價格 = 高點 - (高點 - 低點) × 比例
  例：低點 = 100，高點 = 150
      38.2% 支撐 = 150 - (150-100) × 0.382 = 130.9
      61.8% 支撐 = 150 - (150-100) × 0.618 = 119.1
```

---

## 斐波那契延伸（Fibonacci Extension）

用於估算**突破後的潛在目標位**：

| 延伸比例 | 意義 |
|---------|------|
| **100%** | 等幅延伸 |
| **127.2%** | 常見第一目標 |
| **161.8%** | 黃金延伸，最常用目標 |
| **261.8%** | 強勢延伸目標 |

```python
# 延伸目標計算（在波段 A→B 回調至 C 後的目標）
# AB 為初始波段，BC 為回調，CD 為延伸
extension_1618 = C + (B - A) * 1.618
extension_1272 = C + (B - A) * 1.272
```

---

## 交易規則 (量化嚴謹版)

### 1. 波段識別 (Swing Identification)
- 使用 `argrelextrema(order=N)` 自動鎖定波段高低點。`N` 建議設為 20-50 以捕捉顯著趨勢。

### 2. 匯聚區權重 (Confluence Score) (標籤: `Fib_Confluence`)
單獨的斐波那契位勝率有限，量化實作需結合以下因子計算 **Confluence Score**：
- **Fib_Level** (0.618 / 0.5): +3 分
- **Horizontal_Support** (前高/前低重疊): +2 分
- **EMA_Support** (如 EMA 200): +2 分
- **Round_Number** (整數關卡): +1 分
- **總分 >= 5** 為高信賴度進場點。

### 3. 進場與停損 (標籤: `Fib_Execution`)
- **掛單策略**：在 0.618 匯聚區提前掛出 `Limit Order`。
- **停損 (SL)**：`Entry_Price - (High - Low) * 0.1` 或收盤跌破 `78.6%`。
- **目標 (TP)**：`1.618 * (High - Low)` 延伸位。

---

## 量化優化方向 (Optimization Hooks)

1. **參數掃描 (Grid Search)**：
   - **Swing_Order**: [20, 40, 60] (決定趨勢波段的大小)。
   - **Entry_Level**: [0.382, 0.5, 0.618] (測試不同回撤深度在特定資產的勝率)。
2. **PCA 與特徵貢獻度**：
   - 分析 **「回撤速度 (Time to Retrace)」**。緩慢回撤至 0.618 的勝率通常高於 V 型暴跌回撤。
   - 利用 PCA 分析上述 Confluence 因子中，哪一項對獲利貢獻最大。
3. **實作注意**：
   - 斐波那契位適合作為 **「限價單集群 (Limit Order Cluster)」** 的參考，而非市價單。回測時需考慮滑點與成交機率。

---

## 量化實作

```python
def fibonacci_levels(swing_high, swing_low, trend='up'):
    """
    計算斐波那契回撤位
    trend: 'up' = 上漲趨勢中的回撤；'down' = 下跌趨勢中的反彈
    """
    ratios = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    extension_ratios = [1.0, 1.272, 1.618, 2.618]
    diff = swing_high - swing_low

    if trend == 'up':
        # 上漲趨勢：從高點往下計算回撤支撐
        retracements = {
            f"{r*100:.1f}%": swing_high - diff * r
            for r in ratios
        }
        extensions = {
            f"{r*100:.1f}%": swing_high + diff * (r - 1.0)
            for r in extension_ratios
        }
    else:
        # 下跌趨勢：從低點往上計算反彈壓力
        retracements = {
            f"{r*100:.1f}%": swing_low + diff * r
            for r in ratios
        }

    return retracements

def auto_detect_swings_and_fibs(df, lookback=60):
    """
    自動識別波段高低點並計算斐波那契水平
    """
    from scipy.signal import argrelextrema
    import numpy as np

    close = df['close'].values
    high = df['high'].values
    low = df['low'].values

    # 找局部高點和低點
    local_highs = argrelextrema(high, np.greater, order=5)[0]
    local_lows = argrelextrema(low, np.less, order=5)[0]

    # 取最近一個完整波段
    if len(local_highs) > 0 and len(local_lows) > 0:
        last_high_idx = local_highs[-1]
        last_low_idx = local_lows[-1]

        if last_high_idx > last_low_idx:
            # 下跌後回彈中 → 計算下跌波段的斐波那契反彈壓力
            swing_high = high[last_high_idx]
            swing_low = low[last_low_idx]
            levels = fibonacci_levels(swing_high, swing_low, trend='down')
        else:
            # 上漲後回調中 → 計算上漲波段的斐波那契回撤支撐
            swing_low = low[last_low_idx]
            swing_high = high[last_high_idx]
            levels = fibonacci_levels(swing_high, swing_low, trend='up')

        return levels

def auto_place_limit_orders(levels, current_price, budget, key_levels=[0.618, 0.5, 0.382]):
    """
    在關鍵斐波那契位自動掛限價單
    """
    orders = []
    for level_name, price in levels.items():
        ratio = float(level_name.strip('%')) / 100
        if ratio in key_levels and price < current_price:
            orders.append({
                'price': price,
                'quantity': budget / len(key_levels) / price,
                'level': level_name,
                'stop_loss': levels.get('78.6%', price * 0.95)
            })
    return orders
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：波段高低點的選取必須可重現，建議使用固定 swing 規則，而非人工主觀拉點。
- 必要條件：回撤位僅是潛在反應區，不宜單獨作為成交依據，需搭配結構、量能或趨勢濾網。
- 必要條件：需加入交易成本與停損位置模擬，因 Fib 掛單策略容易反覆試單。
- 可選條件：將 `Fib level touched`、`Confluence Score`、`Swing Strength`、`Retracement Speed` 做成 feature。
- 可選條件：把 extension 目標、前高壓力、VWAP/均線匯聚整合為多因子權重。
- 可選條件：區分 trend pullback 與 counter-trend bounce 兩種子策略分開調優。

---

## 自動掛單策略

根據 CSV 描述，此策略可實現全自動化：
1. 使用 ZigZag 指標自動識別波段高低點
2. 計算 0.618 位置的絕對價格
3. 在該位置自動掛出限價買單（Limit Order）
4. 停損設在 0.786 之下（若跌破則結構被破壞）

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 廣泛使用，具有「自我實現」效應 | 事後選擇哪個回撤位成功存在主觀性 |
| 提供客觀的支撐壓力預估 | 市場不總是在精確比例位置反轉 |
| 適合自動化掛限價單 | 波段起終點的選擇影響計算結果 |
| 可與其他分析工具完美結合 | 單獨使用斐波那契成功率不穩定 |

---

## 延伸閱讀

- *Technical Analysis of the Financial Markets* — John Murphy（斐波那契章節）
- *Elliott Wave Principle* — Frost & Prechter（波浪理論中的斐波那契應用）
- *Fibonacci Ratios with Pattern Recognition* — Larry Pesavento
- TradingView 的 Fibonacci Retracement 工具教學
