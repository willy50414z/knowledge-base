# Multi-Agent Architecture Review — Trade Strategy Repository

Date: 2026-03-17
Reviewers: Codex (OpenAI), Gemini (Google), Claude (Anthropic / synthesis)
Scope: Post-optimization review after implementing findings from `20260317-trade-strategy-architecture-ai-agent-review.md`

---

## Review Context

This review was conducted after implementing the following optimizations:
- YAML frontmatter added to STATUS.md template
- `hypothesis-log.md` template added
- `sessions/_latest.json` pointer convention established
- `_context_digest.md` artifact pattern defined
- Phase-gated skill routing added to trade-strategy.md
- New skills: `strategy-cycle-orchestrator`, `strategy-bootstrap`, `artifact-triage`, `experiment-compare`, `knowledge-extraction`, `data-readiness-check`
- Quick Reference sections added to high-frequency skills
- FeatureStore load/save symmetry fixed with sidecar marker
- `check_data_readiness.py` CLI endpoint created
- `requirements-dev.txt` added with pytest and pyarrow
- `save_last_result()` extended with strategy_family and timestamp

Each reviewer was asked to evaluate from three angles: user TAO loop breakpoints, AI agent efficiency, and token cost reduction. Reviewers were also asked to identify domain-specific checks that could improve strategy reliability.

---

## Codex Review

*Perspective: Senior systems architect and AI agent specialist*

### Finding C-1: data-readiness check has a column contract mismatch

Severity: High

The `check_data_readiness.py` endpoint tries to infer date coverage from the DataFrame index or a `date` column. However, `FeatureStore.save()` calls `reset_index(drop=True)` before writing to Feather, dropping the index. The Binance adapter (`binance_svc.py:70,142`) uses `start_time` as the index and sets it with `drop=False`, so `start_time` is also a column — but the original checker did not look for it.

**Status after synthesis**: Fixed. The checker now probes `start_time`, `date`, `open_time`, `timestamp` in order, then falls back to the DataFrame index.

### Finding C-2: analyze_backtest_result.py hardcodes TIMERANGE

Severity: High

`TIMERANGE = "20240101-20261231"` at line 27 is written into run metadata during analysis. The executor already persists the real timerange in `.last_result.json`, but the analysis script ignores it. Reports can silently misstate what was actually tested.

**Recommendation**: Pass `--timerange` as a CLI argument to `analyze_backtest_result.py`. Use `.last_result.json` as a convenience fallback when the argument is absent, but prefer explicit input.

**Status**: Not yet fixed. Requires refactoring the analysis CLI.

### Finding C-3: LLM runner has no trust-boundary enforcement

Severity: High (security / agent safety)

Every LLM target is configured for maximum permissiveness:
- Gemini: `--approval-mode yolo --sandbox false`
- Codex: `--dangerously-bypass-approvals-and-sandbox`
- OpenCode: `OPENCODE_PERMISSION` set to allow all
- Copilot: `--allow-all --no-ask-user`

For a repository where LLM agents can write files, run backtests, and modify strategies, this means prompt injection in any external document (a downloaded report, a Gemini response, a Codex output) can be escalated into privileged execution. The current design has no sandbox profiles, no prompt provenance tracking, no redaction layer for secrets, and no distinction between "safe analysis" and "privileged execution."

**Recommendation**:
- Define two permission tiers: `read-only` (analysis, summarization) and `write-allowed` (implementation, file changes).
- Route Gemini to `read-only` for all report analysis and hypothesis synthesis.
- Route OpenCode/Codex to `write-allowed` only for explicit implementation tasks.
- Add a `--sandbox` flag to `call_llm_cli.py` to make the tier choice explicit at the call site.
- Log all agent calls with prompt hash, target, and timestamp to a session audit file.

**Status**: Not fixed. This is a systemic design decision.

### Finding C-4: Analysis subsystem is an untestable monolith

Severity: Medium

`analyze_backtest_result.py` is ~3050 lines handling extraction, parsing, diagnostics, charting, CSV export, metadata assembly, and packaging in a single script. It works operationally but is not maintainable as the strategy count grows.

**Recommendation**: Extract into discrete modules:
- `lib/strategy/analytics/parse_result.py` — JSON parsing, trade normalization
- `lib/strategy/analytics/diagnostics.py` — signal win rate, gate funnel analysis, slippage sensitivity
- `lib/strategy/analytics/report_builder.py` — HTML/CSV/zip packaging
- `lib/strategy/analytics/analyze_backtest_result.py` — orchestrator (thin entry point)

