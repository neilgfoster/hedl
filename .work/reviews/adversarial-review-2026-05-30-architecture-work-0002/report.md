# Adversarial Review — WORK-0002 (architecture)

**Log:** adversarial-review-2026-05-30-architecture-work-0002
**Session:** in-session
**Depth:** Standard (4-agent panel; gate-adjacent script)
**Commit:** 5889812..480a8ac

Panel: [security-auditor](security-auditor.md), [determinism-auditor](determinism-auditor.md),
[scope-auditor](scope-auditor.md), [edge-case-hunter](edge-case-hunter.md).
Panel selected by review-dispatcher (which had wrongly skipped determinism —
re-added per the mandatory floor for skill/hedl/scripts/); validated via
`am_i_done.py --check dispatch`. Scope: the gate-only guard in budget_manager.py.
Verdict: **PASS** (CONDITIONAL on first pass; in-scope findings fixed, the rest
rebutted or noted as pre-existing).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Security | PASS — read-only guard; TOCTOU on a concurrent .work delete is out of scope for a single-operator local CLI |
| Determinism | PASS — empty finding set; reads (tier/status) unaffected, guard is a pure fs check |
| Scope containment | PASS — touches budget_manager.py + its test; AC2 reconciled |
| Edge cases | PASS after fix — guard covers all five mutating commands, asserted by test |

## Strengths

- Fixes the reported tier-contract violation cleanly at the single CLI entry point.
- `_MUTATING_COMMANDS` is now a module constant the test pins, so a future writer
  not added to the guard is caught.

## Blocking Findings

None.

## Significant Findings

- **TOCTOU / "guard is in main(), helpers still mkdir"** (security, edge-case) —
  REBUTTED for this tool: the race requires deleting `.work/` mid-command on a
  single-operator local CLI; hardening the helpers would break their
  relied-upon auto-create contract (existing tests + first lightweight+ write)
  and require reworking them. Closed the real sub-concern (a new writer bypassing
  the guard) via the module constant + full-set test coverage instead.
- **Misleading exit 0 / stdout** (security, edge-case) — fixed: no-op message
  moved to stderr; exit 0 means "not applicable in this tier", not failure.
- **AC2 not via `install --tier gate`** (scope, edge-case) — reconciled: the unit
  test exercises the exact gate-only condition (no `.work/`, which is what a gate
  install produces) across all five mutating commands — stronger than one
  install-path check. AC2 wording reconciled on the work item with a reframe.
- **branch named fix/0009-principle-4** (scope) — REBUTTED: stale review context;
  the branch is `fix/0002-budget-gate-only`.
- **`_load_queue` triggers mkdir** (edge-case) — REBUTTED: reads go through
  `_read_or_default`, which does not mkdir.

## Minor Findings

Pre-existing, not introduced here (recorded as possible follow-ups, not fixed):
`REPO_ROOT` env-var derivation (GIT_DIR/GIT_WORK_TREE), and input-validation gaps
on `record-panel` (no `_AGENT_RE`), `record` (n<=0), `drain` (n>len), and an
unlocked read in `suggest-rotation`. `.work` existing as a file (not dir) → silent
no-op: accepted as a far-fetched edge.

## Next Actions

PASS → operator handoff. No fix cycle outstanding. Pre-existing budget_manager
input-validation MINORs could be a future hardening item.
