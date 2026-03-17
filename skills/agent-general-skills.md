# Agent General Skills

Use this file as the entry point for agent-wide, cross-project working rules stored in `knowledge-base`.

## Included Standards

- [File Encoding Standard](./standards/file-encoding.md)
  Apply this before reading, writing, patching, generating, or exporting any text file.
- [Skill Writing Standard](./standards/skill-writing-standard.md)
  Apply this when creating or reorganizing skills in this repository.

## TAO Working Method

All agents in this repository must follow TAO (Thought → Action → Observation) when working on tasks.

**Thought** — Before each action, state in one sentence what you are about to do and why.

**Action** — Take exactly one focused action (read a file, write code, run a command, etc.).

**Observation** — After the action, state what you learned or what changed. If the result is unexpected, adjust your plan before the next step.

Repeat until the task is complete.

### TAO Rules

- Do not batch multiple actions without an observation in between when the outcome of one affects the next.
- Do not skip the Thought step to save tokens — it prevents reasoning errors.
- If an action fails, the Observation must include the root cause, not just the error message.
- When a task is done, state the final observation clearly so the user can verify without re-reading code.

### Example

```
Thought: I need to read freqtrade_executor.py before modifying it to avoid overwriting existing logic.
Action: [Read lib/strategy/execution/freqtrade_executor.py]
Observation: The file uses REPO_ROOT correctly but STRATEGY_PATH is hardcoded. I will fix line 24.

Thought: I will replace the hardcoded STRATEGY_PATH with a repo-relative path.
Action: [Edit lib/strategy/execution/freqtrade_executor.py line 24]
Observation: Edit applied. STRATEGY_PATH now resolves from REPO_ROOT dynamically.
```

## Context Loading Protocol

Before loading skill files or strategy documents, apply the **artifact triage** ladder to minimize cold-start token cost:

1. Read `strategies/<family>/_context_digest.md` first — if fresh, skip to action.
2. If no digest or it is stale: read only `STATUS.md` YAML frontmatter + `sessions/_latest.json`.
3. Load only the SKILL.md sections needed for the current task (Quick Reference first).
4. Escalate to full README.md or full skill content only when required.

See: `knowledge-base/skills/project-skills/trade-strategy/artifact-triage/SKILL.md`

## Usage

- If a task involves text files, load and follow the linked file encoding standard first.
- Apply TAO for all non-trivial tasks (more than one file change or any reasoning required).
- Apply the context loading protocol above before reading large markdown files.
- Add new cross-agent rules here as more shared standards are created.
- Keep this file short; store full rules in linked documents.
