# Adversarial Review — architecture (WORK-0076 .work/ cross-harness layer)

**Log:** adversarial-review-2026-05-31-architecture-work-0076
**Session:** in-session
**Depth:** Standard (edge-case-hunter + scope-auditor + historian)
**Commit:** feat/work-state-cross-harness @ pre-commit working tree

Panel: [edge-case-hunter](edge-case-hunter.md), [scope-auditor](scope-auditor.md),
[historian](historian.md).

Scope: a `backends.md` section framing `.work/` as the cross-harness work-item
layer + `TestGateOnlyNoWorkDir` + a no-lock-in guard on `_append_gate_insight`.

Verdict: **CONDITIONAL → PASS after fixes.** The panel found the no-lock-in claim
overstated/incomplete and a misattribution; all fixed (including one real code
guard).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| No-lock-in claim accuracy (edge-case-hunter) | PASS after fix — claim scoped to the default run; insight no-op guard added; schemas check added |
| Scope/accretion (scope-auditor) | PASS — extends backends.md (no new doc); documents real behaviour; no unbuilt-harness claims |
| Cross-ADR accuracy (historian) | PASS after fix — ADR-036 framing quoted accurately; capability vs deployed-breadth separated |

## Strengths

- Documents real, verifiable behaviour and traces the gate's work-item-awareness
  to concrete checks; no new doc surface.
- The fix turned a documentation claim into an enforced invariant (the gate no
  longer creates `.work/` in a gate-only repo even with insights enabled).

## Blocking Findings

- **`check_dispatch` FAILs (not skips) without `.work/`** (edge-case-hunter) — true
  only via `--check dispatch` / `--panel`; it is NOT in the gate-only default run.
  The blanket "every `.work/`-reading check skips" was overstated. RESOLVED: the
  doc now scopes the claim to the default run and names `check_dispatch` as the
  opt-in (panel/team-tier) exception.

## Significant Findings

- **`_append_gate_insight` creates `.work/insights/` if `[insights] enabled`**
  (edge-case-hunter) — violated "zero `.work/` impact." RESOLVED with a real guard:
  it no-ops when `.work/` is absent (cf. WORK-0002 budget no-op); tested.
- **`check_markdown_schemas` omitted from the list/test** (edge-case-hunter) — it
  does skip (absent `_SCHEMAS_FILE`), but was undocumented/untested. RESOLVED: added
  to the doc list and tested (mocking the frozen `_SCHEMAS_FILE` constant).
- **Misattribution to ADR-036** (historian) — ADR-036 calls `.work/` "the substrate
  that makes the gate work-item-aware," reserving "harness-agnostic" for the
  gate/roadmap. RESOLVED: doc now quotes ADR-036 accurately and frames the
  stdlib-readable/cross-harness property as a *capability* (with WORK-0047 the
  unbuilt projection work), not shipped multi-harness support.
- **Test weaker than the doc implied** (edge-case-hunter) — RESOLVED: test expanded
  to schemas-skip + insight-no-op.

## Minor Findings

- **`check_commands` redundant guard / TOCTOU** (edge-case-hunter) — pre-existing,
  out of scope for WORK-0076; not touched.
- **Naming Copilot/OpenCode/Cursor could imply deployed breadth** (scope-auditor) —
  RESOLVED by the capability-not-deployed rewording.

## Synthesis

The doc was right in spirit but loose: the no-lock-in claim needed scoping (default
run vs the panel-only `check_dispatch`), one genuine code gap closed
(`_append_gate_insight` creating `.work/`), the schemas check added, and the
ADR-036 attribution made precise. After fixes the claim is accurate and enforced.

## Next Actions

PASS → fold the WORK-0076 active→completed transition into the delivering PR; raise;
await operator merge. No auto-merge.
