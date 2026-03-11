# LangChain 簡介

## 什麼是 LangChain

LangChain 是一套用來開發 LLM 應用與 agent 系統的框架。官方定位重點包含：可將模型、工具、檢索、結構化輸出與 agent workflow 串接起來；而其 agent 能力建立在 LangGraph 之上，因此可進一步利用持久化、human-in-the-loop、較耐久的執行流程等能力。:contentReference[oaicite:0]{index=0}

如果用工程觀點來看，LangChain 的角色比較像：

- **LLM 應用編排框架**
- **tool calling / agent workflow 組裝層**
- **RAG 流程整合層**
- **與 LangSmith / LangGraph 搭配的開發工具鏈**

---

## LangChain 可以做什麼

LangChain 常見能力可以分成幾類：

### 1. 模型呼叫封裝
LangChain 可以串接不同模型供應商，讓你用相對一致的方式呼叫 chat model、embedding model、structured output 等能力。這讓你比較容易在同一個應用內替換底層模型。:contentReference[oaicite:1]{index=1}

### 2. Prompt 與 Chain 編排
它可以把 prompt、模型呼叫、後處理、工具使用等步驟串成單一步驟或多步驟流程，方便你把「輸入 → 推理 → 輸出」拆成可維護的元件。這也是很多 LLM app 的基本開發方式。:contentReference[oaicite:2]{index=2}

### 3. Tool calling
LangChain 可讓模型呼叫外部工具，例如：

- 行情 API
- 技術指標計算函式
- 資料庫查詢
- 新聞抓取
- 回測模組

這對需要「查資料後再決策」的應用很重要。:contentReference[oaicite:3]{index=3}

### 4. RAG（Retrieval-Augmented Generation）
LangChain 常被用來做 RAG：把文件切塊、建立索引、檢索相關內容，再把檢索結果餵給模型生成答案。這對知識庫問答、研究助手、策略說明系統很常見。:contentReference[oaicite:4]{index=4}

### 5. Agent workflow
官方現在把 agent 能力與 LangGraph 關聯得很深。LangGraph 將 agent workflow 建模為 graph，核心概念是：

- **State**：目前系統狀態
- **Nodes**：每一步的邏輯
- **Edges**：下一步要走哪條路徑

這很適合多步驟決策流程。:contentReference[oaicite:5]{index=5}

---

## 適合的使用情境

LangChain 比較適合下面這些情境：

- 需要串接多個模型或工具
- 需要 RAG
- 需要多步驟 workflow
- 需要 agent tool use
- 需要觀察 prompt、tool call、state 與 execution trace

如果只是做一個極簡單的單輪聊天介面，LangChain 不一定是必要的；但只要你開始碰到 **工具整合、流程編排、可觀測性**，它就會變得有價值。

---

## 應用範例：以開發 BTC 交易策略為例

下面用一個「BTC 交易策略研究助手 / 半自動策略 agent」來說明 LangChain 可以怎麼用。

### 目標
做一個系統，能協助你：

- 擷取 BTC 行情資料
- 讀取新聞 / 巨觀事件摘要
- 查詢你自己的研究筆記
- 生成策略假說
- 輸出策略說明、風險點與待驗證項目

### 可拆成的模組


使用者問題
   ↓
策略研究 Agent
   ├─ 行情資料工具
   ├─ 技術指標工具
   ├─ 新聞摘要工具
   ├─ 回測結果查詢工具
   └─ RAG 檢索你的策略知識庫
   ↓
輸出策略分析結果

### 可能的工具設計

1. **Market Data Tool**
    
    讀取 BTC OHLCV、成交量、Funding Rate、Open Interest
    
2. **Indicator Tool**
    
    計算 RSI、MACD、ATR、移動平均、波動率等
    
3. **News Tool**
    
    抓取或讀取近期 BTC / crypto macro news
    
4. **Backtest Query Tool**
    
    查詢你已經做過的策略回測結果
    
5. **RAG Retriever**
    
    檢索你自己的 markdown 知識庫，例如：
    
    - `knowledge/investing/btc-breakout.md`
    - `projects/btc-strategy/volatility-regime.md`
    - `ai/prompts/system/trading-analyst.md`

