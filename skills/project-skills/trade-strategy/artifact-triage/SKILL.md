---
name: artifact-triage
description: Load the minimal set of strategy artifacts needed for a task before escalating to larger files. Use at the start of any session to minimize token cost while preserving full context access on demand.
---

# Artifact Triage Skill

Read artifacts in ascending size order. Stop as soon as you have enough context for the task.

## Triage Ladder

```
Level 0 — routing context (always read first)
  → strategies/<family>/_context_digest.md
    If digest is fresh (last_updated today or task is simple): stop here.

Level 1 — compact state (read if Level 0 is missing or stale)
  → strategies/<family>/STATUS.md (YAML frontmatter only)
  → strategies/<family>/sessions/_latest.json
    If current phase + next_action + last stem is enough: stop here.

Level 2 — targeted evidence (read only what the task needs)
  → strategies/<family>/sessions/<latest analysis summary>  (for planning tasks)
  → strategies/<family>/hypothesis-log.md                   (for change proposals)
  → strategies/<family>/experiments/<latest comparison>     (for verdict reviews)
  → relevant SKILL.md for the current phase                 (for execution tasks)
    Stop here for most tasks.

Level 3 — deep diagnostics (read only when thresholds fail or task requires full spec)
  → strategies/<family>/README.md                           (full spec)
  → freqtrade/reports/<stem>_<strategy>.zip                 (full analysis output)
  → full SKILL.md content                                   (for unfamiliar operations)
```

## Rules

- Do not jump to Level 3 artifacts without exhausting Level 0–2 first.
- If Level 0 is more than 1 day old, treat it as Level 1 and re-read STATUS.md frontmatter to verify.
- For implementation tasks (writing code): Level 2 is the minimum — you need the spec.
- For routine phase transitions (run backtest, write summary): Level 0 or 1 is sufficient.

## What Each Level Costs

| Level | Typical tokens | When sufficient |
|-------|---------------|----------------|
| 0 | ~200 | Resume work, status check, phase transition |
| 1 | ~300 | Any task where phase + last stem + next action is enough |
| 2 | ~800 | Planning, comparison, analysis summary writing |
| 3 | ~5000+ | Full spec review, implementation from scratch, deep diagnosis |

## Digest Freshness Check

The digest at `_context_digest.md` is considered fresh if:
- `last_updated` is today's date, AND
- `phase` matches what you expect from the user's request

If either condition fails, re-read STATUS.md frontmatter and update the digest.
