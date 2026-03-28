# 04-05 Cup and Handle（杯柄型態）

## 策略類型
**04 — Pattern Trading（型態學 / 延續型態）**

---

## 概述

杯柄型態（Cup and Handle）由成長股大師 **William J. O'Neil** 於 1988 年在其著作《How to Make Money in Stocks》中首次系統性描述，並作為其 **CANSLIM 系統**（一套結合基本面與技術面的選股方法）的核心進場型態。O'Neil 創辦了《Investor's Business Daily》報紙，其 CANSLIM 系統被廣泛認為是 20 世紀最成功的個人投資方法之一。

此型態在股票市場中最常見，但加密貨幣中也有效。它代表**一個長期整理後的突破**，往往出現在即將進入加速上漲的強勢股身上。

---

## 型態結構

```
        頸線（前高）
前高→  |           |
       |    杯身    |  柄 |→ 突破
       |  (圓弧底)  |    |
       |___________|     |
```

| 組件 | 說明 |
|------|------|
| **杯身（Cup）** | 從前高下跌後的圓弧底部，回調深度通常 12-33%，整理時間 1 週到 65 週 |
| **杯沿（Cup Rim / Neckline）** | 回到前高附近（右側高點，通常在前高的 5% 以內） |
| **杯柄（Handle）** | 在前高附近出現的小幅回調整理（幅度 5-12%），成交量萎縮 |
| **突破（Pivot Point）** | 突破杯柄整理區間高點 |

---

## O'Neil 的 CANSLIM 標準

## 核心規則 (量化嚴謹版)

### 1. 杯身要求 (The Cup)
- **回調深度**：`12% < Depth < 33%`。
- **時間維度**：`T_Cup > 30 bars` (確保不是 V 型反轉)。
- **成交量分佈**：杯底應伴隨成交量顯著萎縮（`Vol < MA_Vol * 0.7`），形成 **U 型成交量分佈**。

### 2. 杯柄要求 (The Handle)
- **相對位置 (關鍵)**：`Handle_Low > (Cup_High + Cup_Low) / 2` (必須在杯身的上半部)。
- **回調深度**：`Handle_Depth < 12%`。
- **成交量**：柄部成交量必須是整個型態中的最低點。

### 3. 進場觸發 (The Breakout) (標籤: `Cup_Entry`)
- **Pivot Point**：柄部的最高點。
- **觸發條件**：`Close > Pivot` 且 `Volume > MA(Vol, 10) * 1.4`。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化**：
   - **Cup_Depth_Max**: [0.20, 0.33, 0.50]。
   - **Handle_Position**: [0.5, 0.6, 0.7] (柄部在杯身的相對百分比)。
2. **PCA 與特徵工程**：
   - **圓弧度 (Roundness)**：分析杯底價格的二階導數，正值越小代表底部越圓。
   - **相對強度 (RS)**：O'Neil 強調突破時 RS 應創 52 週新高。
3. **過濾器**：
   - **均線過濾**：要求 `SMA(50) > SMA(200)` (黃金交叉背景)。
   - **大盤過濾**：僅在市場指數處於 `EMA(50)` 之上時執行該策略。

---

## 關鍵指標

| 指標 | 用途 |
|------|------|
| **均線多頭排列 (SMA 50/150/200)** | 確認長期大趨勢 |
| **RS Line（相對強弱線）** | IBD 專用指標，股票相對於大盤的強度 |
| **成交量分佈** | 確認杯身買盤 vs 柄部量縮 |
| **EPS/盈利增長** | CANSLIM 的基本面過濾（純技術分析可略去） |

---

## 交易規則