### 可實現的工作流

### 範例 A：策略研究

輸入：

> 幫我分析目前 BTC 是否適合做 breakout strategy
> 

Agent 可能步驟：

1. 查近期 BTC 價格與波動率
2. 查成交量與 open interest
3. 查近 7 天重大新聞
4. 檢索你過去寫的 breakout 策略筆記
5. 彙整成：
    - 是否符合 breakout regime
    - 風險因子
    - 需要驗證的條件

### 範例 B：策略產生

輸入：

> 根據最近 90 天 BTC 資料，給我 3 個可以回測的策略想法
> 

Agent 可能輸出：

- 趨勢跟隨策略
- 波動壓縮後突破策略
- 新聞事件驅動策略

並附上：

- 入場條件
- 出場條件
- 風控條件
- 建議回測區間

### 範例 C：結合你的私有研究知識

輸入：

> 依照我過去的研究偏好，設計一個 BTC swing trading 方案
> 

這時 LangChain 的價值不只是呼叫模型，而是：

- 用 RAG 把你的策略偏好檢索出來
- 把這些 context 與即時行情結合
- 再由模型生成更貼近你風格的策略草案

---

## 可視化功能

LangChain 本身常搭配 **LangSmith** 做 trace、觀測、評估與除錯。官方文件指出，LangSmith 可用於：

- trace requests
- evaluate outputs
- test prompts
- monitor 應用行為
- 視覺化 execution path 與 state transition

### 1. Trace / Observability

LangSmith 能把一次請求拆成多個 run / span，顯示：

- prompt 內容
- 模型輸出
- tool call
- tool result
- 最終答案

這對 debug agent 很有用。

### 2. Graph 視覺化

如果你用的是 LangGraph，官方文件指出可以把 workflow 建模成 graph，也提供 graph visualization。當流程複雜時，這對理解 node 與 edge 的關係很有幫助。

### 3. Studio 互動除錯

LangSmith Studio 是一個 agent IDE，可讓你：

- 視覺化 graph architecture
- 與 agent 互動
- 看每一步 prompt / tool call / 中間狀態
- time travel debug agent state

### 4. 評估與監控

LangSmith 也支援 dashboard、alerts、experiments、feedback 等 observability 能力，可用來看效能、穩定性與輸出品質。

---

## 使用 LangChain 開發 BTC 策略時的實際優點

### 優點 1：把流程拆模組

你可以把「行情取得」「策略規則生成」「研究筆記檢索」「輸出報告」拆成不同節點與工具，維護比把所有邏輯塞進一個 prompt 乾淨得多。

### 優點 2：方便整合 RAG

如果你有自己的策略筆記、失敗案例、風險偏好、歷史研究文件，LangChain 很適合當這些文件與模型之間的整合層。

### 優點 3：便於 debug

在交易策略這種高風險場景，不可觀測的 agent 很危險。LangSmith trace 能幫你看它到底查了什麼資料、用了哪些工具、在哪一步做出錯誤判斷。

---

## 你不能完全信任它「變數」的原因

你提到「讓我不能完全信任它的變數」，如果用工程語言來講，這其實非常合理。

這裡的「變數」可以理解成：

- prompt template 參數
- state 裡的欄位
- tool 回傳結果
- 中間推理步驟
- 模型輸出的結構化欄位

下面是幾個核心原因。

### 1. LLM 本質上不是傳統 deterministic function

同一組輸入，即使流程差不多，模型輸出仍可能變動。也就是說，你的 `signal_strength`、`market_regime`、`risk_score` 這種欄位，除非是由明確數學函式算出來，不然很多時候其實是 **模型推論結果**，不是硬邏輯保證值。

### 2. 中間 state 可能被 prompt 與上下文影響

LangGraph 的 state / node / edge 設計很強大，但也代表中間狀態會受到：

- 前一步輸出
- prompt wording
- tool result 格式
- state merge 邏輯
    
    共同影響。官方也特別提到 state 更新與 reducer 設計的重要性；若 reducer 或 state schema 設計不好，內容可能被覆蓋或累積方式不符預期。
    

