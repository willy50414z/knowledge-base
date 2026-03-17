---
name: llm-orchestration
description: Route tasks to the appropriate AI agent or LLM based on task type. Use when deciding which agent to call, how to invoke it via call_llm_cli.py, or how multiple agents should collaborate on a strategy research workflow.
---

# LLM Orchestration Skill

## Agent Capability Table

Each agent has distinct strengths. Route tasks accordingly.

| Task type | Preferred agent | Invocation |
|-----------|----------------|-----------|
| Code review, refactoring, implementation | **Claude** | Direct (current session) |
| Long document reading, PDF analysis, research synthesis | **Gemini** | `call_llm_cli gemini "<prompt>"` |
| Agentic repo-wide code editing, multi-file changes | **OpenCode** | `call_llm_cli opencode "<prompt>" --cwd <repo>` |
| Code completion, inline suggestions | **Codex** | `call_llm_cli codex "<prompt>"` |
| Markdown review, structured writing | **Claude** | Direct |
| Backtest result interpretation, performance narrative | **Gemini** | `call_llm_cli gemini "<prompt>"` |
| Strategy hypothesis validation against domain literature | **Gemini** | `call_llm_cli gemini "<prompt>"` |
| Multi-file implementation sprint | **OpenCode** | `call_llm_cli opencode "<prompt>" --cwd <repo> --timeout 120` |
| Multi-agent consensus on strategy decisions | **All** | See `multi-agent-consensus/SKILL.md` |

## CLI Usage

```bash
# One-shot LLM call
python -m lib.endpoints.call_llm_cli <target> "<prompt>" [--cwd PATH] [--timeout SECONDS]

# Targets: gemini | codex | opencode | copilot
```

Examples:
```bash
# Ask Gemini to analyze a long backtest markdown report
python -m lib.endpoints.call_llm_cli gemini "Summarize the failure modes in: $(cat strategies/btc-shortma/reports/2026-03-17.md)"

# Ask OpenCode to implement a new indicator across multiple files
python -m lib.endpoints.call_llm_cli opencode "Add ATR-based position sizing to BTCShortMA_v1" --cwd E:/Software/trade_strategy --timeout 180
```

## Fallback Chain

When an external agent call fails (non-zero exit code or empty output):

```
Primary:   Gemini  or  Codex   (whichever was specified)
         ↓ if fails
Fallback:  the other one (Gemini ↔ Codex swap)
         ↓ if fails
Final:     Claude handles the task directly in the current session
```

When falling back to Claude, log the failure in `strategies/<family>/sessions/` with the error and timestamp so the user can investigate later.

```bash
# Detect failure
result=$(python -m lib.endpoints.call_llm_cli gemini "$PROMPT")
if [ -z "$result" ]; then
    result=$(python -m lib.endpoints.call_llm_cli codex "$PROMPT")  # first fallback
fi
# If still empty, Claude handles it directly
```

## Multi-Agent Collaboration Pattern

For a typical strategy research cycle:

```
Phase 1 — Research & Hypothesis
  → Claude: scope, hypothesis, spec drafting

Phase 2 — Implementation
  → Claude or OpenCode: Freqtrade strategy .py file

Phase 3 — Backtest & Analysis
  → Claude: python -m lib.endpoints.freqtrade ...
  → Claude: python -m lib.strategy.analytics.analyze_backtest_result

Phase 4 — Report Synthesis
  → Gemini: synthesize long HTML/markdown report into narrative

Phase 5 — Next Iteration Planning
  → Multi-agent consensus (if major decision): see multi-agent-consensus/SKILL.md
  → Claude alone: if minor iteration
```

## Routing Decision Rules

- Prefer Claude for any task requiring code changes or file editing.
- Prefer Gemini when the input is a large document (>2000 tokens of context to read).
- Prefer OpenCode for autonomous multi-file edits without step-by-step supervision.
- Never send secrets (API keys, tokens) in prompts to any external agent.

## Implementation Details

Read this section before modifying any file in `lib/llm_agent/`.

### Module Map

| Purpose | Path |
|---------|------|
| CLI entry point | `lib/endpoints/call_llm_cli.py` |
| LLM subprocess runner | `lib/llm_agent/llm_svc.py` |
| LLM target enum | `lib/llm_agent/llm_target.py` |
| Semantic model router (API targets only) | `lib/llm_agent/litellm_route_svc.py` |
| Codex router config | `lib/llm_agent/llm_model_router_codex.json` |
| Gemini router config | `lib/llm_agent/llm_model_router_gemini.json` |

### `LLMTarget` Enum (`lib/llm_agent/llm_target.py`)

```python
class LLMTarget(Enum):
    GEMINI   = "gemini"
    CODEX    = "codex"
    OPENCODE = "opencode"
    COPILOT  = "copilot"
```

### `run_once()` (`lib/llm_agent/llm_svc.py`)

```python
def run_once(
    target: LLMTarget,
    prompt: str,
    *,
    cwd: str | None = None,
    timeout: float | None = None,
    encoding: str = "utf-8",
) -> str
```

Runs the target CLI as a subprocess and returns stdout as a string. Raises `RuntimeError` on non-zero exit code. Raises `ValueError` if prompt is empty.

**Key behaviours per target:**

| Target | CLI command built | `--model` flag | Special env |
|--------|------------------|---------------|-------------|
| GEMINI | `gemini --approval-mode yolo --sandbox false --prompt <prompt>` | **Never passed** — CLI manages its own model | — |
| CODEX | `codex exec --dangerously-bypass-approvals-and-sandbox <prompt>` | **Never passed** — CLI uses gpt-5.4 internally | — |
| OPENCODE | `opencode run --dir <cwd> --format json <prompt>` | Not supported | `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME` set under `data/tool-runtime/opencode/`; `OPENCODE_PERMISSION` set to allow all |
| COPILOT | `copilot -p <prompt> --allow-all --no-ask-user --output-format text --silent --add-dir <cwd>` | Passed if router returns one | — |

**OPENCODE output parsing**: OPENCODE emits newline-delimited JSON events. `run_once` extracts `text` content blocks and concatenates them. If an `error` event appears, it raises `RuntimeError`.

**Windows CLI resolution**: `_resolve_cli()` tries `<name>.cmd` first (npm-installed CLIs on Windows use `.cmd` wrappers). Falls back to `shutil.which(<name>)`, then bare name.

### Semantic Model Router (`lib/llm_agent/litellm_route_svc.py`)

**Currently inactive for all targets.** `_TARGET_ROUTER_CONFIG = {}` in `llm_svc.py` — no target has a router config assigned.

The router uses TF-IDF + cosine similarity against per-route utterance sets to select a model name. It is designed for **API-based targets** (e.g., a future `LLMTarget.OPENAI` that calls OpenAI API directly), where the same target can serve multiple models and cost matters.

CLI-based targets (GEMINI, CODEX, OPENCODE) do not accept arbitrary `--model` names from outside — they manage model selection internally. Passing `--model` to these CLIs causes failures.

**To activate the router for a new API-based target:**
1. Add a router config JSON to `lib/llm_agent/` (follow the structure of `llm_model_router_codex.json`)
2. Add the target to `_TARGET_ROUTER_CONFIG` in `llm_svc.py`
3. Add a `--model` branch in `run_once()` for the new target

### `call_llm_cli.py` (`lib/endpoints/call_llm_cli.py`)

Thin CLI wrapper around `run_once`. Accepts `target`, `prompt`, optional `--cwd`, `--timeout`, `--encoding`. Prints the result to stdout. Use `python -m lib.endpoints.call_llm_cli` (not direct file execution) to ensure correct module resolution.
