---
name: trade-strategy-development
description: Apply repository-level development rules for folder placement, strategy workspaces, code organization, and migration-safe changes in `trade_strategy`. Use when a task affects project structure, architecture, or repository-wide strategy workflows.
---

# Trade Strategy Development Skill

Repository-level development standards for the `trade_strategy` project.

## Directory Standards

Place code and artifacts by responsibility:

- `lib/`
  Shared Python library code, adapters, orchestration, analytics, and entry points.
- `freqtrade/`
  Freqtrade-specific strategy code, configs, and reports.
- `data/`
  Raw market data, derived features, and reproducible dataset snapshots.
- `strategies/<strategy_family>/`
  Strategy-local markdown artifacts, reviews, reports, experiments, and decision history.
- `knowledge-base/`
  Reusable skills, standards, and supporting knowledge documents.

Do not introduce new code under legacy `com/willy/...` paths.

## Naming and Organization

- Use a stable lowercase strategy slug for folders, for example `btc-breakout` or `eth-mean-reversion`.
- Group all markdown research artifacts for a strategy family under `strategies/<strategy_family>/`.
- Keep engine-specific implementation names aligned with the target engine's conventions.
- Keep generated outputs separate from hand-authored specs and reviews.

## Coding Conventions

- Use absolute imports rooted at `lib` or the relevant top-level package already used by the repository.
- Keep DTOs, adapters, and utilities independent from engine-specific orchestration where possible.
- Do not hardcode machine-specific paths.
- Resolve repo-relative paths from the repository root or from the current module location.

## Workflow Integrity

- Treat strategy markdown artifacts as first-class project assets, not disposable notes.
- Require a clear link between hypothesis, spec, implementation, and report artifacts.
- When a strategy implementation changes materially, update the related strategy-local markdown artifacts in the same task when feasible.
- Keep framework-specific validation inside the relevant framework workflow, currently Freqtrade.
