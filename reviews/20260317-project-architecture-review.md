# Project Architecture Review — Strategy Cycle & Agent Efficiency — 2026-03-17

## Scope

- Review angle: Senior Systems Architect + AI Agent
- Coverage: Full strategy cycle (ideation → implementation → backtest → analysis → next iteration)
- Focus: Agent TAO efficiency, skill precision, token reduction, phase transition integrity

---

## Findings

### 系統架構層面

#### A1 — 策略循環有三個斷點（HIGH）

**斷點 1：分析結束 → 下一輪規劃**
分析完成後，agent 產出的是 `freqtrade/reports/<stem>.zip`。下一個 session 的 agent 必須從 README、reports/、experiments/ 各自讀取才能知道「上次發現什麼、這次要改什麼」。沒有結構化交接文件，每次都要重建 context。

**斷點 2：沒有策略狀態追蹤**
無法從單一文件得知一個策略目前在哪個 phase、上次回測的 stem 是什麼、下一步預計做什麼。

**斷點 3：Phase transition 沒有明確 gate**
各 skill 描述「這個 phase 做什麼」，但沒有定義「這個 phase 結束的條件」。Agent 可能在 config 還沒生成前就去跑回測，或在分析未完成前就開始規劃下一輪。

#### A2 — README agent prompt 與 skills 重複（MEDIUM）

README 的 agent prompt 裡 7 條規則（路徑、格式等）與 skills 內容重複。Agent 加載 skills 後不需要再讀一遍，屬於無效 token 消耗。

#### A3 — Framework skills 內容太薄（MEDIUM）

`backtest-validation`、`performance-analysis`、`parameter-tuning` 三個 skill 各只有 ~15 行，沒有實際判斷標準。Agent 讀了之後仍需要自行推理，等同沒有 skill 的效果。這三個 skill 在功能上是同一個 Freqtrade workflow 的三段，可以合併。

#### A4 — 缺少跨輪改進的結構化格式（MEDIUM）

`improvement-planning` skill 說「找出 weakness，提出新假設」，但沒有固定格式。每次 agent 自由發揮，輸出格式不穩定，下輪 agent 難以直接繼承。

---

### AI Agent 效率層面

#### B1 — Session 開頭重建 context 成本高（HIGH）

每次 session 啟動的最低讀取鏈：

```
agent-general-skills.md   → ~50 tokens
trade-strategy.md         → ~80 tokens
相關 skill 1-2 個         → ~100-200 tokens
README.md（策略文件）     → ~200-500 tokens
相關 code files           → ~500-1500 tokens
```

大部分 token 花在「重建 context」，不在實際工作上。

#### B2 — TAO 缺少 domain-specific checkpoint（MEDIUM）

TAO 規則是通用的，但策略循環各 phase 沒有 domain-specific done criteria。Agent 執行「分析」時不知道分析到什麼程度算完成，容易過早結束或過度展開。

#### B3 — Improvement planning 輸出不可繼承（MEDIUM）

規劃輸出沒有固定結構，下一個 session 的 agent 無法直接讀取並繼承，必須重新推理。

---

## 建議行動項目

### P0 — 加入策略狀態文件 `STATUS.md`

**路徑**：`strategies/<family>/STATUS.md`

**格式**：
```markdown
# <strategy_family> Status

## Current Phase
<!-- implementation / backtest / analysis / planning -->

## Last Backtest
- Stem: <stem>
- Date: <YYYY-MM-DD>
- Key Metrics: PF=1.3, MaxDD=18%, Sharpe=0.9

## Current Hypothesis Being Tested
<一句話說明這輪在驗什麼>

## Blocking Issues
<!-- None，或列出問題 -->

## Next Action
<下一步要做什麼>
```

**效益**：Agent session 開頭一讀即定位，省去 500-1000 tokens 的 context 重建。

---

### P0 — Analysis 結束自動輸出 `analysis-summary.md`

分析完成後，agent 需額外將關鍵結論寫入：

**路徑**：`strategies/<family>/sessions/<YYYYMMDD>-analysis-summary.md`

