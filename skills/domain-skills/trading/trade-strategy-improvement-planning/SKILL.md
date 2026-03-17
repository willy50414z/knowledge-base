---
name: trade-strategy-improvement-planning
description: Build the next strategy iteration plan from observed weaknesses, failure modes, and audit results. Use when deciding how to improve a strategy after backtest review, report analysis, or failed validation.
---

# Trade Strategy Improvement Planning Skill

Refine trading strategies based on historical audit results.

## Input

Read in this order before planning:
1. `strategies/<family>/STATUS.md` — current phase, last backtest context
2. `strategies/<family>/sessions/<latest>-analysis-summary.md` — top failure modes and recommended focus
3. `strategies/<family>/README.md` — current hypothesis and spec (update this if the hypothesis changes)

Do not re-read the full analysis zip or HTML report unless the summary is missing.

## Required Work

- Identify the specific regime (e.g., Sideways, High Vol) where the strategy underperforms.
- Formulate a new hypothesis that addresses the identified failure mode.
- Update `strategies/<family>/README.md` directly if the hypothesis or spec changes — README.md is the single spec file.
- Write the iteration plan (see template below) before starting re-implementation.

## General Decision Rules

- Do not propose changes that are not linked to a specific observed weakness or failure mode.
- Do not batch unrelated improvements into one iteration — attribution becomes unclear.
- Do not re-implement before the revised hypothesis and iteration plan are written.
- Prefer one focused change per iteration. If the plan has more than two `Change` items, split into separate iterations.

## Iteration Plan Template

Write to: `strategies/<family>/sessions/<YYYYMMDD>-iteration-plan.md`

```markdown
# Iteration Plan — <YYYY-MM-DD>

## Source
- Based on: strategies/<family>/sessions/<date>-analysis-summary.md

## Observed Weakness
<具體 regime 或 metric，例：Sideways market 造成 -12% profit drag>

## Root Cause Hypothesis
<為什麼這個 weakness 存在，對應 README.md 的哪個假設>

## Change
<改什麼，要具體到 indicator / parameter / logic>

## Unchanged
<明確列出不改的部分，避免 agent 自行擴題>

## Expected Metric Shift
- Profit Factor: X.X → X.X
- Max Drawdown: XX% → XX%

## Experiment Type
<!-- parameter tweak | logic change | filter addition | regime filter -->

## Test Plan
- IS timerange: <YYYYMMDD-YYYYMMDD>
- OOS timerange: <YYYYMMDD-YYYYMMDD>
```

After writing the plan, update `STATUS.md`: phase → `implementation`.
