---
name: strategy-workflow
description: Organize strategy-family workspaces, markdown artifacts, reviews, reports, sessions, and experiment records in this repository. Use when creating or updating files under `strategies/<strategy_family>/`. This is the single source of truth for record placement rules.
---

# Strategy Workflow Skill

Each strategy family has its own workspace under `strategies/<strategy_family>/`.

## Folder Purpose Reference

| Folder | What goes here |
|--------|---------------|
| `sessions/` | Agent-user conversation summaries, decision context, background discussions. User-managed. Not a formal record — more like a scratchpad capturing *why* a decision was made. |
| `experiments/` | Reproducible experiment comparisons: a specific change vs baseline, with concrete metrics and a KEEP/REVERT conclusion. Must have data to support the conclusion. |
| `reports/` | Formal backtest summaries: a completed run with key metrics, OOS check, verdict, and next actions. Written after a run is concluded, not during. |
| `reviews/` | Risk logs, spec review notes, and decision records. Written when validating or auditing strategy logic. |
| `artifacts/` | Strategy-local generated outputs (e.g. strategy-specific charts). Do not use for markdown records. |

**Key distinction — sessions vs experiments:**
- `sessions/` = *why* a decision was made (context, discussion, reasoning)
- `experiments/` = *what* was tested and *what the data showed* (reproducible, has numbers)

## Single-File-First Rule

Strategy work starts as a single `strategies/<strategy_family>/README.md` that combines scope, hypothesis, spec, and implementation notes.

**Do not split this file unless the user explicitly asks.** A single file gives agents full context in one read and avoids agents reading only part of the spec.

If the user requests a split, use: `scope.md`, `hypothesis.md`, `spec.md`, `implementation.md`. Preserve the README.md until the user confirms the split is complete.

## Record Placement Rules (Single Source of Truth)

- Handwritten formal backtest reports → `strategies/<family>/reports/`
- Experiment comparisons with data → `strategies/<family>/experiments/`
- Validation, testing, troubleshooting notes → `strategies/<family>/experiments/` (promote to `reports/` only when formally concluded)
- Risk and spec review notes → `strategies/<family>/reviews/`
- Conversation and decision context → `strategies/<family>/sessions/`
- Raw engine-generated output (HTML, JSON, ZIP) → `freqtrade/reports/` or `freqtrade/user_data/` — **never** in `strategies/`
- Cross-strategy lessons → `knowledge-base/knowledge/backtest-records/`

Do not place records in the repo root, `lib/`, `freqtrade/strategies/`, or any path outside `strategies/<family>/`.

## What NOT to Do

- Do not create extra review or session files unless the user explicitly requests one.
- Do not mix engine-generated outputs with hand-written summaries in the same folder.
- Do not split README.md automatically when strategy content grows — wait for the user's instruction.
