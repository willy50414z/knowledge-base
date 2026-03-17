# Trade Strategy Architecture And AI Agent Review

Date: 2026-03-17

## Scope

This review evaluates the repository from two viewpoints:

1. User workflow continuity for the TAO loop:
   strategy idea -> implementation -> test -> analysis -> next iteration
2. AI agent execution efficiency:
   skill routing, implementation accuracy, improvement loop speed
3. Token efficiency without reducing reasoning quality

Primary files reviewed:

- `strategies/README.md`
- `strategies/_template/README.md`
- `strategies/_template/STATUS.md`
- `lib/endpoints/freqtrade.py`
- `lib/strategy/execution/freqtrade_executor.py`
- `lib/strategy/analytics/analyze_backtest_result.py`
- `lib/storage/feature_store.py`
- `lib/llm_agent/llm_svc.py`
- `tests/README.md`
- `requirements.txt`
- `knowledge-base/skills/project-skills/trade-strategy.md`
- `knowledge-base/skills/project-skills/trade-strategy/strategy-workflow/SKILL.md`
- `knowledge-base/skills/project-skills/trade-strategy/llm-orchestration/SKILL.md`
- `knowledge-base/skills/framework-skills/freqtrade/freqtrade-analysis-workflow/SKILL.md`

## Executive Summary

The repository already has the right high-level direction: strategy-first workspace, Freqtrade execution entrypoints, post-backtest analytics, and local skill-based guidance for AI agents.

The main problem is not missing concepts. The main problem is that the workflow is only partially systematized. Several key transitions in the loop still depend on manual memory, implicit file conventions, or ad hoc command usage. This creates breakpoints for both human users and AI agents.

The highest-priority optimization is to turn the current template-driven workflow into a state-driven workflow with explicit artifacts, explicit transitions, and smaller structured context units for agents.

---

## Findings

### 1. User TAO loop has multiple breakpoints between phases

Severity: High

Evidence:

- `strategies/_template/STATUS.md` only contains placeholders and a static next step. It is not connected to execution or analysis outputs.
- `knowledge-base/skills/project-skills/trade-strategy/strategy-workflow/SKILL.md` defines phase gates, but there is no automation that enforces or updates them.
- `lib/endpoints/freqtrade.py` runs backtests and stores the latest stem, but it does not sync strategy-local status files.

Why this matters:

The user workflow currently relies on the user or agent remembering what happened in the previous phase. That breaks the TAO loop at exactly the place where iteration quality matters most: after a run is done and before the next hypothesis is chosen.

Observed breakpoints:

1. Strategy idea -> implementation
   The repo has only `_template` and no active strategy family workspace. This means the workflow standard exists, but there is no evidence of an end-to-end path being regularly exercised.
2. Implementation -> test
   There is no project-level "preflight" command that validates strategy file existence, config generation, data readiness, and import health in one step.
3. Test -> analysis
   `lib/strategy/analytics/analyze_backtest_result.py` depends on `.last_result.json` and an implicit latest run selection, instead of explicit input arguments.
4. Analysis -> next implementation
   There is no automated write-back from analysis outputs into `STATUS.md`, `sessions/`, or a next-iteration task list.

Recommended revision direction:

- Add a strategy-local machine-readable state file such as `strategies/<family>/state.json`.
- Make backtest and analysis commands update both `state.json` and `STATUS.md`.
- Add a single orchestration entrypoint such as:
  `python -m lib.endpoints.strategy_cycle <family> <strategy_name> <timerange>`
- The orchestration command should:
  - validate prerequisites
  - run backtest
  - run analysis
  - summarize top metrics
  - update `STATUS.md`
  - generate a next-step stub

---

### 2. Analysis pipeline is not explicit or reproducible enough

Severity: High

Evidence:

- `lib/strategy/analytics/analyze_backtest_result.py:27` hardcodes `TIMERANGE = "20240101-20261231"`.
- `lib/strategy/analytics/analyze_backtest_result.py:2981` to `:3004` loads the latest execution from `.last_result.json` rather than requiring an explicit stem or family.
- `lib/strategy/execution/freqtrade_executor.py:225` to `:235` stores only minimal last-result metadata.

Why this matters:

For a single developer and one current strategy, "latest result" may be tolerable. For an agent-based workflow, it is fragile. If multiple experiments are run, or if the user wants a specific historical run analyzed, the current design can silently analyze the wrong artifact.

