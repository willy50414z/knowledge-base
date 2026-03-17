---
name: multi-agent-consensus
description: Coordinate multiple LLMs to reach a consensus on high-stakes strategy decisions. OpenCode drafts, Gemini and Codex review, Claude decides. Use only for major decisions that affect strategy architecture, core hypothesis, or risk parameters — not routine tasks.
---

# Multi-Agent Consensus Skill

When a decision is consequential enough that a single LLM's perspective carries material blind-spot risk, run a structured multi-agent consensus review before acting.

## When to Trigger

Trigger consensus review for:
- First-version strategy architecture design (entry/exit structure, regime filters, position sizing approach)
- Major hypothesis revision after a failed backtest
- Switching core indicator logic (e.g., trend-following → mean-reversion)
- Changing risk parameters that affect live trading (stoploss multiplier, max drawdown threshold)

Do **not** trigger for:
- Routine parameter tuning (use hyperopt instead)
- Minor code fixes
- Report formatting
- Adding a single indicator to an existing strategy

## Workflow

```
Step 1 — OpenCode drafts
  Prompt: "Draft an implementation plan for [decision]. Include: approach, key assumptions, risks, and alternatives considered."
  Output: a draft plan in the session file (see below)

Step 2 — Gemini + Codex review in parallel
  Gemini prompt: "Review this plan for domain correctness, market logic, and research validity: [paste plan]"
  Codex prompt:  "Review this plan for implementation feasibility, code structure risks, and edge cases: [paste plan]"
  Run both calls concurrently via ThreadPoolExecutor (see CLI Invocation below).
  Output: each agent adds its review section to the session file.

Step 3 — Claude synthesizes
  Read all three contributions, resolve conflicts, and write the DECISION section.
  Claude has final authority.
```

## CLI Invocation

Call `lib.endpoints.call_llm_cli` as a module. Gemini and Codex reviews run in parallel.

```python
# Run from repo root: python consensus_runner.py
import subprocess
from concurrent.futures import ThreadPoolExecutor

DECISION = "your decision topic here"

def call_llm(target: str, prompt: str) -> str:
    result = subprocess.run(
        ["python", "-m", "lib.endpoints.call_llm_cli", target, prompt],
        capture_output=True, text=True, encoding="utf-8", timeout=300
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()

# Step 1 — OpenCode drafts
plan = call_llm(
    "opencode",
    f"Draft an implementation plan for: {DECISION}. "
    "Include: approach, key assumptions, risks, and alternatives considered."
)

# Step 2 — Gemini + Codex review in parallel
with ThreadPoolExecutor(max_workers=2) as ex:
    gemini_fut = ex.submit(call_llm, "gemini",
        f"Review this strategy plan for domain correctness, market logic, and research validity:\n\n{plan}")
    codex_fut  = ex.submit(call_llm, "codex",
        f"Review this strategy plan for implementation feasibility, code structure risks, and edge cases:\n\n{plan}")
    gemini_review = gemini_fut.result()
    codex_review  = codex_fut.result()

# Step 3 — Print for Claude to synthesize
print("=== OPENCODE DRAFT ===\n", plan)
print("=== GEMINI REVIEW ===\n", gemini_review)
print("=== CODEX REVIEW ===\n", codex_review)
```

Or invoke each step manually via shell:

```bash
python -m lib.endpoints.call_llm_cli opencode "Draft a plan for: [your decision]" --cwd E:/Software/trade_strategy
python -m lib.endpoints.call_llm_cli gemini  "Review this plan for market logic: [paste plan]"
python -m lib.endpoints.call_llm_cli codex   "Review this plan for implementation feasibility: [paste plan]"
```

## Session File

Save the full discussion at:

```
strategies/<strategy_family>/sessions/<YYYYMMDD>-consensus-<topic>.md
```

Paste each agent's output into the corresponding section as the review progresses. Claude writes the DECISION section last.

```markdown
# Multi-Agent Consensus — <Topic> — <Date>

## Decision Question
<One sentence: what are we deciding?>

---

## OpenCode Draft

<paste OpenCode output here>

---

## Gemini Review

<paste Gemini output here>

---

## Codex Review

<paste Codex output here>

---

## Claude Decision

**Verdict**: PROCEED / REVISE / REJECT

**Rationale**: <one paragraph synthesizing all three inputs>

**Conflicts resolved**:
- Gemini said X, Codex said Y → chose Z because ...

**Action items**:
- [ ] <next step>
```

## Failure Fallback

If any agent call fails (see llm-orchestration/SKILL.md for fallback chain):
- Skip that agent's review step
- Note the failure in the session file under that agent's section
- Claude proceeds with available input, noting the missing perspective in the rationale
