---
title: multi-agent-harness-quantative-strategy-research
description: Agentic Research Harness 開發初步規格：多代理人協作量化策略自動化研究協議
published: true
date: 2026-04-01T00:00:00.000Z
tags:
editor: markdown
dateCreated: 2026-03-31T15:19:08.763Z
---

# Agentic-Research: 量化交易策略自動化實現協議 (2026)

## 1. 總體目標 (Total Goal)

建立一個基於 **LangGraph** 編排的自動化研究實驗室，將模糊的交易靈感透過「規格驅動開發 (SDD)」與「多代理人協作 (Multi-Agent Collaboration)」，轉化為具備高魯棒性、經過嚴格風險審查且可實際運行的 **Freqtrade** 量化策略。

**設計原則**：
- Claude 作為主管，掌控全局、制定規則與技能；重複性或計算性工作交由其他模型或確定性程式完成。
- Harness 具備自我增強能力：執行過程中主動發現缺口，即時建立 rules/skills/code，並在迭代後固化為可重用知識。

---

## 2. 核心團隊架構 (The Agent Team)

| 角色 | 推薦模型 | 核心職責 | 接入方式 |
| :--- | :--- | :--- | :--- |
| **Harness 主管** | **Claude 4.6** | 流程編排、計畫審核、邏輯驗證、決策下達、規則與技能制定。 | Claude Code CLI |
| **策略情報員** | **Claude WebSearch**（主）/ Perplexity（深度研究選用） | 搜尋策略風險、防坑清單、相似策略成功案例；將結果固化為 skills。 | Claude Code 內建 WebSearch / Perplexity Search API |
| **代碼實作者** | **Gemini 2.5 Flash (Free)** | 根據詳細 tasks.md 撰寫 Freqtrade 策略代碼、指標實作、Boilerplate。 | gemini-api（已整合） |
| **假設挑戰者** | **DeepSeek R1 (Free)** | 質疑策略的市場假設，列舉對立假設與失敗場景，供優化計畫參考。 | DeepSeek API |

> **模型選擇說明**
> - MiniMax 2.5 在 Freqtrade 領域特化代碼上表現未經驗證，以已整合的 Gemini 2.5 Flash 取代。
> - DeepSeek R1 適合「邏輯推演與假設挑戰」，不適合做可以用確定性工具解決的代碼掃描。
> - DeepSeek V3（非 R1）用於複雜代碼 Layer 2 審計，速度比 R1 快 3-5 倍。
> - Perplexity 僅在需要學術論文查找或多源即時彙整時啟用，日常風險搜尋由 Claude WebSearch 處理。

---

## 3. 實現步驟 (Implementation Steps)

### 第一階段：概念細化與規格固化 (Explore & Spec)

* **參與者**：人 + Superpowers (Brainstorm) + OpenSpec (Explore)
* **動作**：
    1. 人提出初始靈感（如：基於波動率的均值回歸）。
    2. **Superpowers** 啟動 `brainstorming` 模式，主動對人進行深度訪談，挖掘參數細節。
    3. 透過 **OpenSpec** 的 `explore` 指令將對話紀錄固化為結構化的 `openspec/spec.md`。

### 第二階段：風險感知與技能增強 (Risk Assessment)

* **參與者**：Claude (主管) + Claude WebSearch（或 Perplexity）
* **動作**：
    1. Claude 讀取 `spec.md`，辨識所屬領域（如：ML 研究或趨勢跟蹤）。
    2. **執行前瞻檢查**（見第 4 節），確認現有 skill/rule 覆蓋範圍，識別缺口。
    3. 透過 **Claude WebSearch** 搜尋：「[策略類型] 在 Freqtrade 回測時的常見風險與 Best Practices」。
    4. 搜尋結果固化為 `rules/constraints.md` 或新增 skill，作為後續開發的硬性約束。
    5. 需要學術論文或深度多源研究時，改用 **Perplexity**。

### 第三階段：任務編排 (Orchestration)

* **參與者**：Claude (主管) + OpenSpec (FF)
* **動作**：
    1. LangGraph 觸發 Claude CLI，執行非交互式指令：`openspec ff`。
    2. **Claude** 根據 `spec.md` 生成極度詳細的 `tasks.md`，每個任務包含：
        - 驗證準則 (Acceptance Criteria)
        - **所需工具確認**：列出執行此任務需要的 skill/parser/rule，並確認是否存在

### 第四階段：紀律化實作 (Implementation & TDD)