Recommended revision direction:

- Make the analysis CLI require one of:
  - `--stem`
  - `--strategy-name`
  - `--strategy-family`
  - `--timerange`
- Keep `.last_result.json` only as a convenience fallback, not the primary contract.
- Extend saved run metadata with:
  - strategy family
  - config hash
  - README hypothesis hash or version
  - analysis completion timestamp
- Generate an artifact index file per strategy family, for example:
  `strategies/<family>/reports/index.json`

---

### 3. Test stage is not reliably executable in a clean environment

Severity: High

Evidence:

- `tests/README.md` instructs users to run `pytest tests/`.
- `requirements.txt` does not include `pytest`.
- In the current environment, `python -m pytest tests/` fails because `pytest` is not installed.

Why this matters:

A workflow that claims implementation -> test but cannot execute tests in a fresh environment is a broken loop. This affects both humans and agents, because the agent cannot cheaply validate small changes before moving to more expensive backtests or analysis.

Recommended revision direction:

- Add `pytest` to a dev requirements file or a unified lockfile.
- Add one canonical setup command in `README.md`.
- Add a minimal health-check command such as:
  `python -m pytest tests/test_type_utils.py tests/test_feature_store.py`
- Distinguish:
  - unit tests
  - integration tests
  - strategy validation checks

---

### 4. Feature persistence has an asymmetric fallback path

Severity: High

Evidence:

- `lib/storage/feature_store.py:73` to `:82` falls back to `to_pickle()` when Feather write is unavailable.
- `lib/storage/feature_store.py:57` to `:68` only loads via `pd.read_feather()`.

Why this matters:

This is a silent data pipeline risk. If Feather write support is absent, data can be saved successfully and then become unreadable through the same abstraction. That is a bad failure mode for both TAO loop stability and agent trust in the storage layer.

Recommended revision direction:

- Make save/load symmetric.
- Either:
  - require Feather support and fail loudly, or
  - support a sidecar format marker and load both Feather and pickle consistently
- Add a unit test that simulates the fallback path.

---

### 5. Agent orchestration guidance is stronger than the actual implementation

Severity: Medium-High

Evidence:

- `knowledge-base/skills/project-skills/trade-strategy/llm-orchestration/SKILL.md` defines routing, fallback chain, and capability mapping.
- `lib/llm_agent/llm_svc.py:33` sets `_TARGET_ROUTER_CONFIG = {}`, so semantic routing is effectively disabled.

Why this matters:

The repository already documents a capable agent orchestration model, but the code path does not yet operationalize most of it. This creates a gap between how the system is supposed to work and how it actually behaves.

Recommended revision direction:

- Decide whether routing is:
  - documentation-only, or
  - a real runtime feature
- If runtime feature:
  - add an orchestration wrapper that chooses target based on task type
  - log fallback decisions
  - store agent call summaries in strategy-local session files when needed
- If not runtime feature:
  - simplify the code and remove inactive routing language to reduce confusion

---

### 6. Too much of the workflow is represented in free-form markdown instead of structured state

Severity: Medium-High

Evidence:

- `strategies/_template/README.md` and `STATUS.md` are the main workflow carriers.
- Skills assume agents will read and interpret large markdown files to reconstruct current state.

Why this matters:

Markdown is suitable for human review, but not as the sole control surface for an agentic workflow. The agent has to repeatedly read large files, infer current status, and rebuild context each time. This increases token cost and creates avoidable ambiguity.

Recommended revision direction:

- Keep markdown for human-readable summaries.
- Add structured sidecars:
  - `state.json`
  - `latest_run.json`
  - `next_actions.json`
  - `context_digest.json`
- Use markdown as the narrative layer, not the only state layer.

---

### 7. There is no dedicated skill for "strategy cycle orchestration"

Severity: Medium

Evidence:

- Skills exist for scope, hypothesis, implementation, analysis, and orchestration.
- There is no single skill that owns the end-to-end cycle from active strategy status -> next concrete action.

Why this matters:

The current skill graph is rich, but the user journey crosses multiple skills every cycle. An agent can follow the standards, but it still spends effort deciding which skill to load and how to sequence them.

Recommended revision direction:

Add a new project skill:

- `strategy-cycle-orchestrator`

Suggested responsibilities:

- read `README.md` and `STATUS.md`
- determine current phase
- pick the next skill chain
- validate required artifacts for the next phase
- emit one concise next-action list
- prefer structured summaries over raw full-file reads

