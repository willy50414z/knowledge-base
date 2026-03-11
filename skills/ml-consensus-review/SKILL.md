---
name: ml-consensus-review
description: 專門用於 ML 專家的多維度審核、衝突解決與執行計畫檢驗。當多個 Session 文件（如 step2.4_session_gemini.md）對同一份程式碼產生不同意見時，使用此流程達成技術共識，並將產出歸檔至指定的實驗命名空間。
---

# ML Consensus Review Workflow (Namespaced)

當被要求以「ML 專家」角度驗證多個來源的風險建議並匯出執行計畫時，必須遵循此標準流程。

## 1. 實驗命名空間規範 (Experiment Namespacing)

- **`reports/`**：存放 `step2.x_session_gemini.md` 等共識報告與 `report_{timestamp}.md` 實驗績效報告。
- **`logs/`**：存放 `session_codex.md` 或訓練過程的細節紀錄。
- **`artifacts/`**：存放 `model.joblib`、`metadata.json` 與 `scaler.joblib`。

**執行原則**：在建立任何新文件前，必須先確認或詢問當前的 `experiment_name`（例如：`bti_xgb_v1`）。

## 2. 核心流程階段 (Core Workflow Phases)

### Phase 1: 衝突識別與審核 (Conflict Identification)

- **識別未達成共識項目**：對比不同來源對同一份代碼的修改建議。
- **批閱評論**：針對每一項建議，根據代碼實際邏輯進行點評。
- **補充意見**：主動補充現有文件未提及的關鍵 ML 風險（如標籤語意、回測偏誤）。

### Phase 2: 爭議整理與共識判定 (Conflict Resolution)

- **整理爭議項目**：明確區分「高優先級核心風險」與「低優先級研究增強項」。
- **判定狀態**：標註為 `[Consensus Reached]` 或 `[Pending Discussion / Expert Overruled]`。

### Phase 3: 執行計畫驗證 (Plan Validation)

- 根據共識結果，整理出具備優先級的 **Consolidated Next Actions**。

---

## 3. 匯出 Markdown 固定格式 (Standard Output Format)

輸出的 `.md` 文件必須包含以下結構：

### A. 溯源資訊 (Metadata)

- **實驗名稱 (Experiment)**: `{experiment_name}`
- **來源文件**: `[來源文件A.md]`, `[來源文件B.md]`
- **目標代碼**: `[目標程式碼.py]`

### B. 核心風險驗證 (Consolidated Validation)

- 使用 `###` 標題區分風險類別。
- 必須包含：**驗證結果**、**專家評估**、**修正建議**。

### C. 爭議項目裁決表 (Expert Ruling Table)

| 爭議項目 | 來源 A 觀點 | 來源 B 觀點 | **專家裁決 (共識狀態)**    |
|:-----|:--------|:--------|:-------------------|
| 項目名稱 | 觀點摘要    | 觀點摘要    | [達成共識/尚須討論] + 裁決理由 |

### D. 綜合執行清單 (Consolidated Next Actions)

- 按優先級（Phase 1: Correctness, Phase 2: Validation, etc.）排序。

---

## 4. 執行原則 (Operational Principles)

1. **代碼為唯一真理**：以實際代碼邏輯作為判斷基準。
2. **優先修復阻塞性風險 (Blockers)**：標籤正確性、回測信噪比優先於 HPO 或特徵選擇。
