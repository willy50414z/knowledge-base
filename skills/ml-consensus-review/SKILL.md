---
name: ml-consensus-review
description: Review a draft execution plan with another LLM through llm_svc.py, reconcile differences, and only then finalize the plan.
---

# ML Consensus Review Skill

Use this skill when the task requires a non-trivial execution plan, especially for ML, trading, validation, architecture, or research-sensitive work.

## Goal

Produce a final execution plan only after:

1. drafting an initial plan locally
2. sending that draft to another LLM through `com/willy/trade_bot/service/llm_svc.py`
3. asking the other LLM to review it from the most relevant expert perspective
4. reconciling both views into a final plan

## Required Invocation Path

- Use `com/willy/trade_bot/service/llm_svc.py`
- Do not bypass it with ad hoc direct CLI calls if this workflow is requested
- Select the target LLM and expert framing based on the task

## Reviewer Selection

Choose the reviewer role that best matches the task:

- ML model training or labeling changes: financial ML expert
- Strategy logic or backtest assumptions: quantitative trading expert
- Data pipeline, joins, or feature generation: data engineering expert
- Validation design, calibration, or split logic: ML validation expert
- Refactor, service boundaries, or architecture: senior software architect
- Reliability, failure modes, or safety controls: risk-focused reviewer

If the task spans multiple areas, pick the dominant risk area first.

## Workflow

### Phase 1: Draft the Initial Plan

Create a preliminary plan that includes:

- objective
- assumptions
- constraints
- proposed execution steps
- key risks
- expected verification

This is not the final plan.

### Phase 2: Ask Another LLM to Review the Draft

Send the draft plan to another LLM through `llm_svc.py` and instruct it to:

- review as a domain expert
- identify missing steps
- challenge weak assumptions
- detect correctness, leakage, validation, or trading risks when relevant
- propose reordered or additional steps
- distinguish blockers from optional improvements

The review request should ask for actionable critique, not generic feedback.

### Phase 3: Reconcile the Opinions

Compare:

- your local draft
- the external LLM review

Then explicitly decide:

- what feedback is adopted
- what feedback is rejected
- why each disagreement is resolved that way

If the external review identifies a high-risk issue, update the plan before finalizing it.

### Phase 4: Produce the Final Plan

The final plan should include:

- the revised execution steps
- integrated safeguards
- verification approach
- any open questions or blockers

If consensus was partial, say so clearly.

## Minimum Final Output Structure

When summarizing the final plan, include:

1. Draft plan summary
2. External expert review summary
3. Reconciled decisions
4. Final execution plan

## Prompting Guidance

The external review prompt should contain:

- task context
- relevant repo paths
- draft plan
- constraints
- explicit request to act as a domain expert
- explicit request to find missing or risky steps

Keep the prompt concrete and scoped to the real task.

## Quality Bar

The plan is not final until:

- another LLM has reviewed it through `llm_svc.py`
- important disagreements are resolved
- major risks have been incorporated or consciously rejected with reasons

## Domain-Specific Emphasis

For ML and trading work, the review must explicitly check:

- look-ahead bias
- target leakage
- split and validation correctness
- calibration or thresholding assumptions
- unrealistic backtest assumptions
- artifact and reproducibility implications
