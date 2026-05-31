# Adversarial Review — architecture (ADR-035 auto-deterministic-detector)

**Log:** adversarial-review-2026-05-31-architecture-adr-035
**Session:** in-session
**Depth:** Standard (3-agent panel; existential-challenger mandatory per ADR-017; determinism-auditor added — the ADR is about determinism)
**Commit:** d1c789a (working tree, branch docs/auto-deterministic-detector-adr)

Panel: [existential-challenger](existential-challenger.md) (mandatory),
[determinism-auditor](determinism-auditor.md), [scope-auditor](scope-auditor.md).

Scope: `.work/decisions/ADR-035-auto-deterministic-detector.md` (whether to ship
an auto-deterministic detector mining insights for ADR-003 violations).

Verdict: **CONDITIONAL → PASS after one revision cycle.** First pass: 2 BLOCKING +
several SIGNIFICANT; all resolved. The revision changed the decision from
DEFER to **REJECT** and removed an ADR-003 loophole.

## Dimension Scores

| Dimension | Verdict |
|---|---|
| ADR-003 integrity (determinism-auditor) | PASS after fix — artefact-level loophole removed; deterministic pattern-matcher (extending WORK-0028) made the only acceptable form |
| Anti-zombie / honest decision (existential) | PASS after fix — DEFER → REJECT; false "measurement substrate" rationale removed; reflect/contribute one honest prove-or-cull |
| Factual accuracy (existential) | PASS after fix — gate_run attributed to am_i_done.py, not record_insights.py |
| Scope containment (scope-auditor) | PASS — docs-only; reflect/contribute fate in scope (ADR-036 deferred it here); review records written so references resolve |

## Strengths

- The real-data investigation is sound and decisive: 682 events, all gate_run,
  0 ADR-003-violation candidates — the first honest measurement of the corpus.
- Correctly refuses to build a miner for uncollected data.

## Blocking Findings

Two on first pass; both resolved:

- **Artefact-level ADR-003 loophole** (determinism-auditor) — blessing an LLM
  classifier that emits deterministic scripts would license inference across the
  toolchain. Resolved: loophole removed; the only acceptable detector form is a
  deterministic pattern-matcher extending WORK-0028.
- **False keep-reflect.py rationale** (existential) — reflect.py measures none of
  the three triggers. Resolved: rationale dropped; reflect/contribute folded into
  one honest prove-or-cull decision.

## Significant Findings

All resolved or routed:

- Zombie-deferral → decision changed to REJECT (existential).
- Quiet work creation (trigger-1 instruments record_insights) → stated as a
  non-committed precondition (existential).
- Deterministic alternative unweighed → added as the preferred form (determinism).
- reflect.py test rigor (sort_keys masks ordering) → NOTED, code finding, routed to
  a future work item if reflect.py survives (determinism).
- record_insights roster drift → NOTED, already WORK-0069 (determinism).
- Self-referential challenge claim → review records written (scope-auditor).

## Minor Findings

- gate_run attribution corrected (existential).
- Reopen trigger now requires the deterministic form be explored first (determinism).
- Prove-or-cull phrased as a recorded trigger, not a state edit (scope-auditor).

## Synthesis

The investigation was right; the first-draft decision oversold and contained an
ADR-003 loophole. The revision is cleaner and more honest: **REJECT** the detector
(no corpus, no demand, and the LLM-classifier form is itself anti-ADR-003); if ever
reopened, it must be a deterministic pattern-matcher extending WORK-0028. The
self-improvement loop (reflect + contribute) gets one honest prove-or-cull date at
/phase-complete. Recorded **Proposed** (operator AFK; ratification = merge).

## Next Actions

PASS → commit the revised ADR + review records, raise PR, await operator
ratification. Code-level findings (reflect.py test, record_insights drift=WORK-0069)
are out of scope for this docs-only PR.

## pr-ready re-review (2026-05-31)

Re-ran existential-challenger (mandatory) + historian on the final diff per
/pr-ready. **No BLOCKING, no SIGNIFICANT requiring revision.** Refinements applied:
Status line tightened to the merged ADR-036 form; Prior-art "solved"→"tractable"
(WORK-0028 ships one such check, the rest are domain rules to add in the same lane);
`main` merged in so the ADR-036 cross-reference resolves on-branch (ADR-036 landed in
#77). Verified: the historian "ADR-036 doesn't exist" finding was branch-visibility
(ADR-036 is on main); the existential "verify the DoD" MINOR is satisfied —
phase-2.json's DoD explicitly lists "self-improvement loop (>=1 /contribute PR
end-to-end or cut)" with "a decision DATE this phase". Stop condition met.