This would reduce both routing overhead and token usage.

---

### 8. Repo has weak support for comparison across iterations

Severity: Medium

Evidence:

- The workflow mentions `experiments/`, `reports/`, and `sessions/`.
- Current implementation writes reports to engine/report locations and leaves strategy-local summary writing largely manual.

Why this matters:

Strategy improvement quality depends on comparing "baseline vs changed variant" with explicit verdicts. Without a consistent comparison artifact, agents and users risk repeating failed ideas or overfitting to whichever latest run they remember.

Recommended revision direction:

- Standardize an experiment comparison record template in:
  `strategies/<family>/experiments/`
- Add a command that compares two stems and emits:
  - IS vs OOS deltas
  - sensitivity deltas
  - trade count changes
  - recommended keep/revert verdict

---

### 9. Token consumption can be cut substantially by changing context shape, not reasoning depth

Severity: Medium

Evidence:

- The repo relies on large markdown briefs and a very large analysis script.
- Skill instructions are already separated, but working state is not compactly serialized.

Why this matters:

Most waste does not come from the model "thinking too much". It comes from repeatedly reloading broad context that should have been compactly summarized into stable, reusable state.

Recommended revision direction:

Adopt a layered context model:

1. Level 0: routing context
   - task type
   - strategy family
   - current phase
2. Level 1: compact state
   - current hypothesis
   - last backtest metrics
   - blocking issues
   - next action
3. Level 2: targeted evidence
   - only the relevant report files or code files
4. Level 3: deep diagnostics
   - large report archives or full analysis outputs only when needed

This can reduce token usage without reducing reasoning quality because the model is still allowed to escalate into deeper context on demand.

---

## TAO Breakpoint Map

### From the user perspective

| Loop stage | Current weakness | Impact |
|-----------|------------------|--------|
| Idea -> spec | Template exists, but no guided bootstrap flow | User must manually translate idea into repo-ready structure |
| Spec -> implementation | No single command validates readiness | Errors appear late |
| Implementation -> test | Test environment is not guaranteed | Fast feedback loop breaks |
| Test -> analysis | Analysis target is implicit | Wrong artifact risk |
| Analysis -> next step | No automatic state write-back | Loop depends on memory |

### From the AI agent perspective

| Agent task | Current weakness | Impact |
|-----------|------------------|--------|
| Choose skill | Many useful skills, but no cycle owner | Routing overhead |
| Build context | Must read markdown to infer state | Token waste |
| Run next action | No orchestration command | More brittle command sequences |
| Improve strategy | Comparison artifacts not standardized | Lower iteration precision |
| Control costs | Inactive runtime routing and no compact context digest | Missed cost-efficiency gains |

---

## Recommended New Skills

### 1. `strategy-cycle-orchestrator`

Purpose:

- Own the full TAO loop for one strategy family

Workflow:

- read current state
- detect current phase
- validate gate
- choose next operation
- write back result summary

### 2. `artifact-triage`

Purpose:

- Read only compact artifacts first before touching large reports

Workflow:

- check `summary.json`
- check `validation.json`
- check `run_metadata.json`
- escalate to deep diagnostics only if thresholds fail

### 3. `experiment-compare`

Purpose:

- Compare baseline and candidate runs in a consistent way

Workflow:

- ingest two stems
- generate key deltas
- label improvement type
- output KEEP / REVERT / NEED MORE DATA

### 4. `strategy-bootstrap`

Purpose:

- Turn a raw trading idea into a complete strategy family workspace

Workflow:

- create folder from template
- fill initial README sections
- generate config skeleton
- initialize status and next action

---

## Recommended Implementation Priorities

### Priority 1: Fix workflow breakpoints

1. Make test setup executable in a clean environment.
2. Make analysis explicit by stem/family instead of implicit latest-result resolution.
3. Add structured strategy state files and automatic write-back.

### Priority 2: Improve agent reliability

1. Add `strategy-cycle-orchestrator` skill.
2. Add artifact index and run comparison utilities.
3. Decide whether LLM routing is active runtime behavior or only documentation.

### Priority 3: Reduce token cost

1. Add compact state artifacts per strategy.
2. Add artifact triage before deep report reading.
3. Keep markdown narrative, but stop using markdown as the only state mechanism.

---

## Concrete Next Actions