* **參與者**：Gemini 2.5 Flash (Coder) + Superpowers (TDD)
* **動作**：
    1. LangGraph 將 `tasks.md` 中的微型任務派發給 **Gemini 2.5 Flash**。
    2. **Superpowers** 強制執行「測試驅動開發」，要求每寫一個指標必須通過對應的 `pytest`。
    3. 複雜邏輯或集成問題由 **Claude** 介入處理。

### 第五階段：審計與回測 (Audit & Backtest)

* **參與者**：既有 Skills (Layer 1) + DeepSeek V3 (Layer 2, 選用) + Freqtrade 環境

#### Layer 1：確定性審計（必做）

| 檢查項目 | Skill | 說明 |
| :--- | :--- | :--- |
| 前瞻偏差掃描 | `look-ahead-bias-check` | 掃描 `shift(-N)`、`merge_informative_pair` 等模式 |
| 回測前置三閘門 | `backtest-preflight` | 資料完整性、bias verdict、config 完整性 |
| OOS 驗證 | `oos-validation-gate` | OOS/IS profit factor ratio ≥ 0.5 |

Layer 1 全部 PASS 才進入回測。

#### 回測執行

```bash
freqtrade backtesting --config config.json --strategy <StrategyName> --timerange <range>
```

#### 結果解析（確定性 Parser，無 LLM）

Freqtrade 輸出為結構化 JSON，用 Python Parser 轉換為 agent-friendly 摘要再交給 Claude：

```
results.json → Python Parser → 診斷摘要（markdown）→ Claude 分析
```

Parser 職責：
- 提取關鍵指標（Sharpe、Drawdown、Win Rate、Profit Factor、交易次數）
- 對照 spec 門檻自動判定 PASS / WARN / FAIL
- 計算衍生指標（OOS/IS ratio、與 baseline 比較）
- 標記異常（如 Profit Factor > 3.0 → 前瞻偏差紅旗）

> **原則**：結構化資料用確定性程式解析，不讓 LLM 直接讀原始 JSON，避免數字誤讀與 token 浪費。

#### Layer 2：LLM 深度審計（選用）

若策略包含複雜邏輯（動態 shift、巢狀條件、ML 特徵），由 **DeepSeek V3** 執行深度代碼審查。

### 第六階段：結果分析與閉環迭代 (Evaluation & Loop)

* **參與者**：Claude (主管) + DeepSeek R1 (假設挑戰者)

#### 達標路徑

```
診斷摘要 PASS → Claude 確認 → openspec archive 封存策略
```

#### 未達標路徑

```
診斷摘要 FAIL
    ↓
DeepSeek R1：質疑策略市場假設
    「這個策略假設 X，在哪些情況下 X 根本不成立？列舉 3 個對立假設。」
    ↓
Claude：載入 trade-strategy-improvement-planning skill
    結合（失敗分析 + 對立假設 + 原始 spec + 過往迭代摘要）→ 修改後的 spec
    ↓
知識回饋步驟（見第 5 節）
    ↓
重啟迴圈（回到第一階段或第三階段）
```

---

## 4. 自我增強機制 (Self-Improvement Mechanisms)

這是 Harness 從「被動執行」進化為「主動準備」的關鍵設計。

### 4.1 前瞻檢查節點（Harness 層）

在 LangGraph 每個主要階段開始前，加入輕量 reflection node，Claude 執行以下自問：

```
給定任務：[task description]
1. 這類任務有哪些已知風險？
2. 查 knowledge-base/agent_cli_file/catalogue.md，現有 skills 是否覆蓋？
3. 若有缺口，需要先建立什麼工具才能繼續？
```

**行為結果**：
- 已有對應 skill → 載入，繼續執行
- 缺口存在 → 暫停主流程，先建立工具，再繼續

此節點本身不做實際工作，只做工具盤點。實作上可作為 graph.py 的 `preflight_node`，在 `plan_node` 之前執行。

### 4.2 CLAUDE.md 觸發規則

在 `CLAUDE.md` 加入明確觸發條件，Claude 在執行中自動識別並回應：

```markdown
## 工具建立觸發規則

**遇到 ML 元素**（特徵工程、模型訓練、預測信號）
→ 必須先查 `ml-trading-strategy` skill 確認前瞻偏差規則。
→ 若規則不存在，先透過 WebSearch 建立 `rules/ml-risk-constraints.md`，再繼續。

**遇到結構化輸出**（JSON、CSV、DB query result）需要 LLM 分析時
→ 必須先確認是否有對應的確定性 parser。
→ 若不存在，先建立 parser code，再由 Claude 分析 parser 輸出，不直接讀原始資料。

**第二次遇到相同類型的錯誤**
→ 不能只修 bug，必須將防錯邏輯建立為 rule 或加入對應 skill 的 checklist。

**執行任何回測前**
→ 必須執行 `backtest-preflight` skill 的三個閘門，無例外。
```

