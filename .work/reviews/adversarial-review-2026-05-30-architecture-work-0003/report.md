# Adversarial Review — WORK-0003 (architecture)

**Log:** adversarial-review-2026-05-30-architecture-work-0003
**Session:** in-session
**Depth:** Standard (docs-only; light panel)
**Commit:** 92ead87..f04e0c5

Panel: [scope-auditor](scope-auditor.md), [edge-case-hunter](edge-case-hunter.md).
Panel selected by review-dispatcher (docs-only diff); validated via
`am_i_done.py --check dispatch`. Scope: docs/versioning.md correction to match code.
Verdict: **PASS** (one accuracy fix applied; the change_class bookkeeping folded
into the completion transition).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Code-vs-doc accuracy | PASS after fix — phantom `[hedl] schema_version` removed; schema 1→2; migration row corrected |
| Scope containment | PASS — the schema-number + migration-row edits are required by AC1 ("matches code exactly"), not creep |

## Strengths

- Corrects a real external-review finding (a documented read path that no code
  implements) by making the doc match the verified code.

## Blocking Findings

- **scope-auditor — `change_class` still `fix`; AC3 requires `docs` once the doc
  path is chosen.** Resolved: set to `docs` in the completion transition (the
  standards.md fold-into-delivering-PR step), with the resolution recorded.

## Significant Findings

- **edge-case-hunter — the added 1→2 migration row said "Relocates".** Inaccurate:
  `install.py` only writes `hedl.toml` when `state_backend` was non-default, and
  always drops the key from `context.json`. Fixed (row reworded + a note that one
  `--migrate` applies all pending steps).

## Minor Findings

Pre-existing `--doctor` status-table nuances, out of WORK-0003 scope (a different
section; not the schema_version/hedl.toml defect) — recorded, not fixed:
`not-installed` is emitted as prose not a bracketed token; `not-installed` is
triggered by an absent `context.json` regardless of tier (doc says "gate-only");
non-integer `schema_version` strings silently read as unversioned. Candidates for
a future versioning.md / `--doctor` pass.

## Next Actions

PASS → operator handoff. The "Relocates" accuracy fix is applied; the
`change_class` → `docs` update is in the completion transition. No fix cycle
outstanding.
