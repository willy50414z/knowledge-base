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

The detailed artifacts should not stay only on local disk if the system is expected to run in the cloud.

Recommended principle:

- PostgreSQL stores structured state, indexes, run metadata, launch-gate decisions, and query-friendly summaries
- MinIO stores large immutable artifacts produced by Freqtrade and downstream analysis
- markdown files remain human-readable repo artifacts when needed, but are not the runtime system of record

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

## Recommended Storage Split For Cloud Deployment

For this repo, a practical split is:

### PostgreSQL should store

- strategy status and current phase
- run history and run lifecycle state
- trigger source, user, and agent session identity
- run parameters and config snapshot metadata
- strategy code hash / git commit / version tag
- IS and OOS metric summaries
- launch-gate evaluation output
- regime breakdown summaries
- error summaries and retryability flags
- references to all stored artifacts

### MinIO should store

- raw Freqtrade backtest result JSON
- exported trades CSV / JSON
- `summary.json`
- `trade_points_chart.html`
- generated plots and report bundles
- agent-produced markdown reports such as analysis summaries when they are treated as run artifacts
- any large per-trade, per-candle, or equity-curve exports

### Why this split fits the repo

Some of the most useful data already exists in Freqtrade outputs. That data does not need to be duplicated field-for-field into PostgreSQL if:

- the raw artifact is stored durably in MinIO
- PostgreSQL stores the artifact key and the subset of fields needed for filtering, comparison, launch gating, and chat answers

This keeps the control plane queryable without turning PostgreSQL into a blob store.

## Suggested Structured Tables Beyond The Minimal Model

If this concept moves toward implementation, the minimal model above will likely need to expand into a few clearer logical records.

### `backtest_runs`

Purpose: one row per execution attempt.

Suggested fields:

- `run_id`
- `strategy_id`
- `run_type` (`IS`, `OOS`, `WF`, `hyperopt`)
- `status` (`queued`, `running`, `completed`, `failed`)
- `triggered_by`
- `trigger_source` (`web`, `agent`, `manual`, `schedule`)
- `started_at`
- `finished_at`
- `agent_session_id`
- `git_commit`
- `request_json`
- `error_message`

### `run_snapshots`

Purpose: preserve reproducibility without forcing the DB to hold full large artifacts.

Suggested fields:

- `run_id`
- `strategy_class`
- `strategy_version`
- `strategy_code_hash`
- `config_hash`
- `params_json`
- `exchange`
- `market_type`
- `timeframe`
- `informative_timeframes_json`
- `pairlist_json`
- `timerange_start`
- `timerange_end`
- `data_snapshot_json`

### `run_metrics`

Purpose: flattened query layer for the values the UI and agent ask for most often.

Suggested fields:

- `run_id`
- `is_trade_count`
- `oos_trade_count`
- `is_profit_factor`
- `oos_profit_factor`
- `sharpe`
- `sortino`
- `calmar`
- `max_drawdown_pct`
- `max_drawdown_duration_days`
- `win_rate`
- `pl_ratio`
- `recovery_factor`
- `expectancy`
- `trades_per_day`
- `avg_trade_duration`
- `final_balance`

### `run_evaluations`

Purpose: store the launch-gate output so the agent does not need to recompute it from markdown.

Suggested fields:

- `run_id`
- `strategy_profile` (`A`, `B`, `C`)
- `tier_verdict` (`REJECT`, `BORDERLINE`, `PROMISING`)
- `launch_verdict` (`BLOCK`, `CONDITIONAL`, `GO_LIVE_READY`)
- `decision` (`REVERT`, `NEED_MORE_DATA`, `KEEP`)
- `pf_degradation_ratio`
- `confidence_adjusted_pf_json`
- `trigger_codes_json`
- `regime_breakdown_json`
- `scorecard_json`
- `llm_summary`

### `run_artifacts`

Purpose: map each run to durable MinIO objects.

Suggested fields:

- `artifact_id`
- `run_id`
- `artifact_type`
- `storage_backend` (`minio`)
- `bucket`
- `object_key`
- `content_type`
- `size_bytes`
- `checksum`
- `created_at`

