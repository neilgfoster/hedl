# Phase 0 Complete — Setup → Discipline restoration

Retrospective and adversarial phase-boundary review for the Phase 0 → Phase 1
transition, performed via `/phase-complete` under WORK-0017.

**Log:** phase-0-complete-2026-05-28
**Session:** in-session
**Depth:** Full
**Commit:** df3623e

Duration: 2026-05-28 → 2026-05-28 (Phase 0 authored and closed retroactively).

## Dimension Scores

| Dimension | Reviewer | Verdict |
|---|---|---|
| Scope (work exceeding the item) | scope-auditor | FAIL pre-transition → resolved |
| History / ADR & principle consistency | historian | FAIL pre-transition → resolved |
| Existential (ADR-013 cull cycle) | existential-challenger | CONDITIONAL |

The two FAIL verdicts were dominated by findings that the transition state
(context.json flags, transition_log, CLAUDE.md current phase) had not yet been
written — expected, because the panel reviewed the proposed phase files *before*
the transition edits. Those are now written (see Next Actions for what was and
was not actioned). The genuine, non-mechanical findings are recorded below.

## Strengths

- The Phase-1 diagnosis is correct: the real waste (security RCE surface,
  ADR-vs-code divergences, count drift, `budget_manager`) is already captured in
  the backlog and in `docs/alternatives.md`.
- Phase-0 DoD criteria are all verifiable now and were honestly scoped (the gate
  criterion explicitly annotates that CI execution was broken throughout Phase 0).
- The phase definitions map cleanly to the recorded backlog bands.

## Blocking Findings

None that survive the transition. The pre-transition BLOCKINGs were:

- (historian, scope-auditor) context.json `phase_0_complete`/`_edit_me`,
  empty `transition_log`, stale CLAUDE.md current phase — all were the
  transition steps themselves. Now written.
- (historian) Phase-0 DoD over-claiming a working gate. Resolved: the gate DoD
  criterion now states it ran locally and notes the CI break repaired in Phase 1
  via WORK-0030.

## Significant Findings

- (existential-challenger) **ADR-013 is not wired into `/phase-complete`.**
  `skill/hedl/commands/phase-complete.md` names a phase panel of scope-auditor,
  historian, evidence-checker, assumption-challenger — not existential-challenger,
  which ADR-013 makes mandatory. This cycle ran existential-challenger only because
  the operator/loop invoked it by hand. Recorded for WORK-0005 (see Next Actions).
- (existential-challenger, scope-auditor) **Phase-1 carried a self-contradiction:**
  its no-new-capability constraint conflicted with the backlog's WORK-0011 / 0032 /
  0033 (net-new features promoted to Phase 1 in commit #19). Resolved in this item:
  phase-1.json constraint #1 now carves an explicit, documented exception for the
  ADR-022 github-issues backend and ADR-020 workstream templates, rather than
  silently overriding the operator's recent promotion.
- (scope-auditor) WORK-0032/0033 depend on WORK-0007, which carries
  `priority_band: DEFERRED`. Phase-1 DoD line 5 already permits "closed or
  explicitly reclassified", so the dependency chain is accommodated, but the
  band/phase mismatch in work.json should be groomed (Next Actions).

## Minor Findings

- (existential-challenger) `scope-auditor` is `always_required` yet returned
  0/0/0 in the only real review run on record (repo-health-2026-05-28). One
  zero-finding self-review is weak justification for a per-dispatch tax; the
  alternatives.md measurement window already covers this.
- (existential-challenger) WORK-0018's headline LOC ratio (4650 process / 4145
  code) has already inverted (~3316 process / ~7467 code today). The discipline
  phase is justified by the RCE surface and ADR divergences, not the ratio; the
  WORK-0018 criterion risks being trivially true and should tie to the concrete
  reconciliations.
- (existential-challenger) `budget_manager.py` (531 lines) remains off the active
  path and causes WORK-0002. Confirmed cull/shrink candidate; already watchlisted
  in alternatives.md and cross-linked from WORK-0002.
- (historian, scope-auditor) Phase-0 learning goal about ADR-019 reframed to
  implementation feasibility (ADR-019 is already Accepted).