```
前提：股票（或資產）在大趨勢均線之上，且近期有強勢表現

1. 確認杯身：從一個高點開始的 U 型回調，底部圓滑
2. 確認杯沿：右側價格回到前高附近（< 5% 差距）
3. 等待杯柄：出現 1-3 週的量縮整理，微微向下傾斜
4. 進場觸發：收盤帶量突破杯柄的最高點（Pivot）
5. 停損：杯柄最低點下方 2-3%
6. 加碼規則：突破後在 5% 以內可再加碼，超過不追
7. 目標：通常可持有至型態量度目標，或等待下一個型態信號
```

### 量度目標
```
目標高度 = 杯底至杯沿的距離
目標價 = 突破點 + 目標高度
```

---

## 量化實作要點

```python
def detect_cup_and_handle(df, min_cup_weeks=7, max_cup_drawdown=0.33,
                           handle_max_drawdown=0.12, breakout_vol_ratio=1.4):
    """
    偽代碼示意
    """
    # 找前高（開始形成杯身的起點）
    cup_start = find_recent_high(df, lookback=260)  # 52週內

    # 計算杯身深度
    cup_low = df['low'].iloc[cup_start:].min()
    cup_depth = (df['high'].iloc[cup_start] - cup_low) / df['high'].iloc[cup_start]

    if cup_depth > max_cup_drawdown:
        return None  # 回調過深，型態失效

    # 確認右側杯沿（回到前高的 5% 以內）
    cup_rim_right = df['high'].iloc[-30:].max()
    cup_rim_diff = abs(cup_rim_right - df['high'].iloc[cup_start]) / df['high'].iloc[cup_start]

    if cup_rim_diff > 0.05:
        return None  # 未回到前高附近

    # 確認杯柄（最近 1-4 週的整理）
    handle_period = 15  # 約 3 週
    handle_high = df['high'].iloc[-handle_period:].max()
    handle_low = df['low'].iloc[-handle_period:].min()
    handle_drawdown = (handle_high - handle_low) / handle_high
    handle_vol = df['volume'].iloc[-handle_period:].mean()
    pre_handle_vol = df['volume'].iloc[-handle_period-20:-handle_period].mean()

    vol_contracting = handle_vol < pre_handle_vol * 0.8  # 量縮 20%

    if handle_drawdown > handle_max_drawdown or not vol_contracting:
        return None

    # 突破確認
    pivot = handle_high
    current_close = df['close'].iloc[-1]
    current_vol = df['volume'].iloc[-1]
    vol_avg_10d = df['volume'].iloc[-11:-1].mean()

    breakout = (current_close > pivot) and (current_vol > breakout_vol_ratio * vol_avg_10d)

    if breakout:
        return {
            'pivot': pivot,
            'stop_loss': handle_low,
            'target': pivot + (cup_rim_right - cup_low)
        }
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：杯身與杯柄需設定最短形成時間，避免把短期 V 轉或一般旗型誤判為杯柄。
- 必要條件：柄部回撤深度與位置必須限制在杯身上半部，否則結構已弱化。
- 必要條件：回測需計入突破滑點與成交量門檻，杯柄突破常發生在快速拉抬時。
- 可選條件：將杯深、杯寬、左右對稱度、柄部斜率、柄部量縮程度做成 feature。
- 可選條件：加入營收成長、板塊強度、相對強弱作為 CANSLIM 的量化代理變數。
- 可選條件：測試「直接突破」與「突破後 1-3 根內回踩杯沿」兩種進場法。

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 高勝率且量度目標明確（O'Neil 驗證） | 完整型態需要數週至數月 |
| 適合強勢股的加速突破 | 杯身要求圓弧形，主觀性較強 |
| 風報比佳（柄部提供明確停損） | 在熊市中多數杯柄型態失敗 |

---

## 延伸閱讀

- *How to Make Money in Stocks* — William J. O'Neil（CANSLIM 系統原著）
- *Trade Like an O'Neil Disciple* — Gil Morales & Chris Kacher
- Investor's Business Daily (IBD)：MarketSmith 工具提供 Cup and Handle 掃描
- CANSLIM 7 大法則中的 "C, A, N" 代表盈利、年成長、新趨勢
