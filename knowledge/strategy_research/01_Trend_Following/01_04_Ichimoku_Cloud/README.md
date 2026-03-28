# 01-04 Ichimoku Cloud（一目均衡表）

## 策略類型
**01 — Trend Following（趨勢跟蹤 / 綜合指標）**

---

## 概述

一目均衡表（Ichimoku Kinko Hyo，日文：一目で均衡を見る）由日本記者 **細田悟一（Goichi Hosoda）** 以筆名「一目山人」花費約 30 年研究，於 1969 年正式發表。名稱意為「一眼看出均衡狀態」，是一套**自成體系（Self-contained）的完整交易系統**，無需搭配其他指標即可判斷：

- 趨勢方向
- 動能強弱
- 支撐與壓力位
- 進出場時機

---

## 五條線的組成

| 線名 | 日文 | 計算方式 | 標準參數 | 意義 |
|------|------|---------|---------|------|
| **轉換線** | 転換線 (Tenkan-sen) | (9日最高 + 9日最低) ÷ 2 | 9 | 短期均衡（類似 9 日 MA） |
| **基準線** | 基準線 (Kijun-sen) | (26日最高 + 26日最低) ÷ 2 | 26 | 中期均衡（趨勢支撐/壓力） |
| **先行帶A** | 先行スパンA (Senkou Span A) | (轉換線 + 基準線) ÷ 2，**向前平移 26 期** | — | 雲層上緣 |
| **先行帶B** | 先行スパンB (Senkou Span B) | (52日最高 + 52日最低) ÷ 2，**向前平移 26 期** | 52 | 雲層下緣 |
| **遲行線** | 遅行スパン (Chikou Span) | 當前收盤價，**向後平移 26 期** | — | 確認趨勢強度 |

> **標準參數 (9, 26, 52)** 對應日本傳統 6 天交易週（一週休息 1 天）：9 天 ≈ 一週半，26 天 ≈ 一個交易月，52 天 ≈ 兩個交易月。若用於 7 天交易的加密市場，常調整為 **(10, 30, 60)**。

---

## 雲層（Kumo）解讀

```
先行帶A > 先行帶B → 上升雲（多頭雲，通常顯示為綠色）
先行帶A < 先行帶B → 下降雲（空頭雲，通常顯示為紅色）
```

| 位置關係 | 解讀 |
|---------|------|
| 價格在雲層上方 | 多頭市場 |
| 價格在雲層下方 | 空頭市場 |
| 價格在雲層內部 | 趨勢不明，方向混沌 |
| 雲層厚 | 支撐/壓力強 |
| 雲層薄 | 容易突破 |

---

## 交易規則 (量化嚴謹版)

### 強烈做多訊號 (標籤: `Ichimoku_Bull`)
1. **雲層過濾 (Cloud)**：`Close > Senkou_Span_A` 且 `Close > Senkou_Span_B`。
2. **交叉確認 (Cross)**：`Tenkan_Sen > Kijun_Sen` (黃金交叉)。
3. **強度確認 (Chikou)**：`Close[0] > Close[-26]` (當前收盤高於 26 期前收盤)。
4. **未來預測 (Future)**：`Senkou_Span_A.shift(-26) > Senkou_Span_B.shift(-26)` (前方雲層為綠色)。

### 進場執行
- **進場點**：所有條件滿足後的下一個開盤價，或回踩基準線時掛單。
- **停損 (SL)**：~~收盤跌破基準線~~ `Close < Kijun_Sen` 或雲層下緣。

---

## 量化優化與參數調優 (標籤: `Optimization`)

1. **參數組合建議**：
   - **傳統型**：(9, 26, 52) - 適合週線或日線。
   - **加密貨幣型**：(10, 30, 60) 或 (20, 60, 120) - 增加平滑度以過濾高波動。
2. **PCA 分析點**：
   - **雲層厚度 (Cloud Thickness)**：`abs(SpanA - SpanB) / Close`。厚雲層通常代表更強的支撐，可作為權重指標。
   - **偏離度**：價格與基準線的距離，過高則不宜追多。
3. **過濾器組合**：
   - 在量化實作中，單獨使用一目表在橫盤期表現較差，建議結合 `ADX > 20`。

---

## 量化實作

```python
import pandas as pd

def ichimoku(high, low, close, tenkan=9, kijun=26, senkou_b=52):
    # 轉換線 (Tenkan-sen): (9-period high + 9-period low)/2
    tenkan_sen = (high.rolling(tenkan).max() + low.rolling(tenkan).min()) / 2

    # 基準線 (Kijun-sen): (26-period high + 26-period low)/2
    kijun_sen = (high.rolling(kijun).max() + low.rolling(kijun).min()) / 2

    # 先行帶A (Senkou Span A): (Tenkan + Kijun)/2 平移 kijun 期
    senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)

    # 先行帶B (Senkou Span B): (52-period high + 52-period low)/2 平移 kijun 期
    senkou_b_line = ((high.rolling(senkou_b).max() +
                      low.rolling(senkou_b).min()) / 2).shift(kijun)

    # 遲行線 (Chikou Span): Close 向後平移 kijun 期
    # 注意：量化回測中 Chikou[0] = Close[0] > Close[-26]
    chikou_check = close > close.shift(kijun)

    return tenkan_sen, kijun_sen, senkou_a, senkou_b_line, chikou_check

# 進場訊號邏輯
# 1. 價格在雲上
# 2. TK 交叉
# 3. 遲行線確認
# 4. 前方雲層顏色
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：先行帶與遲行線含有位移，回測時必須嚴格用當下可得資訊重建，不可直接引用繪圖後的前移結果。
- 必要條件：需定義雲層厚度過濾，例如雲太薄時降低權重，避免把弱突破當成有效趨勢。
- 必要條件：執行假設需納入交易成本與滑點，因 TK 交叉在低週期容易頻繁翻向。
- 可選條件：將 `Cloud_Thickness`、`Price_to_Kijun`、`Future_Kumo_Twist_Distance` 納入 feature set。
- 可選條件：加入波動率或成交量條件，避免在極低量環境使用純指標突破。
- 可選條件：針對 24/7 市場測試非標準參數組，例如 `(10,30,60)`、`(20,60,120)` 的穩健性。

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 一張圖同時提供趨勢、動能、支撐壓力資訊 | 初學者視覺上容易混亂，五條線資訊量大 |
| 數學定義明確，適合自動化 | 在震盪市場產生大量假訊號 |
| 雲層提供前瞻性的支撐壓力預告 | 標準參數設計為傳統市場，加密市場需調整 |
| 遲行線提供額外的確認機制 | 訊號出現相對滯後 |

---

## 延伸閱讀

- *Ichimoku Charts* — Nicole Elliott
- 細田悟一原著（日文）《一目均衡表》
- 加密市場常用調整參數：**(10, 30, 60)** 以適應全天候交易
- TradingView 一目均衡表文件：支援自訂參數
