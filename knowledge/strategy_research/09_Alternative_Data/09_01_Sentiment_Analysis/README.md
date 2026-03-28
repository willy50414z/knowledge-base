# 09-01 Sentiment Analysis（市場情緒分析）

## 策略類型
**09 — Alternative Data（另類數據）**

---

## 概述

市場情緒分析策略基於**行為金融學（Behavioral Finance）**的核心發現：**市場價格不僅反映資訊，更反映人類的情緒狀態。** 當市場參與者集體陷入恐慌時，往往過度拋售；當集體貪婪時，往往過度追高。透過量化測量這種情緒的極端性，可以作為**逆市場情緒（Contrarian）**或**順勢（Momentum）**的交易訊號。

在加密貨幣領域，由於市場以散戶為主、社群媒體影響力巨大，情緒分析~~效果尤為顯著~~ 通常較容易觀察到可量化的影響，但穩定性仍需透過樣本外驗證確認。與傳統技術分析不同，情緒分析屬於**另類數據（Alternative Data）**範疇，是現代量化交易與 AI 融合的重要研究方向。

---

## 主要情緒數據來源

### 1. 恐懼與貪婪指數（Fear & Greed Index）
由 Alternative.me 發布的加密市場綜合情緒指數（0-100）：

| 分數 | 情緒等級 | 逆向操作建議 |
|------|---------|------------|
| 0-24 | 極度恐慌（Extreme Fear） | 潛在做多機會 |
| 25-44 | 恐慌（Fear） | 偏多考量 |
| 45-55 | 中性（Neutral） | 觀望 |
| 56-74 | 貪婪（Greed） | 偏空考量 |
| 75-100 | 極度貪婪（Extreme Greed） | 潛在做空機會 |

**組成因子：**
- 波動率（25%）
- 市場動量/交易量（25%）
- 社交媒體情緒（15%）
- 調查問卷（15%）
- 比特幣主導率（10%）
- 趨勢搜尋（Google Trends）（10%）

**API：**
```python
import requests

def get_fear_greed_index():
    url = "https://api.alternative.me/fng/?limit=1&format=json"
    response = requests.get(url)
    data = response.json()
    return {
        'value': int(data['data'][0]['value']),
        'classification': data['data'][0]['value_classification'],
        'timestamp': data['data'][0]['timestamp']
    }
```

### 2. 社交媒體情緒（Social Media Sentiment）

**數據來源：**
- **Twitter/X**：BTC、ETH 的提及量、正/負面情緒
- **Reddit（r/CryptoCurrency, r/Bitcoin）**：帖子情緒
- **Telegram / Discord**：社群情緒（需自行爬取）

**工具：**
- **LunarCrush**：專業的加密社群情緒指標 API
- **Santiment**：社交媒體 + 鏈上數據分析
- **Glassnode**：鏈上情緒指標
- **CoinMarketCap Trending**：熱度追蹤

### 3. 新聞情緒 NLP（News Sentiment）

**數據源：**
- CryptoPanic.com API：聚合加密新聞並提供情緒分類
- NewsAPI.org：廣泛新聞聚合
- RSS 訂閱 + 自行 NLP 分析

### 4. 鏈上情緒數據（On-chain Sentiment）
- **NUPL（Net Unrealized Profit/Loss）**：持幣者的未實現盈虧分佈
- **Long/Short Ratio**：合約市場多空比
- **Whale Alert**：大額轉帳監控

---

## 策略邏輯與量化框架 (標籤: `AI_Sentiment_Logic`)

### 1. LLM 結構化輸出 (Standardized JSON)
為確保 AI 輸出可用於自動回測，必須強制 LLM 遵循以下 schema：
```json
{
  "sentiment_score": -0.85, 
  "confidence": 0.92,
  "impact_window_hours": 24,
  "signal_type": "CONTRARIAN_BUY",
  "reasoning_tags": ["fear", "panic_sell", "capitulation"]
}
```

### 2. 情緒背離過濾器 (Sentiment Divergence)
- **多頭背離**：價格下跌但 `Social_Sentiment` 轉為正面或提及量激增，預示底部。
- **空頭背離**：價格創高但 `Social_Sentiment` 卻持平或下降，預示動能衰竭。

---

## 量化優化方向 (Optimization Hooks)

1. **參數掃描**：
   - **Sentiment_Threshold**: [-0.7, -0.8, -0.9] (決定逆向操作的極端度)。
   - **Lookback_Correlation**: [24h, 72h, 7d] (情緒對價格影響的半衰期)。
2. **PCA 與另類數據分析**：
   - 分析 **「恐懼與貪婪指數」** 與 **「資金費率」** 的相關性。當兩者同時達到極端值時，反轉機率最高。
   - **Google Trends**：將特定關鍵字（如 "Buy BTC" vs "Sell BTC"）的搜尋量作為因子輸入 PCA。
3. **實作建議**：
   - 情緒數據通常具有 **長尾效應 (Long Tail)**，建議使用非線性模型或 LLM 進行特徵提取，再輸入標準量化策略中作為**權重因子 (Weighting Factor)**。