This lets the UI fetch or render the artifact without making local filesystem assumptions.

## Draft PostgreSQL Schema Direction

This section is still conceptual, but concrete enough to guide an eventual MVP implementation.

### Design goals

- keep query paths simple for chat and dashboard use cases
- preserve reproducibility for every run
- avoid storing large blobs in PostgreSQL
- support both human-triggered and agent-triggered execution

### Suggested relational shape

#### `strategy_status`

One row per active strategy family.

Suggested columns:

- `strategy_id` `text primary key`
- `phase` `text not null`
- `next_action` `text`
- `latest_run_id` `uuid`
- `latest_backtest_stem` `text`
- `latest_analysis_artifact_id` `uuid`
- `updated_at` `timestamptz not null`

Suggested indexes:

- `(phase)`
- `(updated_at desc)`

#### `backtest_runs`

One row per execution attempt.

Suggested columns:

- `run_id` `uuid primary key`
- `strategy_id` `text not null`
- `run_type` `text not null`
- `status` `text not null`
- `triggered_by` `text`
- `trigger_source` `text not null`
- `agent_session_id` `text`
- `git_commit` `text`
- `engine_version` `text`
- `started_at` `timestamptz not null`
- `finished_at` `timestamptz`
- `request_json` `jsonb not null default '{}'::jsonb`
- `error_message` `text`

Suggested constraints:

- `run_type in ('IS','OOS','WF','hyperopt','analysis')`
- `status in ('queued','running','completed','failed','cancelled')`
- `trigger_source in ('web','agent','manual','schedule')`

Suggested indexes:

- `(strategy_id, started_at desc)`
- `(status, started_at desc)`
- `(trigger_source, started_at desc)`

#### `run_snapshots`

One row per run. Used for reproducibility.

Suggested columns:

- `run_id` `uuid primary key references backtest_runs(run_id)`
- `strategy_class` `text not null`
- `strategy_version` `text`
- `strategy_code_hash` `text not null`
- `config_hash` `text not null`
- `params_json` `jsonb not null default '{}'::jsonb`
- `exchange` `text not null`
- `market_type` `text not null`
- `timeframe` `text not null`
- `informative_timeframes_json` `jsonb not null default '[]'::jsonb`
- `pairlist_json` `jsonb not null default '[]'::jsonb`
- `timerange_start` `timestamptz not null`
- `timerange_end` `timestamptz not null`
- `data_snapshot_json` `jsonb not null default '{}'::jsonb`

Suggested indexes:

- `(exchange, market_type, timeframe)`

#### `run_metrics`

Flattened summary metrics used by the UI, launch gate, and agent responses.

Suggested columns:

- `run_id` `uuid primary key references backtest_runs(run_id)`
- `is_trade_count` `integer`
- `oos_trade_count` `integer`
- `is_profit_factor` `numeric(10,4)`
- `oos_profit_factor` `numeric(10,4)`
- `sharpe` `numeric(10,4)`
- `sortino` `numeric(10,4)`
- `calmar` `numeric(10,4)`
- `max_drawdown_pct` `numeric(10,4)`
- `max_drawdown_duration_days` `integer`
- `win_rate` `numeric(10,4)`
- `pl_ratio` `numeric(10,4)`
- `recovery_factor` `numeric(10,4)`
- `expectancy` `numeric(10,4)`
- `trades_per_day` `numeric(10,4)`
- `avg_trade_duration_minutes` `integer`
- `final_balance` `numeric(18,8)`
- `result_summary_json` `jsonb not null default '{}'::jsonb`

Suggested indexes:

- `(oos_profit_factor desc)`
- `(max_drawdown_pct asc)`
- `(sharpe desc)`

#### `run_evaluations`

Stores the structured launch-gate result.

Suggested columns:

