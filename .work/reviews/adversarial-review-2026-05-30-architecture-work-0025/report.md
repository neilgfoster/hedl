# Adversarial Review — WORK-0025 (architecture)

**Log:** adversarial-review-2026-05-30-architecture-work-0025
**Session:** in-session
**Depth:** Standard (2 cycles + Copilot thread)
**Commit:** dba822f..883a12d

Panel: [security-auditor](security-auditor.md), [determinism-auditor](determinism-auditor.md),
[scope-auditor](scope-auditor.md), [edge-case-hunter](edge-case-hunter.md).
Panel selected by review-dispatcher from the diff; validated via
`am_i_done.py --check dispatch`. Scope: the `state-sync` gate check in
am_i_done.py, its tests, the AC4 install test, getting-started.md, and the
WORK-0025 AC reconciliation.
Verdict: **PASS** (after one fix cycle; residual MINORs closed; one Copilot
thread fixed).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Security | PASS after fixes — crash-safe reads, realpath containment, size cap; errno-only error text (no path leak) |
| Determinism | PASS — pure function of filesystem state; ordered tuple; binary compare (cycle-1 empty finding) |
| Scope containment | PASS after fixes — AC2 reframe recorded on the work item; AC4 test added |
| Correctness / edge cases | PASS after fixes — dir/broken-symlink/oversized/unreadable/missing-tree all FAIL cleanly |

## Strengths

- Deterministic byte-compare, framework-repo-scoped so adopters are never nagged.
- Reframe of the work item (template-vs-projection, not duplication) is recorded
  explicitly rather than applied silently.
- Hardened reads bring the new gate code above the adjacent check_config bar.

## Blocking Findings

Two raised in cycle 1, both fixed in cycle 2:

- **edge-case-hunter — unhandled OSError on read crashes the gate.** Fixed:
  reads are isfile-guarded, size-capped, and OSError-wrapped, each FAILing
  cleanly (gate no-traceback discipline).
- **scope-auditor — AC4 unmet** (tests covered drift, not "fresh install
  reproduces .work/ from the template"). Fixed: reproduction test added in
  test_install.py.

## Significant Findings

All raised in cycle 1, resolved in cycle 2:

- **edge-case-hunter / security — silent false-green if the template tree goes
  missing.** Fixed: framework repo detected via skill/hedl/ at root; a missing
  tree FAILs rather than skipping.
- **edge-case-hunter — directory-at-path / broken-symlink crash.** Fixed by the
  isfile guard.
- **scope-auditor — AC2 reframe only in the commit message.** Fixed: AC2 text
  reconciled in work.json with a recorded `reframe` field.
- **security — realpath containment / unbounded read.** Resolved: size cap +
  isfile in cycle 2; realpath containment added when closing residual MINORs.

## Minor Findings

Closed after the cycle-2 PASS:

- realpath-containment residual + REPO_ROOT-not-canonical → local realpath of
  both roots + containment check in `_read`.
- empty `_STATE_SYNC_GUARDED` vacuous PASS → explicit FAIL.
- brittle global `open` patch in the unreadable test → path-scoped.
- **Copilot reviewer (PR #62 thread):** `unreadable` message used `str(exc)`,
  embedding the absolute path → changed to errno/strerror only. Resolved.

Recorded follow-up (out of scope): unify realpath-contained reads across
`check_config` and `check_state_template_sync` as a shared helper.

## Next Actions

PASS → operator handoff. All BLOCKING/SIGNIFICANT resolved; MINORs and the
Copilot thread closed. No fix cycle outstanding.
