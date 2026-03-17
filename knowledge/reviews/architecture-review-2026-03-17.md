# Architecture & Skills Review — 2026-03-17

> 以資深系統架構師與 AI Agent 雙角度對 `trade_strategy` 專案的審查報告。

---

## 一、資深系統架構師視角

### 整體評估

架構方向正確，但骨架多於肉。分層概念清楚，可擴展性設計合理，但核心業務層尚未實作，存在幾個部署與維護風險。

---

### 優點

- **分層清晰**：`lib/`（應用層）/ `freqtrade/`（引擎層）/ `data/`（資料層）/ `strategies/`（策略文件層）概念邊界明確
- **可擴展的 enum 設計**：exchange / market_type / timeframe 以 enum 定義，新增品種只需加值
- **Feather 格式快取**：kline 資料以 Apache Feather 快取，I/O 效能合理
- **策略文件與程式碼分離**：`strategies/<family>/` 存 markdown artifact，引擎程式碼在 `freqtrade/`，不混雜

---

### 問題與建議

#### P0-1｜`lib/strategy/` 是空殼 — 最大架構缺口

```
lib/strategy/research/     # 空
lib/strategy/execution/    # 空
lib/strategy/analytics/    # 空
lib/strategy/registry/     # 空
```

這是整個專案最核心的一層，但完全沒有實作。目前策略流程實際上是：

```
手動讀文件 → 手動寫 freqtrade/strategies/*.py → 手動執行回測
```

沒有任何 orchestration 層。

**建議**：在真正有第一個策略家族之前，先定義 `execution/` 的介面（`strategy_runner.py`），讓 freqtrade 成為其中一個 backend，而不是唯一入口。

---

#### P0-2｜`config.ini` 不存在於 repo，但是 runtime 依賴

`config_util.py` 和 `telegram_svc.py` 都依賴 `lib/utils/config.ini`，但這個檔案不在 repo 中。

**問題**：新環境部署會直接 `FileNotFoundError`，且沒有任何文件告訴使用者要怎麼建立。

**建議**：提供 `config.ini.example` 模板，或改用環境變數（更符合 12-factor app 原則）。

---

#### P1-1｜策略與 Freqtrade 緊耦合，`execution_engine/` 是空的

`lib/client/execution_engine/` 存在但沒有任何程式碼。目前策略直接寫成 Freqtrade class，未來換引擎成本很高。

**建議**：至少定義一個 `BaseEngine` 抽象介面：

```python
class BaseEngine:
    def run_backtest(self, strategy, config) -> BacktestResult: ...
    def run_hyperopt(self, strategy, config) -> HyperoptResult: ...
```

即使現在只有 Freqtrade 實作，介面存在就能防止耦合惡化。

---

#### P1-2｜Storage 層完全缺失，I/O 邏輯散落在 adapter

`lib/client/storage/` 是空的，但 `binance_svc.py` 直接做檔案讀寫（.feature 檔）。Storage concern 混入了 exchange adapter。

**建議**：建立 `lib/client/storage/feature_store.py`，把 Feather 讀寫封裝進去，`binance_svc` 只負責 API 呼叫。

---

#### P1-3｜`analyze_backtest_result.py` 過度膨脹

這個檔案超過 41,000 行，完全違反 single responsibility。任何修改都需要在巨型檔案中定位。

**建議**：拆成至少三個模組：

- `report_loader.py`：讀取 Freqtrade JSON 報告
- `report_analyzer.py`：計算 Sharpe、Drawdown 等指標
- `report_formatter.py`：輸出格式化結果

---

#### P1-4｜資料路徑雙軌並存，沒有自動清理機制

```
data/EXCHANGE/MARKETTYPE/          # 舊路徑（legacy）
data/features/EXCHANGE/MARKETTYPE/ # 新路徑（preferred）
```

`binance_svc.py` 同時支援兩者，但沒有 migration script，也沒有截止點。時間久了會讓人不知道哪個才是 source of truth。

**建議**：設定一個明確的 cutoff（例如 2026-Q3），舊路徑之後只讀不寫，並在 README 標記 deprecated。

---

#### P2-1｜5 個 Agent 指令檔完全相同，沒有差異化

`CLAUDE.md` / `AGENTS.md` / `CODEX.md` / `COPILOT.md` / `GEMINI.md` 內容一樣。違反 DRY，更重要的是沒有發揮每個 agent 的優勢。

**建議**：共用指令抽到 `AGENTS_SHARED.md` 讓各檔案 include，然後各自加上差異化指令（例如 Claude 擅長程式碼推理，Gemini 擅長長文件分析）。

---

#### P3-1｜缺少測試框架

整個 `lib/` 沒有任何 unit test 或 integration test。對於策略邏輯（如技術指標計算、資料驗證），測試是防止 silent bug 的唯一保障。

**建議**：建立 `tests/` 目錄，至少對 `tech_idx_svc.py`、`ml_svc.py`、`type_utils.py` 加基本測試。

---

## 二、AI Agent 視角

### 整體評估

知識庫設計紮實，18 個 skill 覆蓋完整的策略研究生命週期，防偏誤意識強。但載入路徑過深、缺少實作引導，Agent 使用成本偏高。

---

### 優點

- **18 個 skill 覆蓋全面**：從 scope → hypothesis → design → implementation → tuning → analysis，完整的策略研究生命週期
- **防偏誤意識強**：lookahead bias、OOS 驗證、基準比較在多個 skill 中強調
- **分類合理**：domain / framework / project / general 四層分類清晰

---

### 問題與建議

#### P1-1｜載入鏈過深，token 消耗高

一個 agent 開始工作前需要讀：

