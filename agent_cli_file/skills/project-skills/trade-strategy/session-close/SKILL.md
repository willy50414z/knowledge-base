---
name: session-close
description: Mandatory end-of-session cleanup. Runs the session_close CLI to update STATUS.md, _latest.json, and _context_digest.md. Run this before ending any agent session to prevent stale state in the next session.
---

# Session Close Skill

Ensures all state artifacts are consistent before the session ends.

## Quick Reference — Use the CLI (preferred)

```bash
python -m lib.endpoints.session_close <family> \
  --is-stem <IS stem> \
  [--oos-stem <OOS stem>] \
  --phase <backtest|analysis|planning> \
  [--analysis-summary <YYYYMMDD-analysis-summary.md>] \
  [--iteration-plan <YYYYMMDD-iteration-plan.md>] \
  [--commit]
```

The CLI handles all artifacts automatically:

| Artifact | What gets updated |
|----------|------------------|
| `STATUS.md` | YAML frontmatter: phase, stems, IS/OOS metrics, next_action, last_updated |
| `sessions/_latest.json` | analysis_summary / iteration_plan filenames |
| `_context_digest.md` | Full rebuild from current STATUS + _latest.json |
| git commit | Staged + committed (only when `--commit` is passed) |

**Full pipeline alternative:** Use `run_backtest_suite` to chain backtest + report + session_close in one command — see `strategy-workflow/SKILL.md`.

---

## Manual fallback steps (only if CLI unavailable)

### Step 1 — Update STATUS.md

Read `strategies/<family>/STATUS.md` and update the YAML frontmatter:

```yaml
phase: <current phase>         # implementation | backtest | analysis | planning
last_updated: <YYYY-MM-DD>
next_action: <one sentence, max 60 chars>
```

Write the updated STATUS.md back. Do not modify the human-readable sections.

---

## Step 2 — Write session record

Create a session summary file (max 200 words):

```
strategies/<family>/sessions/<YYYYMMDD>-<type>.md
```

Where `<type>` is one of: `implementation`, `backtest`, `analysis`, `planning`, `debug`.

Minimum content:

```markdown
# Session — <YYYY-MM-DD> — <type>

## What was done
<1-3 bullet points>

## Current state
- Phase: <phase>
- Last stem: <stem or none>
- Key metrics: PF <x.xx> | DD <xx%> | WR <xx%>

## Next action
<one sentence>

## Skill used
- primary_skill: <skill-name>
- skill_section: "<Phase N — Section Name>"
```

---

## Step 3 — Update _latest.json

Read `strategies/<family>/sessions/_latest.json` and update only the relevant pointers for the current phase:

| Current phase | Update field |
|---------------|-------------|
| `analysis` | `"analysis_summary": "<YYYYMMDD>-analysis-summary.md"` |
| `planning` | `"iteration_plan": "<YYYYMMDD>-iteration-plan.md"` |
| Any | `"last_updated": "<YYYY-MM-DD>"` |

Do not add fields not already in `_latest.json`. Schema is: `analysis_summary`, `iteration_plan`, `last_updated`.

---

## Step 4 — Regenerate _context_digest.md

Write `strategies/<family>/_context_digest.md` with these 6 fields:

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
- primary_skill: <skill-name>
- skill_section: "<Phase N — Section Name>"
```

---

## Completion Checklist

- [ ] STATUS.md frontmatter: `phase`, `last_updated`, `next_action` updated
- [ ] `sessions/<YYYYMMDD>-<type>.md` written
- [ ] `sessions/_latest.json` `last_updated` updated; phase-appropriate pointer updated
- [ ] `_context_digest.md` contains 6 fields including `primary_skill` + `skill_section`

If any item is unchecked, the session is **INCOMPLETE**. Complete before ending.

---

## When to Skip (with justification)

Session-close may be skipped only if:
- The session produced zero file changes (read-only exploration)
- State was already updated mid-session via another mechanism

If skipping: state the reason explicitly so the next session's agent can verify.