1. Add a review-driven improvement epic that starts with workflow state and artifact contracts, not model changes.
2. Implement a single `strategy_cycle` orchestration CLI for one family.
3. Fix `FeatureStore` load/save symmetry.
4. Add missing test dependencies and define a reproducible dev setup.
5. Refactor analysis CLI to accept explicit inputs and use `.last_result.json` only as fallback.
6. Add one new project skill: `strategy-cycle-orchestrator`.
7. Add compact per-strategy context files to reduce repeated markdown loading.

---

## Supplemental Findings — 2026-03-17

The following findings extend the original review with additional observations from a senior systems architecture and AI agent perspective, focused on: (1) TAO loop breakpoints not yet captured, (2) agent routing and implementation precision gaps, (3) token efficiency improvements that do not reduce reasoning quality.

---

### 10. The "idea → scope" entry point has no structured intake path

Severity: High

Evidence:

- `trade-strategy.md` maps "New strategy from scratch" to `trade-strategy-scope` + `trade-strategy-hypothesis-baseline`.
- `trade-strategy-scope/SKILL.md` requires symbol, market type, success criteria, rejection criteria, and fee/slippage assumptions before proceeding.
- `trade-strategy-bootstrap` is proposed in the Recommended New Skills section of this document but does not yet exist.

Why this matters:

The gap between "user has a vague trading idea" and "strategy family workspace is initialized with a valid scope document" is the first breakpoint in every TAO loop. The current path requires the user to know which skills to invoke, in what order, and to manually create the folder structure. If this step is manual and slow, iterations slow down from the very start.

There is also a conceptual asymmetry: the end of the loop (planning → implementation) has a formal iteration plan template, but the beginning of the loop (idea → scope) has no equivalent structured intake. A user revisiting an old idea and a user starting fresh follow completely different implicit paths.

Observed consequence:

An agent receiving "I have an idea for a new strategy" cannot bootstrap the workspace without reading three skills and making multiple decisions about folder naming, config template selection, and initial STATUS.md state. This sequence is predictable and should be encoded in a single skill.

Recommended revision direction:

- Create `strategy-bootstrap` skill (already proposed in this review).
- The skill should: accept a raw idea description, generate a structured scope draft for user confirmation, then create the workspace atomically.
- Add an explicit "intake checklist" to the bootstrap that enforces all `trade-strategy-scope` gates before writing any files.

---

### 11. Hypothesis lineage has no index, enabling silent re-testing of rejected ideas

Severity: Medium-High

Evidence:

- Each iteration plan goes into `strategies/<family>/sessions/<date>-iteration-plan.md`.
- Each analysis summary goes into `strategies/<family>/sessions/<date>-analysis-summary.md`.
- The `experiments/` folder holds comparison records but has no master index.
- `README.md` is updated when hypothesis changes, but old hypotheses are overwritten, not archived.

Why this matters:

After four or five iterations, neither the user nor the agent has a reliable way to answer: "Have we tried adding a regime filter before? What was the verdict?" The agent would need to read all session files chronologically to reconstruct hypothesis history. A user working without an agent is entirely dependent on personal memory.

This is especially dangerous for the "analysis → planning" transition. The planning skill correctly says: "Do not propose changes that are not linked to a specific observed weakness." But if the agent cannot check whether a proposed change was tried before, it may propose a change that was previously rejected as ineffective or harmful.

Observed consequence:

Iterations risk circular exploration. The loop looks forward but has no backward traceability, which reduces the value of each completed iteration.

Recommended revision direction:

- Add `strategies/<family>/hypothesis-log.md` that records each hypothesis version with: version tag, what changed, why it changed, and the verdict after testing.
- Update the iteration plan template to require a "Prior Art" line: "Has this change been tried before? If yes, cite the date and outcome."
- Update `strategy-workflow/SKILL.md` to include hypothesis-log maintenance in the planning → implementation gate.

---

### 12. No data readiness check in the backtest preflight

Severity: Medium-High

Evidence:

- `strategy-workflow/SKILL.md` and `freqtrade-analysis-workflow/SKILL.md` both define preflight gates that check: strategy file existence, config generation, and import health.
- Neither preflight checks whether historical OHLCV data is present and covers the requested timerange.
- `lib/endpoints/freqtrade.py` runs the backtest command but does not validate data before invoking Freqtrade.
- Data lives at `data/features/<EXCHANGE>/<MARKET_TYPE>/` and is managed by a separate `data-pipeline` skill.

Why this matters:

