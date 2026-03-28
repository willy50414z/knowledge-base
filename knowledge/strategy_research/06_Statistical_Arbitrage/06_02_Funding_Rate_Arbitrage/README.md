# 06-02 Funding Rate Arbitrage（資金費率套利）

## 策略類型
**06 — Statistical Arbitrage（量化統計套利）**

---

## 概述

資金費率套利（Funding Rate Arbitrage）是加密貨幣衍生性商品市場特有的低風險套利策略。它利用的是**永續合約（Perpetual Futures）**市場獨特的**資金費率（Funding Rate）機制**：永續合約為了持續錨定現貨價格，會定期（通常每 8 小時）在多空雙方之間轉移資金。當市場情緒極度偏向多頭時，多單需向空單支付費率；反之亦然。

透過**同時持有現貨多單 + 永續合約空單**（或反之），組合成 **Delta 中性**（不受價格漲跌影響）的倉位，並穩定收取資金費率，實現「躺賺」。

---

## 資金費率機制

### 資金費率公式（Binance 為例）
```
Funding Rate = Premium Rate + clamp(Interest Rate - Premium Rate, -0.05%, 0.05%)

Premium Rate = (Max(0, Impact Bid Price - Mark Price) - Max(0, Mark Price - Impact Ask Price)) / 現貨指數

Interest Rate（利率）= Binance 固定為 0.01% / 每 8 小時（即年化約 10.95%）
```

**資金費率的方向：**
- **正費率（Positive）**：多單付費給空單（市場看漲情緒旺盛）
- **負費率（Negative）**：空單付費給多單（市場看跌情緒旺盛）

### 結算時間（Binance 永續合約）
- 每 8 小時結算一次：**00:00, 08:00, 16:00 UTC**
- 費率每隔 8 小時更新預測值

---

## 策略核心構建

### 基礎版：現貨 + 永續空單（Cash and Carry）

| 倉位 | 操作 | 目的 |
|------|------|------|
| **現貨（Spot）** | 買入 1 BTC | 對沖永續空單的方向風險 |
| **永續合約（Perp）** | 做空 1 BTC（等值） | 收取正資金費率 |
| **淨暴露** | Delta ≈ 0 | 不受 BTC 漲跌影響 |
| **收益來源** | 每 8 小時的資金費率 | 穩定現金流 |

**年化收益估算：**
```
假設資金費率 = +0.1% / 每 8 小時
年化收益 = 0.1% × 3 次 × 365 天 = 109.5%（理論值，實際費率波動）
```

### 進階版：交叉所平套利

| 倉位 | 說明 |
|------|------|
| 在費率高的交易所持空單 | 收取高費率 |
| 在費率低的交易所持多單（或現貨） | 對沖方向 |
| 淨收益 = 費率差 | 兩所費率之間的套利空間 |

---

## 關鍵指標與監控

| 指標 | 數值範圍 | 操作建議 |
|------|---------|---------|
| **當前資金費率** | > 0.05%/8h | 考慮建立套利倉位 |
| **預測費率（Next Funding Rate）** | — | 提前佈局參考 |
| **費率持續時間** | 連續多期正/負 | 費率越穩定，策略越有效 |
| **基差（Basis = Spot - Perp）** | — | 監控現貨與合約的偏差 |
| **交易成本** | 手續費 + 滑點 | 確保套利空間扣成本後仍為正 |

---

## 交易規則

## 交易規則 (量化嚴謹版)

### 1. 進場門檻 (標籤: `Arb_Threshold`)
- **最小費率**：`Predicted_Rate > 0.01% / 8h` (考慮到手續費後的損益兩平點)。
- **推薦進場**：`Predicted_Rate > 0.03% / 8h` (年化約 30%+)。

### 2. Delta 漂移與再平衡 (Rebalancing) (標籤: `Risk_Mgmt`)
- **漂移監控**：由於現貨與永續價格變動不完全同步，需定期檢查 `Delta = Spot_Value - Abs(Perp_Value)`。
- **觸發條件**：當 `abs(Delta) / Total_Equity > 5%` 時，自動執行小額買賣以恢復中性。
- **複利邏輯**：每 8 小時收取的費用應自動劃轉至現貨帳戶，並根據新的總價值按比例加倉。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化**：
   - **Rebalance_Threshold**: [1%, 3%, 5%] (平衡執行成本與風險)。
   - **Exit_Rate**: [0.005%, 0.01%] (決定何時撤離以保留利潤)。
2. **跨平臺統計分析 (Basis Analysis)**：
   - 使用 PCA 分析多個交易所（Binance, Bybit, OKX）的費率相關性。
   - **偏離度套利**：若某交易所費率遠高於均值，則在該所開空，在其他所開多。