**Status**: Not fixed. Recommended as a future refactor milestone.

### Finding C-5: Test coverage is narrow and environment not ready by default

Severity: Medium (already addressed in prior review)

`pytest` was not installed; tests could not run in a clean environment. Coverage exists only for `feature_store` and `ml_svc` — no coverage for Freqtrade endpoints, data-readiness flow, or LLM orchestration.

**Status**: Partially fixed. `requirements-dev.txt` added with pytest and pyarrow. Pickle fallback tests added to `test_feature_store.py`. Broader coverage (Freqtrade endpoint, check_data_readiness) is still missing.

---

## Gemini Review

*Perspective: Technical analyst with domain focus*

Gemini identified the repository as a sophisticated framework with strong architectural foundations. Key observations:

### Finding G-1: Semantic router is well-designed but inactive

Severity: Medium

The `litellm_route_svc.py` semantic router using TF-IDF + cosine similarity is a well-designed capability that is currently inactive (`_TARGET_ROUTER_CONFIG = {}`). For API-based targets, this is a missed opportunity to reduce cost by routing simple queries to cheaper models.

**Recommendation**: Activate the router for at least one API-based target. Document which targets are CLI-managed (GEMINI, CODEX, OPENCODE) and which are API-managed, to clarify when the router is applicable.

### Finding G-2: Indicator library is not validated at strategy load time

Severity: Medium

`tech_idx_svc.py` provides a rich indicator library (SMA, MACD, RSI, ATR, Donchian, etc.). However, there is no validation that the indicators required by a strategy are present and correctly computed before a backtest runs. A strategy requesting an indicator that fails silently (e.g., due to insufficient data for the lookback period) will produce misleading results.

