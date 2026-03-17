# Web Strategy Conversational Control Plane Concept

Date: 2026-03-17

## Purpose

This note captures an early concept only.

It is not an implementation decision, schema contract, or required workflow change yet.

The intent is to preserve the design direction while the broader strategy workflow is still being revised.

## Problem Statement

If the future goal is to let a user interact through a web chat interface to:

- ask the current progress of a strategy
- manage strategy state and next actions
- trigger or approve execution steps
- inspect recent run history and results
- ask the system to recommend the next step

then the current file-only workflow will eventually become a limiting factor.

Markdown files and report artifacts are still valuable, but they are weak as the only source for:

- real-time status queries
- historical run lookup
- filtering and comparison
- chat-driven orchestration
- auditability of who triggered what and why

## Recommended Direction

Use a layered design rather than a pure "chatbot over the repo" design.

The recommended future shape is:

1. A web UI with a chat panel plus structured strategy views
2. A control-plane backend that owns state, execution requests, and history lookup
3. Controlled tools/actions that the conversational agent can call
4. Existing markdown and report files retained as human-readable artifacts
5. A database as the primary source for structured status and run history

In this model, chat is the interaction surface, not the system of record.

## Key Architectural Principle

Do not let the LLM infer the whole strategy state by repeatedly scanning markdown, folder names, and report directories.

Instead:

- store structured state in a queryable form
- expose a small set of controlled actions
- let the LLM translate user intent into those actions
- render the result back into chat and dashboard views

This reduces ambiguity and makes the system safer to operate.

## Why A Database Becomes Important

If the system needs to answer questions such as:

- "Which phase is strategy X currently in?"
- "What was the last successful backtest?"
- "Show the last 5 failed runs."
- "What changed between the latest two iterations?"
- "Who triggered this run?"
- "What should happen next?"

then file scanning will be increasingly fragile and slow.

A database should eventually hold at least:

- current structured strategy status
- execution run history
- run parameters
- summarized results
- artifact references
- failure information
- timestamps and trigger source

The detailed artifacts can still remain on disk.

Recommended principle:

- database stores indexes, summaries, and state
- filesystem stores detailed reports, exports, and human-readable narratives

## Suggested Future Data Model

This is intentionally minimal and provisional.

### `strategy_status`

Suggested fields:

- `strategy_id`
- `phase`
- `next_action`
- `latest_run_id`
- `latest_backtest_stem`
- `updated_at`

### `strategy_runs`

Suggested fields:

- `run_id`
- `strategy_id`
- `run_type`
- `status`
- `started_at`
- `finished_at`
- `triggered_by`
- `params_json`
- `result_summary_json`
- `artifact_path`
- `error_message`

The database does not need to replace report archives.
It only needs to make status and history queryable and reliable.

## How This Fits The Existing Repo

The current repository already has useful building blocks:

- Freqtrade execution entrypoints
- backtest analysis generation
- Telegram notification capability
- strategy status conventions
- report artifacts on disk

The future control plane should wrap these capabilities rather than replace them.

Likely future pattern:

1. User issues a request from the web UI
2. Chat orchestrator interprets intent
3. Backend calls a controlled tool/action
4. Execution result updates the database
5. Human-readable files and reports are updated as needed
6. UI and chat both read from the structured state/history layer

## Recommended Scope For A Future MVP

When the workflow stabilizes, a practical MVP could include:

1. strategy list view
2. single strategy detail page
3. interactive chat panel
4. query current strategy status
5. query recent run history
6. trigger backtest with confirmation
7. analyze latest backtest
8. write back a structured summary

This is enough to validate the control-plane model without overcommitting to full agent autonomy.

## What Not To Do

For the future implementation, avoid these patterns:

- using markdown as the only source of state
- deriving full history only from folder scanning
- allowing chat to execute arbitrary shell commands directly
- storing only the latest result and discarding failed run history
- mixing narrative notes and machine state into one unstructured blob

## Supplemental Findings — Added 2026-03-17

The following gaps were identified after initial review.

### Gap 1: Real-time run progress

Backtests can take several minutes. The UI should not poll for completion; it should receive streaming progress events. Recommended mechanism: WebSocket connection from the control-plane backend pushed to the chat panel and a progress indicator.

Without this, the user has no feedback during a long run and the chat panel appears frozen.

### Gap 2: Authentication and operation scope

The spec assumes a single-user setup, but even single-user deployments need a session boundary to prevent unauthorized execution. Recommended minimum: bearer token or session cookie on all API calls. Define explicitly whether remote access (not just localhost) is in scope for the MVP.

### Gap 3: Artifact viewer (HTML report inline)

The analysis pipeline already generates `trade_points_chart.html`, `summary.json`, and `trades.csv` under `freqtrade/reports/<stem>/`. The MVP should render the HTML report inline in the web UI, not just show a file path. Without this, the user still needs a terminal to view results, defeating the purpose of the web layer.

### Gap 4: Strategy comparison view

The spec focuses on single-strategy detail. Comparing two runs side-by-side (baseline vs candidate) is a core workflow (`experiment-compare` skill). The data model already has `strategy_runs`; the UI needs a comparison panel that shows two `result_summary_json` objects in parallel columns.

### Gap 5: Hypothesis timeline

The `hypothesis-log.md` already records every version with KEEP/REVERT/PENDING verdicts. The web UI should render this as a visual timeline (version list with verdict badges), not require the user to read the markdown file.

Data model implication: add `hypothesis_versions` table or extend `strategy_status` with a `hypothesis_log` JSON field.

### Gap 6: Notification channel configuration

The repo has a Telegram notification service (`telegram_svc.py`). The web UI should expose notification preference management (enable/disable, channel selection) rather than requiring environment variable edits.

### Gap 7: CLI parity contract

All actions available in the web UI must remain executable from the CLI with identical behavior. The control-plane backend should call the same Python endpoints (`lib/endpoints/`) as the CLI does. This prevents the web layer from drifting into a parallel implementation.

Enforcement rule: no business logic in the web backend itself. The web layer is a translation surface, not an execution engine.

### Gap 8: Approval tiers for destructive actions

Not all actions carry the same risk. Suggest three tiers:

| Tier | Examples | UI behavior |
|------|---------|-------------|
| Safe | View status, view history, view reports | No confirmation |
| Reversible | Trigger backtest, trigger analysis | Single-click with brief confirmation |
| Irreversible | Phase transition to deployment, live trading toggle | Two-step confirmation with explicit acknowledgement |

The chat agent should enforce these tiers programmatically via the action definitions, not rely on prompt engineering alone.

---

## Current Decision Status

Nothing in this note should be treated as approved implementation work yet.

This is a concept placeholder for future design discussion after the strategy workflow itself is settled.

## Revisit Trigger

Revisit this concept when at least one of the following becomes true:

- the strategy workflow and phase transitions are stabilized
- there is more than one active strategy family
- users need a web dashboard for progress visibility
- users need interactive chat-based run management
- execution history becomes too cumbersome to reconstruct from files alone

## Bottom Line

If the long-term goal is a web-based conversational interface for asking, managing, and advancing strategy work, then adding structured execution history and strategy state to a database is the right direction.

The database should complement existing markdown and report artifacts, not replace them.

The chat layer should sit on top of a controlled control plane, not on top of raw repository inference.
