---
name: trade-strategy-deployment-prep
description: Validate that a trading strategy is reproducible, controlled, and ready for dry-run or constrained live deployment.
---

# Trade Strategy Deployment Prep Skill

Use this skill when the task starts from final acceptance, dry-run preparation, or deployment readiness review.

## Goal

Confirm the strategy is safe and reproducible enough to move beyond research.

## Required Work

- verify final logic matches the validated version
- verify configs, artifacts, and parameters are reproducible
- verify monitoring, limits, and rollback conditions
- verify final OOS or walk-forward acceptance

## Output

- deployment readiness checklist
- accepted parameter set
- operational guardrails
