---
title: multi-agent-harness-quantative-strategy-research
description: 
published: true
date: 2026-03-31T15:19:08.763Z
tags: 
editor: markdown
dateCreated: 2026-03-31T15:19:08.763Z
---

# Agentic-Research: 量化交易策略自動化實現協議 (2026)

## 1. 總體目標 (Total Goal)
建立一個基於 **LangGraph** 編排的自動化研究實驗室，將模糊的交易靈感透過「規格驅動開發 (SDD)」與「多代理人協作 (Multi-Agent Collaboration)」，轉化為具備高魯棒性、經過嚴格風險審查且可實際運行的 **Freqtrade** 量化策略。

---

## 2. 核心團隊架構 (The Agent Team)

| 角色 | 推薦模型 | 核心職責 | 接入方式 |
| :--- | :--- | :--- | :--- |
| **Harness 主管** | **Claude 4.5/4.6** | 流程編排、計畫審核、邏輯驗證、決策下達。 | Claude Code CLI |
| **策略情報員** | **Perplexity Pro** | 網路搜尋經典策略、論文、回測注意事項與防坑指南。 | Perplexity Search API |
| **代碼實作者** | **MiniMax 2.5 (Free)** | 負責大量的 Boilerplate 代碼撰寫、指標實作。 | OpenAI-compatible API |
| **紅隊審核員** | **DeepSeek R1 (Free)** | 代碼邏輯審計、前瞻偏差 (Look-ahead) 偵測、Bug 獵人。 | DeepSeek API |

---

## 3. 實現步驟 (Implementation Steps)

### 第一階段：概念細化與規格固化 (Explore & Spec)
* **參與者**：人 + Superpowers (Brainstorm) + OpenSpec (Explore)
* **動作**：
    1. 人提出初始靈感（如：基於波動率的均值回歸）。
    2. **Superpowers** 啟動 `brainstorming` 模式，主動對人進行深度訪談，挖掘參數細節。
    3. 透過 **OpenSpec** 的 `explore` 指令將對話紀錄固化為結構化的 `openspec/spec.md`。

### 第二階段：風險感知與技能增強 (Risk Assessment)
* **參與者**：Claude (主管) + Perplexity (情報)
* **動作**：
    1. Claude 讀取 `spec.md`，辨識所屬領域（如：ML 研究或高頻交易）。
    2. 自動指派 **Perplexity** 搜尋：「[策略類型] 在 Freqtrade 回測時的常見風險與 Best Practices」。
    3. 將搜尋結果轉化為 `rules/constraints.md`，作為後續開發的硬性約束。

### 第三階段：任務編排 (Orchestration)
* **參與者**：Claude (主管) + OpenSpec (FF)
* **動作**：
    1. LangGraph 觸發 Claude CLI，執行非交互式指令：`openspec ff`。
    2. **Claude** 根據 `spec.md` 生成極度詳細的 `tasks.md`，包含每個任務的 **驗證準則 (Acceptance Criteria)**。

### 第四階段：紀律化實作 (Implementation & TDD)
* **參與者**：MiniMax 2.5 (Coder) + Superpowers (TDD)
* **動作**：
    1. LangGraph 將 `tasks.md` 中的微型任務派發給 **MiniMax**。
    2. **Superpowers** 強制執行「測試驅動開發」，要求 MiniMax 每寫一個指標必須通過對應的 `pytest`。
    3. 複雜邏輯或集成問題由 **Claude** 介入處理。

### 第五階段：紅隊審計與回測 (Audit & Backtest)
* **參與者**：DeepSeek R1 (Validator) + 外部 Freqtrade 環境
* **動作**：
    1. **DeepSeek** 掃描產出的 `strategy.py`，尋找是否有「偷看未來數據」或「手續費漏算」等邏輯錯誤。
    2. 通過審核後，自動在 Docker 容器內執行 `freqtrade backtesting`。
    3. 解析結果 JSON 文件。

### 第六階段：評估與閉環迭代 (Evaluation & Loop)
* **參與者**：Claude (主管) + 人
* **動作**：
    1. 如果績效 (Sharpe, Drawdown) 達標，進入 `openspec archive` 封存策略。
    2. 如果不達標，由 **Claude** 根據失敗日誌分析原因，並決定是否修改 `spec.md` 重新啟動循環。

---

## 4. 自動化環境配置規範 (Harness Config)

### .clinerules / CLAUDE.md 元規則
```markdown
# 專案執行憲法
- **自動化優先**：當任務涉及量化開發，必須先調用 Perplexity 獲取「防坑清單」。
- **規格導向**：未經 `spec.md` 定義，嚴禁直接修改 `strategy.py`。
- **測試隔離**：所有代碼實作必須在 `Superpowers` 的獨立 Worktree 下完成。
- **回測保護**：DeepSeek 審計報告未通過前，禁止執行正式回測任務。