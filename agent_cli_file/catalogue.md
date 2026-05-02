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

## 目錄結構

### Rules

`rules/` 放的是跨 agent、跨專案的規則、標準、政策與常駐行為指引。
這些文件不是可執行 skill，而是應優先遵守的共通約束。

@./rules/agent-general-rules.md
@./rules/file-encoding.md
@./rules/markdown-output-language.md
@./rules/tao-working-method.md
@./rules/skill-writing-standard.md
@./rules/trading-domain-constraints.md
@./rules/development-standards.md
@./rules/documentation-standards.md

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
- [trading-domain-constraints.md](./rules/trading-domain-constraints.md)
  交易領域常駐約束：費用、滑點、市場機制轉換，以及保守看待 model edge 的要求。
- [development-standards.md](./rules/development-standards.md)
  專案目錄結構、命名、編碼慣例與工作流完整性規範。
- [documentation-standards.md](./rules/documentation-standards.md)
  文件與程式碼保持一致的常駐規則：工作流變動時更新文件、以程式碼為準。

### Skills

`skills/` 放的是可執行工作流、任務技能。

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

#### Framework Skills

framework skill 用於特定技術框架或工具鏈。

Freqtrade：

- [backtest-preflight](./skills/framework-skills/freqtrade/backtest-preflight/SKILL.md)
- [data-readiness-check](./skills/framework-skills/freqtrade/data-readiness-check/SKILL.md)
- [download-data](./skills/framework-skills/freqtrade/download-data/SKILL.md)
- [freqtrade-analysis-workflow](./skills/framework-skills/freqtrade/freqtrade-analysis-workflow/SKILL.md)
- [look-ahead-bias-check](./skills/framework-skills/freqtrade/look-ahead-bias-check/SKILL.md)
- [oos-validation-gate](./skills/framework-skills/freqtrade/oos-validation-gate/SKILL.md)
- [trade-strategy-freqtrade-implementation](./skills/framework-skills/freqtrade/trade-strategy-freqtrade-implementation/SKILL.md)

#### General Skills

general skill 用於可重用的一般工作流。

Docs：

- [documentation-workflow](./skills/general-skills/docs/documentation-workflow/SKILL.md)
- [markdown-review](./skills/general-skills/docs/markdown-review/SKILL.md)

Agent Config：

- [agent-config-maintenance](./skills/general-skills/agent-config/agent-config-maintenance/SKILL.md)

Planka：

- [planka-debug](./skills/general-skills/planka-debug/SKILL.md)

## 分類原則

簡單判斷方式：

- 如果內容是「應該一直遵守的規則」，放 `rules/`
- 如果內容是「遇到某類任務時要執行的流程」，放 `skills/`

## 維護規則

- 新增 rule 時，更新本目錄的 `Rules` 區塊，並在 `@` import 清單加入對應檔案。
- 新增 skill 時，更新對應分類區塊。
- 若某份文件從 skill 轉為 rule，應同步更新本目錄與所有引用。
- 若某份文件只是 redirect stub，不應長期保留；完成搬遷後應刪除。
