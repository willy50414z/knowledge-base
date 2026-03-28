# 04-07 Harmonic Patterns（諧波型態）

## 策略類型
**04 — Pattern Trading（型態學 / 幾何）**

---

## 概述

諧波型態（Harmonic Patterns）將幾何圖形（如 W 型、M 型的變體）與**嚴格的斐波那契比例**結合，用以識別極高精確度的「潛在反轉區（Potential Reversal Zone, PRZ）」。此系統由 **H.M. Gartley** 於 1935 年在《Profits in the Stock Market》中初步提出，後由 **Scott Carney** 在《Harmonic Trading》（2004, 2007）系列著作中大幅擴展和系統化，成為完整的諧波交易體系。

諧波型態的核心信念：**市場的自然波動遵循黃金比例（Fibonacci 比例），特定的比例組合預示趨勢反轉。**

---

## 五個核心諧波型態

所有諧波型態均由 5 個點（X, A, B, C, D）構成，D 點為進場點（PRZ）。

## 型態比例要求 (量化嚴謹版)

諧波交易在量化中需設置 **容錯率 (Tolerance)**，建議預設為 `±5%` (0.05)。

| 型態 | B 點回調 (XA) | D 點位置 (XA) | 量化門檻 (標籤: `Fib_Logic`) |
|------|--------------|----------------|----------------|
| **蝙蝠 (Bat)** | 0.382 - 0.500 | 0.886 | `abs(AD/XA - 0.886) < Tolerance` |
| **加特利 (Gartley)** | **0.618** | 0.786 | `abs(AB/XA - 0.618) < Tolerance` |
| **蝴蝶 (Butterfly)** | 0.786 | 1.272 | `D 點 > X 點` (延伸型) |
| **螃蟹 (Crab)** | 0.382 - 0.618 | 1.618 | 最強大的反轉預測 |

---

## PRZ（潛在反轉區）與進場邏輯 (標籤: `PRZ_Entry`)

1. **PRZ 定義**：
   - PRZ 不是單一價位，而是一個區間：`[D_Price * (1-Tolerance), D_Price * (1+Tolerance)]`。
2. **進場觸發 (Trigger)**：
   - 價格進入 PRZ **且** 出現反轉信號（如 `Close > High[-1]` 或 `RSI` 脫離超賣區）。
3. **失效條件 (Invalidation)**：
   - 價格收盤突破 **X 點**。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化**：
   - **Tolerance**: [0.02, 0.05, 0.08] (測試不同嚴格度下的樣本數與勝率)。
   - **ZigZag_Order**: [5, 10, 20] (影響識別到的轉折點數量)。
2. **PCA 與權重分析**：
   - 使用 PCA 分析 **B 點、C 點比例** 對 D 點反轉成功率的貢獻。通常 B 點越精確，型態越可靠。
   - **RSI 背離權重**：在 PRZ 區域同時出現 RSI 背離時，加倍倉位。
3. **實作注意事項**：
   - 諧波型態在 **「盤整趨勢轉折」** 時效果最佳，在強單邊趨勢中容易被「打穿」，建議結合 `ADX < 30` 使用。

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：所有 XA/AB/BC/CD 比例都應以同一套 ZigZag 或 swing 演算法產生，否則型態識別不可重現。
- 必要條件：PRZ 不宜直接視為成交價，需明確定義限價掛單、確認 K 線或反轉觸發條件。
- 必要條件：回測需納入交易成本與低流動性滑點，諧波型態常出現在較細緻的波段結構。
- 可選條件：將各腿比例誤差、PRZ 寬度、D 點反轉力度、完成時間做成 quality score。
- 可選條件：加入多時間框架匯聚，例如日線 PRZ 加 4H 反轉觸發。
- 可選條件：把 pattern family one-hot 化，分析不同型態在不同 regime 下的相對優勢。

---

## 型態的 M/W 分類

| 分類 | 說明 | 進場方向 |
|------|------|---------|
| **看漲諧波型態** | W 型結構，D 點為低點 | 做多 |
| **看跌諧波型態** | M 型結構，D 點為高點 | 做空 |

---

## 加特利 (Gartley) 詳解

加特利是最古老、最廣為人知的諧波型態：