Freqtrade backtests with missing data either fail with a cryptic error or silently truncate the timerange, producing results that look valid but cover a shorter period than intended. Both failure modes are invisible in the preflight phase.

This creates a breakpoint between implementation and test that is purely operational, not logical. The user or agent cannot distinguish "strategy is wrong" from "data was missing" without inspecting the actual backtest timerange in the output.

Recommended revision direction:

- Add a data readiness check to the backtest preflight:
  - Verify `data/features/<exchange>/<market_type>/<pair>_<timeframe>.feather` (or equivalent) exists.
  - Verify the file's date range covers the requested timerange.
- Expose this check as a single command:
  `python -m lib.endpoints.check_data_readiness <pair> <timeframe> <timerange>`
- Add this gate to `freqtrade-analysis-workflow/SKILL.md` Phase 1 preflight.

---

### 13. Skill routing has no disambiguation protocol for ambiguous user requests

Severity: Medium-High

Evidence:

- `trade-strategy.md` provides a Task → Skill mapping table.
- The table requires the agent to identify the task type from the user's request.
- Real user requests are often phase-ambiguous: "improve the strategy" maps differently depending on whether the user is post-analysis (→ `trade-strategy-improvement-planning`) or post-implementation (→ `freqtrade-analysis-workflow`).
- No disambiguation protocol exists. The agent must infer the current phase from STATUS.md and then map to the right skill.

Why this matters:

Routing errors are silent and costly. If an agent loads `trade-strategy-improvement-planning` when the user meant "run the backtest first", it will propose spec changes without having current test data. The user then has to explicitly redirect the agent, losing context and wasting tokens.

The current design assumes the agent always reads STATUS.md before loading a skill, but the skills themselves do not enforce this. The Task → Skill table does not include a "read STATUS.md first" instruction, and the skills themselves only say "read STATUS.md as input", not "use STATUS.md to verify this skill is appropriate for the current phase".

Recommended revision direction:

- Add a disambiguation step to the agent's task intake: before loading any skill, read STATUS.md and use current phase to filter which skills are valid.
- Add a `current-phase → valid-skill` constraint table to `trade-strategy.md`:

| Current phase | Valid primary skills |
|--------------|---------------------|
| `implementation` | `trade-strategy-freqtrade-implementation` |
| `backtest` | `freqtrade-analysis-workflow` |
| `analysis` | `freqtrade-analysis-workflow`, `trade-strategy-improvement-planning` |
| `planning` | `trade-strategy-improvement-planning`, `trade-strategy-prototype-design` |

- When a user request maps to a skill that is not valid for the current phase, the agent should surface this conflict explicitly before acting.

---

### 14. Every new agent session re-pays the same cold-start context cost

Severity: Medium

Evidence:

- Every new session requires the agent to read: CLAUDE.md → `agent-general-skills.md` → `trade-strategy.md` → relevant skill file(s) → `README.md` → `STATUS.md`.
- This sequence is predictable and constant regardless of task complexity.
- The only artifact that changes between sessions is STATUS.md and the latest session file in `sessions/`.
- There is no compressed "agent resume" artifact that pre-builds the relevant portion of this chain.

Why this matters:

For short iterative tasks (e.g., "run the backtest and update STATUS"), the cold-start reads can consume more tokens than the actual task. This is not a reasoning quality problem — the agent still reasons correctly — but it is an avoidable cost that accumulates across every iteration.

The layered context model in Finding 9 identifies this problem structurally. This finding specifies the cold-start sequence as the specific target for optimization.

Recommended revision direction:

- Add a `strategies/<family>/_context_digest.md` file that compresses the frequently-read chain into one file:
  - Current strategy summary (2-3 sentences from README)
  - Current phase (from STATUS.md)
  - Last backtest stem and key metrics (from STATUS.md)
  - Next action (from STATUS.md or latest session)
  - Active skill(s) for current phase (pre-resolved from phase)
- Update this digest automatically whenever STATUS.md is updated (by agent or by the `strategy_cycle` orchestration CLI proposed in Finding 1).
- Agent reads `_context_digest.md` first. Only escalates to full README/STATUS/skill files if the task requires deeper context.

---

### 15. SKILL files load entirely even for simple confirmatory operations

Severity: Medium

Evidence:

- `freqtrade-analysis-workflow/SKILL.md` is a 125-line document covering all four phases.
- A task like "update STATUS.md after backtest completes" requires only the post-backtest gate rules, but the agent loads the full file.
- Similarly, `trade-strategy-improvement-planning/SKILL.md` contains the iteration plan template that is only needed once per cycle.