### 4.3 工具類型判斷標準

遇到需要建立工具時，依以下標準選擇類型：

| 產出類型 | 建立時機 | 範例 |
| :--- | :--- | :--- |
| **Rule** | 這個約束在所有同類任務都成立 | ML 訓練必須用 walk-forward，不能 random split |
| **Skill** | 這個工作流會重複出現在不同策略 | 每次回測後都需要解讀 OOS/IS ratio |
| **Code（parser/tool）** | 輸入是結構化資料，解析邏輯是確定性的 | Freqtrade JSON → 診斷摘要 |

**判斷原則**：若同樣的工作會在下一個策略研究中再次出現，就固化；若是一次性的就不用。

### 4.4 知識回饋步驟（每次迭代結束時）

第六階段結束後，Claude 執行一輪知識提取反思：

```
反思問題：
1. 本次迭代有哪些「臨時建立的工具」？→ 評估是否升級為正式 skill
2. 有哪些重複出現的錯誤模式？→ 加入 rules/constraints.md
3. 有哪些臨時寫的解析 code？→ 確認是否已整合進 codebase
```

輸出：`session-learnings.md`，由人審閱後決定哪些固化、哪些捨棄。

---

## 5. 完整流程圖

```
第一階段：Brainstorm + OpenSpec Explore → spec.md
    ↓
第二階段：前瞻檢查 → Claude WebSearch → rules/constraints.md + skills（補缺口）
    ↓
第三階段：OpenSpec FF → tasks.md（含 Acceptance Criteria + 所需工具確認）
    ↓
第四階段：Gemini 2.5 Flash 實作 + TDD（pytest）
    ↓
第五階段：Skills 審計 Layer 1 → Freqtrade 回測 → Python Parser → 診斷摘要
    [複雜邏輯] → DeepSeek V3 審計 Layer 2
    ↓
第六階段：Claude 分析診斷摘要
    [PASS] → Archive
    [FAIL] → R1 挑戰假設 → Claude 擬定優化計畫
    ↓
知識回饋：session-learnings.md → 固化 skills/rules/code → 重啟迴圈
```

---

## 6. 自動化環境配置規範 (Harness Config)

### CLAUDE.md 元規則

```markdown
# 專案執行憲法
- **規格導向**：未經 `spec.md` 定義，嚴禁直接修改 `strategy.py`。
- **前瞻檢查**：每個階段開始前，查 catalogue.md 確認工具覆蓋，有缺口先補工具再繼續。
- **搜尋優先**：量化開發前，必須先透過 Claude WebSearch 獲取防坑清單，並固化為 skill。
- **測試隔離**：所有代碼實作必須在獨立 Worktree 下完成。
- **審計閘門**：Skills Layer 1 審計未通過前，禁止執行正式回測。
- **Parser 優先**：遇到結構化輸出需要 LLM 分析時，必須先建立確定性 parser，不直接讀原始資料。
- **錯誤固化**：第二次遇到相同類型錯誤，必須建立 rule 防止再犯。
```

### LLM_CHAIN 建議配置

```bash
# Spec Review（多輪評審）
LLM_CHAIN=claude-api,gemini-api,deepseek-api

# 低成本開發模式
LLM_CHAIN=gemini-api,gemini-api
```

---

## 7. 各模型與工具職責邊界

| 任務類型 | 負責者 | 理由 |
| :--- | :--- | :--- |
| 流程決策、規則制定 | Claude | 需要完整脈絡與高可靠性 |
| 前瞻檢查 / 工具盤點 | Claude（reflection node） | 知道 catalogue 結構，判斷缺口 |
| 策略風險搜尋 | Claude WebSearch | 免費，已整合 |
| 深度研究 / 論文查找 | Perplexity（選用） | 多源彙整優勢 |
| Freqtrade 代碼生成 | Gemini 2.5 Flash | 免費，代碼品質佳，已整合 |
| 確定性代碼掃描（bias） | 既有 Skills + grep | 速度快，結果確定，無幻覺風險 |
| 複雜代碼深度審計 | DeepSeek V3 | 快，代碼理解足夠 |
| 假設挑戰 / 反向推演 | DeepSeek R1 | 推理能力，適合質疑前提 |
| 結構化資料解析 | Python Parser（確定性） | 結構化資料不交 LLM，避免誤讀與 token 浪費 |
| 結果分析 / 優化計畫 | Claude | 需要完整脈絡，跨迭代推理 |
| 知識固化判斷 | Claude + 人工審閱 | 機器提案，人決定是否固化 |
