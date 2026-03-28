# 04-04 Bull / Bear Flag（多頭 / 空頭旗型）

## 策略類型
**04 — Pattern Trading（型態學 / 延續型態）**

---

## 概述

旗型（Flag Pattern）是趨勢交易中最常見的**延續型態（Continuation Pattern）**之一，代表強勢趨勢的中途休息而非反轉。其外型由兩部分組成：**旗桿（Flagpole）**— 代表初始的猛烈單邊移動；**旗面（Flag）**— 隨後的短暫平行整理。整理結束後，價格通常會以相似的幅度繼續延伸。

旗型是**成功率最高、量度目標最為可靠**的型態之一，深受量化交易者喜愛，因為其條件定義較其他型態更為精確。

---

## 型態結構

### 多頭旗型（Bull Flag）
```
旗桿     旗面        突破
  ↑       ___         ↑↑
 /|      /   \       /
/ |     /     \     /
/  |   /  整理  \   /
```

| 組件 | 說明 |
|------|------|
| **旗桿（Flagpole）** | 短時間內猛烈上漲，通常 10-20%+ |
| **旗面（Flag）** | 平行收斂，微微向下傾斜（小於 45°）的震盪整理 |
| **突破（Breakout）** | 向上突破旗面上軌，完成型態 |

### 空頭旗型（Bear Flag）
```
旗桿（下跌）     旗面（反彈整理）     繼續下跌
     \            ___
      \          /   \
       \        /     \
        \      /  整理  \
         ↓               ↓↓
```

---

## 關鍵識別標準 (量化嚴謹版)

| 標準 | 多頭旗型 (Bull Flag) | 量化定義 (標籤: `Param_Flag`) |
|------|---------|---------|
| **旗桿幅度 (Pole)** | 猛烈上漲 | `ROC(Close, 5) > 10%` 且 `Volume > MA(Vol, 20) * 2` |
| **旗桿時間** | 快速成型 | `T_Pole < 10 bars` |
| **旗面回撤 (Flag)** | 幅度適中 | `Drawdown < Pole_Height * 0.382` (回撤不可超過旗桿的 38.2%) |
| **旗面時間** | 短暫整理 | `T_Flag < T_Pole * 3` (整理時間不可過長) |
| **成交量萎縮** | 賣壓耗盡 | `Avg_Vol_Flag < Avg_Vol_Pole * 0.5` |
| **突破確認** | 二度爆發 | `Close > Flag_High` 且 `Vol > MA_Vol_Flag * 1.5` |

---

## 交易規則 (標籤: `Flag_Execution`)

### 進場
- **進場位**：`Close` 突破旗面整理的上軌線。
- **過濾器**：確保價格在 `EMA(20)` 之上。

### 停損與目標
- **停損 (SL)**：`Flag_Low` (旗面最低點) 或 `Entry - 1.5 * ATR`。
- **目標 (TP)**：`Breakout_Price + Pole_Height` (1:1 投射)。

---

## 量化優化方向 (Optimization Hooks)

1. **參數空間**：
   - **Pole_Threshold**: [10%, 15%, 20%] (決定旗桿的猛烈程度)。
   - **Flag_Duration_Max**: [10, 20, 30 bars]。
2. **PCA 分析點**：
   - 分析 **「旗面回撤深度」與「後續目標達成率」** 的相關性。
   - **斜率優化**：旗面理想斜率應為負值且絕對值小於旗桿斜率。
3. **實作注意事項**：
   - 旗型是回測中表現最穩定的型態之一，但需注意在 **「山寨幣（Altcoins）」** 中，旗桿往往過於陡峭導致滑點過大，需加入流動性過濾 (Volume > Threshold)。

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：需先定義旗桿的最小報酬與旗面的最大回撤，否則很容易把一般整理誤判成旗型。
- 必要條件：旗型策略本質是趨勢延續，應加入大盤與標的 regime filter，避免在震盪期追價。
- 必要條件：突破訊號需用已完成 K 線與成交量確認，並納入滑點模擬。
- 可選條件：將旗桿長度、旗面斜率、整理天數、ATR 壓縮率、突破量比做成 pattern score。
- 可選條件：加入相對強弱或領漲板塊因子，旗型常出現在強勢標的。
- 可選條件：測試半倉突破、半倉回踩加碼的分段進場方式。

