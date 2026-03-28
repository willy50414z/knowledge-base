# 03-01 Momentum Breakout（動量爆發）

## 策略類型
**03 — Momentum Trading（動能交易）**

---

## 概述

動量爆發策略（Momentum Breakout）捕捉的是市場中**最強勢資產的瞬間加速**現象。其理論基礎來自行為金融學：當資產在短時間內出現異常的漲幅與成交量，往往代表資訊不對稱的消弭（如重大消息揭露）或大資金的集中進場，而**追隨這種動能具有正期望值**，這在學術研究中被稱為「動量效應（Momentum Effect）」。

Jegadeesh & Titman（1993）的研究表明，過去 3-12 個月強勢的股票，未來 3-12 個月仍傾向保持強勢（動量持續性）。

---

## 核心邏輯

> **「漲得最快的繼續漲，在確認動能真實性後順勢追入。」**

動量的真實性需透過**量價同步**來驗證：
- **價格突破**：超越近期阻力位或歷史高點
- **成交量放大**：爆量確認資金真實湧入
- **趨勢強度**：ADX 確認方向性明確

---

## 關鍵指標

| 指標 | 參數 | 用途 |
|------|------|------|
| **成交量 (Volume)** | 20 期均量 | 確認量能是否為平均的 2 倍以上 |
| **相對強弱指標 (RSI)** | 14 期 | 確認動能強度（50-70 進場，>80 可能追高過度） |
| **平均方向指數 (ADX)** | 14 期 | 確認趨勢強度（>25 代表明確趨勢）|
| **跳空缺口 (Gap)** | — | 可作為額外動能確認 |
| **歷史新高 (52-week High)** | — | 新高往往是最佳動量訊號 |

---

## 交易規則 (量化嚴謹版)

### 進場條件 (標籤: `Momentum_Logic`)

1. **突破確認 (Breakout)**：
   - `Close > High[1...N].max()`。`N` 建議為 20 (短線) 或 55 (中長線)。
2. **成交量激增 (Volume Surge)**：
   - `Volume > MA(Volume, 20) * Multiplier`。
   - `Multiplier` 建議設為變數 `[1.5, 2.0, 3.0]` 進行優化。
3. **動能過濾 (Trend Strength)**：
   - `ADX(14) > 25` 且 `+DI > -DI`。
   - `RSI(14)` 處於 `[55, 75]` 區間。
4. **相對強度過濾 (Relative Strength - 可選)**：
   - 當前資產在同板塊或全市場的 5 日報酬率排名處於前 20%。

### 進場執行
- **進場時機**：~~突破確認當根 K 線收盤時~~ 改用 `Limit Order` 設於突破位上方或 `Market Order` 於收盤確認。

---

## 停損與目標 (標籤: `Risk_Mgmt`)

| 項目 | 規則 | 量化參數 |
|------|------|------|
| **初始停損 (SL)** | `Entry_Price - ATR(14) * 2` | 可優化 ATR 倍數 |
| **移動停損 (Trailing)** | `Max(High_Since_Entry) - ATR(14) * 1.5` | 隨趨勢上移 |
| **目標 (TP)** | 無固定目標，由移動停損觸發平倉 | 讓利潤奔跑 |

---

## 量化優化方向 (Optimization Hooks)

1. **參數掃描 (Grid Search)**：
   - **N (Lookback)**: [20, 40, 60] (決定阻力位的有效性)
   - **Vol_Multiplier**: [1.2, 1.5, 2.0] (決定「爆量」的嚴格程度)
2. **PCA 與因子分析**：
   - 分析 **RSI** 與 **ADX** 的交互作用。
   - **跨資產輪動**：在多個符合訊號的資產中，優先選擇 **RS (Relative Strength)** 指標最高的標的。
3. **假突破過濾**：
   - 增加「收盤價需高於突破位 N%」的緩衝區 (Buffer)。

---

## 量化實作

```python
def momentum_breakout_signal(df, volume_multiplier=2.0, adx_threshold=25):
    """
    df: OHLCV DataFrame
    返回進場訊號
    """
    # 計算指標
    df['vol_ma20'] = df['volume'].rolling(20).mean()
    df['high_20'] = df['high'].rolling(20).max()
    df['adx'] = compute_adx(df, period=14)
    df['rsi'] = compute_rsi(df['close'], period=14)

    # 進場條件
    volume_surge = df['volume'] > volume_multiplier * df['vol_ma20']
    price_breakout = df['close'] > df['high_20'].shift(1)
    strong_trend = df['adx'] > adx_threshold
    momentum_ok = (df['rsi'] > 50) & (df['rsi'] < 80)

    buy_signal = volume_surge & price_breakout & strong_trend & momentum_ok
    return buy_signal
```

---

## 常見過濾器

### 跳空缺口過濾
```python
gap_up = open_price > close_price.shift(1) * 1.02  # 跳空 2% 以上
```

### 歷史新高過濾
```python
new_52w_high = close > close.rolling(252).max().shift(1)  # 股票市場
new_30d_high = close > close.rolling(30).max().shift(1)   # 加密市場
```

### 相對強度過濾（跨資產比較）
```python
# 選擇最強的 Top N 資產進場（多空輪動）
returns_5d = close.pct_change(5)
top_assets = returns_5d.nlargest(5)  # 選最強的 5 個
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：突破必須搭配流動性與成交額門檻，避免把低流動性標的的瞬間拉抬誤判為動量。
- 必要條件：訊號產生與成交模擬需分離，建議用 `close_confirm -> next_bar_open/stop`，不要直接假設訊號 K 線收盤必定成交。
- 必要條件：需加入交易成本與 slippage model，尤其是在量價同時爆發時。
- 可選條件：加入相對強弱、52 週新高距離、Gap percentile 作為 ranking features。
- 可選條件：加入 `Volume Acceleration`、`Range Expansion`、`Close Location Value` 供 PCA 壓縮。
- 可選條件：設計失敗突破偵測，若突破後 `N` 根內跌回區間則標記為 false breakout 樣本。

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 勝率低但盈虧比高（趨勢延伸） | 震盪市場假突破多，頻繁小止損 |
| 邏輯清晰、完全可量化 | 需實時監控多個標的的量價變化 |
| 結合多個過濾器後精準度提升 | 爆量後才進場，容易在高點追入 |
| 適用於強勢牛市環境 | 滑點在流動性差的市場可能顯著 |

---

## 延伸閱讀

- Jegadeesh & Titman (1993)：*Returns to Buying Winners and Selling Losers*（動量效應的學術基礎）
- *Momentum Masters* — Mark Minervini 等人的動能交易訪談錄
- Stan Weinstein《Stan Weinstein's Secrets for Profiting in Bull and Bear Markets》
- ADX 計算：J. Welles Wilder 於《New Concepts in Technical Trading Systems》（1978）
