# TAO 循環優化 - 最終實施計劃

**Date**: 2026-03-18
**Multi-Agent Review**: OpenCode (初稿) → Gemini + Codex (review) → Claude (synthesis + 實施)
**Scope**: P0 & P1 Priority Items
**Based on**: `knowledge-base/reviews/20260317-tao-cycle-optimization-review.md`

---

## Multi-Agent Consensus 摘要

### Gemini 主要意見
- P0 優先序正確
- 強制 checklist 需要 "N/A with justification" 逃生閥，避免非標準場景下 agent 卡死
- B3、B5、B6 應明確標記為 P2 Roadmap
- monolith 拆分需要 regression check 步驟

### Codex 主要意見（高優先採納）
- **重要**: `session-close` 作為 skill 仍是 markdown 指令，沒有真正的強制執行機制。這是已知限制；在沒有 CLI hook 的情況下，明確的 skill 引用仍比現狀好。
- **修正**: 不在 `_latest.json` 新增 `last_session` 欄位——會破壞現有 schema。只更新現有欄位（`analysis_summary`, `iteration_plan`, `last_updated`）。
- **修正**: `analyze_backtest_result.py` 拆分不用 `__init__.py` wrapper——保持 `analyze_backtest_result.py` 為 thin orchestrator，提取 helpers 到旁邊的模組。
- **修正**: P1-2 (SKILL_QUICK.md) 必須同時更新 `agent-general-skills.md`，否則 token 節省效益不會實現。

### Claude 決策
採納 Codex 所有修正意見。Gemini N/A 逃生閥已加入所有 checklist。P2 roadmap 明確列出。

---

## 實施狀態（2026-03-18 已完成）

### P0 已完成

| Item | 修改的文件 | 狀態 |
|------|-----------|------|
| P0-1: 創建 session-close skill | `knowledge-base/skills/project-skills/trade-strategy/session-close/SKILL.md` (新建) | ✅ |
| P0-1: Orchestrator 引用 session-close | `strategy-cycle-orchestrator/SKILL.md` Step 4 改為強制引用 | ✅ |
| P0-2: Backtest→Analysis gate | `freqtrade-analysis-workflow/SKILL.md` Phase 1 末尾加 PHASE TRANSITION GATE | ✅ |
| P0-2: Analysis→Planning gate | `freqtrade-analysis-workflow/SKILL.md` Phase 3 末尾加 PHASE TRANSITION GATE | ✅ |
| P0-2: Improvement-planning prerequisites | `trade-strategy-improvement-planning/SKILL.md` 頂部加 MANDATORY PREREQUISITES | ✅ |

### P1 已完成

| Item | 修改的文件 | 狀態 |
|------|-----------|------|
| P1-1 (T1): Digest 加 primary_skill + skill_section | `strategy-cycle-orchestrator/SKILL.md` Step 4 digest 模板更新 | ✅ |
| P1-2 (T2): SKILL_QUICK.md — freqtrade-analysis-workflow | `freqtrade-analysis-workflow/SKILL_QUICK.md` (新建) | ✅ |
| P1-2 (T2): SKILL_QUICK.md — strategy-cycle-orchestrator | `strategy-cycle-orchestrator/SKILL_QUICK.md` (新建) | ✅ |
| P1-2 (T2): SKILL_QUICK.md — freqtrade-implementation | `trade-strategy-freqtrade-implementation/SKILL_QUICK.md` (新建) | ✅ |
| P1-2 (T2): agent-general-skills.md 更新 | Context Loading Protocol 加入 SKILL_QUICK.md 說明 | ✅ |
| P1-2 (T2): artifact-triage 更新 | Level 2 改為優先載入 SKILL_QUICK.md | ✅ |
| P1-3 (S5): analyze_backtest_result.py 拆分計劃 | 技術債記錄（見下方，不修改代碼） | ✅ |

### 額外已完成（Review 其他項目）

| Item | 修改的文件 | 狀態 |
|------|-----------|------|
| S2: freqtrade-implementation 加 Quick Reference | `trade-strategy-freqtrade-implementation/SKILL.md` 加 Quick Reference section | ✅ |
| S3: trade-strategy.md 加 orchestrator 為 SOT note | `trade-strategy.md` Phase-Gated table 前加 note | ✅ |
| S4: LLM 路由手動建議表 | `llm-orchestration/SKILL.md` 加 Task Complexity table | ✅ |
| S6: data-readiness-check 加 freshness check | `data-readiness-check/SKILL.md` 加 Step 3a freshness check | ✅ |
| B3: 非結構化 idea routing | `trade-strategy.md` 加 Unstructured Idea Routing section | ✅ |
| trade-strategy.md: session-close 加入 Skill Index | `trade-strategy.md` Task→Skill Mapping + Skill Index | ✅ |

---

## P2 Roadmap（本次不實施）

| Item | 原始編號 | 說明 |
|------|---------|------|
| backtest-preflight composite skill | B5 | 整合 data-readiness-check + look-ahead-bias-check + config check 為一個入口 |
| config.json placeholder 問題 | B6 | freqtrade-implementation 末尾加「Run generate_freqtrade_config」步驟 |
| STATUS.md 純 YAML | T3 | 人工敘述 migrate 到 sessions/，每次讀 STATUS.md 省 50-75% |
| hypothesis-log summary header | T4 | 頂部加 3-5 行 quick summary index |
| analysis summary 固定 schema | T5 | KEY_METRICS / FAILURE_MODE / REGIME_ANALYSIS / FULL_DIAGNOSTICS 分層載入 |
| session-close CLI 強制執行 | — | Codex 指出 markdown skill 無真正強制力；未來可實作 `python -m lib.endpoints.session_close <family>` |
| analyze_backtest_result.py 實際拆分 | S5 | P1-3 已記錄計劃；實際代碼拆分需另開任務，保留 analyze_backtest_result.py 為 thin orchestrator |

---

## 技術債記錄：analyze_backtest_result.py 拆分計劃

**目標結構**（Codex 修正版 — 保留 CLI 入口）:

```
lib/strategy/analytics/
├── analyze_backtest_result.py   # 保留為 thin orchestrator + CLI 入口 (python -m ...)
├── parse_result.py              # JSON 解析、trade normalization
├── diagnostics.py              # Signal WR vs Trade WR、regime analysis、slippage sensitivity
├── report_builder.py            # CSV export、metadata assembly
└── chart.py                     # Visualization
```

**重要**: 不使用 `__init__.py` wrapper。保持 `analyze_backtest_result.py` 為公開 CLI 入口，內部 import 各子模組。此方式保持 `python -m lib.strategy.analytics.analyze_backtest_result` 路徑不變。

**實施前提**: 需要 regression check——對比拆分前後分析輸出完全一致。

---

## 驗收標準

| Item | Success Criteria |
|------|-----------------|
| P0-1 session-close | Skill 存在；orchestrator Step 4 明確引用；digest 模板含 primary_skill + skill_section |
| P0-2 phase gates | freqtrade-analysis-workflow Phase 1 + Phase 3 末尾各有 checklist；improvement-planning 頂部有 prerequisites |
| P1-1 digest format | orchestrator Step 4 digest 模板含 6 fields |
| P1-2 SKILL_QUICK.md | 3 個高頻 skill 各有 SKILL_QUICK.md；agent-general-skills.md + artifact-triage 已更新 |
| B3 idea routing | trade-strategy.md 有 Unstructured Idea Routing section |

---

*End of Plan — Status: IMPLEMENTED 2026-03-18*