---

## 量度目標

```
多頭旗型目標 = 突破點 + 旗桿高度
空頭旗型目標 = 突破點 - 旗桿高度
```

**示例：**
```
旗桿底部 = 100，旗桿頂部 = 120（旗桿 = 20）
整理後突破旗面上軌 = 118
目標 = 118 + 20 = 138
```

---

## 交易規則

### 多頭旗型進場
```
1. 識別旗桿：近 N 天出現 > 15% 的快速漲幅，且成交量放大
2. 識別旗面：隨後 5-20 根 K 線，ATR 顯著下降，形成平行下傾通道
3. 等待突破：收盤突破旗面上軌
4. 確認：突破成交量 > 旗面整理期間均量 × 1.3
5. 進場：突破確認後立即進場
6. 停損：旗面最低點下方，或突破點 - 1 × ATR
7. 目標：旗桿幅度等量投射
```

---

## 量化實作

```python
def detect_bull_flag(df, flagpole_min_return=0.10, flag_max_bars=20,
                      flag_max_drawdown=0.08, breakout_vol_mult=1.3):
    """
    檢測多頭旗型
    flagpole_min_return: 旗桿最小漲幅
    flag_max_bars: 旗面最大持續K線數
    flag_max_drawdown: 旗面最大回撤容忍
    """
    signals = []

    for i in range(50, len(df)):
        # 往前找旗桿：快速上漲
        for pole_start in range(i - 30, i - 3):
            pole_return = (df['high'].iloc[pole_start:i].max() -
                          df['close'].iloc[pole_start]) / df['close'].iloc[pole_start]

            if pole_return < flagpole_min_return:
                continue

            pole_top_idx = df['high'].iloc[pole_start:i].idxmax()

            # 旗面：從旗桿頂部到當前
            flag_bars = i - df.index.get_loc(pole_top_idx)
            if flag_bars > flag_max_bars or flag_bars < 3:
                continue

            flag_high = df['high'].iloc[pole_top_idx:i].max()
            flag_low  = df['low'].iloc[pole_top_idx:i].min()
            flag_drawdown = (flag_high - flag_low) / flag_high

            # 旗面整理幅度不能太大
            if flag_drawdown > flag_max_drawdown:
                continue

            # ATR 應在旗面期間萎縮
            atr_now = compute_atr(df.iloc[i-5:i], 5).iloc[-1]
            atr_pole = compute_atr(df.iloc[pole_start:pole_start+5], 5).iloc[-1]
            if atr_now >= atr_pole:
                continue

            # 突破條件
            if df['close'].iloc[i] > flag_high:
                vol_flag_avg = df['volume'].iloc[pole_top_idx:i].mean()
                if df['volume'].iloc[i] > breakout_vol_mult * vol_flag_avg:
                    pole_height = df['high'].iloc[pole_start:pole_top_idx+1].max() - df['close'].iloc[pole_start]
                    target = df['close'].iloc[i] + pole_height
                    signals.append({'bar': i, 'target': target, 'stop': flag_low})

    return signals
```

---

## Thomas Bulkowski 統計數據

| 型態 | 勝率（達到目標） | 平均漲幅 | 失敗率 |
|------|--------------|---------|--------|
| **多頭旗型** | 約 54% | +23% | 約 4% |
| **空頭旗型** | 約 61% | -22% | 約 3% |
| **旗型（帶量突破）** | 顯著更高 | — | 顯著更低 |

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 條件定義清晰，適合程式化 | 旗桿後的整理時間不易精確判斷 |
| 量度目標可靠 | 整理期間可能演變為反轉型態 |
| 進場停損比例佳 | 在震盪行情中旗桿本身難以定義 |
| 適用任何時間框架 | 旗面傾斜度的判斷帶有主觀性 |

---

## 延伸閱讀

- *Encyclopedia of Chart Patterns* — Thomas Bulkowski（含完整統計）
- *How to Make Money in Stocks* — William O'Neil（旗型是 CANSLIM 核心型態之一）
- *Mastering the Trade* — John Carter
