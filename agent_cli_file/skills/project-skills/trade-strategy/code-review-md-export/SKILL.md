---
name: code-review-md-export
description: Conduct a structured multi-agent code or spec review using a shared markdown session file. Each agent writes to a labeled section; Claude synthesizes the final verdict. Use when reviewing strategy code, ML logic, or spec documents with multiple LLM perspectives.
---

# Code Review MD Export

A shared markdown file acts as the session document where multiple agents contribute reviews, respond to each other, and converge on a decision.

## When to Use

- Reviewing strategy implementation code against spec
- Auditing ML logic for leakage or correctness risks
- Reconciling code with a risk log or spec document
- Any review where multiple LLM perspectives reduce blind spots

For lightweight single-agent review, respond in chat unless the user explicitly names a markdown file to update.

## Session File Location

Store in `strategies/<strategy_family>/reviews/<YYYYMMDD>-<topic>.md`.

## Session Structure

Each review file follows this fixed structure:

```markdown
# Code Review — <Topic> — <Date>

## Scope
- Files reviewed: ...
- Spec reference: ...

---

## Round 1 — Individual Reviews

### Gemini
- [ ] <Risk item> — <Evidence: file:line or behavior>
- [ ] <Risk item> — <Evidence>

### Codex
- [ ] <Risk item> — <Evidence>

### Claude
- [ ] <Risk item> — <Evidence>

---

## Round 2 — Cross-Response (optional)

### Gemini responding to Codex
> <quote the Codex item>
<Gemini's response: agree / disagree / additional evidence>

### Claude responding to Gemini
> <quote>
<Claude's response>

---

## Decision (Claude — Final)

**Verdict**: PASS / FAIL / CONDITIONAL

**Action items**:
- [ ] <specific fix with file:line>
- [ ] <specific fix>

**Rationale**: <one paragraph>
```

## Checkbox Rules (Standard GFM)

Use only standard GFM checkboxes. Do not use `[v]`.

| State | Meaning |
|-------|---------|
| `- [ ]` | Risk identified, not yet resolved |
| `- [x]` | Risk resolved or ruled out — add one-line reason below |

When reviewing:
- Add new risks with `- [ ]`
- Mark `- [x]` only when you have evidence the risk does not apply or is fixed
- Never change another agent's checkbox without stating your reasoning

## Review Standard

Organize findings in this priority order:
1. **Leakage / correctness** — data leakage, future-peeking, incorrect indicators
2. **Validation** — missing OOS split, wrong train/test boundary
3. **Trading applicability** — fees not modeled, signal frequency too low
4. **Next actions** — specific, file-level, actionable

Use the code as the source of truth. Do not preserve a checkbox state just because the markdown already says so.

## Repo Workflow

- Discover actual code path and review file path from the task context — do not assume fixed paths.
- If a strategy-local workspace exists, store the review in `strategies/<strategy_family>/reviews/`.
- Read both the code and the existing review file before editing.
- Do not create duplicate review files — update the existing session file.
