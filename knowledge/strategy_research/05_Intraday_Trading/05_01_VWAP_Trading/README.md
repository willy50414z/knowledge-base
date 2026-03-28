# 05-01 VWAP Trading（VWAP 均價回歸）

## 策略類型
**05 — Intraday Trading（日內交易）**

---

## 概述

VWAP（Volume-Weighted Average Price，成交量加權平均價）是機構交易員最廣泛使用的**基準價格指標**之一。它代表「公平成本（Fair Value）」的概念：在一個交易日內，按照成交量加權計算出的平均成交價格。散戶交易者、機構法人、演算法交易系統都以 VWAP 作為成本基準，因此價格偏離 VWAP 過多時，回補力量自然出現。

VWAP 策略最初廣泛用於**機構大單拆分執行**（如 VWAP 演算法），後被日內交易員（Day Trader）採用為交易決策工具，尤其在**美股開盤後的前 2-3 小時**最為有效。

---

## VWAP 計算公式

```
VWAP = Σ(典型價格 × 成交量) / Σ(成交量)

典型價格（Typical Price, TP）= (High + Low + Close) / 3

VWAP_t = Σ(TP_i × Volume_i, i=1..t) / Σ(Volume_i, i=1..t)
```

**關鍵特性：**
- VWAP 是**每日重新計算**（從開盤重置）
- 多數平台以分鐘 K 線為基礎累計計算
- 不能跨日使用（跨日 VWAP 失去意義）

---

## VWAP 的延伸：VWAP 標準差帶

類似布林通道，可在 VWAP 上下各加 1-2 個標準差，形成動態支撐壓力帶：

```
上帶 = VWAP + n × σ（σ 為典型價格的標準差）
下帶 = VWAP - n × σ
```

常用設定：±1σ, ±2σ

---

## 關鍵指標

| 指標 | 用途 |
|------|------|
| **VWAP** | 當日公平成本基準 |
| **VWAP ±1σ/±2σ 帶** | 偏離程度的量化邊界 |
| **相對成交量（RVOL）** | 當前成交量 / 同時段歷史均量，衡量市場活躍度 |
| **開盤第一根 K 線的高低點** | 當日偏差方向的早期訊號 |

---

## 核心策略模式 (量化嚴謹版)

### 模式一：VWAP 均值回歸 (Fade) (標籤: `VWAP_Mean_Reversion`)
- **進場條件**：
  - `Price < VWAP - 2.0 * Sigma` (超賣)。
  - **RVOL (Relative Volume) < 0.8** (量能衰竭，代表賣壓不再延伸)。
  - `RSI(14) < 30`。
- **目標 (TP)**：回到 `VWAP`。
- **停損 (SL)**：`VWAP - 2.5 * Sigma` 或跌破當日最低點。

### 模式二：VWAP 趨勢突破 (Breakout) (標籤: `VWAP_Trend`)
- **進場條件**：
  - `Price` 帶量突破 `VWAP`。
  - **RVOL > 1.5** (爆量確認)。
  - `Close > VWAP` 且 `VWAP` 斜率向上。
- **目標 (TP)**：`VWAP + 1.5 * Sigma` 或 `+2.0 * Sigma`。

---

## 量化優化方向 (Optimization Hooks)

1. **參數掃描**：
   - **Sigma_Multiplier**: [1.0, 1.5, 2.0, 2.5] (決定進場的極端程度)。
   - **RVOL_Threshold**: [1.2, 1.5, 2.0] (定義「突破量」)。
2. **日內時間效應 (Time Decay)**：
   - **黃金時段**：開盤後 30-120 分鐘。
   - **量化建議**：建立一個權重函數，隨時間流逝降低均值回歸的權重，因為收盤前的趨勢通常不回頭。
3. **PCA 分析點**：
   - 分析 **「VWAP 斜率」與「回歸成功率」** 的相關性。斜率越平坦，均值回歸效果越好；斜率越陡，則應順勢而為。
4. **Anchored VWAP (錨定 VWAP)**：
   - 除了日級別 VWAP，嘗試在「重大新聞發布點」或「日內爆量點」錨定 VWAP，作為更強的支撐壓力參考。

