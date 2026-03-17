---
name: code-review-md-export
description: Review code against an existing markdown review or spec file and update checkbox states and reasoning consistently. Use when a task requires reconciling repository code with a user-specified markdown review log, risk list, or spec document.
---

# Code Review MD Export

Use this skill when the user asks you to:

- inspect or review code
- update an existing markdown review log or spec file
- reconcile code with an existing markdown file that tracks risks, findings, or training specs

## Repo workflow

For this repository:

- do not assume any fixed legacy strategy path
- discover the actual code path and markdown artifact path from the current task context
- treat user-specified markdown files as the source of truth for where review output belongs
- if a strategy-local workspace exists, prefer `strategies/<strategy_family>/reviews/` or another user-specified file inside `strategies/<strategy_family>/`

Do not create or export extra review files by default.

Only update or create markdown files when the user explicitly asks for that file-level change.
If the user only asks for a code review or discussion, respond in chat unless they explicitly name a markdown file to update.

## Required workflow

When exporting review results to markdown:

1. Read the target code and the target markdown file before editing.
2. Compare each existing risk item in the markdown file against the actual code.
3. Update checkbox states using these rules exactly.

## Checkbox rules

- For every newly identified risk item, add it with an empty checkbox: `- [ ]`.
- If an existing risk item already has an empty checkbox `- [ ]` and you agree the code still has that risk, change it to `- [v]`.
- If an existing risk item already has an empty checkbox `- [ ]` and you do not agree the code has that risk, change it to `- [x]` and add the reason under that item.
- If an existing risk item already has a crossed checkbox `- [x]`, review the reason written under it.
- If the reason under an existing `- [x]` item is reasonable, revise the risk item so the markdown reflects that conclusion accurately.
- If the reason under an existing `- [x]` item is not reasonable, keep it as `- [x]` and append your additional reasoning under that item.

## Review standard

For ML or trading code reviews, prefer organizing conclusions as:

1. leakage or correctness risk
2. validation risk
3. trading applicability risk
4. concrete next actions

When judging an item, use the code as the source of truth. Do not preserve a checkbox state just because the markdown already says so.

## Output style

- Keep edits concise and auditable.
- Prefer updating the user-specified markdown file instead of creating duplicate review files.
- If documentation and code disagree, state the reason directly under the affected item.
