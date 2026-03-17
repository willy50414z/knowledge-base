# TAO 循環優化 Review

**Date**: 2026-03-17
**Reviewer**: Claude Sonnet 4.6（系統架構師 + AI Agent 視角）
**Scope**: 基於現有 multi-agent review（20260317）已修復項目之上的第二輪 review
**Dimensions**:
1. 用戶 TAO 循環斷點（策略發想 → 實現 → 測試 → 分析 → 下一步）
2. AI Agent skill 調用與效率優化
3. Token 消耗優化（不降低推理精準度）

---

## 前提說明

multi-agent review（20260317）已處理第一輪問題（FeatureStore 對稱性、OOS gate、phase-gated routing、data-readiness-check 等）。本 review 的對象是**目前仍存在的斷點與優化空間**，不重複已修復的問題。

---

## Part 1：用戶 TAO 循環斷點

### B1 — 最嚴重：`_context_digest.md` 無自動更新（PENDING A-3）

這是目前整個循環最脆弱的單點。

- Digest 是 L0 cold-start artifact，設計上每次 session 結束要更新
- A-3 狀態仍是 PENDING：沒有任何機制確保它被更新
- **後果**：Stale digest 比沒有 digest 更危險——agent 讀到舊的 phase/metrics，執行錯誤的 skill，用戶以為 session 是連續的但實際上是在過時的狀態上操作

**現象**：用戶開新 session 說「繼續上次的分析」，agent 讀到 stale digest → phase 顯示 `backtest`，但實際 STATUS.md 已是 `analysis` → 載入錯誤的 skill。

**建議**：把 digest 更新加進 `strategy-cycle-orchestrator` 的最後一步（已有 4 步流程，加第 5 步）；或創建 `session-close` skill（見 S1）。

---

### B2 — 高：Phase 轉換依賴 agent 自律，無強制機制

`implementation → backtest → analysis → planning` 轉換需要 agent 主動更新 STATUS.md。但：

- 沒有任何 gate 檢查「STATUS.md 是否已更新到對應 phase」
- 如果 agent 跑完 backtest 但沒更新 phase，下個 session 的 phase-gated routing 會把它視為仍在 `backtest`
- 用戶無感知，只看到 agent「又在跑 backtest」

**斷點位置**：`backtest 執行完畢` → `STATUS.md phase = analysis`（這一步最容易被遺漏）

**建議**：`freqtrade-analysis-workflow` Phase 1 的最後一個步驟，加上強制 checklist：「必須更新 STATUS.md phase 到 analysis，否則不視為完成」。

---

### B3 — 高：Idea → Scope 入口沒有結構化觸發

- 用戶說「我有個新想法：RSI 背離進場」→ agent 不一定知道要走 `strategy-bootstrap` → `trade-strategy-scope` 鏈
- `trade-strategy.md` 有 Task → Skill Mapping，但沒有「模糊輸入的消歧義協議」
- **斷點**：用戶的自然語言 idea 和正式 scope 文件之間，沒有結構化的轉換流程

**建議**：在 `trade-strategy.md` 的 Quick Context 加一段「If user input is an unstructured idea, route to `strategy-bootstrap` first」的明確規則。

---

### B4 — 中：`experiment-compare` 和 `knowledge-extraction` 無自動觸發

- 每次 iteration 完成後，應該比較 anchor baseline 並提取 lesson
- 這兩個 skill 存在，但需要用戶主動知道並要求
- 如果用戶直接說「開始下一個 iteration」，這兩步就被跳過
- **累積效應**：hypothesis-log.md 沒有 KEEP/REVERT 記錄，anchor 永遠不更新，cross-strategy knowledge 沉沒

**建議**：在 `trade-strategy-improvement-planning` 的 Quick Reference 最前面加硬性 prerequisite：「Must run `experiment-compare` first. Must run `knowledge-extraction` if verdict is KEEP.」

---

### B5 — 中：Backtest preflight 分散在三個 skill，無 composite 入口

用戶說「跑 backtest」，agent 理論上要依序執行：
1. `data-readiness-check`
2. `look-ahead-bias-check`（新 implementation 後第一次）
3. 確認 `config.json` 完整性（有 trading_mode、fees 等）

但這三個 skill 是獨立的，沒有 composite skill 把它們串成 preflight checklist。Agent 可能記得其中兩個、忘記第三個。

**建議**：創建 `backtest-preflight` skill，內容就是三個 gate 的 checklist，在 `freqtrade-analysis-workflow` Phase 1 最前面強制引用。

---

### B6 — 低但重要：config.json placeholder 問題

`strategies/btc-momentum-pullback/engine/freqtrade/config.json` 目前是 placeholder，缺少 `trading_mode`、fees 等從 `freqtrade/configs/base.json` 繼承的參數。

