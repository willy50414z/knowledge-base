# 08-01 Smart Money Concepts（聰明錢概念 / SMC）

## 策略類型
**08 — Institutional Order Flow（機構訂單流）**

---

## 概述

聰明錢概念（Smart Money Concepts, SMC）是近年來在散戶社群中迅速流行的交易方法論，主要由匿名交易員 **ICT（Inner Circle Trader，真名 Michael Huddleston）** 在其大量 YouTube 教學內容中系統化整理。SMC 的核心假設是：

> **「散戶大多數時候都是錯的，因為機構（大資金）故意設計來獵殺散戶停損單的陷阱。理解機構的真實意圖，就能趁機搭便車。」**

SMC 拒絕傳統指標，只看**裸 K 線（Naked Price Action）**，透過識別機構留下的「足跡（Footprints）」來判斷真實的買賣意圖。

---

## 核心概念

### 1. 流動性（Liquidity）
機構需要大量的流動性才能建立倉位，**散戶的停損單就是最好的流動性來源**。

| 流動性類型 | 位置 | 散戶行為 | 機構行為 |
|-----------|------|---------|---------|
| **買方流動性（Buy-side Liquidity）** | 明顯高點（前高）上方 | 散戶的突破買單和賣方停損 | 機構在此出售（吸收流動性後做空）|
| **賣方流動性（Sell-side Liquidity）** | 明顯低點（前低）下方 | 散戶的跌破賣單和多方停損 | 機構在此買入（吸收流動性後做多）|

**「流動性獵殺（Liquidity Sweep / Stop Hunt）」**：
```
現象：價格短暫突破關鍵高低點（引爆停損）後迅速反轉
解讀：機構刻意將價格推到停損密集區，收集流動性後做反向操作
→ 突破後迅速反轉 = 流動性獵殺 = 強烈的反向訊號
```

### 2. 訂單塊（Order Block, OB）
訂單塊是機構**大量集中建立倉位的 K 線位置**，留下「機構的成本區」。

**識別方法：**
```
多頭訂單塊（Bullish OB）：
  = 在下跌序列中，緊接大漲 K 線之前的最後一根下跌（陰）K 線
  當價格回測此 OB 時 → 機構再次補倉 → 強力支撐

空頭訂單塊（Bearish OB）：
  = 在上漲序列中，緊接大跌 K 線之前的最後一根上漲（陽）K 線
  當價格回測此 OB 時 → 機構再次做空 → 強力壓力
```

## 核心規則 (量化嚴謹版)

### 1. FVG 識別算法 (標籤: `FVG_Logic`)
- **嚴格定義**：`Candle3_Low > Candle1_High + (ATR * 0.1)` (增加最小間隙閾值，過濾微小波動)。
- **緩衝過濾**：FVG 形成後的 5 根 K 線內若未被填補，視為「強失衡區」。

### 2. 流動性獵殺觸發 (Liquidity Sweep) (標籤: `SMC_Sweep`)
- **條件**：`Price_High > Max(High[前 20 日])` 且 `Close < Max(High[前 20 日])`。
- **成交量**：突破時必須伴隨成交量突增 (`Vol > MA*2`)，隨後迅速縮量回落。

### 3. 訂單塊 (Order Block) 權重
- **優選 OB**：必須與 FVG 同時出現的 OB 最具參考價值。
- **回測進場**：在價格回到 OB 區間且 `RSI` 出現背離時進場。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化**：
   - **FVG_Min_Size**: [0.001, 0.002, 0.005] (過濾雜訊)。
   - **Sweep_Lookback**: [20, 55, 100] (決定流動性池的層級)。
2. **PCA 與因子分析**：
   - 分析 **「FVG 的回填率」** 與大趨勢強度的關係。
   - **溢價/折價 (Premium/Discount)**：將 `(Price - Min) / (Max - Min)` 作為進場權重，僅在折價區執行多單。
