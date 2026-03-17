# 交易策略實作步驟與 AI 協作建議 (Master Workflow)

這份文件定義了從概念到上線的完整流程，並針對您的工具鏈 (**Claude / Gemini / Codex / OpenCode**) 提供 **[Worker (執行)]** 與 **[Verifier (驗證)]** 的模型分配建議。

## 主流程與 LLM 推薦

### 1. 定義研究項目與交易目標 (Scope)
*   **Claude 3.7 Sonnet (Thinking)** - **[Verifier/架構師]** 定義嚴謹的金融邊界與目標。
*   **OpenCode (DeepSeek R1)** - **[邏輯檢查]** 推理目標中潛在的博弈漏洞或邏輯矛盾。
*   **Gemini 2.0 Flash** - **[快速檢索]** 對比 Repo 歷史項目，確保目標一致性。
*   **Codex** - **[實作可行性 reviewer]** 提前檢查目標是否會與現有 repo 結構、Freqtrade 實作方式或 artifact 流程衝突。

### 2. 歷史資料收集與 Point-in-time 驗證 (Data)
*   **Gemini 2.0 Pro (2M Context)** - **[Worker]** 唯一能處理超長 OHLCV 日誌並找出數據斷層的模型。
*   **Claude 3.7 Sonnet** - **[Verifier]** 驗證資料分割 (Train/OOS) 與防止 Look-ahead bias。
*   **OpenCode (DeepSeek R1)** - 負責推論複雜的數據異常與統計分佈偏移。
*   **Codex** - **[資料流程實作者]** 產出資料檢查腳本、欄位對齊修正與 repo 內可重現的資料處理程式。

### 3. 提出策略假說與 Baseline (Hypothesis)
*   **OpenCode (DeepSeek R1)** - **[Worker]** 深度推理策略 Alpha 來源與數學假說的正確性。
*   **Claude 3.7 Sonnet** - **[Verifier]** 檢查假說是否符合市場常識與風險控制。
*   **Gemini 2.0 Pro** - 提供歷史相似策略的橫向對比數據。
*   **Codex** - **[baseline 落地 reviewer]** 檢查假說是否能順利轉成可回測的 baseline 與策略檔，而不是停留在抽象想法。

### 4. 設計進出場、風險與原型 (Design)
*   **Claude 3.7 Sonnet** - **[Worker]** 撰寫標準化技術規範 (Spec) 與 `dbg_` 欄位定義。
*   **OpenCode (DeepSeek R1)** - **[Verifier]** 模擬極端行情測試進出場邏輯的數學邊界。
*   **Gemini 2.0 Flash** - 快速對齊專案 DTO 與 Service 介面規範。
*   **Codex** - **[實作映射 reviewer]** 檢查 spec 是否足夠具體到能直接映射成 `populate_indicators`、`populate_entry_trend` 與 `populate_exit_trend`。

### 5. Freqtrade 代碼實作 (Implementation)
*   **Codex / Claude 3.7 Sonnet** - **[Worker]** 產出 Freqtrade API 實作與複雜指標開發。
*   **Claude 3.7 Sonnet** - **[Verifier]** 執行 Code Review 並確保遵循 `Trade Strategy Development Skill`。
*   **Gemini 2.0 Flash** - 快速搜索相關 Python 函式庫用法與樣板。
*   **Codex** - **[首選 Worker]** 適合直接修改 repo 內檔案、補測試、調整策略路徑與同步更新相關 skill / markdown。

### 6. 回測、偏誤檢查與 OOS 驗證 (Backtest)
*   **Gemini 2.0 Pro** - **[Worker]** 分析巨量回測 JSON，找出 Look-ahead bias 與異常交易。
*   **Claude 3.7 Sonnet** - **[Verifier]** 判斷 PnL 曲線穩定度與 go/no-go 決策。
*   **OpenCode (DeepSeek R1)** - 負責計算與驗證高階風險指標（如 Ulcer Index）。
*   **Codex** - **[驗證流程實作者]** 產出回測自動化腳本、報表整理工具與 repo 內驗證流程修正。

### 7. 參數調整與穩定性檢查 (Tuning)
*   **Codex** - **[Worker]** 撰寫快速的 Hyperopt 搜尋空間腳本。
*   **Gemini 1.5 Pro** - **[分析員]** 從大量調參結果中尋找穩定高原。
*   **OpenCode (DeepSeek R1)** - **[Verifier]** 驗證參數意義是否符合物理性而非過度擬合。
*   **Claude 3.7 Sonnet** - **[Verifier]** 補充檢查調參結論是否真的回到風險與商業目標，而不是只優化單一分數。

### 8. 分析績效來源、失敗場景與風險特徵 (Analysis)
*   **Claude 3.7 Sonnet** - **[首席審計師]** 整合 `analyze_backtest_result.py` 報告，產出定論。
*   **Gemini 2.0 Pro** - 處理長交易紀錄的標籤化分類與關聯性檢索。
*   **OpenCode (DeepSeek R1)** - 深度分析失敗交易與市場 Regime 的潛在關聯。
*   **Codex** - **[分析管線實作者]** 補充分析腳本、欄位輸出與報告格式，讓失敗場景可重現追查。

### 9. 擬定下一迭代修改計劃 (Improvement)
*   **Claude 3.7 Sonnet** - 整合教訓並制定下一個 Major/Minor 版本計畫。
*   **OpenCode (DeepSeek R1)** - 提供跳脫框架的邏輯改進建議與數學修正。
*   **Gemini 2.0 Pro** - 對比歷史多版本演進數據。
*   **Codex** - **[變更影響 reviewer]** 檢查計畫是否需要同步修改策略檔、訓練腳本、artifact 命名、skill 與 session 文件。

### 10. Walk-forward 與部署前驗證 (Deployment)
*   **Claude 3.7 Sonnet** - **[Worker]** 編寫高安全性的 Dockerfile 與相對路徑檢測腳本。
*   **Gemini 2.0 Flash** - **[Verifier]** 比對本機與 Container 環境一致性。
*   **Codex** - 快速產出部署手冊與環境變數文件。
*   **Codex** - **[部署落地 Worker]** 適合實際修改啟動腳本、環境設定、路徑處理與 dry-run 驗證相關檔案。

## 使用指引
- 各步驟的詳細 **Detailed Skill** 請參考 `knowledge-base/skills/trade-strategy-*`。
- 開發時應嚴格遵守 `knowledge-base/skills/project-skills/trade-strategy/trade-strategy-development/SKILL.md` 的路徑與命名規範。
- 若任務包含「需要直接改 repo、補腳本、修 skill、同步更新 markdown」這類落地工作，預設優先讓 **Codex** 擔任 Worker，再交由其他模型做 verifier 或專項分析。