`generate_freqtrade_config.py` 存在但 skill 沒有說明它何時被調用、輸出是否自動 merge base.json。如果用戶直接跑 backtest 而沒先生成 config，會得到 cryptic Freqtrade error，而不是清楚的「config 不完整」提示。

**建議**：`trade-strategy-freqtrade-implementation` 末尾加一步「Run `generate_freqtrade_config` to produce final config.json」。

---

## Part 2：AI Agent Skill 調用與效率優化

### S1 — `session-close` skill 缺失

目前沒有強制 session 結束流程。Agent 可能完成了工作但沒有：
- 更新 `_context_digest.md`
- 更新 `sessions/_latest.json` 指針
- 更新 STATUS.md phase

這是導致 B1、B2 問題的根本原因。

**建議**：創建 `session-close` skill，包含：
```
1. Update STATUS.md phase + last_updated + next_action
2. Write sessions/<date>-<type>.md
3. Update sessions/_latest.json pointer
4. Regenerate _context_digest.md (4 fields: phase, metrics, next_action, loaded_skill)
```
在 `strategy-cycle-orchestrator` 的步驟 4「update digest」處加強制引用。

---

### S2 — `trade-strategy-freqtrade-implementation` skill 沒有 Quick Reference

這是最 code-heavy 的 phase，但此 skill 沒有 Quick Reference section（高頻 skill 都應該有）。

Agent 每次都要讀完整 skill 才知道：strategy class 必要 methods、indicator 計算規範、informative pairs 的正確用法。

**建議**：加 Quick Reference，包含：
- Strategy class 必要 methods checklist（`populate_indicators`, `populate_entry_trend`, `populate_exit_trend`）
- 常見 look-ahead bias 陷阱的快速對照表（cross-reference `look-ahead-bias-check`）
- Config 生成指令

---

### S3 — `strategy-cycle-orchestrator` 和 `trade-strategy.md` Phase-Gated Table 形成雙重來源

兩個地方都定義「當前 phase → 應該做什麼」：
1. `trade-strategy.md` 的 Phase-Gated Skill Routing table
2. `strategy-cycle-orchestrator/SKILL.md` 的 4-step workflow

如果兩者對某 phase 的 valid skills 不一致，agent 無法判斷以哪個為準。

**建議**：`trade-strategy.md` 的 Phase-Gated table 加 note：「This table is a quick reference. For full orchestration logic, use `strategy-cycle-orchestrator`.」讓 `strategy-cycle-orchestrator` 成為唯一 source of truth。

---

### S4 — LLM Semantic Router 仍然 inactive

設計很好（TF-IDF + cosine），但 inactive 狀態意味著：
- 所有任務都送到同一個 model，包括 trivial tasks
- 複雜的多步推理和簡單的格式化任務消耗相同成本

**建議**：即使不啟用完整的 semantic router，至少在 `llm-orchestration` skill 加一個手動路由建議表：

| Task complexity | Model suggestion |
|---|---|
| Simple formatting / lookup | haiku-class |
| Code generation / analysis | sonnet-class |
| Architecture decision | opus-class / multi-agent-consensus |

---

### S5 — `analyze_backtest_result.py` 3050 行 monolith 阻礙 agent 精準修改

當 agent 需要修改分析邏輯的某一部分（如 regime diagnostic），要讀 3050 行才能找到目標。也讓 agent 更容易引入 side effects。

**建議**（技術債，不緊急但影響大）：按 multi-agent review 建議拆分為：
- `parse_result.py` — JSON 解析、trade normalization
- `diagnostics.py` — signal vs trade WR、regime analysis、slippage sensitivity
- `report_builder.py` — CSV export、metadata assembly
- `chart.py` — visualization

---

### S6 — `data-pipeline` skill 沒有 data freshness check

`data-readiness-check` 檢查 existence + truncation，但不檢查 **freshness**（cached features 是否已覆蓋最新請求的 timerange）。

如果用戶要 backtest 至最新日期，但 feature cache 已過期幾週，此問題不一定被 catch。

**建議**：在 `data-readiness-check` skill 加一個明確的 freshness check 步驟：「Verify feature end_date ≥ requested timerange end_date.」

---

## Part 3：Token 消耗優化

> 已有的機制（artifact triage、digest、quick reference、phase-gated routing）設計良好，以下是仍有空間的部分。

### T1 — `_context_digest.md` 應包含 `primary_skill` + `skill_section` hint

目前 digest 包含：phase、metrics、next_action、summary。

但沒有包含「上次用了哪個 skill 的哪個 section」。新 session 啟動時，agent 還是要去 `trade-strategy.md` 查 phase → skill mapping。