```
看漲加特利（Bullish Gartley）：

X
 \
  A (0.618 回調至 B)
 /
B
 \
  C (AB 的 0.382~0.886 反彈)
 /
D (D 點在 XA 段的 0.786，即 PRZ)
→ 在 D 點做多
```

**嚴格比例要求：**
- AB = XA × 0.618（B 點）
- BC = AB × 0.382 ~ 0.886（C 點）
- CD = BC × 1.272 ~ 1.618（C 到 D 的距離）
- AD = XA × 0.786（D 點位置）

---

## PRZ（潛在反轉區）計算

PRZ 通常由**多個 Fibonacci 比例匯聚**在同一價格區間來確定：

```python
# 加特利的 PRZ 計算示例
def gartley_prz(X, A, B, C):
    """
    返回 D 點的 PRZ 範圍
    """
    # D 點應該在 XA 的 0.786
    d_xa = A + (X - A) * 0.786  # 看漲時：從 A 回調到 X-A 距離的 78.6%

    # D 點也應在 BC 的延伸
    d_bc_1272 = C + (B - C) * 1.272
    d_bc_1618 = C + (B - C) * 1.618

    prz_center = d_xa
    prz_range = (min(d_bc_1272, d_xa) * 0.99,
                 max(d_bc_1618, d_xa) * 1.01)

    return prz_center, prz_range
```

---

## 交易規則

### 進場（以看漲加特利為例）
```
1. 識別 X, A, B, C 四個轉折點
2. 計算 PRZ（D 點區間）
3. 等待價格進入 PRZ
4. 確認訊號：
   - K 線型態（錘頭、吞噬等）
   - RSI 底背離
   - 成交量放大
5. 進場：在 PRZ 附近分批進場（如三筆）
6. 停損：超過 X 點（PRZ 被破壞，型態失效）
7. 目標 T1：C 點
         T2：A 點
         T3：D 點的 1.272 延伸
```

---

## 量化實作（ZigZag + 比例驗證）

```python
def detect_gartley(zigzag_points, tolerance=0.05):
    """
    zigzag_points: 由 ZigZag 指標輸出的轉折點列表 [(index, price), ...]
    tolerance: 比例容錯率
    """
    patterns = []

    for i in range(4, len(zigzag_points)):
        X, A, B, C, D = [p[1] for p in zigzag_points[i-4:i+1]]

        # 看漲加特利：X>A, A<B<X, B>C, C<A, D>C
        if not (X > A and B > A and B < X and C > A and C < B):
            continue

        # 比例驗證
        xa = abs(X - A)
        ab = abs(A - B)
        bc = abs(B - C)
        ad = abs(A - D)

        # AB/XA 應接近 0.618
        ab_xa_ratio = ab / xa
        if not (0.618 * (1 - tolerance) <= ab_xa_ratio <= 0.618 * (1 + tolerance)):
            continue

        # AD/XA 應接近 0.786
        ad_xa_ratio = ad / xa
        if not (0.786 * (1 - tolerance) <= ad_xa_ratio <= 0.786 * (1 + tolerance)):
            continue

        patterns.append({
            'type': 'Bullish_Gartley',
            'X': X, 'A': A, 'B': B, 'C': C, 'D': D,
            'PRZ': D,
            'stop_loss': X,
            'target_1': C,
            'target_2': A
        })

    return patterns
```

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 進場點極為精確（PRZ 定義明確） | 學習曲線陡峭，需熟悉多種比例 |
| 停損點數學定義明確 | 日常出現的型態並不完全符合嚴格比例 |
| 適合程式自動掃描 | 假型態導致的停損發生率不低 |
| 多個 Fibonacci 比例匯聚增加可信度 | 對小時間框架噪音敏感 |

---

## 常用 Python 套件

- **`harmonic-trader`**：Python 諧波型態辨識庫
- **`pandas-ta`**：包含 ZigZag 等指標
- TradingView 的 Auto Harmonic Pattern 腳本

---

## 延伸閱讀

- *Profits in the Stock Market* — H.M. Gartley（1935，原始 Gartley 型態）
- *Harmonic Trading, Volume 1 & 2* — Scott Carney（完整諧波系統）
- *The Harmonic Trader* — Scott Carney（入門）
- HarmonicTrader.com — Scott Carney 的官方網站
