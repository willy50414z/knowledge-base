# LangChain 學習計畫與功能概覽

這份計畫旨在引導您從基礎概念逐步深入到進階的 LangChain 生態系應用。

---

### 第一階段：基礎核心 (Model I/O)
學習如何與大語言模型（LLM）進行最基本的互動。
*   **Prompts (提示詞)**：學習提示詞模板 (Prompt Templates) 的建立與參數化。
*   **Chat Models & LLMs**：區分封裝後的聊天模型與傳統 LLM 的呼叫方式。
*   **Output Parsers (輸出解析器)**：將模型的字串輸出轉換為結構化資料（如 JSON、Pydantic 物件）。

### 第二階段：資料連接 (Data Connection)
學習如何讓 LLM 存取外部私有資料（即 RAG 流程）。
*   **Document Loaders (文件載入器)**：讀取 PDF、HTML、TXT、Notion 等各種格式。
*   **Document Transformers (文件轉換)**：學習文字分割 (Text Splitting) 策略。
*   **Text Embedding Models (嵌入模型)**：將文字轉為向量。
*   **Vector Stores (向量資料庫)**：儲存與檢索向量資料（如 Chroma, Pinecone, FAISS）。
*   **Retrievers (檢索器)**：進階檢索演算法（如 Multi-query, Contextual compression）。

### 第三階段：鏈 (Chains)
學習如何將多個元件串接在一起。
*   **LCEL (LangChain Expression Language)**：掌握最新的宣告式開發語法（管道符號 `|`）。
*   **Sequential Chains**：串接多個處理步驟。
*   **Runnable Interface**：理解 `invoke`, `batch`, `stream` 等標準化介面。

### 第四階段：記憶 (Memory)
學習如何讓模型記住對話上下文。
*   **Chat Message History**：儲存對話紀錄。
*   **Conversation Buffer**：管理對話窗口的大小與摘要。

### 第五階段：代理人 (Agents & Tools)
學習如何讓 LLM 自動決定要使用哪些工具。
*   **Tools (工具)**：封裝 API 或函式供模型呼叫。
*   **AgentExecutor**：執行代理人的循環邏輯。
*   **Toolkits**：針對特定場景（如 SQL 資料庫、GitHub）的預設工具包。

### 第六階段：進階生態系
學習如何構建生產級別的應用。
*   **LangGraph**：建立複雜、有狀態的多代理人循環系統（目前的業界主流）。
*   **LangSmith**：進行鏈與代理人的追蹤 (Tracing)、調試 (Debugging) 與評估。
*   **LangServe**：將 LangChain 物件快速部署為 REST API。

---
*最後更新日期：2026-03-10*
