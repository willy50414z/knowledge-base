# 05-02 Opening Range Breakout（開盤區間突破 / ORB）

## 策略類型
**05 — Intraday Trading（日內突破）**

---

## 概述

開盤區間突破（Opening Range Breakout, ORB）是日內交易中~~最簡潔有效的策略之一~~ 相對規則清晰、易於量化測試的策略之一。策略基於一個廣泛觀察到的市場現象：**開盤初期（通常是前 15-30 分鐘）的價格波動，往往奠定了當日的主要交易方向。** 突破這段開盤區間的高點或低點，通常代表當日趨勢的確立。

此策略由 **Toby Crabel** 在其 1990 年著作《Day Trading with Short Term Price Patterns》中系統化記錄，後成為美股及期貨市場日內交易的經典策略，並被廣泛移植至加密貨幣市場。

---

## 為何開盤區間重要？

1. **流動性集中**：開盤時大量訂單同時進入市場，形成明顯的供需博弈
2. **機構定向**：機構交易員在開盤初期根據夜間新聞、美盤收盤等訊息調整部位，其行為決定日內方向
3. **心理關鍵位**：當日高低點是日內交易員的重要參考位，突破後引發追單效應
4. **方向確立**：統計上，超過 60% 的交易日，當日高點或低點在開盤後 2 小時內形成

---

## 開盤區間的定義

| 市場 | 建議時段 |
|------|---------|
| **美股** | 開盤後 15 分鐘（9:30-9:45 EST）或 30 分鐘（9:30-10:00）|
| **台股** | 開盤後 30 分鐘（09:00-09:30）|
| **加密幣（UTC）** | 00:00-00:30、08:00-08:30（亞洲時段開始）、13:30-14:00（美股前市）|
| **外匯** | 倫敦開盤後 30-60 分鐘（08:00-09:00 GMT）|

---

## 關鍵指標

| 指標 | 用途 |
|------|------|
| **開盤區間高點（ORH）** | 向上突破的觸發位 |
| **開盤區間低點（ORL）** | 向下突破的觸發位 |
| **ATR (前日)** | 過濾假突破（突破幅度 < 10% ATR 視為無效） |
| **VWAP** | 確認突破方向（突破方向應與 VWAP 相對位置一致） |
| **相對成交量（RVOL）** | 確認突破是否有量能支撐 |
| **前日收盤 / 前高前低** | 提供更廣的支撐壓力參考 |

---

## 交易規則 (量化嚴謹版)

### 做多進場 (標籤: `ORB_Long`)
1. **區間定義**：記錄開盤前 15/30 分鐘的 `High` (ORH) 與 `Low` (ORL)。
2. **突破觸發**：`Price > ORH + (ATR * 0.1)` (增加緩衝 Buffer，防止針頭穿刺)。
3. **動量確認 (必要)**：
   - `Volume > MA(Volume, 20) * 1.5`。
   - **VWAP 對齊**：價格必須同時在當前 `VWAP` 之上。
4. **進場執行**：收盤價確認突破或使用 `Buy Stop` 掛單。

---

## 量化優化方向 (Optimization Hooks)

1. **區間長度掃描 (Duration)**：
   - [5, 15, 30, 60] 分鐘。較短區間適合高頻，較長區間適合大波段。
2. **緩衝係數 (Buffer)**：
   - [0, 0.1, 0.2] * ATR。分析不同 Buffer 對降低假突破的貢獻。
3. **PCA 與權重分析**：
   - **Gap 效應**：分析「開盤跳空大小」與「ORB 成功率」的關係。大缺口後的 ORB 往往具有極強的延續性。
   - **前日趨勢**：如果當日 ORB 突破方向與前日趨勢一致，給予更高的權重。
4. **出場優化**：
   - 測試 **「時間止盈」** (例如 14:30 結束交易) vs **「移動止盈 (Trailing Stop)」**。通常 ORB 策略在午盤（12:00-13:30）會進入震盪，建議在此時段上移停損。

