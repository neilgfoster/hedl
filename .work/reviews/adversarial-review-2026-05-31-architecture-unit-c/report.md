# Adversarial Review — architecture (Unit C backlog reconciliation)

**Log:** adversarial-review-2026-05-31-architecture-unit-c
**Session:** in-session
**Depth:** Standard (scope-auditor + historian; the strategic challenge was absorbed by ADR-036's panel, which this reconciliation implements)
**Commit:** d1c789a (working tree, branch chore/phase-2-backlog-reconciliation)

Panel: [scope-auditor](scope-auditor.md), [historian](historian.md).

Scope: `.work/work.json` reconciliation per ADR-036 (DIRECTION-2) + ADR-035.

Verdict: **CONDITIONAL → PASS after one revision cycle.** Both agents partly
mis-read ADR-036/035 as "non-existent" — they reviewed `main`, where the Unit B/D
ADRs are not yet merged (they live on sibling branches, PRs #77/#78). The genuine
findings were fixed; the false ones rebutted.

## Dimension Scores

| Dimension | Verdict |
|---|---|
| ADR numbering integrity (both, via the false-positive path) | PASS after fix — Unit B renumbered 034->036 because ADR-013 records a rejected "standalone ADR-034" |
| Instruction fidelity (scope-auditor) | PASS after fix — PILLAR band reverted to "high" (operator said "to high"); pillars marked by ordering + note |
| Phase discipline (historian) | PASS after fix — WORK-0075 rescoped so completion no longer depends on an external adopter event |
| Decision consistency (historian) | PASS — WORK-0010/0011 deferral matches the recorded 2026-05-30 /phase-complete "defer, not cull" decision |
| Scope containment (scope-auditor) | PASS with recorded judgement — 3 items minted to make operator-named pillars top items |

## Strengths

- Faithful, deterministic implementation of ADR-036's recorded dispositions.
- Honest contingency labelling (every change tagged "Contingent on ADR-036 ratification").
- No item dropped; no field clobbered; no orphan supersede fabricated.

## Blocking Findings

None upheld. The two "ADR-034/035 do not exist" BLOCKINGs were false positives
(sibling-branch visibility), BUT they surfaced a real adjacent issue — the ADR-034
*number* collides with a rejected concept recorded in ADR-013. Resolved by
renumbering Unit B to **ADR-036** (Unit D stays ADR-035 — no collision there).

## Significant Findings

- **PILLAR band deviates from "promote to high" and is undocumented** (scope-auditor)
  — FIXED: reverted to "high"; the five pillars are marked by being ordered first +
  named in the reconciliation_note.
- **Minting 3 work items exceeds "reorder"** (scope-auditor) — RETAINED with
  recorded judgement: the operator named five pillars as the top-five items; three
  had no item, so they were minted (clearly tagged "Minted by Unit C", contingent).
  Defensible under the AFK delegated-authority instruction; flagged here for the
  operator to veto at merge.
- **WORK-0075 phase-discipline violation** (historian) — FIXED: rescoped so the
  in-phase deliverable is the doc graduation; the external-adopter "proven" claim
  is a documented gate, not a completion criterion.
- **WORK-0050 demotion vs distribution pillar** (historian) — RETAINED: the
  operator's plan placed WORK-0050 in the framework-feature direction; the note
  honestly records it is distribution-adjacent but not the gate itself.

## Minor Findings

- **WORK-0035 reframed though not in the explicit reframe-list** (scope-auditor) —
  RETAINED: the operator's plan named WORK-0035 a DIRECTION-1 framework-feature
  item; the adjacent note is faithful to that framing.
- Commit-type "chore" undersells item-minting (scope-auditor) — noted; the PR body
  itemizes the minting and band changes explicitly.

## Synthesis

The reconciliation is sound and faithful to ADR-036. The panel's most valuable
catch came through a false premise: the ADR-034 number collision with ADR-013's
rejected substrate-trigger, fixed by renumbering Unit B to ADR-036. The WORK-0075
phase-discipline fix and the PILLAR->high reversion tighten instruction fidelity.
The minting of three pillar items is recorded as a judgement call for operator veto.
All changes are contingent on ADR-036 ratification (no auto-merge).

## Next Actions

PASS → commit + PR; await operator ratification of ADR-036/035 then this. If
DIRECTION-1 is chosen, revert.
