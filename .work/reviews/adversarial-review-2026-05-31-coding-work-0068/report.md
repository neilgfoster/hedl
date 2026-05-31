# Adversarial Review — coding (WORK-0068 gate-tier CI install fix)

**Log:** adversarial-review-2026-05-31-coding-work-0068
**Session:** in-session
**Depth:** Standard (security-auditor + edge-case-hunter; supply-chain-relevant CI change)
**Commit:** 022bdc6 (working tree, branch fix/gate-tier-ci-install)

Panel: [security-auditor](security-auditor.md), [edge-case-hunter](edge-case-hunter.md).

Scope: `skill/hedl/workflows/am-i-done.yml` (shipped gate-tier template) +
`skill/hedl/tests/test_install.py` (new guard). Fix: swap setup-uv +
`uv sync --frozen` → `actions/setup-python@v6.2.0` + `pip install -r requirements-ci.txt`,
since the gate tier projects `requirements-ci.txt` but not `pyproject.toml`/`uv.lock`.

Verdict: **PASS** (1 supply-chain hardening applied; remaining findings rebutted as
pre-existing/out-of-scope or not-a-regression).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Supply-chain (security-auditor) | PASS after fix — `--require-hashes` added (verified installs clean); new action SHA-pinned per repo convention |
| Workflow correctness (edge-case-hunter) | PASS — install resolves from the projected manifest; python3-vs-python is not a regression |
| Scope | PASS — checkout-SHA drift + drift-guard left to WORK-0062 (surgical) |

## Strengths

- Fixes a verified adopter-blocking bug (fresh gate-tier CI failed before the gate ran).
- Adds a regression guard asserting the shipped workflow installs only from projected files.

## Blocking Findings

None.

## Significant Findings

- **Add `--require-hashes`** (security-auditor, edge-case-hunter) — requirements-ci.txt
  is a fully hash-pinned uv-export closure. APPLIED and verified: `pip install
  --require-hashes -r requirements-ci.txt` installs clean (exit 0) in a throwaway venv.
- **Checkout SHA divergence** shipped v5.0.1 vs Hedl-live v6.0.2 (security-auditor) —
  REBUTTED as out-of-scope: pre-existing drift owned by **WORK-0062** (sync shipped
  templates + CI guard). Surgical-change principle: not touched here.
- **`python3` hardcoded** in check_budget/check_template vs the setup-python `python`
  (edge-case-hunter) — REBUTTED as not-a-regression: under both `uv run` (before) and
  setup-python (after), a `python3` subprocess resolves to the active, package-bearing
  interpreter (setup-python puts both `python`/`python3` first on PATH). Orthogonal
  pre-existing pattern.
- **Python 3.14 may be absent from setup-python** (edge-case-hunter) — REBUTTED:
  reasoning was from stale mid-2025 data; 3.14 is GA, Hedl's own CI already targets the
  3.14 matrix, and setup-python v6.2.0 (latest) supports it.

## Minor Findings

- **Test only scanned `run:` lines** (edge-case-hunter) — FIXED: the guard now scans
  all non-comment, non-blank lines (covers multi-line run blocks; excludes the
  intentional uv-mentioning comment).
- **requirements-ci.txt drift not CI-enforced** (both) — out-of-scope, **WORK-0062**.
- **check_pr_template ImportError masking** (edge-case-hunter) — pre-existing/orthogonal;
  check_pr_template is stdlib-only.

## Synthesis

The fix is correct and minimal. The one genuinely actionable hardening
(`--require-hashes`) was applied after local verification. The remaining findings are
either pre-existing drift already owned by WORK-0062, or not regressions introduced by
this change. The new test guards the exact failure mode (install referencing
unprojected artifacts).

## Next Actions

PASS → commit + PR (no auto-merge). The work.json `WORK-0068` status transition is
deferred to after #79 (Unit C) merges, to avoid a work.json conflict with the in-flight
reconciliation that re-bands WORK-0068.