**優化**：digest 加兩個 fields：
```yaml
primary_skill: freqtrade-analysis-workflow
skill_section: "Phase 3 — Analyze Performance"
```

**節省**：每次 cold-start 省約 400–600 tokens（routing table + skill index 部分）。

---

### T2 — SKILL.md Quick Reference 應能獨立載入

Quick Reference 在 SKILL.md 最上方，但 agent 仍讀整個文件。

**優化**：把 Quick Reference 拆成獨立 `SKILL_QUICK.md`，完整版保留為 `SKILL.md`。artifact triage Level 2 只載入 `SKILL_QUICK.md`，Level 3 才載入 `SKILL.md`。

**節省**：高頻 skill 每次省約 60–70% 的 skill token。

---

### T3 — STATUS.md 的人工敘述應移到 sessions/

STATUS.md 目前：
```
YAML frontmatter (機器可讀, ~100 tokens)
+ 人工敘述區段 (agent 幾乎不需要, ~200-400 tokens)
```

Agent 每次讀 STATUS.md 都讀到不需要的人工敘述。

**優化**：STATUS.md 只保留 YAML frontmatter，人工敘述 migrate 到 `sessions/<date>-status-note.md`。

**節省**：每次 STATUS.md read 省 50–75%。

---

### T4 — `hypothesis-log.md` 應加 summary header

Improvement planning 要讀 hypothesis-log.md 做「prior art check」。隨著 iteration 增加，這個文件會越來越大。

**優化**：hypothesis-log.md 最上方維護 3–5 行的摘要 section：
```markdown
## Quick Summary (prior art index)
- Anchor: v3-ema-adx (OOS PF 1.42)
- Last tested: v5-volume-filter (REVERT, OOS PF 0.87)
- Open question: RSI threshold not yet tested
```

**節省**：planning phase 每次省 30–50% hypothesis-log token（隨 iteration 數增長效益越大）。

---

### T5 — 分析 summary 應有固定 schema，允許 section-level 載入

`sessions/<date>-analysis-summary.md` 目前是自由格式，agent 要讀完才知道關鍵結論。

**優化**：強制使用固定 section 結構：
```markdown
## KEY_METRICS (always load)
## FAILURE_MODE (load when planning)
## REGIME_ANALYSIS (load when regime filter work)
## FULL_DIAGNOSTICS (load only when debugging)
```

**節省**：planning session 只需讀 KEY_METRICS + FAILURE_MODE（約 30% of full analysis）。

---

### T6 — Cold-start chain 可透過 digest 短路

目前每個 session：CLAUDE.md → agent-general-skills.md → trade-strategy.md（約 1000 tokens）。

如果 `_context_digest.md` 包含 `primary_skill` hint（見 T1），這個鏈可以縮短為：
```
CLAUDE.md → _context_digest.md → SKILL_QUICK.md（直達）
```

**節省**：每個 session cold-start 省約 600–800 tokens。

---

## 優先順序建議

| 優先 | 項目 | 類型 | 影響 |
|------|------|------|------|
| P0 | B1 + S1：創建 `session-close` skill，強制更新 digest | 新 skill | 修復循環最脆弱點 |
| P0 | B2：`freqtrade-analysis-workflow` phase 轉換加強制 checklist | skill 修改 | 防止 phase stale |
| P1 | S5：拆分 `analyze_backtest_result.py` | code refactor | agent 精準修改能力 |
| P1 | T2：Quick Reference 拆成獨立 `SKILL_QUICK.md` | skill 結構重組 | 每次省 60–70% skill token |
| P1 | T1：digest 加 `primary_skill` + `skill_section` | artifact 格式改進 | 每次 cold-start 省 400–600 token |
| P2 | B5：創建 `backtest-preflight` composite skill | 新 skill | 減少 gate 遺漏 |
| P2 | T3：STATUS.md 純 YAML | artifact 格式改進 | 每次 STATUS read 省 50–75% |
| P2 | S4：LLM 路由手動建議表 | skill 修改 | 成本意識 |
| P3 | T4：hypothesis-log 加 summary header | artifact 格式改進 | 長期累積效益 |
| P3 | T5：analysis summary 固定 schema | 約定改進 | section-level 載入 |
| P3 | B4：experiment-compare + knowledge-extraction 加 prerequisite 強制提示 | skill 修改 | 防止 lesson 遺失 |

---

## 整體評估

框架設計成熟，skill taxonomy 覆蓋完整，quality gate 機制嚴謹。主要風險集中在**狀態持久化**（digest 和 phase transition 缺乏強制機制）和**token 效率**（large files 仍整體載入）。P0 兩個問題修復後，TAO 循環的穩定性會有顯著提升。
