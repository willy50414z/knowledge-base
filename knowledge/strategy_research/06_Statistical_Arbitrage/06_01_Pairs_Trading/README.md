# 06-01 Pairs Trading（配對交易）

## 策略類型
**06 — Statistical Arbitrage（統計套利）**

---

## 概述

配對交易（Pairs Trading）是統計套利的經典策略，由 **Nunzio Tartaglia** 領導的摩根士丹利（Morgan Stanley）量化團隊於 1980 年代首創。策略核心是尋找**兩個歷史上高度相關（協整）的資產**，當兩者價格關係出現統計上的異常偏離時，做多被低估的資產、同時做空被高估的資產，並等待兩者價差回歸歷史均值，從中獲利。

配對交易屬於**市場中性策略（Market Neutral）**：不論市場整體漲跌，只賺取兩個資產之間的**相對價差**，因此受到系統性風險的衝擊遠小於單向交易。

---

## 核心邏輯

> **「強相關的兩個資產分開走，是暫時的噪音，不是永久的分叉。等它們回來。」**

**類比**：把兩隻狗用一條橡皮筋綁在一起，不論牠們如何分開，橡皮筋始終會把牠們拉回來。配對交易就是在橡皮筋被拉伸到極限時建倉。

---

## 理論基礎

### 協整（Cointegration）vs 相關（Correlation）

| 概念 | 說明 | 適用性 |
|------|------|--------|
| **相關（Correlation）** | 衡量兩序列同漲同跌的程度 | 不穩定，可能是短暫巧合 |
| **協整（Cointegration）** | 即使各自是非平穩序列，其**線性組合**是平穩的（均值回歸） | 配對交易的真正基礎 |

**協整檢定（Engle-Granger / Johansen 法）：**
- 若兩個時間序列 $P_A$ 和 $P_B$ 協整，則存在 $\beta$ 使得：
  $$\text{Spread} = P_A - \beta \times P_B$$
  此價差序列是**平穩（Stationary）**的。

---

## 關鍵指標

| 指標 | 說明 | 工具 |
|------|------|------|
| **相關係數（Pearson Correlation）** | 快速篩選候選對 | `pandas.DataFrame.corr()` |
| **協整 p 值** | 確認長期均值回歸特性 | `statsmodels.coint()` |
| **Z-Score** | 衡量當前價差偏離的標準差倍數 | 自行計算 |
| **套期比（Hedge Ratio, β）** | OLS 回歸估計的最佳組合比例 | `numpy.polyfit()` |

---

## 交易規則

### 步驟一：選對（Pair Selection）
```python
from statsmodels.tsa.stattools import coint
import pandas as pd

# 篩選協整對
def find_cointegrated_pairs(price_df, p_threshold=0.05):
    n = price_df.shape[1]
    pairs = []

    for i in range(n):
        for j in range(i+1, n):
            asset_a = price_df.iloc[:, i]
            asset_b = price_df.iloc[:, j]

            # Engle-Granger 協整檢定
            _, pvalue, _ = coint(asset_a, asset_b)

            if pvalue < p_threshold:
                pairs.append((price_df.columns[i], price_df.columns[j], pvalue))

    return sorted(pairs, key=lambda x: x[2])
```

## 交易規則 (量化嚴謹版) (標籤: `Stat_Arb_Logic`)

### 1. 協整檢定與配對選擇
- **動態檢定**：每隔 24 小時重新運行一次 `Coint Test`。
- **平穩性要求**：價差序列 `Spread` 的 ADF 檢定 p-值必須持續低於 `0.05`。

### 2. 動態套期比 (Beta) 計算
- **量化細節**：不使用靜態 Beta，改用 **Rolling OLS** (窗口建議 60-120 根 K 線) 來捕捉兩個資產間關係的漂移。
  ```python
  # 使用滾動回歸獲取動態 Beta
  model = RollingOLS(y=df['A'], x=df['B'], window=90).fit()
  beta = model.params
  ```

### 3. Z-Score 進場門檻
- **進場 (Entry)**：`abs(Z_Score) > 2.0`。
- **出場 (Exit)**：`abs(Z_Score) < 0.5` 或回歸至 `0`。
- **強硬停損 (Stop)**：`abs(Z_Score) > 4.0` (代表協整關係破裂，不可死扛)。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化 (Grid Search)**：
   - **Lookback Window**: [60, 90, 120, 250] (影響均值回歸的敏感度)。
   - **Entry/Exit Thresholds**: Entry [1.5, 2.0, 2.5] / Exit [0, 0.5]。
2. **PCA 與多因子配對**：
   - **PCA 殘差套利**：不僅限於兩兩配對，可利用 PCA 找出板塊中與主成分偏離最遠的資產進行交易。
3. **風險管理**：
   - **波動率加權**：根據兩個資產的 ATR 動態調整持倉名義價值，確保 Delta 真正中性。
   - **行業過濾**：僅在同類行業或具備相同基本面邏輯的資產間進行配對，降低「偽協整」風險。

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：配對需定期重做協整與穩定性檢定，不能只因歷史相關高就長期視為同一 pair。
- 必要條件：執行面需同步處理兩腿成交、套期比與借券/融券成本，否則名義上中性、實際上仍有方向曝險。
- 必要條件：spread、beta、z-score 的估計視窗要與交易視窗分離，避免樣本內過擬合。
- 可選條件：將 half-life、ADF p-value、residual volatility、rolling beta stability 做成 feature。
- 可選條件：加入產業、板塊或鏈上敘事暴露，避免 pair 兩邊其實承受不同 regime shock。
- 可選條件：測試 Kalman Filter 動態 beta 與固定 beta 的差異。

---

## 加密市場的典型對

| 配對 | 邏輯 |
|------|------|
| **BTC / ETH** | 最廣泛使用的加密配對，歷史相關性高 |
| **BTC Spot / BTC Perpetual** | 基差套利（Basis Trading） |
| **ETH / BNB** | 大市值主流幣之間 |
| **SOL / AVAX** | 同類 L1 公鏈代幣 |

---

## 風險與注意事項

### 協整失效（Regime Change）
- 最大風險：原本協整的對子**永久分叉**（如某加密項目崩潰）
- 防護措施：設置最大虧損停損（如 Z-Score > 4 時強制止損）

### 滾動視窗 vs 靜態
- 建議使用**滾動 OLS（Rolling OLS）**動態估計 β，而非固定值
- 滾動視窗建議：60-120 天

### 槓桿風險
- 做多一個 + 做空另一個 = 名義上的 2x 槓桿
- 在高波動市場（如加密市場）需謹慎控制倉位

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 市場中性，不受大盤漲跌影響 | 協整失效風險（最大風險） |
| 有堅實的統計理論基礎 | 需要同時維護兩個倉位，資金效率較低 |
| 在震盪市場中表現出色 | 需要足夠的歷史資料建立統計基礎 |
| 可擴展至多對 / 多空輪動 | 實現需要一定的數學與統計能力 |

---

## 延伸閱讀

- *Pairs Trading: Quantitative Methods and Analysis* — Ganapathy Vidyamurthy（2004）
- *Statistical Arbitrage* — Andrew Pole（2007）
- Ernie Chan：《Quantitative Trading》 及 《Algorithmic Trading》（含配對交易實作）
- [QuantLib](https://www.quantlib.org/) / [statsmodels](https://www.statsmodels.org/) 的協整模組
