# Phase-1 Existential Review — Discipline restoration

**Log:** phase-1-complete-2026-05-30
**Session:** in-session
**Depth:** Full (phase-boundary; 5-agent panel)
**Commit:** caa800e (main HEAD at review time)

Panel: [existential-challenger](existential-challenger.md) (mandatory, ADR-013),
[scope-auditor](scope-auditor.md), [historian](historian.md),
[evidence-checker](evidence-checker.md), [assumption-challenger](assumption-challenger.md).
This is the ADR-013 phase-boundary cycle required by DoD #6.

## Verdict

**CONDITIONAL — Phase 1 is NOT complete; transition BLOCKED until the boundary
actions below are done.** The discipline-restoration *goal is substantively met*
for the items in scope (BLOCKING + security + GOVERNANCE reconciliation all
landed; the gate is green on main with the four required matrix contexts enforced;
the validation loop now closes with ~11 real review runs produced inside Phase 1).
But four DoD criteria are unmet and several boundary decisions are unresolved.

## Dimension Scores

| Dimension | Verdict |
|---|---|
| DoD #2 security RCE fixes + regression tests | VERIFIED |
| DoD #3 GOVERNANCE closed, one source of truth | VERIFIED (zero GOVERNANCE items in backlog) |
| DoD #7 am_i_done passes | VERIFIED (12 substantive checks green, 413 tests; git/branch FAIL only because HEAD was on main) |
| DoD #1 BLOCKING closed + gate green w/ required checks | FAILED — WORK-0018 (BLOCKING tracker) still open (gated on #4) |
| DoD #4 WORK-0018 closed + repo-health re-run shows findings resolved | FAILED — no repo-health re-run since 2026-05-28 (the run that *raised* the findings) |
| DoD #5 every remaining item closed or reclassified-with-rationale | FAILED — 7 non-tracker items still phase:1/backlog, unreclassified |
| DoD #6 phase existential cycle recorded | IN PROGRESS — this document satisfies it once committed |

## Strengths

- Genuine restoration: the gate now runs in CI (WORK-0030 — it never had), RCE
  surface fixed with fail-before tests, ADR-vs-code divergences reconciled to one
  source of truth, README repositioned per ADR-011. Process-to-code ratio flipped
  (Python now ~2.9x process text).
- The validation loop is real: ~11 adversarial review runs produced inside Phase 1,
  each persisted under .work/reviews/ — the validation-theatre finding is resolved.

## Blocking Findings

- **DoD #5 — 7 open items unreclassified** (scope-auditor, evidence-checker,
  assumption-challenger): WORK-0032/0033/0011/0010/0015/0001/0035 are all phase:1
  status:backlog. Each must be closed OR reclassified to a later phase with recorded
  rationale before transition. WORK-0018's AC1 ("every other item closed first")
  also blocks until this is resolved.
- **DoD #4 — no repo-health re-run** (evidence-checker, existential-challenger):
  .work/reviews/ holds only repo-health-2026-05-28 (the run that *found* the
  goal-displacement / validation-theatre findings). There is no re-run showing them
  *resolved*. WORK-0018 cannot close without it.
- **DoD #6 — phase existential cycle** (evidence-checker): satisfied by committing
  this artifact.
- **Watchlist verdicts not recorded** (existential-challenger): alternatives.md set
  ~8 falsifiable objectives "measuring at the Phase-1 boundary" (review-panel signal,
  routing-table shrink, self-improvement PR, ADR discipline, multi-operator,
  PR-template, hooks, workstream-templates). None has a recorded verdict. The
  watchlist exists to force boundary decisions; leaving them unforced is itself the
  validation-theatre pattern.

## Significant Findings

- **Cull candidates carried, not cut** (existential-challenger): the recursive
  cluster (WORK-0010, WORK-0011, ADR-031) is gated on a model that ADR-019's
  supersession + the 2026-05-29 dogfood (benefit only above ~5-7 concurrent
  workstreams, never hit) say is unbuilt and demand-gated; budget_manager is an
  explicit alternatives.md culling-candidate whose evidence window (a rescued
  deferral case) closed with no case shown. The boundary should decide cull-vs-defer
  for each, not silently carry them.
- **WORK-0035 out of scope** (scope-auditor, existential-challenger): the external
  review kit is net-new forward-capability not in the sanctioned exception set
  (github-issues backend + workstream templates); reclassify to Phase 2.
- **LG2 + LG3 unanswered** (assumption-challenger): learning goals about the
  recursive model (WORK-0010) and the github-issues dogfood (WORK-0032/0033) cannot
  be answered — that work was deferred. The retro must record them UNANSWERED (not
  N/A), inherited by Phase 2. LG1 (lead-with-gate readability) was answered with
  evidence (WORK-0014 + the new-engineer review), qualified as a Claude proxy.
- **Assumption 1 partial** (assumption-challenger): "surplus process retired or
  justified without losing discipline" — discipline preserved (gate green), but
  surplus was largely *justified/carried*, not *retired* (budget_manager + recursive
  cluster uncut; the Lume bootstrap accreted 5 new ADR-class items). Record as
  partially validated.
- **Named forward-capability exceptions slipped** (assumption-challenger): the two
  items the phase named as proof that "a workstream ends in capability" — the
  github-issues backend (WORK-0032/0033) and workstream templates (WORK-0011) — did
  not ship. Re-anchor the claim on what did ship (RCE fixes, /pr-ready, /iterate-to-PR).

## Minor Findings

- **historian**: WORK-0010's description still opens "Per ADR-019" though ADR-019 is
  superseded; standards.md heading "Work item workstreams" mixes old/new terms —
  both safely deferred to WORK-0015's terminology sweep.
- **Assumption 2** (reconcile ADRs to implementation): validated for most governance
  items; WORK-0027 is the counter-instance (superseded ADR-019 rather than
  implementing it) — in-policy (supersede-via-historian), leaving a WORK-0015 tail.
- **scope-auditor**: the AC reframes this session (WORK-0025/0027/0002/0014/0048)
  were all recorded and legitimate; WORK-0037's scope-auditor-FAIL override is a
  precedent to apply consistently to WORK-0035.

## Next Actions

Phase transition is BLOCKED. Before re-attempting:
1. **Operator decisions** on cull-vs-defer: recursive cluster (WORK-0010/0011/ADR-031),
   budget_manager, and reclassification of WORK-0032/0033/0001/0015/0035 to Phase 2.
2. **Record watchlist verdicts** (alternatives.md) or explicitly defer the re-eval.
3. **Run a repo-health re-run**, persist under .work/reviews/, confirm the
   goal-displacement / validation-theatre findings resolved (DoD #4).
4. **Close WORK-0018** once 1–3 done (DoD #1).
5. Re-validate DoD; then retro (record LG2/LG3 unanswered, assumption-1 partial),
   release bump, next-phase proposal, transition.
