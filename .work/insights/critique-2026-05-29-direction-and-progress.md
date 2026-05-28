# Direction and Progress Critique — 2026-05-29

Mid-Phase-1 honest assessment. Triggered out-of-band (not at /phase-
complete) because the data warranted intervention.

## Numbers

| Metric | Value |
|---|---|
| Accepted ADRs | 22 |
| Proposed ADRs | 8 |
| Total ADRs | 30 |
| Work items completed since v0.1.0 tag | 8 |
| Work items remaining (Phase 1 + Phase 2) | 28 |
| Code LOC (skill/hedl/scripts/) | 4050 |
| Process artefact LOC (ADRs + docs + references) | 4433 (1.09× scripts) |
| End-user-facing shipped capabilities | 2 (gate, install) |
| Lume bootstrap progress | Untouched, 3 days idle |

## What works

- The discipline catches real things: 3 structural bugs found via dogfood
  (WORK-0029/0030/0016); one verified false positive resolved without a
  wasteful fix (WORK-0019).
- Required status checks now enforce the gate; structurally impossible to
  merge a red PR. Most important structural improvement of the arc.
- Operator has internalised the workflow ("merge /iterate"); cognitive
  load reducing over time as designed.
- ADR-010 (honesty over marketing) holds under pressure. False positive
  recorded; superseded hypotheses preserved.
- The Opus 4.8 reaction was the framework's own competitive-lifecycle
  mechanism working as designed — sharpened watchlist objectives, no
  panic-cull, no defensive rationalisation.

## What is at risk

1. The Proposed-ADR pile is approaching a cliff. 8 Proposed ADRs (021,
   025, 026, 027, 028, 029, 030, 033) sit untouched in the tree because
   /phase-complete has not run. We have been proposing faster than we
   have been deciding. Idea inventory accumulating without evaluation.

2. The framework is being built BY itself, ON itself, FOR itself. Every
   work item closed in this arc has been framework-internal: gate fixes,
   symlink bugs, count drift, governance, ADR housekeeping. Zero items
   are consumer-driven. The ADR-008 test ("would another adopter want
   this?") has not been exercised once.

3. Lume sat idle for 3 days while Hedl churned through 17 PRs. The whole
   arc started with "Hedl will help me build Lume". Hedl has consumed the
   operator's attention; Lume has received none. The framework is eating
   the work it was supposed to enable.

4. Goal displacement is real and worse than /repo-health flagged. The
   ratio improved only because tests grew, not because shipped
   capabilities did. End-user-facing capability count is still 2 (gate,
   install).

5. Substrate moved while we were tuning the engine. Opus 4.8 Dynamic
   Workflows shipped natively what ADR-031/021 proposed. Anthropic ships
   continuously; Hedl iterates on itself slowly. Unique-value surface
   shrinks if this pattern persists.

6. Sample size remains one. Discipline that one operator finds elegant
   may be incomprehensible to a second adopter. Every new Proposed ADR
   widens the cognitive surface without validating it.

## Honest read

The engine is real and runs. Discipline holds. Bugs are caught. But the
engine has only ever run on itself. The thing the framework was built
to enable (Lume bootstrap; broader adoption) has not been touched. The
engine is impressive; the train has not moved.

The framework is at risk of preferring tuning to driving. Every new
Proposed ADR, every meta-observation captured, every drift fix surfaced
feels productive because the framework's own mechanisms applaud this
kind of work. The disciplines are working; they are working on
themselves. There is no external pressure yet to refute or refine them.

This is a structural pattern in self-improving frameworks. They optimise
their own substrate before they serve their stated purpose. The honest
test is whether the operator notices and redirects.

## Recommendations

These are real choices, recorded so /phase-complete can act on them:

1. **Hard moratorium on new Proposed ADRs** until the first /phase-
   complete evaluates the existing 8. Capture future ideas in scratch
   notes outside the repo, not as ADR files.

2. **Accelerate to Lume.** Pull WORK-0010 (workstream data model), WORK-
   0011 (workstream templates), WORK-0015 (terminology audit) to the
   top of Phase 1. Defer everything else except the in-flight RCE
   security fixes. As soon as 0010/0011/0015 land, tag v0.2.0 and
   immediately start Lume bootstrap.

3. **Trigger /phase-complete early.** Do not wait for all 22 Phase 1
   items. Run the existential cycle on the 8 Proposed ADRs under real
   pressure. Cull what does not survive. Tag v0.2.0.

4. **Accept that some Proposed ADRs will die.** ADR-031 (parallel work)
   is probably superseded by Dynamic Workflows. ADR-021 (autonomous
   orchestration) likely too. Mark Status: Superseded honestly. The
   framework has the vocabulary; use it.

5. **Apply ADR-012 to Hedl itself.** Which capabilities, in light of
   Opus 4.8 + a not-yet-existent Lume, should move to culling-
   candidate? Honest answer is probably more than zero. The
   adversarial-review panel was already watchlisted; the dispatcher
   prompt itself may need revisiting; the budget-tier accounting is
   already a culling-candidate but has not been retired.

## The single biggest signal

Lume sat idle for 3 days. If the operator looks at that and feels
uncomfortable, the framework is working too well on itself and not
enough on the work. If the operator looks at it and feels "yes that
is fine, Hedl needed this groundwork", then the open question is
whether the operator can honestly distinguish necessary groundwork
from self-serving polish.

This critique does not answer that question. It surfaces it.

---

## Editor's note (2026-05-29)

Preserved verbatim as the assessment. One reconciliation for future readers,
because the framework's own honesty discipline (ADR-010) demands the record be
accurate: the "8 Proposed ADRs (021, 025, 026, 027, 028, 029, 030, 033)" in
risk #1 is a snapshot that predates the same session's cleanups. ADR-029 and
ADR-030 were never created — they FAILed existential review and became a
`standards.md` convention; ADR-034 (drafted after this snapshot) was likewise
folded into ADR-013. The live Proposed set is smaller (025-028, plus 031 and
033 carrying Proposed-deferred/-gated status). This does not change the
critique's thrust — the pile is still unevaluated pending the first
`/phase-complete`, and the proposing-faster-than-deciding pattern is exactly
what the critique names. If anything, the drops/folds are early evidence of the
moratorium-and-cull the critique recommends.