```
CLAUDE.md → agent-general-skills.md → trade-strategy.md → SKILL.md（task-specific）
```

最少 4 次檔案讀取，且 `trade-strategy.md` 本身就列出 15 個 skill。每次對話都要重複這個過程。

**建議**：在 `CLAUDE.md` 加入 **quick context summary**（5-10 行），讓 agent 不需要讀完整 skill 鏈就能處理簡單任務。只有複雜任務才深入載入。

---

#### P1-2｜Skill 選擇指引太粗略，agent 容易誤判

`trade-strategy.md` 底部的 Selection Guidance 只有 4 條規則，但實際情境往往跨越邊界。

例如「分析這次回測結果並更新 improvement plan」同時涉及 `performance-analysis` + `improvement-planning`，現有指引無法處理。

**建議**：加入 **task pattern → skill 組合** 的對照表：

| 任務類型 | 主要 Skill | 輔助 Skill |
|---------|-----------|-----------|
| 新策略起步 | trade-strategy-scope | trade-strategy-hypothesis-baseline |
| 回測後改進 | trade-strategy-performance-analysis | trade-strategy-improvement-planning |
| ML 策略實作 | trade-strategy-freqtrade-implementation | ml-trading-strategy |
| 資料準備 | data-pipeline（待建） | trade-strategy-data-validation |

---

#### P1-3｜Skills 沒有引用現有程式碼，agent 要猜模組位置

所有 skill 都是概念性描述，沒有指向實作。當 agent 要「計算技術指標」時，它不知道應該用 `lib/ohlcv_data_handler/tech_idx_svc.py`；要「抓 Binance 資料」時也不知道 `lib/client/crypto_exchange/binance_svc.py`。

**建議**：在對應 skill 結尾加 **Code Reference** 段落，例如：

```markdown
## Code Reference
- 技術指標計算：`lib/ohlcv_data_handler/tech_idx_svc.py`
- Binance 資料：`lib/client/crypto_exchange/binance_svc.py`
- ML 工具：`lib/ml/ml_svc.py`
```

---

#### P2-1｜缺少「資料工作流」Skill

現有 skill 覆蓋策略研究和 Freqtrade 實作，但沒有一個 skill 說明：

- 什麼時候要 fetch 新資料
- 如何驗證資料完整性（缺 candle > 0.1% 要重拉）
- feature cache 的有效期和更新策略

這些邏輯散落在 `trade-strategy-data-validation/SKILL.md` 的邊緣，沒有獨立的操作指引。

**建議**：新增 `data-pipeline/SKILL.md`，覆蓋 fetch → validate → cache → version 的完整流程。

---

#### P2-2｜缺少 LLM 協作 / 多 agent 使用指引

`lib/llm_agent/` 有完整的 LLM routing 實作，但 knowledge-base 完全沒有說明如何使用它。Agent 不知道：

- 什麼任務該 call Gemini vs Codex vs OpenCode
- `call_llm_cli.py` 的使用時機
- 多 agent 如何協作完成一個策略研究流程

**建議**：新增 `llm-orchestration/SKILL.md`，說明各 LLM 的分工和 CLI 用法。

---

#### P2-3｜`knowledge-base/knowledge/` 嚴重未被利用

目前只有 LangChain 入門和 BTC 15m LSTM 一個策略記錄。這裡應該是最有價值的長期知識沉澱點（失敗的策略、市場觀察、參數調整的歷史紀錄），但幾乎是空的。

**建議**：建立主題資料夾（如 `knowledge/trading/market-regime/`），讓每次策略分析的洞察都沉澱為可引用的知識。

---

#### P3-1｜Skill 沒有版本或有效期概念

Strategy skill 裡寫的費率（0.04%）、成功門檻（Profit Factor > 1.5）等數字是靜態的。市場環境變化後這些數字可能失效，但沒有機制提醒更新。

**建議**：在每個包含市場假設的 skill 加 `last_reviewed:` frontmatter，超過一定時間（如 6 個月）時提示使用者驗證是否仍適用。

---

## 三、優先改善建議彙整

| 優先級 | 項目 | 類別 | 預期效益 |
|--------|------|------|---------|
| P0 | 提供 `config.ini.example` | 架構 | 防止新環境部署失敗 |
| P0 | 定義 `lib/strategy/execution/` 介面 | 架構 | 防止策略層空殼化 |
| P1 | 建立 `lib/client/storage/feature_store.py` | 架構 | 解除 I/O 與 adapter 的耦合 |
| P1 | 定義 `BaseEngine` 介面 | 架構 | 防止策略與 Freqtrade 深度耦合 |
| P1 | 拆分 `analyze_backtest_result.py` | 架構 | 可維護性提升 |
| P1 | Skill 加 Code Reference 段落 | Agent | Agent 定位程式碼更快 |
| P1 | 加入 task pattern → skill 對照表 | Agent | 減少 skill 選擇錯誤 |
| P1 | `CLAUDE.md` 加入 quick context summary | Agent | 降低每次對話的載入成本 |
| P2 | 新增 `data-pipeline/SKILL.md` | Agent | 補充資料工作流指引 |
| P2 | 新增 `llm-orchestration/SKILL.md` | Agent | 讓多 agent 協作有依據 |
| P2 | 設定舊資料路徑 deprecated cutoff | 架構 | 消除雙軌資料路徑混亂 |
| P2 | 5 個 agent 指令檔差異化 | 兩者 | 發揮各 agent 強項 |
| P3 | Skill 加 `last_reviewed` frontmatter | Agent | 防止過時假設被沿用 |
| P3 | 建立 `tests/` | 架構 | 防止 silent bug |
