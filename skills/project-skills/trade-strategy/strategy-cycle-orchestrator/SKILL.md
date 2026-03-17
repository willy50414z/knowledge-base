---
name: strategy-cycle-orchestrator
description: Determine the current state of a strategy family and emit the next concrete action. Use when the user's request is ambiguous, when resuming work after a break, or when unsure which skill to load next.
---

# Strategy Cycle Orchestrator Skill

Reads current state and emits one concrete next action without requiring the user to specify phase manually.

## Quick Reference

1. Read `strategies/<family>/_context_digest.md` if it exists → skip to Step 4
2. If no digest: read `strategies/<family>/STATUS.md` YAML frontmatter
3. Validate phase gate for the current phase (see gate table below)
4. Emit next action and load the appropriate skill

---

## Workflow

### Step 1 — Load state

Priority order (stop as soon as you have enough):

```
1. strategies/<family>/_context_digest.md   → compact resume artifact
2. strategies/<family>/STATUS.md frontmatter → phase + last stem + next_action
3. strategies/<family>/sessions/_latest.json → analysis_summary / iteration_plan filenames
```

Do not read README.md unless the task requires spec-level context.

### Step 2 — Validate phase gate

| Phase | Gate check |
|-------|-----------|
| `implementation` | Does `freqtrade/strategies/<StrategyName>.py` exist with no TODO markers? |
| `backtest` | Is data READY? (`check_data_readiness`) Is config.json generated? |
| `analysis` | Does `freqtrade/user_data/backtest_results/<stem>.json` exist? |
| `planning` | Does `sessions/<date>-analysis-summary.md` exist? Is `_latest.json` current? |

If any gate fails, report the specific blocker. Do not proceed past a failed gate.

### Step 3 — Emit next action

Based on phase and gate status, emit ONE specific next action in this format:

```
Phase: <current phase>
Gate status: PASS | BLOCKED (<reason>)
Next action: <exact command or step>
Skill to load: <skill name>
```

Examples:

```
Phase: backtest
Gate status: BLOCKED (data missing for BTCUSDT 1h 20250101-20260101)
Next action: python -m lib.endpoints.check_data_readiness BTCUSDT 1h 20250101-20260101
Skill to load: data-readiness-check
```

```
Phase: analysis
Gate status: PASS
Next action: python -m lib.strategy.analytics.analyze_backtest_result
Skill to load: freqtrade-analysis-workflow (Phase 3)
```

### Step 4 — Update context digest

After completing the action, update `strategies/<family>/_context_digest.md`:

```markdown
# Context Digest — <strategy_family>

Last updated: <YYYY-MM-DD>

## Strategy Summary
<2-3 sentences from README.md — what the strategy does and its core hypothesis>

## Current State
- Phase: <phase>
- Last backtest stem: <stem or "none yet">
- Last metrics: PF <x.xx> | DD <xx%> | WR <xx%> | Sharpe <x.xx>
- Blocking issues: <none | description>

## Next Action
<one sentence>

## Active Skill
<skill name valid for current phase>
```

---

## When to Use This Skill vs Others

- Use `strategy-cycle-orchestrator` when: user says "what should we do next", "resume work", "where are we", or the request is phase-ambiguous.
- Do not use this skill when: the user gives a specific action ("run the backtest", "write the analysis summary") — route directly to the relevant skill.