- `run_id` `uuid primary key references backtest_runs(run_id)`
- `strategy_profile` `text`
- `tier_verdict` `text not null`
- `launch_verdict` `text not null`
- `decision` `text not null`
- `pf_degradation_ratio` `numeric(10,4)`
- `confidence_adjusted_pf_json` `jsonb not null default '{}'::jsonb`
- `trigger_codes_json` `jsonb not null default '[]'::jsonb`
- `regime_breakdown_json` `jsonb not null default '{}'::jsonb`
- `scorecard_json` `jsonb not null default '{}'::jsonb`
- `llm_summary` `text`
- `evaluated_at` `timestamptz not null`

Suggested constraints:

- `strategy_profile in ('A','B','C')`
- `tier_verdict in ('REJECT','BORDERLINE','PROMISING')`
- `launch_verdict in ('BLOCK','CONDITIONAL','GO_LIVE_READY')`
- `decision in ('REVERT','NEED_MORE_DATA','KEEP')`

Suggested indexes:

- `(tier_verdict, evaluated_at desc)`
- `(launch_verdict, evaluated_at desc)`

#### `run_artifacts`

References durable MinIO objects.

Suggested columns:

- `artifact_id` `uuid primary key`
- `run_id` `uuid not null references backtest_runs(run_id)`
- `artifact_type` `text not null`
- `storage_backend` `text not null default 'minio'`
- `bucket` `text not null`
- `object_key` `text not null`
- `content_type` `text`
- `size_bytes` `bigint`
- `checksum` `text`
- `created_at` `timestamptz not null`

Suggested constraints:

- `artifact_type in ('freqtrade_result_json','summary_json','trades_csv','trade_points_chart_html','analysis_summary_md','equity_curve_json','log_bundle')`

Suggested indexes:

- `(run_id, artifact_type)`
- `(bucket, object_key)`

### Minimum MVP query paths

The schema should support these queries efficiently:

- latest run per strategy
- last successful backtest per strategy
- runs that failed launch gate
- compare two runs by `run_id`
- fetch all artifacts for a run
- answer "what happened last?" without reading markdown

## Draft MinIO Bucket And Object Key Convention

To avoid ad hoc artifact naming, use a stable path convention from the start.

### Suggested bucket split

- `trade-strategy-runs`
- `trade-strategy-reports`
- `trade-strategy-logs`

If simplicity is more important than separation in MVP, a single bucket is acceptable:

- `trade-strategy-artifacts`

### Suggested object key pattern

Use a path shaped like:

```text
strategies/<strategy_id>/runs/<run_id>/<artifact_type>/<filename>
```

Examples:

```text
strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/freqtrade_result_json/backtest-result.json
strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/summary_json/summary.json
strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/trades_csv/trades.csv
strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/trade_points_chart_html/trade_points_chart.html
strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/analysis_summary_md/20260318-analysis-summary.md
```

### Naming rules

- `strategy_id` should always use the repo family slug
- `run_id` should always be a UUID generated by the control plane, not derived from Freqtrade stem text
- `artifact_type` should match the enum stored in PostgreSQL
- file names may keep the original tool-generated name for easier debugging

### Metadata to attach to each object

Recommended object metadata:

- `strategy_id`
- `run_id`
- `artifact_type`
- `git_commit`
- `checksum`
- `content_type`
- `created_at`

### Lifecycle policy direction

Suggested retention policy:

- raw logs: shorter retention unless tied to failed runs
- backtest outputs and analysis reports: long retention
- artifacts tied to promoted or deployment-candidate strategies: never auto-delete without explicit policy

## Draft Web API Payload Examples

These are conceptual payloads for the future control plane. They are not approved contracts yet.

### Start a backtest

`POST /api/strategies/{strategy_id}/runs`

```json
{
  "run_type": "IS",
  "timerange": {
    "start": "2023-01-01T00:00:00Z",
    "end": "2024-12-31T23:59:59Z"
  },
  "strategy_class": "BTCMomentumPullback",
  "exchange": "binance",
  "market_type": "futures",
  "timeframe": "15m",
  "informative_timeframes": ["1h"],
  "pairlist": ["BTC/USDT:USDT"],
  "params": {
    "fee": 0.0004
  },
  "require_confirmation": true,
  "trigger_source": "web"
}
```