Why this matters:

Skill files are loaded as a unit. An agent performing a narrow operation (e.g., "write the analysis summary") loads the entire skill including sections for backtest, validate, tune, and code reference. Most of that content is irrelevant for the current operation and adds token overhead without improving output quality.

This is structurally similar to the markdown-state problem in Finding 6 but at the skill layer rather than the strategy layer.

Recommended revision direction:

- Add a standardized `## Quick Reference` section at the top of each SKILL.md that covers the 80% case in 5–10 lines.
- Full skill content follows below the quick reference, loaded only when the task requires a phase not covered by the quick reference.
- Adopt the convention: if the task matches a quick reference operation, stop reading after that section.

Example for `freqtrade-analysis-workflow`:

```markdown
## Quick Reference

| Operation | Command | Gate |
|-----------|---------|------|
| Run backtest | `python -m lib.endpoints.freqtrade <family> <name> <timerange> --mode backtest` | config.json + strategy file exist |
| Run analysis | `python -m lib.strategy.analytics.analyze_backtest_result` | stem.json exists |
| After backtest | Update STATUS.md: phase → analysis, fill stem | — |
| After analysis | Write sessions/<date>-analysis-summary.md, STATUS.md: phase → planning | — |
```

---

### 16. Session file discovery adds latency to agent context loading

Severity: Low-Medium

Evidence:

- `trade-strategy-improvement-planning/SKILL.md` instructs: "Read `strategies/<family>/sessions/<latest>-analysis-summary.md`."
- There is no canonical "latest" pointer. The agent must: list the directory, sort by date prefix, identify the target file type, then read it.
- In a busy strategy workspace, `sessions/` may contain analysis summaries, iteration plans, consensus records, and general notes, all with similar date prefixes.

Why this matters:

This is a low-cost structural inefficiency, but it compounds across every iteration because the "read latest analysis summary" step appears in multiple skills. File discovery requires a tool call before the file read, doubling the overhead for a routine step.

Recommended revision direction:

- Maintain a canonical pointer file: `strategies/<family>/sessions/_latest.json`

```json
{
  "analysis_summary": "20260315-analysis-summary.md",
  "iteration_plan": "20260317-iteration-plan.md",
  "last_updated": "2026-03-17"
}
```

- When any skill writes a new session file, it updates `_latest.json` atomically.
- Agent reads `_latest.json` to resolve file names. One read replaces a directory listing + sort + filter sequence.

---

### 17. STATUS.md is human-readable but not directly machine-parseable

Severity: Medium

Evidence:

- `strategies/<family>/STATUS.md` carries the current phase, last backtest stem, current hypothesis, and next action.
- The current template is free-form markdown prose.
- An agent extracting "current phase" must perform a text search or parse markdown structure.
- Finding 6 of this review already identifies this as part of the markdown-state problem. This finding specifies STATUS.md as the highest-priority instance.

Why this matters:

STATUS.md is read at the start of almost every skill. If it can be parsed programmatically, agents skip text inference and read fields directly. This benefits both token efficiency and accuracy (no risk of misreading a phase transition buried in prose).

Recommended revision direction:

- Add a YAML frontmatter block to `strategies/<family>/STATUS.md`:

```yaml
---
phase: analysis
last_backtest_stem: btc-shortma-20260315
last_run_metrics:
  profit_factor: 1.42
  max_drawdown: 14.2
  win_rate: 58.3
  sharpe: 1.21
next_action: "Write analysis summary, then update phase to planning"
last_updated: "2026-03-17"
---
```

- Keep the human-readable narrative sections below the frontmatter.
- Update all skills that read STATUS.md to extract from frontmatter first.

---

### 18. Cross-strategy knowledge extraction has no trigger or skill

Severity: Medium

Evidence:

- `strategy-workflow/SKILL.md` states: "Cross-strategy lessons → `knowledge-base/knowledge/backtest-records/`."
- No skill has a phase gate that prompts writing to `knowledge-base/knowledge/backtest-records/`.
- The improvement planning skill, analysis workflow skill, and workflow skill all operate at the strategy-family level and do not reference the cross-strategy knowledge store.

Why this matters:

