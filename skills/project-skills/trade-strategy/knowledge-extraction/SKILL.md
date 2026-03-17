---
name: knowledge-extraction
description: Distill cross-strategy lessons from a completed iteration into the shared knowledge base. Use after writing an analysis summary or experiment comparison when the finding has applicability beyond the current strategy family.
---

# Knowledge Extraction Skill

Prevents hard-won strategy lessons from staying siloed in one strategy's sessions/ folder.

## When to Trigger

Trigger this skill after completing:
- An analysis summary that identifies a regime-specific behavior pattern
- An experiment comparison with a KEEP or REVERT verdict
- A failed hypothesis that reveals a structural market limitation

Do NOT trigger for:
- Parameter tuning results that are strategy-specific
- Bug fixes or implementation corrections
- Minor OOS validation notes

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Read the analysis summary or experiment record |
| 2 | Ask: is this finding applicable to other strategy families? |
| 3 | If yes: write to `knowledge-base/knowledge/backtest-records/` |
| 4 | If no: skip — no cross-strategy value |

---

## Workflow

### Step 1 — Read the source record

Read one of:
- `strategies/<family>/sessions/<date>-analysis-summary.md`
- `strategies/<family>/experiments/<date>-compare-<topic>.md`

### Step 2 — Assess cross-strategy applicability

Ask these questions:
1. Does this finding describe a **market structure** pattern (e.g., BTC behavior in low-volatility regimes)?
2. Does this finding reveal a **common indicator limitation** (e.g., RSI false signals in trending markets)?
3. Does this finding establish a **cost/fee sensitivity threshold** applicable to similar strategies?
4. Does this finding reveal a **data or implementation pitfall** that any Freqtrade strategy could encounter?

If the answer to any question is yes → proceed to Step 3.
If all answers are no → stop. No cross-strategy value.

### Step 3 — Write extraction record

Write to: `knowledge-base/knowledge/backtest-records/<YYYYMMDD>-<topic>.md`

```markdown
---
source_family: <strategy_family>
source_date: <YYYY-MM-DD>
applicability: <general | crypto-futures | btc-specific | trend-following | mean-reversion>
---

# <Topic> — <YYYY-MM-DD>

## Finding
<One paragraph: what was observed, in what conditions, with what evidence>

## Cross-Strategy Implication
<One or two sentences: what this means for strategies beyond <family>>

## Do / Avoid
- Do: <positive guidance>
- Avoid: <what not to do based on this finding>

## Source
- Strategy: strategies/<family>/
- Record: strategies/<family>/sessions or experiments/<filename>
```

### Step 4 — Update the backtest records index (if it exists)

If `knowledge-base/knowledge/backtest-records/index.md` exists, add a one-line entry:
`- [<YYYY-MM-DD> <topic>](<filename>) — <one-line summary>`