### 做空進場（對稱邏輯）
```
收盤跌破 ORL → 做空
停損 = ORH 或 ORL + 0.5 × ATR
目標 = ORL - (ORH - ORL)
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：需固定交易所時區、夏令時間與交易日曆，否則 OR 區間會被切錯。
- 必要條件：日內突破對手續費、滑點與延遲極敏感，回測必須使用保守成交假設。
- 必要條件：應明確設定當日平倉規則與禁做時段，避免 ORB 無意間變成隔夜策略。
- 可選條件：加入 `Opening Gap %`、前日區間壓縮、首 5 分鐘 RVOL、VWAP 斜率作為 feature。
- 可選條件：將趨勢日與均值回歸日分群，只在 trend day score 高時啟動 ORB。
- 可選條件：測試開盤後首次回踩 ORH/ORL 再進場，以降低假突破率。

---

## 開盤區間的變形

### 1. 5 分鐘 ORB（Ultra Short）
- 使用開盤後 5 分鐘的高低點
- 適合高頻日內交易
- 假突破率較高，需搭配成交量確認

### 2. 首日區間（First Hour Range）
- 使用開盤後 60 分鐘的高低點
- 更可靠但機會較少

### 3. 亞洲盤 ORB（適用加密幣）
- 以亞洲盤時段（00:00-08:00 UTC）的高低點為參考
- 突破亞洲盤高/低點視為歐美盤的方向確認

---

## 量化實作

```python
import pandas as pd

def orb_strategy(df, orb_minutes=30, vol_multiplier=1.5, atr_filter=0.002):
    """
    df: 分鐘 OHLCV DataFrame
    orb_minutes: 開盤區間時間（分鐘）
    """
    signals = []

    # 按日期分組
    for date, day_df in df.groupby(df.index.date):
        if len(day_df) < orb_minutes + 10:
            continue

        # 開盤區間（前 orb_minutes 分鐘）
        opening_range = day_df.iloc[:orb_minutes]
        orh = opening_range['high'].max()
        orl = opening_range['low'].min()

        # 開盤區間成交量均值
        orb_vol_avg = opening_range['volume'].mean()

        # 前日 ATR
        prev_atr = ...  # 前日 ATR 計算

        # 後續 K 線的突破掃描
        for i in range(orb_minutes, len(day_df)):
            bar = day_df.iloc[i]

            # 上行突破
            if bar['close'] > orh:
                if bar['volume'] > vol_multiplier * orb_vol_avg:
                    signals.append({
                        'date': date,
                        'direction': 'LONG',
                        'entry': bar['close'],
                        'stop': orl,
                        'target': bar['close'] + (orh - orl)
                    })
                    break

            # 下行突破
            elif bar['close'] < orl:
                if bar['volume'] > vol_multiplier * orb_vol_avg:
                    signals.append({
                        'date': date,
                        'direction': 'SHORT',
                        'entry': bar['close'],
                        'stop': orh,
                        'target': bar['close'] - (orh - orl)
                    })
                    break

    return signals
```

---

## Toby Crabel 的統計發現

根據 Crabel 的原始研究（對大量期貨合約的統計）：
- 開盤後突破的方向在**同一交易日內持續的機率 > 65%**
- 開盤區間越窄（ATR% 越低），突破後的趨勢延伸幅度越大
- 「Inside Day」（當日高低點在前日高低點內）次日的 ORB 效果顯著增強

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 邏輯極清晰，完全可自動化 | 假突破在震盪日非常頻繁 |
| 進場停損目標明確，操作機械化 | 過夜缺口會干擾開盤區間參考 |
| 適用多種市場（股票、期貨、加密） | 需要實時低延遲資料 |
| 每日提供固定的交易機會 | 加密市場 24 小時無明確開盤時段，需自訂 |

---

## 延伸閱讀

- *Day Trading with Short Term Price Patterns & Opening Range Breakout* — Toby Crabel（1990，稀有絕版書）
- *How to Day Trade for a Living* — Andrew Aziz（包含 ORB 策略）
- Jake Bernstein 的開盤時段研究