3. **風險管理 (Security First)**：
   - **保證金覆蓋率 (Margin Ratio)**：自動監控合約端保證金，若 `Mark_Price` 接近 `Liquidation_Price` 的 20% 範圍，自動從現貨端劃轉資金。
   - **交易成本模型**：將交易所 VIP 等級產生的手續費差異納入策略模型，優化淨收益。

### 平倉條件
```
- 資金費率跌至 < 0.01%（接近零利潤）
- 費率預測變為負值
- 合約端接近強平價位
- 已達預期收益目標
```

---

## 量化實作（Binance API）

```python
import ccxt
import time

class FundingRateArbitrage:
    def __init__(self, api_key, secret):
        self.spot = ccxt.binance({'apiKey': api_key, 'secret': secret})
        self.futures = ccxt.binanceusdm({'apiKey': api_key, 'secret': secret})

    def get_funding_rate(self, symbol='BTC/USDT:USDT'):
        info = self.futures.fetch_funding_rate(symbol)
        return info['fundingRate']

    def get_predicted_rate(self, symbol='BTC/USDT:USDT'):
        info = self.futures.fetch_funding_rate(symbol)
        return info.get('nextFundingRate', info['fundingRate'])

    def open_arbitrage(self, symbol, usdt_amount, min_rate_threshold=0.0003):
        """
        開啟套利倉位：買現貨 + 做空永續
        """
        predicted_rate = self.get_predicted_rate(symbol)

        if predicted_rate < min_rate_threshold:
            print(f"費率 {predicted_rate:.4%} 低於閾值，不進場")
            return False

        # 獲取當前價格
        spot_price = self.spot.fetch_ticker(symbol.split(':')[0])['last']
        quantity = usdt_amount / spot_price

        # 同時下達現貨買單和合約空單
        try:
            spot_order = self.spot.create_market_buy_order(
                symbol.split(':')[0], quantity
            )
            futures_order = self.futures.create_market_sell_order(
                symbol, quantity
            )
            print(f"套利倉位已建立：現貨買 {quantity:.4f}，合約空 {quantity:.4f}")
            return True
        except Exception as e:
            print(f"下單失敗：{e}")
            return False

    def monitor_and_rebalance(self, symbol):
        """
        監控倉位並在費率變化時調整
        """
        while True:
            current_rate = self.get_funding_rate(symbol)
            predicted_rate = self.get_predicted_rate(symbol)

            print(f"當前費率: {current_rate:.4%}, 預測費率: {predicted_rate:.4%}")

            if predicted_rate < 0:
                print("費率即將轉負，準備平倉")
                self.close_arbitrage(symbol)
                break

            time.sleep(300)  # 每 5 分鐘檢查一次
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：需同時計入 funding、交易手續費、借幣成本、提幣/轉倉成本與 basis 風險，不能只看表面年化費率。
- 必要條件：應明確監控再平衡規則與保證金安全邊際，避免在大波動時被動去槓桿或遭清算。
- 必要條件：不同交易所的費率公告時間、結算時間與 mark price 規則需做資料對齊。
- 可選條件：將 funding percentile、open interest、basis、borrow rate、OI change 做成 feature。
- 可選條件：加入交易所信用風險與資金分散限制，避免單一 venue tail risk。
- 可選條件：測試事件前後費率扭曲，例如上幣、unlock、ETF 新聞、季度結算。

---

## 風險分析

| 風險類型 | 說明 | 防護措施 |
|---------|------|---------|
| **費率反轉風險** | 費率突然轉負，從收費變成付費 | 監控預測費率，設閾值自動平倉 |
| **清算風險** | 合約倉位保證金不足被強平 | 使用低槓桿（1-2x），留足保證金 |
| **滑點風險** | 大額訂單影響市價，縮小套利空間 | 拆單分批執行，使用 Limit Order |
| **交易所風險** | 交易所倒閉或提款限制 | 分散資產於多個交易所 |
| **Delta 偏移** | 現貨與合約價值比例漂移 | 定期再平衡（如每週） |

---

## 費率資料來源

- **Binance**：[binance.com/en/futures/funding-history](https://www.binance.com/en/futures/funding-history)
- **Bybit**：Funding Rate History API
- **Coinglass**：[coinglass.com/FundingRate](https://www.coinglass.com/FundingRate)（多所費率比較）

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 幾乎完全規避方向性風險（Delta 中性） | 牛市頂峰後費率迅速衰減 |
| 在強勢行情中費率收益極高 | 需要大量資本才能覆蓋交易成本 |
| 100% API 自動化，無需人工介入 | 交易所 API 風控可能限制自動化操作 |
| 穩定的現金流策略 | 需要同時管理兩個交易所的帳戶 |

---

## 延伸閱讀

- Binance 資金費率說明文件：[docs.binance.com](https://docs.binance.com)
- Coinglass 資金費率歷史：[coinglass.com](https://www.coinglass.com/FundingRate)
- *Crypto Market Making* — GSR, Wintermute 等做市商的公開報告
- Delta One 對沖策略：機構量化研究報告
