# Knowledge Base 知識庫

本 repository 是一個 **集中式 Markdown 知識庫**，主要用於：

* 個人知識管理
* AI 開發資源整理
* Prompt library
* RAG 資料來源
* 專案文件管理

所有內容皆以 **Markdown 檔案**保存，方便：

* 本地編輯（VS Code 等）
* AI 系統讀取
* Wiki / 文件網站瀏覽
* Git 版本控制

---

# Repository 架構

```
knowledge-base
│
├─ knowledge/          # 長期知識與學習資料
│  ├─ ai/              # AI 技術知識與研究筆記
│  ├─ investing/       # 投資策略與研究
│  ├─ semiconductor/   # 半導體相關知識
│  ├─ tools/           # 好用工具整理
│  └─ learning/        # 一般學習筆記
│
├─ ai/                 # AI 系統資源
│  ├─ prompts/         # Prompt library
│  │  ├─ system/
│  │  ├─ coding/
│  │  └─ agents/
│  │
│  ├─ rag/             # RAG 設計與配置
│  └─ agents/          # Agent 設計與技能
│
├─ projects/           # 各專案文件
│
├─ daily/              # 每日筆記
│
└─ inbox/              # 快速捕捉筆記
```

---

# 各資料夾用途

## knowledge/

此資料夾存放 **長期知識與學習資料**。

例如：

* AI 概念
* 技術筆記
* 研究整理
* 學習筆記

範例：

```
knowledge/ai/transformer架構.md
knowledge/investing/因子投資.md
knowledge/semiconductor/mosfet基礎.md
```

這些內容通常是 **穩定知識**，適合做為 **RAG 資料來源**。

---

## ai/

此資料夾存放 **AI 系統會直接使用的資源**。

例如：

* system prompts
* agent 設計
* RAG config
* workflow

範例：

```
ai/prompts/system/research-agent.md
ai/prompts/coding/code-review.md
ai/rag/chunking-strategy.md
ai/agents/langchain-agent-template.md
```

這些資源通常會被：

* AI agent
* automation workflow
* RAG pipeline

直接使用。

---

## projects/

每個專案建立一個資料夾。

範例：

```
projects/
  ai-trading-agent/
    overview.md
    architecture.md
    prompts.md
```

用途：

* 專案知識
* 系統設計
* 實驗紀錄

---

## daily/

每日工作與研究紀錄。

範例：

```
daily/
  2026-03-10.md
  2026-03-11.md
```

內容可能包含：

* 開發進度
* 學習筆記
* 研究心得

---

## inbox/

快速記錄想法或臨時筆記。

範例：

```
inbox/
  ai-agent-idea.md
  interesting-tool.md
```

之後應該整理到：

* knowledge
* projects
* ai

---

# 知識流動流程

一般 workflow：

```
想法 / 筆記
     │
     ▼
   inbox
     │
     ▼
   整理
     │
     ▼
knowledge / projects / ai
```

每日紀錄流程：

```
daily notes
     │
     ▼
提取重要知識
     │
     ▼
knowledge
```

---

# AI / RAG 整合

此 repository 也可作為 **AI RAG 系統的資料來源**。

建議 ingestion：

```
RAG sources
  ├─ knowledge/
  └─ projects/
```

排除：

```
daily/
inbox/
```

原因：

* daily 與 inbox 多為暫時資料
* 噪音較多

---

# 建議使用方式

1. 想法先記錄在 `inbox/`
2. 每日工作記錄在 `daily/`
3. 穩定知識整理到 `knowledge/`
4. AI 資源放在 `ai/`
5. 專案相關資料放在 `projects/`

---

# 此架構的優點

* Markdown 集中管理
* 適合 AI RAG 系統
* 知識與系統資源分離
* Git 版本控制
* 可搭配 Wiki / Docs UI