Example response:

```json
{
  "run_id": "2c2d58b4-8a4c-4d95-b51f-96d6ab4db123",
  "status": "queued",
  "strategy_id": "btc-momentum-pullback"
}
```

### Get run status

`GET /api/runs/{run_id}`

Example response:

```json
{
  "run_id": "2c2d58b4-8a4c-4d95-b51f-96d6ab4db123",
  "strategy_id": "btc-momentum-pullback",
  "run_type": "IS",
  "status": "completed",
  "started_at": "2026-03-18T14:55:00Z",
  "finished_at": "2026-03-18T15:01:30Z",
  "metrics": {
    "profit_factor": 0.8011,
    "win_rate": 0.218,
    "max_drawdown_pct": 0.551,
    "sharpe": -1.5127
  },
  "evaluation": {
    "tier_verdict": "REJECT",
    "launch_verdict": "BLOCK",
    "decision": "REVERT"
  }
}
```

### List recent runs for a strategy

`GET /api/strategies/{strategy_id}/runs?limit=10`

Example response:

```json
{
  "strategy_id": "btc-momentum-pullback",
  "items": [
    {
      "run_id": "2c2d58b4-8a4c-4d95-b51f-96d6ab4db123",
      "run_type": "IS",
      "status": "completed",
      "started_at": "2026-03-18T14:55:00Z",
      "tier_verdict": "REJECT",
      "launch_verdict": "BLOCK"
    }
  ]
}
```

### Trigger analysis on latest completed run

`POST /api/runs/{run_id}/analyze`

```json
{
  "include_launch_gate": true,
  "write_markdown_artifact": true,
  "trigger_source": "agent"
}
```

### Fetch artifact references for a run

`GET /api/runs/{run_id}/artifacts`

Example response:

```json
{
  "run_id": "2c2d58b4-8a4c-4d95-b51f-96d6ab4db123",
  "artifacts": [
    {
      "artifact_type": "summary_json",
      "bucket": "trade-strategy-artifacts",
      "object_key": "strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/summary_json/summary.json"
    },
    {
      "artifact_type": "trade_points_chart_html",
      "bucket": "trade-strategy-artifacts",
      "object_key": "strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/trade_points_chart_html/trade_points_chart.html"
    }
  ]
}
```

### Chat tool request shape

If the conversational layer calls a controlled backend action, the request should be explicit and machine-auditable.

Example:

```json
{
  "action": "start_backtest",
  "strategy_id": "btc-momentum-pullback",
  "arguments": {
    "run_type": "OOS",
    "timerange": {
      "start": "2025-01-01T00:00:00Z",
      "end": "2026-01-01T00:00:00Z"
    }
  },
  "requested_by": "web-chat",
  "agent_session_id": "session_abc123"
}
```

## Recommended Tooling Decision For This Repo

If only one experiment platform is introduced first, prefer `MLflow` over `Langfuse`.

### Reason

The immediate problem in this repo is not LLM trace observability. The immediate problem is durable tracking of:

- backtest runs
- parameters
- metrics
- run comparison
- artifact references
- historical execution outcomes

That is much closer to MLflow's role than Langfuse's role.

### Practical positioning

- `MLflow` should be the experiment tracking layer for strategy runs
- `PostgreSQL` should remain the control-plane state layer
- `MinIO` should remain the artifact store for large run outputs
- `Langfuse` is optional later if agent tracing, prompt management, or LLM evaluation becomes a priority

### Selection rule

If forced to choose only one first:

- choose `MLflow`
- do not choose `Langfuse` first

Langfuse may still be added later, but it should not replace run tracking for the trading workflow.

## Recommended Hybrid Architecture

The most practical near-term shape is:

1. Web UI
2. Control-plane backend
3. PostgreSQL for structured state and workflow decisions
4. MLflow for run tracking, metrics, params, and experiment history
5. MinIO for raw Freqtrade artifacts and large report objects

### Responsibility split

#### PostgreSQL

Store:

- strategy phase and next action
- approval state
- run lifecycle state
- launch-gate verdicts
- artifact references
- agent action history