## Next Actions

- **Actioned in WORK-0017:** phase-0.json / phase-1.json authored; transition_log,
  context.json flags, CLAUDE.md updated; phase-1 constraint exception documented;
  CI-gate and ADR-019 wording corrected.
- **Recorded for WORK-0005:** extend it to wire existential-challenger into
  `skill/hedl/commands/phase-complete.md`'s phase panel, not only dispatch-rules —
  so ADR-013's mandatory cycle is enforced, not hand-invoked.
- **Backlog grooming (operator):** reconcile WORK-0007's `DEFERRED` band with its
  Phase-1 placement and its `normal`-band dependents WORK-0032/0033.
- **WORK-0018 (operator):** re-baseline its acceptance metric from the LOC ratio
  (already inverted) to the concrete reconciliation items it tracks.
- **Confirm before Phase-1 close:** required status checks actually enforced on
  main (do not repeat Phase 0's "green locally, never ran in CI" pattern).

## What we built (Phase 0 — Setup)

The framework was seeded and bootstrapped to a self-hosting state, pre-tracker:
the deterministic completion gate (`am_i_done.py`), the installable skill across
three tiers (gate / lightweight / team), the core slash commands, the adversarial
review system (named agents + composable library + dispatch rules), the ADR
governance foundation, and the `.work/` work-tracking machinery. No work items
were tracked during Phase 0 — it predates the tracker, which is why phase-0.json
was the EDIT-ME stub until this item authored it retroactively.

## Definition of Done — final status

All seven Phase-0 DoD criteria VERIFIED (2026-05-28):

1. Gate exists, runs locally, exits 0 — `am_i_done.py` green on this branch.
2. Skill installs across tiers gate / lightweight / team — `tiers.json` confirms.
3. Core slash commands present in `.claude/commands/` and routed from SKILL.md.
4. Adversarial review system: 7 named agents + review-library + dispatch-rules.
5. ADR foundation recorded: 23 ADRs in `.work/decisions/`.
6. Work-tracking machinery present: work.json, context.json, phases/.
7. `am_i_done.py` passes.

## Learning goals — what we learned

- *Can a deterministic gate + adversarial review ship as one tiered, installable
  skill?* Yes — the skill self-hosts. But "installable" hid a real defect:
  GitHub-parsed `.github` files were symlinked, so the CI gate never ran during
  Phase 0 (WORK-0030).
- *Does dogfooding surface contradictions the design missed?* Strongly yes — the
  entire Phase-1 backlog is contradictions dogfooding surfaced (ADR-vs-code
  divergence, RCE surface, count drift, this very phase machinery being uninitialised).
- *Did process stay proportionate to shipped capability?* No — this assumption was
  invalidated. Goal-displacement (process > product) is precisely why Phase 1 is
  discipline-restoration.

## What surprised us

The phase machinery itself was never initialised: phases.json said Phase 0,
work.json said Phase 1, phase-0.json was the template stub, and phase-1.json did
not exist. The framework that enforces phase discipline had not applied it to
itself.

## What we'd do differently

Initialise the phase definition at seed time, not retroactively. Run the gate in
CI from the first PR (the symlink defect would have been caught immediately).
Treat "one shipped capability per workstream" as the unit of progress from day one,
rather than accumulating process artefacts ahead of product.

## Release bump

Deterministic calc (`release.py --phase 0`) returns `bump: patch` but `groups: {}`
— no completed work items are attributable to Phase 0. No version change applied.
(`context.json` `project_version` is `0.0.0` while CHANGELOG records `v0.1.0`; that
versioning inconsistency predates this item and is out of scope here.)

## Direction changes made during this phase

None recorded in `phases.json` direction_changes.

## Impact on next phase

Phase 1's DoD and constraints already encode the learnings above: lead with the
gate, require regression tests on every security fix, reconcile ADRs to code (or
supersede explicitly), and run a real existential cycle at the Phase-1 boundary.
This report is the first real review run produced inside Phase 1 — partial
evidence toward WORK-0018's closure criterion.
