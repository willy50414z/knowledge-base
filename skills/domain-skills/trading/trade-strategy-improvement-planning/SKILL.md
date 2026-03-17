---
name: trade-strategy-improvement-planning
description: Build the next strategy iteration plan from observed weaknesses, failure modes, and audit results. Use when deciding how to improve a strategy after backtest review, report analysis, or failed validation.
---

# Trade Strategy Improvement Planning Skill

Refine trading strategies based on historical audit results.

## Core Standards

- Document improvement plans in the host repository's strategy research area.
- Decide whether the next iteration is a major logic change or a minor parameter revision.

## Required Work

- Identify the specific regime (e.g., Sideways, High Vol) where the strategy underperforms.
- Formulate a new hypothesis to fix the identified "Pain Point."
- Update the Prototype Design spec before re-implementing.

## General Decision Rules

- Do not propose changes that are not linked to a specific observed weakness or failure mode.
- Do not batch unrelated improvements into one iteration if that would make validation attribution unclear.
- Do not re-implement before the revised hypothesis and prototype changes are written down clearly enough to test.