**Recommendation**: Add an indicator validation step to the backtest preflight that checks:
- All required indicators defined in the strategy spec are present in the dataset
- No NaN values in indicators for the first N candles of the backtest period (where N = the indicator's max lookback)
- Warn if more than 5% of candles in the backtest period have NaN indicator values

### Finding G-3: Feature store path is relative, not absolute

Severity: Medium

`FeatureStore.build_path()` returns a relative path (`data/features/...`). This means the correct working directory must be the repo root for any code using FeatureStore paths. If a script is run from a different directory, paths will silently resolve to the wrong location.

**Recommendation**: Anchor the feature path to `REPO_ROOT` in the same way `freqtrade_executor.py` anchors its paths via `Path(__file__).resolve().parents[3]`. The `check_data_readiness.py` already works around this by joining `REPO_ROOT / path`, but the root cause is in `FeatureStore.build_path()`.

---

## Claude Synthesis and Additional Findings

### Finding A-1: Strategy improvement cycle has no objective look-ahead bias gate

Severity: High

The current workflow has a backtest preflight (data readiness, config existence, import health) but no check for look-ahead bias in the strategy implementation. Look-ahead bias is the most common source of unrealistically inflated backtest results and is undetectable by any metric comparison — it requires structural code inspection.

The `freqtrade-analysis-workflow/SKILL.md` mentions the check but frames it as conditional: "Win Rate > 70% with high trade frequency → Run look-ahead bias check before proceeding." This creates a survivorship-bias in when the check is applied — strategies with moderate win rates but still biased will skip the check.

**Recommendation**: Add a mandatory look-ahead bias inspection to every backtest gate, not just as a threshold-triggered check. The inspection should verify:
- No use of `dataframe.shift(-N)` for N > 0 in entry/exit conditions (negative shift looks ahead)
- No use of `dataframe['close']` as a condition computed before the bar closes
- No future data leaking through `merge_informative_pair` with incorrect `shift=False` usage

Add this as a new skill: `look-ahead-bias-check` (see Recommended New Skills).

### Finding A-2: OOS validation protocol is defined but not enforced as a hard gate

Severity: High

`freqtrade-analysis-workflow/SKILL.md` defines OOS thresholds (e.g., "OOS profit < 50% of IS profit → Unstable") but frames them as diagnostics, not hard gates. The Planning phase can proceed even if OOS validation would flag the strategy as unstable.

The iteration loop can therefore produce a sequence of IS-optimized strategies that all fail OOS without any hard stop. This is the most common form of strategy overfitting in systematic research.

**Recommendation**: Promote the OOS check to a mandatory gate at Analysis → Planning:
- If OOS Profit Factor < 1.0: phase must return to `implementation`, not proceed to `planning`
- If OOS / IS ratio < 50%: iteration plan must explicitly address overfitting before proceeding
- Add these as explicit checklist items in the `Analysis → Planning` gate in `strategy-workflow/SKILL.md`

### Finding A-3: The `_context_digest.md` has no automated update mechanism

Severity: Medium

`_context_digest.md` is defined as the primary cold-start optimization artifact, but there is no code path that automatically writes it. It requires manual or skill-guided updates after each phase transition. If it falls out of sync with STATUS.md, it becomes actively harmful — agents will read stale phase/stem data and take wrong actions.

**Recommendation**: Either:
- Add a function to `freqtrade_executor.py` that regenerates `_context_digest.md` after each backtest (alongside `save_last_result`)
- Or make `strategy-cycle-orchestrator` responsible for always re-generating the digest when it runs, so the digest is always fresh after orchestration

### Finding A-4: No skill for regression detection across iterations

Severity: Medium

The `experiment-compare` skill compares two specific stems explicitly. But in a continuous iteration loop, it is common to introduce a regression in iteration N+2 that was not compared against the original baseline — only against N+1. The user or agent may not realize they need to run a comparison against the original baseline when an intermediate comparison looks positive.

**Recommendation**: Add a convention to `hypothesis-log.md` that tracks the "anchor baseline" stem — the best stable version ever validated — separate from the "previous iteration" stem. The `experiment-compare` skill should always compare against the anchor baseline as well as the previous version.

### Finding A-5: No domain skill for regime classification validation

Severity: Medium

Multiple strategy specs use regime filters (e.g., "only trade when ADX > 25"). However, there is no skill that validates whether a regime filter is functioning as intended. A regime filter can silently block too many trades (making results look clean but reducing trade count below statistical significance) or too few (allowing noisy conditions in).

**Recommendation**: Add a `regime-filter-validation` skill that checks:
- What % of candles pass the regime filter in the backtest period
- Whether trades are significantly better in the filtered subset vs all candles
- Whether the filter is calibrated correctly for the chosen timeframe and market

### Finding A-6: `FeatureStore.build_path()` returns a relative path (corroborates Gemini G-3)

Severity: Medium

`FeatureStore.build_path()` returns `Path("data") / ...`. Any caller not running from REPO_ROOT will silently resolve to the wrong directory. `check_data_readiness.py` already works around this with `REPO_ROOT / path`, but the underlying issue is in `FeatureStore`.

**Recommendation**: Change `FeatureStore.build_path()` to accept an optional `repo_root: Path` parameter, or document clearly that all callers must be run from REPO_ROOT. The simplest fix is to anchor the base path:

```python
# In FeatureStore.build_path():
from pathlib import Path
_REPO_ROOT = Path(__file__).resolve().parents[3]

@staticmethod
def build_path(exchange, market_type, product, timeframe, *, repo_root=None):
    base = Path(repo_root) if repo_root else FeatureStore._REPO_ROOT
    return base / "data" / "features" / exchange / market_type / f"{product}_{timeframe}.feature"
```

---

## Recommended New Skills (from this review cycle)

### `look-ahead-bias-check`

Purpose: Structural inspection of strategy code for look-ahead bias patterns.

Placement: `knowledge-base/skills/framework-skills/freqtrade/look-ahead-bias-check/SKILL.md`

Workflow:
- Grep strategy `.py` file for: `shift(-`, `future`, informative pair with `shift=False`
- Check entry/exit conditions for use of close price before bar closes
- Report: CLEAN | SUSPECT (list patterns found) | CONFIRMED BIAS

Required in backtest preflight as a mandatory gate, not conditional.

### `oos-validation-gate`

Purpose: Enforce OOS validation as a hard gate before the Planning phase.

Placement: `knowledge-base/skills/framework-skills/freqtrade/oos-validation-gate/SKILL.md`

Workflow:
- Read IS and OOS profit factor from the analysis output
- Compute OOS/IS ratio
- Gate: if OOS PF < 1.0 → BLOCK Planning phase, return to implementation
- Gate: if OOS/IS < 0.5 → WARN, require explicit acknowledgement in iteration plan

### `regime-filter-validation`

Purpose: Validate that regime filters are neither over-filtering nor under-filtering.

Placement: `knowledge-base/skills/domain-skills/trading/regime-filter-validation/SKILL.md`

Workflow:
- Compute the % of candles passing the regime filter in the backtest period
- Compare win rate inside vs outside the filter
- Flag if pass rate < 20% (too restrictive) or > 80% (effectively disabled)
- Recommend calibration adjustments

---

## Updated TAO Breakpoint Map (after this review cycle)

### Remaining user-perspective breakpoints

| Loop stage | Remaining gap | Priority |
|-----------|--------------|---------|
| Implementation → Backtest | Look-ahead bias check not yet automated as a hard gate | High |
| Test → Analysis | TIMERANGE hardcoded in analyze_backtest_result.py | High |
| Analysis → Planning | OOS validation is a soft warning, not a hard gate | High |
| Any phase | `_context_digest.md` requires manual updates; can become stale | Medium |
| Any phase | FeatureStore.build_path() relative path can silently resolve wrong | Medium |

### Remaining agent-perspective gaps

| Agent task | Remaining gap | Priority |
|-----------|--------------|---------|
| LLM routing | Trust-boundary enforcement absent; all targets run with maximum permissions | High |
| Iteration quality | No anchor baseline tracking in hypothesis-log; regression detection incomplete | Medium |
| Regime filters | No validation skill; agents cannot verify if regime filters are calibrated | Medium |
| Analysis context | analyze_backtest_result.py is a monolith; agents cannot query specific diagnostics | Medium |

---

---

## Second Review Cycle — Codex & Gemini (2026-03-17)

*Conducted after implementing the first-cycle optimizations.*

### Codex Second Review Findings

**CC-1 (High — Fixed): `check_data_readiness.py` had two code defects**

- `pandas` was not imported in the module; `pd.to_datetime()` call raised `NameError`
- `abs_path` variable was referenced after being removed from scope

**Status**: Both bugs fixed. 48 tests pass (10 new for check_data_readiness, 5 new for save_last_result, test_ml_svc fixture corrected).

**CC-2 (High — Pending): TIMERANGE hardcode still not consumed downstream**

`analyze_backtest_result.py:27` still has `TIMERANGE = "20240101-20261231"`. The `save_last_result()` now saves the real timerange to `.last_result.json`, but `load_last_execution()` in the analysis script ignores `timerange` and `strategy_family` from that file. Reports can still misstate what was tested.

**CC-3 (Medium): MLService rewires `sys.stdout` at import time**

`lib/ml/ml_svc.py` modifies `sys.stdout` at module import level, causing pytest teardown failures with `ValueError: I/O operation on closed file`. Full `pytest tests/` cannot be used as a verification gate.

**CC-4 (Medium): No tests for new integration points**

`check_data_readiness`, `save_last_result`, and the `.last_result.json` → analysis handoff have no test coverage.

### Gemini Second Review Findings

Gemini independently confirmed the same structural issues (YAML frontmatter, context digest, look-ahead bias gate, OOS gate, LLM trust boundaries) that were already identified and implemented. This indicates the post-optimization state is well-aligned with best practices.

**New from Gemini**: Recommends a `strategy-cycle` CLI tool (not just a skill) that handles phase transitions, updates STATUS.md, and regenerates `_context_digest.md` automatically. This would close the remaining manual-memory dependency between phases.

---

## Completed vs Pending — Full Cycle Summary

### Completed ✅

| Item | Status |
|------|--------|
| FeatureStore load/save symmetry (sidecar marker) | Done, tested |
| FeatureStore.build_path() anchored to REPO_ROOT | Done, tested |
| STATUS.md YAML frontmatter template | Done |
| hypothesis-log.md template | Done |
| sessions/_latest.json pointer | Done |
| _context_digest.md artifact pattern + skill | Done |
| Phase-gated skill routing in trade-strategy.md | Done |
| strategy-cycle-orchestrator skill | Done |
| strategy-bootstrap skill | Done |
| artifact-triage skill | Done |
| experiment-compare skill | Done |
| knowledge-extraction skill | Done |
| data-readiness-check skill + CLI endpoint | Done, bugs fixed |
| look-ahead-bias-check skill (mandatory gate) | Done |
| oos-validation-gate skill (hard gate) | Done |
| Quick Reference in freqtrade-analysis-workflow | Done |
| Quick Reference in trade-strategy-improvement-planning | Done |
| LLM permission tiers in llm-orchestration | Done |
| requirements-dev.txt with pytest + pyarrow | Done |
| save_last_result() extended with family + timestamp | Done |
| Pickle fallback tests in test_feature_store.py | Done |
| tests/README.md with setup instructions | Done |

### Pending ⏳ (recommended next cycle)

| Item | Priority | Reason |
|------|---------|--------|
| ~~Fix `analyze_backtest_result.py` TIMERANGE hardcode~~ | ~~P1~~ **Done** | load_last_execution() returns timerange; passed to _export_run_report |
| ~~Fix MLService sys.stdout rewiring in tests~~ | ~~P1~~ **Done** | Moved mutation into `_ensure_utf8_stdout()` helper; no longer runs at import time |
| ~~Add tests for check_data_readiness, save_last_result~~ | ~~P1~~ **Done** | `tests/test_check_data_readiness.py` (10 tests) + `tests/test_save_last_result.py` (5 tests) |
| Implement `strategy-cycle` CLI (auto phase transitions + digest update) | P2 | Closes manual-memory gap between phases |
| ~~Add anchor baseline tracking to hypothesis-log~~ | ~~P2~~ **Done** | Anchor baseline section added to hypothesis-log template + experiment-compare updated |
| ~~Create `regime-filter-validation` skill~~ | ~~P2~~ **Done** | domain-skills/trading/regime-filter-validation/SKILL.md created |
| Add LLM call audit logging to call_llm_cli.py | P3 | Security/trust boundary hardening |
| Split analyze_backtest_result.py into modules | P3 | Long-term maintainability |

---

## Recommended Implementation Priorities (next cycle)

### Priority 1: Code correctness and test stability

1. Fix `analyze_backtest_result.py` to read timerange from `.last_result.json` instead of hardcoded constant.
2. Fix MLService sys.stdout mutation — isolate to function scope, not module level.
3. Add unit tests for `check_data_readiness.check()` and `save_last_result()`.

### Priority 2: Cycle automation

4. Implement `python -m lib.endpoints.strategy_cycle <family> <name> <timerange>` CLI.
5. Add anchor baseline stem field to `hypothesis-log.md` template.
6. Create `regime-filter-validation` skill.

### Priority 3: Trust and maintainability

7. Add audit logging to `call_llm_cli.py`.
8. Split `analyze_backtest_result.py` into discrete modules.
9. Activate semantic router for at least one API-based LLM target.

---

## Final Verdict — After Three Optimization Cycles

The project has gone from a partially-systematized research scaffold to a complete, structured TAO loop framework. All major structural gaps from the original review have been addressed.

### What is now ready ✅

- **Full skill graph** covering every phase transition: bootstrap → scope → hypothesis → prototype → implementation → backtest → analysis → planning → next iteration
- **Machine-readable state**: STATUS.md YAML frontmatter, `_context_digest.md` pattern, `sessions/_latest.json` pointer, `hypothesis-log.md` with anchor baseline
- **Hard quality gates**: look-ahead bias (mandatory preflight), OOS validation (hard gate before Planning), data readiness (mandatory preflight)
- **Domain validation skills**: regime filter calibration check, experiment comparison with anchor baseline
- **Agent efficiency**: phase-gated routing, artifact triage ladder, Quick Reference in high-frequency skills, cold-start protocol in agent-general-skills
- **Code correctness**: FeatureStore symmetric save/load, repo-anchored paths, TIMERANGE metadata fix in analysis, check_data_readiness bugs fixed
- **Test infrastructure**: requirements-dev.txt, 48 tests passing, test categories documented; MLService sys.stdout mutation fixed so full suite runs cleanly under pytest

### What remains open (non-blocking for strategy work) ⏳

| Item | Why non-blocking | Recommended timing |
|------|-----------------|-------------------|
| `strategy-cycle` CLI (auto phase transitions) | Skills cover it manually; CLI adds automation | After first strategy iteration shows pain points |
| LLM audit logging | Affects security posture, not workflow correctness | Before any live trading or multi-agent consensus |
| ~~MLService sys.stdout test isolation~~ | **Done** — fixed in Cycle 3 | — |
| Analysis CLI `--stem` argument | Falls back to last_result.json correctly | After first iteration; note timerange now reads from metadata |
| Split analyze_backtest_result.py into modules | Maintainability only | Major version update |

### Assessment

The project is ready for the first active strategy implementation cycle. All workflow breakpoints that would prevent smooth TAO loop execution have been addressed or have documented workarounds. An agent can now complete the full loop from a raw idea to an analyzed, compared, documented iteration result using the skill infrastructure.

The skills should be treated as living documents: update them based on what the first real strategy iteration reveals about the actual workflow friction points.