---

## 交易規則

| 項目 | 規則 |
|------|------|
| **時間框架** | 主要用於 1-15 分鐘線 |
| **有效時段** | 開盤後前 2 小時（美股 9:30-11:30 EST，台股 9:00-11:00） |
| **停損** | VWAP ±0.5σ 之外（失去均值回歸前提） |
| **日內收盤** | **不持倉過夜**（VWAP 隔日重置，失去參考意義） |

---

## 量化實作

```python
import pandas as pd

def calculate_vwap(df):
    """
    df: 分鐘 OHLCV DataFrame，日期欄位為 'date'
    """
    df = df.copy()
    df['tp'] = (df['high'] + df['low'] + df['close']) / 3
    df['tp_vol'] = df['tp'] * df['volume']

    # 按日分組重置
    df['date_only'] = df.index.date
    df['cumvol'] = df.groupby('date_only')['volume'].cumsum()
    df['cumtpvol'] = df.groupby('date_only')['tp_vol'].cumsum()

    df['vwap'] = df['cumtpvol'] / df['cumvol']

    # 計算標準差帶
    df['sq_diff'] = (df['tp'] - df['vwap']) ** 2
    df['variance'] = df.groupby('date_only')['sq_diff'].cumsum() / \
                     df.groupby('date_only').cumcount().add(1)
    df['sigma'] = df['variance'] ** 0.5

    df['vwap_upper1'] = df['vwap'] + df['sigma']
    df['vwap_lower1'] = df['vwap'] - df['sigma']
    df['vwap_upper2'] = df['vwap'] + 2 * df['sigma']
    df['vwap_lower2'] = df['vwap'] - 2 * df['sigma']

    return df

def vwap_mean_reversion_signal(df):
    """
    VWAP 均值回歸訊號
    """
    buy_signal = df['close'] < df['vwap_lower1']   # 跌破 -1σ
    sell_signal = df['close'] > df['vwap_upper1']   # 突破 +1σ
    exit_long = df['close'] >= df['vwap']            # 回到 VWAP 平倉
    exit_short = df['close'] <= df['vwap']           # 回到 VWAP 平倉

    return buy_signal, sell_signal
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：必須明確定義 session reset、交易時區與盤前盤後是否納入 VWAP 計算。
- 必要條件：日內策略需計入手續費、滑點與 queue 位置，否則 VWAP 回歸的微利模型會被高估。
- 必要條件：需區分回歸型與突破型 regime，可用開盤缺口、早盤成交量、VWAP 斜率分類。
- 可選條件：將 `Price-VWAP distance`、`VWAP slope`、`VWAP band z-score`、`OFI` 做成 feature set。
- 可選條件：加入午盤禁做或流動性衰退過濾，降低噪音交易。
- 可選條件：測試 anchored VWAP、事件 VWAP 與日內 VWAP 的組合效果。

---

## 機構使用 VWAP 的方式

機構投資者（如共同基金、ETF）在**執行大額訂單**時使用 VWAP 演算法：
- 將大額訂單拆分為小單，按照歷史成交量分佈在一天中分批執行
- 目標：使實際成交均價接近當日 VWAP（減少市場衝擊）
- 這也是為何 VWAP 具有「磁吸效應」的根本原因

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 機構真實使用的指標，「磁吸效應」強 | 僅對日內交易有效，不適用長線 |
| 計算透明，無落後（即時更新） | 需要逐分鐘資料，資料成本較高 |
| 適合震盪與趨勢兩種市況 | 強趨勢日均值回歸會連續虧損 |
| 程式化實作相對簡單 | 開盤初期（前 30 分鐘）VWAP 不穩定 |

---

## 延伸閱讀

- *The Inner Circle Trader (ICT)* 的 VWAP 應用課程
- *Mastering the Trade* — John Carter（VWAP 交易技術）
- 機構 VWAP 演算法：[Investopedia VWAP](https://www.investopedia.com/terms/v/vwap.asp)
- 錨定 VWAP（Anchored VWAP）：從特定歷史事件點開始計算的 VWAP，由 Brian Shannon 推廣