3. **實作挑戰**：
   - SMC 的多時間框架同步 (HTF/LTF) 在量化引擎中需特別處理，防止 **前瞻偏差 (Look-ahead Bias)**。建議統一將 HTF 訊號落後一期使用。

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：FVG、OB、Liquidity Sweep 的定義需完全數值化，包含最小失衡寬度、掃流動性的超越幅度與收回條件。
- 必要條件：若研究目標含日內執行，需確保 L2/L3 或至少低週期資料品質，否則 SMC 容易退化成普通 price action。
- 必要條件：回測必須納入滑點、手續費與消息驅動跳價，因為失衡區回補常發生在高速行情。
- 可選條件：將 FVG 寬度、回補比例、OB 成交量、sweep 深度、回收速度做成 feature。
- 可選條件：加入 OFI、CVD、Liquidation data 驗證「機構吸收/掃流動性」是否真實存在。
- 可選條件：把高週期 bias 與低週期 trigger 分開建模，避免所有判斷擠在同一個 timeframe。

---

## SMC 交易流程

```
1. 多時間框架分析（HTF → LTF）
   例：日線確認大方向 → 1H 找結構 → 15M 尋找進場觸發

2. 識別關鍵流動性池（前高/前低）
   → 機構下一步的目標

3. 等待流動性獵殺
   → 價格突破關鍵位後迅速反轉

4. 確認 FVG 或 OB 的回測
   → 在機構「成本區」進場

5. 進場觸發
   → CHoCH / BOS 在低時間框架確認

6. 停損與目標
   停損：FVG 的另一側 / OB 下方
   目標：下一個流動性池（下一個前高/前低）
```

---

## 量化實作

```python
def detect_fvg(df, min_size_pct=0.001):
    """
    識別 Fair Value Gap（公平價值缺口）
    """
    fvgs = []

    for i in range(2, len(df)):
        c1 = df.iloc[i-2]  # 第一根
        c2 = df.iloc[i-1]  # 第二根（主動根）
        c3 = df.iloc[i]    # 第三根

        # 多頭 FVG：c1 高點 < c3 低點（中間有空白）
        if c3['low'] > c1['high']:
            fvg_size = (c3['low'] - c1['high']) / c1['high']
            if fvg_size >= min_size_pct:
                fvgs.append({
                    'type': 'bullish',
                    'top': c3['low'],
                    'bottom': c1['high'],
                    'index': i,
                    'mid': (c3['low'] + c1['high']) / 2
                })

        # 空頭 FVG：c1 低點 > c3 高點
        elif c3['high'] < c1['low']:
            fvg_size = (c1['low'] - c3['high']) / c1['low']
            if fvg_size >= min_size_pct:
                fvgs.append({
                    'type': 'bearish',
                    'top': c1['low'],
                    'bottom': c3['high'],
                    'index': i,
                    'mid': (c1['low'] + c3['high']) / 2
                })

    return fvgs

def detect_order_block(df, fvg_index):
    """
    識別 FVG 前的訂單塊（Order Block）
    多頭 OB = FVG 前最後一根陰線
    """
    for i in range(fvg_index - 1, max(0, fvg_index - 10), -1):
        if df.iloc[i]['close'] < df.iloc[i]['open']:  # 陰線
            return {
                'type': 'bullish_OB',
                'high': df.iloc[i]['high'],
                'low': df.iloc[i]['low'],
                'index': i
            }
    return None
```

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| FVG 和 OB 的定義數學化，適合程式掃描 | 部分概念（如流動性獵殺）帶有主觀詮釋 |
| 風報比通常極高（進場精確、停損小） | 需要多時間框架同步分析，較複雜 |
| 解釋了傳統技術分析無法解釋的假突破 | SMC 社群資訊混亂，說法不一 |
| 適合波動率大的加密市場 | 效果難以用傳統回測工具完整驗證 |

---

## 延伸閱讀

- ICT（Inner Circle Trader）YouTube 頻道：完整的 SMC 教學體系
- ICT Mentorship（2022 版）：最新系統化課程
- *The Art of Trading* — ICT 相關書籍
- TradingView 的 SMC 指標：Luxalgo、Market Structure SMC 等免費腳本