### 3. Tool output 不一定可信

如果你的 BTC 系統串接：

- 行情 API
- 新聞 API
- 回測資料庫
- 自己寫的指標函式

那麼變數錯誤未必來自 LangChain，而可能來自：

- API 資料延遲
- 欄位格式變更
- 時區錯誤
- 指標函式 bug
- 回測資料污染

LangChain 只是 orchestration layer，不會自動保證外部資料正確。

### 4. 結構化輸出不代表語義正確

你可以要求模型輸出：

```
{
  "regime":"trend",
  "confidence":0.82,
  "entry_signal":true
}
```

即使格式正確，也不代表內容正確。

也就是說，**schema valid ≠ strategy valid**。

### 5. Prompt 變數名稱有時會帶來假穩定感

例如你定義：

- `trend_score`
- `volatility_regime`
- `macro_bias`

看起來很像嚴謹金融變數，但如果這些值是 LLM 經由文字敘述推導出來的，它們本質上比較接近：

- 模型主觀判斷
- 語義壓縮結果
- 啟發式標籤

而不是嚴格數值模型。

### 6. Agent 可能在錯誤前提下繼續推理

Agent workflow 最大的風險之一，是前面一步用了錯資料，後面步驟仍會繼續合理化。

例如：

1. tool 抓錯 BTC 時區資料
2. agent 誤判為放量突破
3. 再根據這個錯前提生成完整策略說明

最後你會得到一份**看起來很合理、其實建立在錯誤 state 上**的報告。

---

## 如何降低不可信任感

### 1. 把關鍵變數分成兩類

建議你區分：

### A. 可驗證變數

例如：

- 收盤價
- ATR
- RSI
- 報酬率
- 交易量
- funding rate

這些應該由程式或資料源直接算，不要交給 LLM 猜。

### B. 解釋型變數

例如：

- 市場情緒
- 宏觀偏多 / 偏空
- 策略風格建議
- 風險摘要

這些可以由模型生成，但必須標記為 **interpretive / heuristic**。

### 2. 為每個重要結論附上來源

例如讓 agent 輸出：

- 使用了哪些行情資料
- 哪篇研究筆記被檢索到
- 哪個工具算出的數值
- 這個結論是 rule-based 還是 model-inferred

### 3. 對關鍵節點做 deterministic 化

例如：

- 訊號判定規則改成 Python 函式
- 技術指標改成固定函式
- 風險參數改成 config
- 模型只負責「解釋」與「摘要」

### 4. 用 LangSmith 看中間過程

如果你覺得某個變數不可信，最好的方式不是猜，而是直接 trace。LangSmith 可以讓你看到 prompt、tool call、結果與最終輸出的鏈路。

---

## 實務建議：LangChain 在 BTC 策略系統裡應該扮演什麼角色

比較穩健的做法是：

### 適合交給 LangChain / LLM 的部分

- 策略想法生成
- 研究摘要
- 多來源資訊整合
- 將數據轉成可讀分析報告
- 從知識庫檢索你的歷史研究

### 不適合完全交給 LangChain / LLM 的部分

- 精確數值計算
- 訊號生成核心規則
- 風控參數決定
- 回測績效統計
- 真實下單條件判斷

一句話說：

> **LangChain 很適合當研究助手與流程編排層，不適合直接當最終交易決策引擎。**
> 

---

## 總結

LangChain 的核心價值，在於幫你把：

- 模型
- prompt
- 工具
- RAG
- agent workflow
- observability

整合成一個較完整的 LLM 應用開發框架。其 agent 相關能力又能進一步搭配 LangGraph 與 LangSmith，提供 graph workflow、視覺化與 tracing。

如果你拿它來做 BTC 交易策略開發，它最適合做的是：

- 研究流程自動化
- 策略知識整合
- RAG 問答
- 報告生成
- agent workflow orchestration

但你不應該完全相信它產生的中間變數，因為很多欄位其實只是模型推論結果，而不是傳統金融系統裡可驗證、可重現的 deterministic 變數。真正關鍵的交易邏輯，仍應由可測試、可回放、可驗證的程式規則掌控。