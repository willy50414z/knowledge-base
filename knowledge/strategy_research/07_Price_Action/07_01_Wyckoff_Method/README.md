# 07-01 Wyckoff Method（威科夫操盤法）

## 策略類型
**07 — Price Action（價格行為 / 週期分析）**

---

## 概述

威科夫操盤法（Wyckoff Method）由美國股票交易員和金融作家 **Richard D. Wyckoff**（1873-1934）所創立。Wyckoff 被認為是繼 Charles Dow 之後最重要的技術分析先驅之一。他透過觀察數十年的市場行為，總結出「**大資金（Composite Man / 合成人）**」如何推動市場的完整框架。

Wyckoff 的核心洞察：市場的價格波動並非隨機，而是由「**主力資金（Composite Man）**」的四階段操作週期所主導：**吸籌（Accumulation）→ 拉升（Markup）→ 派發（Distribution）→ 下跌（Markdown）**。理解這個週期，就能在主力之前佈局，在主力出貨前退場。

---

## 三大法則

### 1. 供需法則（Law of Supply and Demand）
- 需求 > 供給 → 價格上漲
- 供給 > 需求 → 價格下跌
- 成交量是供需的直接體現

### 2. 因果法則（Law of Cause and Effect）
- 吸籌期（因）的大小決定了後續漲幅（果）的幅度
- 吸籌越久、箱體越大 → 後續爆發力越強

### 3. 努力與結果法則（Law of Effort vs Result）
- **成交量（努力）**與**價格移動（結果）**應該成比例
- 大量但價格小動（背離）→ 主力在悄悄吸/派

---

## 市場四階段週期

### 階段一：吸籌（Accumulation）
> 主力在低位悄悄買入，避免拉高引起散戶注意

**典型結構：**
```
PS  → Preliminary Support（初步支撐）
SC  → Selling Climax（拋售高潮，量大價跌）
AR  → Automatic Rally（自動反彈）
ST  → Secondary Test（二次測試前低）
Spring → 假跌破（彈簧效應，嚇出最後的散戶）
LPS → Last Point of Support（最後支撐點）
SOS → Sign of Strength（力量展示，突破箱體）
BU  → Back Up（回測箱體頂部後確認）
```

**核心關注點：Spring（彈簧效應）：**
```
在吸籌箱體底部，價格短暫跌破（假跌破）後快速拉回
特徵：
  - 短暫跌破前低（SC 的低點）
  - 成交量縮小（賣盤枯竭）或瞬間放量後迅速回升
  - 收盤快速站回前低之上
→ 這是吸籌完成、即將拉升的訊號
```

### 階段二：拉升（Markup）
- 主力帶動價格上漲，散戶追入
- 正常回調（Back Up / LPS）是加碼機會

### 階段三：派發（Distribution）
> 主力在高位悄悄出售，與吸籌結構鏡像

**典型結構：**
```
PSY → Preliminary Supply（初步供給）
BC  → Buying Climax（買入高潮，量大價漲）
AR  → Automatic Reaction（自動回落）
ST  → Secondary Test（測試前高）
SOW → Sign of Weakness（力量疲弱訊號）
LPSY → Last Point of Supply（最後供給點）
UTAD → Upthrust After Distribution（派發後的假突破）
```

**核心關注點：Upthrust（上推 / 假突破）：**
- 在箱體頂部假突破（引誘追高者），隨即回落
- 與 Spring 相反方向的陷阱設計

### 階段四：下跌（Markdown）
- 主力籌碼出清後，價格進入自由落體

---

## 成交量分析

Wyckoff 非常強調**成交量與價格的關係（Price × Volume 協同分析）**：

| 情況 | 解讀 |
|------|------|
| 大量 + 大漲 | 需求強勁，多頭健康 |
| 大量 + 小漲 | 賣盤吸收中，可能是派發 |
| 縮量 + 小跌 | 需求仍在，正常回調 |
| 大量 + 大跌 | 拋售高潮（SC），可能接近底部 |
| 縮量 + 小漲 | 需求不足，反彈後可能繼續跌 |

---

## 量化識別標準 (量化嚴謹版)

### 1. 吸籌箱體識別 (Accumulation Range)
- **結構定義**：`Consolidation_Width < 15%` 且持續時間 `T > 60 bars`。
- **量能特徵**：箱體後半段成交量應低於前半段的 70% (`Volume_Decline`)。
- **波動率**：`ATR(14)` 持續下降至近期平均值的 80% 以下。

### 2. Spring (彈簧效應) 觸發邏輯 (標籤: `Wyckoff_Spring`)
- **假跌破**：`Low < Range_Low` 且 `(Range_Low - Low) / Range_Low < 0.02` (跌破幅度不宜過大)。
- **快速回收**：收盤價必須在 3 根 K 線內站回 `Range_Low` 之上。
- **測試確認 (Test)**：回收後的回踩成交量應極小，代表賣壓枯竭。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化**：
   - **Range_Lookback**: [60, 120, 200] (決定結構的大週期)。
   - **Spring_Tolerance**: [0.01, 0.02, 0.03] (假跌破的容忍深度)。
2. **PCA 與特徵工程**：
   - **Volume Profile POC**：將「當前價格與 POC (籌碼密集區) 的偏離度」作為特徵輸入。
   - **一階/二階導數**：分析價格在箱體底部的斜率變化，捕捉「止跌」的數學特徵。
3. **實作建議**：
   - 威科夫法在量化上常與 **OBV (能量潮)** 結合，分析資金流向與價格的背離。建議將 `OBV 斜率` 加入作為吸籌階段的確認因子。

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：吸籌區、Spring、SOS 等事件都必須以右側確認方式定義，否則極易出現事後看圖才成立的偏誤。
- 必要條件：成交量資料品質很重要，若使用加密資料需確認 wash trading 與假量問題。
- 必要條件：應加入市場狀態過濾，Wyckoff 反轉訊號在強單邊趨勢中常延後或失效。
- 可選條件：將箱體長度、Spring 穿越深度、收回速度、Volume Spread Analysis 特徵做成 feature。
- 可選條件：加入 Volume Profile、Delta、Liquidation Spike 強化「主力吸收」的代理判定。
- 可選條件：把 Accumulation/Distribution 視為分類問題，由 agent 輔助標註再訓練。

---

## 進階工具：量能分佈圖（Volume Profile）

Wyckoff 的現代量化升級是使用**Volume Profile**找出籌碼密集區（Point of Control, POC）：

```python
# Volume Profile 找 POC（量化版本的 Wyckoff 支撐）
# POC = 特定區間內成交量最大的價格水平
# 當價格跌破 POC 後又迅速站回 → 類似 Spring 的訊號
```

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 基於供需的根本邏輯，理解市場本質 | 學習曲線長，型態辨識帶有主觀性 |
| 成交量分析使訊號更可靠 | 純量化實作困難，通常需要結合 Volume Profile |
| 適用所有市場和時間框架 | 吸籌/派發週期可能持續很長時間 |
| 揭示機構行為，有先機優勢 | 在快速市場（如加密牛市）結構不完整 |

---

## 延伸閱讀

- *Studies in Tape Reading* — Richard D. Wyckoff（1910）
- Wyckoff Analytics：[wyckoffanalytics.com](https://www.wyckoffanalytics.com)
- Roman Bogomazov & Bruce Fraser：Wyckoff 的現代詮釋
- Volume Profile 工具：TradingView 的 Volume Profile Visible Range
- *The Wyckoff Methodology in Depth* — Rubén Villahermosa（現代補充）
