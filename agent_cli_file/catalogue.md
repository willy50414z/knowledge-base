# Agent CLI File Catalogue

這份目錄是 `knowledge-base/agent_cli_file` 的總覽入口。

目的：

- 讓任何專案中的 Markdown 文件或 agent，在需要了解這個路徑下有哪些規則與技能時，可以先讀這份目錄。
- 快速分辨哪些文件屬於 `rules`，哪些屬於 `skills`。
- 降低冷啟動時的搜尋成本，避免直接在整個樹狀結構中盲讀。

## 使用方式

建議讀取順序：

1. 先看 `rules/`，理解共通規則、輸出格式、編碼、工作方法。
2. 再看 `skills/`，依任務類型選擇對應技能。
3. 若任務屬於交易策略專案，先讀 project routing 文件，再進入對應 `SKILL.md`。

## 目錄結構

### Rules

`rules/` 放的是跨 agent、跨專案的規則、標準、政策與常駐行為指引。
這些文件不是可執行 skill，而是應優先遵守的共通約束。

@./rules/agent-general-rules.md
@./rules/codex-execution-permissions.md
@./rules/file-encoding.md
@./rules/markdown-output-language.md
@./rules/tao-working-method.md
@./rules/skill-writing-standard.md

- [agent-general-rules.md](./rules/agent-general-rules.md)
  規則總入口。適合當作 agent 冷啟動時的第一份索引。
- [file-encoding.md](./rules/file-encoding.md)
  文字檔一律使用 UTF-8、UTF-8 without BOM、保留既有換行等編碼規則。
- [markdown-output-language.md](./rules/markdown-output-language.md)
  產出或改寫 Markdown 時，預設使用中文。
- [tao-working-method.md](./rules/tao-working-method.md)
  TAO 工作法：Thought、Action、Observation。
- [skill-writing-standard.md](./rules/skill-writing-standard.md)
  skill 與 rule 的分類、命名、放置與維護規則。

### Skills

`skills/` 放的是可執行工作流、任務技能、專案 routing 文件，以及少數 prompt 資產。

#### Project Skills

project skill 用於專案層級 routing、流程控制、專案特有工作流。

- [trade-strategy.md](./skills/project-skills/trade-strategy.md)
  交易策略專案的 routing 入口。
- [common_prompt.md](./skills/project-skills/trade-strategy/common_prompt.md)
  交易策略相關 prompt 資產。

交易策略專案技能：

- [artifact-triage](./skills/project-skills/trade-strategy/artifact-triage/SKILL.md)
- [backtest-analysis-review](./skills/project-skills/trade-strategy/backtest-analysis-review/SKILL.md)
- [code-review-md-export](./skills/project-skills/trade-strategy/code-review-md-export/SKILL.md)
- [experiment-compare](./skills/project-skills/trade-strategy/experiment-compare/SKILL.md)
- [knowledge-extraction](./skills/project-skills/trade-strategy/knowledge-extraction/SKILL.md)
- [llm-orchestration](./skills/project-skills/trade-strategy/llm-orchestration/SKILL.md)
- [multi-agent-consensus](./skills/project-skills/trade-strategy/multi-agent-consensus/SKILL.md)
- [session-close](./skills/project-skills/trade-strategy/session-close/SKILL.md)
- [strategy-bootstrap](./skills/project-skills/trade-strategy/strategy-bootstrap/SKILL.md)
- [strategy-cycle-orchestrator](./skills/project-skills/trade-strategy/strategy-cycle-orchestrator/SKILL.md)
- [strategy-workflow](./skills/project-skills/trade-strategy/strategy-workflow/SKILL.md)
- [trade-strategy-deployment-prep](./skills/project-skills/trade-strategy/trade-strategy-deployment-prep/SKILL.md)
- [trade-strategy-development](./skills/project-skills/trade-strategy/trade-strategy-development/SKILL.md)

#### Domain Skills

domain skill 用於特定領域知識與方法，不綁定某個單一專案。

ML：

- [ml-trading-strategy](./skills/domain-skills/ml/ml-trading-strategy/SKILL.md)
- [ml-workflow](./skills/domain-skills/ml/ml-workflow/SKILL.md)

Trading：

- [data-pipeline](./skills/domain-skills/trading/data-pipeline/SKILL.md)
- [regime-filter-validation](./skills/domain-skills/trading/regime-filter-validation/SKILL.md)
- [strategy-performance-evaluation](./skills/domain-skills/trading/strategy-performance-evaluation/SKILL.md)
- [trade-strategy-data-validation](./skills/domain-skills/trading/trade-strategy-data-validation/SKILL.md)
- [trade-strategy-hypothesis-baseline](./skills/domain-skills/trading/trade-strategy-hypothesis-baseline/SKILL.md)
- [trade-strategy-improvement-planning](./skills/domain-skills/trading/trade-strategy-improvement-planning/SKILL.md)
- [trade-strategy-prototype-design](./skills/domain-skills/trading/trade-strategy-prototype-design/SKILL.md)
- [trade-strategy-scope](./skills/domain-skills/trading/trade-strategy-scope/SKILL.md)
- [trading-domain](./skills/domain-skills/trading/trading-domain/SKILL.md)

#### Framework Skills

framework skill 用於特定技術框架或工具鏈。

Freqtrade：

- [backtest-preflight](./skills/framework-skills/freqtrade/backtest-preflight/SKILL.md)
- [data-readiness-check](./skills/framework-skills/freqtrade/data-readiness-check/SKILL.md)
- [download-data](./skills/framework-skills/freqtrade/download-data/SKILL.md)
- [freqtrade-analysis-workflow](./skills/framework-skills/freqtrade/freqtrade-analysis-workflow/SKILL.md)
- [look-ahead-bias-check](./skills/framework-skills/freqtrade/look-ahead-bias-check/SKILL.md)
- [oos-validation-gate](./skills/framework-skills/freqtrade/oos-validation-gate/SKILL.md)
- [trade-strategy-backtest-validation](./skills/framework-skills/freqtrade/trade-strategy-backtest-validation/SKILL.md)
- [trade-strategy-freqtrade-implementation](./skills/framework-skills/freqtrade/trade-strategy-freqtrade-implementation/SKILL.md)
- [trade-strategy-parameter-tuning](./skills/framework-skills/freqtrade/trade-strategy-parameter-tuning/SKILL.md)
- [trade-strategy-performance-analysis](./skills/framework-skills/freqtrade/trade-strategy-performance-analysis/SKILL.md)

#### General Skills

general skill 用於可重用的一般工作流。

Docs：

- [documentation-workflow](./skills/general-skills/docs/documentation-workflow/SKILL.md)
- [markdown-review](./skills/general-skills/docs/markdown-review/SKILL.md)

## 分類原則

簡單判斷方式：

- 如果內容是「應該一直遵守的規則」，放 `rules/`
- 如果內容是「遇到某類任務時要執行的流程」，放 `skills/`
- 如果內容是「某專案的入口導覽」，保留在 `skills/project-skills/*.md`
- 如果內容是 prompt 資產或模板，不必硬改成 rule 或 skill，但應在這份目錄中列出

## 維護規則

- 新增 rule 時，更新本目錄的 `Rules` 區塊。
- 新增 skill 時，更新對應分類區塊。
- 若某份文件從 skill 轉為 rule，應同步更新本目錄與所有引用。
- 若某份文件只是 redirect stub，不應長期保留；完成搬遷後應刪除。