The repository's long-term value comes from accumulated knowledge, not from individual strategy results. If each strategy's lessons stay siloed in `strategies/<family>/sessions/`, the knowledge-base never grows. An agent or user starting a new strategy will re-discover patterns that were already found in a previous family.

This is a structural gap in the TAO loop's outbound path: the loop has strong inbound guidance (how to start a strategy) but weak outbound guidance (how to extract lessons when an iteration is completed or a strategy is retired).

Recommended revision direction:

- Add a "lessons extraction" step to the `Analysis → Planning` gate in `strategy-workflow/SKILL.md`:
  - After writing the analysis summary, ask: "Does this result surface a cross-strategy pattern (e.g., regime filter behavior, drawdown structure, fee sensitivity threshold)?"
  - If yes, write a short entry to `knowledge-base/knowledge/backtest-records/<YYYYMMDD>-<topic>.md`.
- Create a `knowledge-extraction` skill or integrate this step into `trade-strategy-improvement-planning`.

---

## Supplemental TAO Breakpoint Map

### Additional user-perspective breakpoints

| Loop stage | Gap not previously captured | Impact |
|-----------|------------------------------|--------|
| Idea → scope | No structured intake path; user must know to invoke scope + hypothesis skills in order | Slow and error-prone for first iteration |
| Scope → implementation | No check that data for the requested pair and timerange exists before backtest | Cryptic backtest failure or silent data truncation |
| Analysis → planning | No hypothesis lineage index; agent cannot check if a proposed change was already tried | Circular exploration risk |
| Planning → next idea | No cross-strategy lesson extraction trigger | Knowledge stays siloed; next strategy starts without prior learnings |

### Additional agent-perspective breakpoints

| Agent task | Gap not previously captured | Impact |
|-----------|------------------------------|--------|
| Determine current phase | No phase-gated skill routing constraint | Wrong skill loaded for current phase |
| Load session context | No latest-file pointer; agent must list and sort sessions/ | Extra tool call per session |
| Read STATUS.md | Free-form markdown; agent must text-search for field values | Inference risk; extra token cost |
| Start new session | No context digest; agent re-reads full skill and spec chain | Predictable cold-start token cost |
| Load skill for common operation | Full skill file loaded for narrow operations | Token overhead for routine tasks |
| Complete iteration | No extraction gate for cross-strategy lessons | Knowledge accumulation blocked |

---

## Supplemental Recommended New Skills

### 5. `knowledge-extraction`

Purpose:

- Distill cross-strategy patterns from a completed iteration

Workflow:

- Read analysis summary and experiment comparison records
- Identify if any finding has cross-strategy applicability
- Write a short structured entry to `knowledge-base/knowledge/backtest-records/`
- Update hypothesis-log with final verdict

### 6. `data-readiness-check`

Purpose:

- Verify data availability before any backtest or analysis run

Workflow:

- Accept pair, timeframe, and timerange as inputs
- Verify feature file exists and covers the full requested range
- Output: READY / MISSING / TRUNCATED with specific gap details
- Integrates into backtest preflight gate

---

## Supplemental Implementation Priorities

### Priority 1 additions

4. Add `strategies/<family>/hypothesis-log.md` template and maintenance gate.
5. Add data readiness preflight command and integrate into backtest skill gate.

### Priority 2 additions

4. Add phase-gated skill routing constraint table to `trade-strategy.md`.
5. Add `strategies/<family>/_context_digest.md` and update it on every STATUS.md write.
6. Add `sessions/_latest.json` pointer and update skill write steps to maintain it.

### Priority 3 additions

4. Add YAML frontmatter to STATUS.md template and update skill read steps.
5. Add `## Quick Reference` section to high-frequency skills (`freqtrade-analysis-workflow`, `trade-strategy-improvement-planning`).
6. Add cross-strategy lesson extraction gate to `Analysis → Planning` transition.

---

## Final Verdict

The project already has a strong conceptual foundation, especially in strategy workspace design and skill taxonomy. The main optimization opportunity is operational: make the workflow state explicit, make each phase transition auditable, and give agents smaller structured context objects.

That will improve three things at once:

- user iteration speed
- agent execution precision
- token efficiency

The supplemental findings above identify where the existing optimization direction has specific structural gaps: the intake side of the TAO loop is weaker than the analysis side, the agent's cold-start cost is not addressed at the session layer, and knowledge compounds in silos rather than flowing to a shared store. Addressing these gaps in priority order will incrementally close the remaining breakpoints without requiring a large rewrite.
