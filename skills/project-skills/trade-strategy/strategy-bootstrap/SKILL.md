---
name: strategy-bootstrap
description: Initialize a new strategy family workspace from a raw trading idea. Use when starting a brand-new strategy from scratch — creates the full folder structure, prefills spec sections, and sets initial STATUS.md. Use instead of manually copying the _template folder.
---

# Strategy Bootstrap Skill

Turns a raw trading idea into a complete, ready-to-develop strategy workspace in one session.

## Quick Reference

| Step | Action |
|------|--------|
| 1. Gather scope | Ask user for: market, pair, timeframe, long/short, success criteria |
| 2. Confirm slug | Agree on `strategy_family` slug (e.g. `btc-breakout`) |
| 3. Create workspace | Copy `strategies/_template/` → `strategies/<slug>/` |
| 4. Fill README.md | Complete all sections using user input + hypothesis-baseline skill |
| 5. Fill STATUS.md | Set frontmatter phase to `implementation`, fill next_action |
| 6. Initialize hypothesis-log | Write v1 entry with PENDING verdict |
| 7. Validate scope gates | Confirm all `trade-strategy-scope` requirements are met |

---

## Workflow

### Step 1 — Intake

Ask the user (or infer from their description) the following scope items. Do not proceed until all are defined:

- Symbol (e.g. BTC/USDT:USDT)
- Market type (Futures / Spot)
- Timeframe (e.g. 1h)
- Direction (Long / Short / Both)
- Target Profit Factor minimum
- Maximum Allowable Drawdown
- Rejection criteria (e.g. "If OOS Sharpe < 1.0, reject")
- What the strategy should NOT do

### Step 2 — Confirm family slug

Generate a suggestion: `<symbol>-<direction>-<style>`, e.g. `btc-short-ma`, `eth-mean-reversion`.
Confirm with the user before creating files.

### Step 3 — Create workspace

Copy from template:
```
strategies/_template/  →  strategies/<slug>/
```

Files to create:
- `strategies/<slug>/README.md`
- `strategies/<slug>/STATUS.md`
- `strategies/<slug>/hypothesis-log.md`
- `strategies/<slug>/sessions/_latest.json`
- `strategies/<slug>/engine/freqtrade/config.json` (placeholder — generate later)
- `strategies/<slug>/experiments/.gitkeep`
- `strategies/<slug>/reports/.gitkeep`

### Step 4 — Fill README.md

Complete every section of README.md using the intake answers:
- Section 0: Summary (one-line description + current status = 草稿)
- Section 1: Scope (market, pair, venue, timeframe, direction, success criteria)
- Section 2: Hypothesis (core alpha logic + why the edge exists + baseline + failure risks)
- Section 3: Strategy Spec (entry, exit, stoploss, regime filters, position sizing, indicators)
- Section 4: Implementation Notes (strategy class name, config path, implementation risks)
- Section 5: Open Questions (top uncertainties + what agent should validate first)

### Step 5 — Fill STATUS.md

Update the YAML frontmatter:
```yaml
phase: implementation
next_action: "Generate config and implement strategy"
last_updated: <today>
```

### Step 6 — Initialize hypothesis-log.md

Write v1 entry with the initial hypothesis and PENDING verdict.

### Step 7 — Validate scope gates

Confirm before handing off to implementation:
- [ ] Success criteria include Profit Factor target AND max drawdown
- [ ] Rejection criteria are defined
- [ ] Fee and slippage assumptions are specified (default: 0.04% fee, 0.1% slippage for Binance Futures)
- [ ] At least one baseline comparison is defined

---

## Handoff

After bootstrap completes, tell the user:
- Workspace location: `strategies/<slug>/`
- Next step: load `trade-strategy-freqtrade-implementation` skill to implement the strategy
- Config generation command: `python -m lib.endpoints.generate_freqtrade_config <slug> <StrategyName> <pair>`