---

## AI 驅動的情緒分析實作（LLM 版）

這是目前最前沿的實作方式，結合大型語言模型（LLM）實時分析：

```python
import anthropic
import requests
from datetime import datetime

class CryptoSentimentAnalyzer:
    def __init__(self, anthropic_api_key, news_api_key):
        self.llm_client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.news_api_key = news_api_key

    def fetch_recent_news(self, query="Bitcoin OR Ethereum", hours=6):
        """獲取最近N小時的加密新聞"""
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 20,
            'apiKey': self.news_api_key
        }
        response = requests.get(url, params=params)
        articles = response.json().get('articles', [])
        return [f"{a['title']}: {a['description']}" for a in articles[:10]]

    def analyze_sentiment_with_llm(self, headlines: list[str]) -> dict:
        """
        使用 Claude 分析新聞標題情緒
        """
        prompt = f"""你是一位加密貨幣市場情緒分析師。
請分析以下新聞標題的整體情緒，並輸出：
1. 情緒分數（-1 到 1，-1 極度恐慌，0 中性，1 極度樂觀）
2. 主要情緒關鍵詞
3. 對 BTC/ETH 價格的短期（24H）影響預測

新聞標題：
{chr(10).join(f'- {h}' for h in headlines)}

請以 JSON 格式回覆：
{{"score": <float>, "keywords": [<str>], "prediction": "<str>", "confidence": "<low/medium/high>"}}"""

        message = self.llm_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        try:
            return json.loads(message.content[0].text)
        except:
            return {"score": 0, "keywords": [], "prediction": "neutral", "confidence": "low"}

    def generate_trading_signal(self, sentiment_score: float,
                                 fear_greed_index: int,
                                 price_trend: str) -> str:
        """
        綜合情緒分數 + 恐懼貪婪指數 + 價格趨勢 → 交易訊號
        """
        if sentiment_score > 0.5 and fear_greed_index > 70 and price_trend == 'up':
            return "STRONG_BUY"
        elif sentiment_score < -0.5 and fear_greed_index < 25 and price_trend == 'down':
            return "CONTRARIAN_BUY"  # 逆向做多（極度恐慌）
        elif sentiment_score > 0.7 and fear_greed_index > 85:
            return "TAKE_PROFIT"  # 極度貪婪，考慮獲利了結
        elif sentiment_score < -0.7 and fear_greed_index < 15:
            return "STRONG_BUY"   # 極度恐慌，逆向大倉買入
        else:
            return "HOLD"

# 使用示例
analyzer = CryptoSentimentAnalyzer(
    anthropic_api_key="your_key",
    news_api_key="your_key"
)

headlines = analyzer.fetch_recent_news("Bitcoin")
sentiment = analyzer.analyze_sentiment_with_llm(headlines)
fg = get_fear_greed_index()

signal = analyzer.generate_trading_signal(
    sentiment_score=sentiment['score'],
    fear_greed_index=fg['value'],
    price_trend='up'
)
print(f"交易訊號: {signal}, 情緒分數: {sentiment['score']:.2f}")
```

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：所有情緒資料都必須以「可被市場看到的時間戳」對齊價格，避免用到事後補發、重新編輯或延遲聚合資料。
- 必要條件：需做去重、去機器人、去轉貼與來源可信度評分，否則情緒因子很容易被 spam 汙染。
- 必要條件：情緒因子不宜直接單獨下單，建議先作為權重或 filter，並限制最大部位影響。
- 可選條件：將 source-level reliability、topic cluster、情緒離散度、熱度加速度納入 feature。
- 可選條件：加入多語言 embedding 與事件分類，區分監管、技術故障、ETF、駭客等不同敘事。
- 可選條件：測試情緒半衰期與 regime 互動，例如牛市追價情緒與熊市恐慌情緒的表現差異。

---

## 情緒指標的歷史驗證

| 情緒事件 | F&G 指數 | BTC 後續表現 |
|---------|---------|------------|
| 2018/12 | 9（極恐） | +300%（6個月） |
| 2020/03 | 12（極恐） | +500%（12個月） |
| 2021/11 | 90（極貪） | -75%（1年後） |
| 2022/12 | 25（恐慌） | +160%（6個月） |

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 捕捉技術指標無法感知的市場情緒 | 情緒持續時間不確定，可能滯後 |
| 逆向策略在極端情緒時效果顯著 | 社群媒體數據噪音大，需要過濾 |
| 可與 AI/LLM 無縫整合 | API 成本（LunarCrush、Santiment 等） |
| 加密市場中情緒驅動效應特別強 | 極端情緒可能持續更長時間才反轉 |

---

## 延伸閱讀

- *Irrational Exuberance* — Robert Shiller（行為金融學經典）
- Alternative.me Fear & Greed：[alternative.me/crypto/fear-and-greed-index/](https://alternative.me/crypto/fear-and-greed-index/)
- LunarCrush API：社群媒體情緒數據
- Santiment：[santiment.net](https://santiment.net)
- Glassnode Studio：[studio.glassnode.com](https://studio.glassnode.com)（鏈上情緒數據）
