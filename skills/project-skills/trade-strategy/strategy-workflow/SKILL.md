---
name: strategy-workflow
description: Organize strategy-family workspaces, markdown artifacts, reviews, reports, and session records in this repository. Use when creating or updating files under `strategies/<strategy_family>/`.
---

# Strategy Workflow Skill

Each strategy family should have its own workspace under `strategies/<strategy_family>/`.

## Folder Structure

- User-managed discussion summaries should live under that strategy folder's `sessions/`.
- Reviews should live under that strategy folder's `reviews/`.
- Backtest summaries and performance write-ups should live under that strategy folder's `reports/`.
- Experiment and tuning notes should live under that strategy folder's `experiments/`.
- Generated artifacts may live under that strategy folder's `artifacts/` only when strategy-local storage is useful.
- Do not create extra review or session markdown files unless the user explicitly asks for one.
