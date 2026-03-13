# Project Skills Index

Shared source of truth for all project-specific AI agent skills in this repository.

## Core Working Rules

- Read existing code before changing behavior.
- Prefer minimal, targeted edits over broad refactors.
- Preserve time-series correctness and avoid look-ahead bias.
- Do not change model assumptions silently; document any ML logic change.
- When updating training logic, also review related markdown docs in `com/willy/trade_bot/ml/`.
- Save created or modified files as UTF-8 without BOM when feasible to avoid Windows encoding issues.

## Skills Index Maintenance Skill

- `knowledge-base/skills/ai_agent_skill.md` is the project-wide skills catalog.
- Whenever a new skill is added under `knowledge-base/skills/`, update this file in the same task.
- The update must include the new skill name, a short description, and the correct path to its `SKILL.md`.
- Do not leave newly created skills undocumented in the catalog.
- If a skill is renamed, moved, split, or removed, sync the catalog in the same change.

## Skill Directory

Each skill below is defined in its own directory with a `SKILL.md` file.

For trade strategy work:

- `trade-strategy-development` is the end-to-end overview skill.
- `trade-strategy-*` skills are step-specific skills and should be preferred when the task starts from a specific stage.

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| **ML Workflow** | Guidelines for ML engineering and research changes. | [ml-workflow/SKILL.md](./ml-workflow/SKILL.md) |
| **Strategy Workflow** | Standards for trading strategy folder structure and files. | [strategy-workflow/SKILL.md](./strategy-workflow/SKILL.md) |
| **Documentation** | Keeping documentation aligned with actual code. | [documentation-workflow/SKILL.md](./documentation-workflow/SKILL.md) |
| **Markdown Review** | Rules for high-quality markdown feedback and revision. | [markdown-review/SKILL.md](./markdown-review/SKILL.md) |
| **Trading Domain** | Fundamental constraints for trading-related logic. | [trading-domain/SKILL.md](./trading-domain/SKILL.md) |
| **ML Trading Strategy** | Specialized check for look-ahead bias and backtest assumptions. | [ml-trading-strategy/SKILL.md](./ml-trading-strategy/SKILL.md) |
| **Plan Consensus Review** | Multi-agent review workflow for substantial plan validation. | [ml-consensus-review/SKILL.md](./ml-consensus-review/SKILL.md) |
| **Code Review Export** | Workflow for exporting code review findings to markdown. | [code-review-md-export/SKILL.md](./code-review-md-export/SKILL.md) |
| **Trade Strategy Dev** | Specific workflow for strategy development. | [trade-strategy-development/SKILL.md](./trade-strategy-development/SKILL.md) |
| **Trade Strategy Scope** | Define research scope, constraints, and success criteria before strategy work begins. | [trade-strategy-scope/SKILL.md](./trade-strategy-scope/SKILL.md) |
| **Trade Strategy Data Validation** | Collect and validate the dataset used for strategy research and backtesting. | [trade-strategy-data-validation/SKILL.md](./trade-strategy-data-validation/SKILL.md) |
| **Trade Strategy Hypothesis Baseline** | Turn a strategy idea into a testable hypothesis with explicit baselines. | [trade-strategy-hypothesis-baseline/SKILL.md](./trade-strategy-hypothesis-baseline/SKILL.md) |
| **Trade Strategy Prototype Design** | Define entry, exit, and risk logic before implementation. | [trade-strategy-prototype-design/SKILL.md](./trade-strategy-prototype-design/SKILL.md) |
| **Trade Strategy Freqtrade Implementation** | Implement the strategy in Freqtrade with auditable signal mapping. | [trade-strategy-freqtrade-implementation/SKILL.md](./trade-strategy-freqtrade-implementation/SKILL.md) |
| **Trade Strategy Backtest Validation** | Backtest the strategy and run the required validation checks. | [trade-strategy-backtest-validation/SKILL.md](./trade-strategy-backtest-validation/SKILL.md) |
| **Trade Strategy Parameter Tuning** | Tune strategy parameters while checking robustness instead of curve fitting. | [trade-strategy-parameter-tuning/SKILL.md](./trade-strategy-parameter-tuning/SKILL.md) |
| **Trade Strategy Performance Analysis** | Diagnose where performance comes from and where the strategy fails. | [trade-strategy-performance-analysis/SKILL.md](./trade-strategy-performance-analysis/SKILL.md) |
| **Trade Strategy Improvement Planning** | Build the next iteration plan from observed weaknesses and evidence. | [trade-strategy-improvement-planning/SKILL.md](./trade-strategy-improvement-planning/SKILL.md) |
| **Trade Strategy Deployment Prep** | Validate deployment readiness, guardrails, and reproducibility. | [trade-strategy-deployment-prep/SKILL.md](./trade-strategy-deployment-prep/SKILL.md) |

## Preferred Output Style

- Be concise and direct.
- Present ML review results as:
    1. leakage or correctness risk
    2. validation risk
    3. trading applicability risk
    4. concrete next actions

## Safe Defaults

- Prefer reproducible parameters over `now()`-driven experiments when adding new training flows.
- Prefer UTF-8 safe logs and avoid console output that may break on Windows encodings.
- If a change affects saved model artifacts, call that out explicitly.