**格式**：
```markdown
# Analysis Summary — <stem> — <YYYY-MM-DD>

## Key Metrics
- Profit Factor: X.XX
- Max Drawdown: XX%
- Win Rate: XX%
- Sharpe: X.XX
- Slippage 0.1% impact: -X.XX PF

## Top Failure Modes
1. <regime/condition>: <metric impact>
2. <regime/condition>: <metric impact>
3. <regime/condition>: <metric impact>

## Recommended Focus for Next Iteration
<具體建議，一到兩句>
```

**效益**：下輪 planning agent 只讀這一份，不需要重讀整個 zip 或 report。消除斷點 1。

---

### P1 — Phase Gate Checklist 加入 strategy-workflow/SKILL.md

在 `strategy-workflow/SKILL.md` 新增一節，明確各 phase 的完成條件：

```
Implementation 完成條件：
- [ ] freqtrade/strategies/<Name>.py 存在且無 TODO 標記
- [ ] strategies/<family>/engine/freqtrade/config.json 已生成（非 template placeholder）
- [ ] python -m lib.endpoints.freqtrade --mode backtest 可執行不報 import error
- [ ] STATUS.md 更新為 "backtest"

Backtest 完成條件：
- [ ] freqtrade/user_data/backtest_results/<stem>.json 存在
- [ ] STATUS.md 的 Last Backtest 已填入 stem 與 key metrics

Analysis 完成條件：
- [ ] freqtrade/reports/<stem>_<strategy>.zip 存在
- [ ] strategies/<family>/sessions/<date>-analysis-summary.md 已寫入
- [ ] STATUS.md 更新為 "planning"

Planning 完成條件：
- [ ] strategies/<family>/sessions/<date>-iteration-plan.md 已寫入
- [ ] STATUS.md 更新為 "implementation"（下一輪開始）
```

**效益**：消除斷點 3；agent 不會提早跳 phase；每輪結束留下可追蹤記錄。

---

### P1 — 精簡 README 的 agent prompt

**現況**：prompt 有 7 條規則（路徑、格式等），全部已在 skills 裡。

**建議改為**：
```
請先讀以下文件，再開始實作：
- knowledge-base/skills/agent-general-skills.md
- knowledge-base/skills/project-skills/trade-strategy.md

策略文件：strategies/<strategy_family>/README.md
策略狀態：strategies/<strategy_family>/STATUS.md

請先回覆：
- 你對這個策略的理解
- 你第一輪要做的事情
- 你預計會建立或修改哪些檔案
```

去掉重複規則後 prompt 縮短約 60%，skills 已是 source of truth。

---

### P2 — Improvement Iteration 模板加入 improvement-planning/SKILL.md

讓每輪改進有固定輸出格式，寫入 `strategies/<family>/sessions/<YYYYMMDD>-iteration-plan.md`：

```markdown
## Iteration N+1 Plan — <YYYY-MM-DD>

- **Observed weakness**: <具體 regime 或 metric>
- **Root cause hypothesis**: <為什麼這個 weakness 存在>
- **Change**: <改什麼>
- **Unchanged**: <不改什麼，避免 agent 自行擴題>
- **Expected metric shift**: PF > X.X, MaxDD < XX%
- **Experiment type**: parameter tweak / logic change / filter addition
- **Test timerange**: <OOS 區間>
```

**效益**：下輪 implementation agent 讀這份就知道要做什麼，不需要重讀分析報告。

---

### P2 — 合併三個薄 framework skills

`trade-strategy-backtest-validation` + `trade-strategy-performance-analysis` + `trade-strategy-parameter-tuning` 合併為單一 `freqtrade-analysis-workflow/SKILL.md`。

**理由**：三者功能上是同一 workflow 的三段（跑回測 → 看報告 → 調參數），合併後 agent 一次載入，省去多次讀取。

---

## 優先順序總覽

| 優先 | 項目 | 解決的問題 | 成本 |
|------|------|-----------|------|
| P0 | 加 `STATUS.md` 到每個策略 family 的 template | Session 開頭零重建成本 | 低 |
| P0 | Analysis 結束寫 `analysis-summary.md` | 分析→規劃斷點消除 | 低 |
| P1 | Phase gate checklist 加入 strategy-workflow | Agent 不會提早跳 phase | 低 |
| P1 | 精簡 README agent prompt | 開頭節省 60% prompt token | 低 |
| P2 | Improvement iteration 模板 | Planning 輸出格式穩定可繼承 | 低 |
| P2 | 合併三個薄 framework skills | 載入文件數減少 | 中 |