#### MLflow

Store:

- experiment and run identity
- params
- metrics
- tags
- run comparison data
- links to stored artifacts

#### MinIO

Store:

- raw Freqtrade result JSON
- `summary.json`
- `trades.csv`
- `trade_points_chart.html`
- generated plots
- markdown analysis artifacts when treated as run outputs

### Operating principle

The control plane should not force users to browse raw storage systems for routine decisions.

Instead:

- the web page shows a concise structured summary
- detailed run artifacts are available through hyperlinks
- MLflow is the drill-down destination for experiment comparison
- MinIO-backed artifact links are the drill-down destination for raw outputs and reports

## Web Page Presentation Rule

For the future strategy run page, the default view should display summaries, not raw artifact dumps.

### Page should display directly

- strategy name
- current phase
- latest run status
- IS / OOS summary metrics
- launch-gate verdict
- next recommended action
- recent run list

### Page should link out to detail systems

- MLflow run page for experiment details, params, metrics history, and comparison
- MinIO artifact links for raw outputs such as `summary.json`, `trades.csv`, and `trade_points_chart.html`

### Recommended UX rule

The page should behave like a control-plane dashboard:

- show summary inline
- show important decisions inline
- show artifact and experiment links as secondary actions

Do not make the user open MinIO or MLflow just to answer basic questions like:

- what happened in the latest run
- did the strategy pass launch gate
- what should happen next

## Suggested Web Summary Payload

The backend response used by the web page can remain compact if the heavy detail lives in MLflow and MinIO.

Example response shape:

```json
{
  "strategy_id": "btc-momentum-pullback",
  "phase": "analysis",
  "latest_run": {
    "run_id": "2c2d58b4-8a4c-4d95-b51f-96d6ab4db123",
    "status": "completed",
    "run_type": "OOS",
    "started_at": "2026-03-18T15:01:00Z",
    "finished_at": "2026-03-18T15:07:00Z"
  },
  "summary": {
    "is_profit_factor": 0.8011,
    "oos_profit_factor": 0.7057,
    "win_rate": 0.246,
    "max_drawdown_pct": 0.308,
    "sharpe": -2.9085
  },
  "evaluation": {
    "tier_verdict": "REJECT",
    "launch_verdict": "BLOCK",
    "decision": "REVERT",
    "next_action": "tighten entry filters and rerun IS backtest"
  },
  "links": {
    "mlflow_run_url": "https://mlflow.example/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123",
    "summary_json_url": "https://minio.example/trade-strategy-artifacts/strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/summary_json/summary.json",
    "trades_csv_url": "https://minio.example/trade-strategy-artifacts/strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/trades_csv/trades.csv",
    "chart_html_url": "https://minio.example/trade-strategy-artifacts/strategies/btc-momentum-pullback/runs/2c2d58b4-8a4c-4d95-b51f-96d6ab4db123/trade_points_chart_html/trade_points_chart.html"
  }
}
```

This keeps the page lightweight while preserving access to the full experiment record.

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
7. Large result artifacts are fetched from MinIO by reference when needed

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

For a cloud deployment, these artifacts should be uploaded to MinIO after the run completes. The UI should render them via artifact metadata stored in PostgreSQL rather than assuming local repo paths.

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

### Gap 9: Storage contract for cloud execution

The current concept says "database + files", but cloud deployment needs a clearer storage boundary.

Recommended contract:

- PostgreSQL is the source of truth for structured strategy state and run queryability
- MinIO is the source of truth for large run artifacts and raw Freqtrade outputs
- local filesystem is only a temporary workspace during execution

Without this contract, the web layer will become environment-dependent and difficult to scale across workers.

### Gap 10: Reproducibility metadata

If users will trigger runs from a web UI through an LLM agent, each run must remain reproducible after deployment.

Minimum reproducibility metadata:

- git commit
- strategy code hash
- config hash
- timerange
- pairlist
- timeframe set
- engine version
- artifact checksums

Without this, historical run comparison becomes weak and auditability degrades quickly.

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
