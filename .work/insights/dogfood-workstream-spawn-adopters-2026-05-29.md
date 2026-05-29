# Dogfood observation: a "spawn-adopters" workstream emerged at N=2

**Date:** 2026-05-29
**Discovered during:** bootstrapping a second adopter (Wyrd) in the same session
that bootstrapped Lume.
**Status:** Investigated. Decision: **C (hybrid)** — see below. Not a mid-phase
pivot. **N=2 confirmed** by the per-seed comparison
(`seed-comparison-lume-wyrd-2026-05-29.md`): the prose template held, divergence
was healthy, and the WORK-0010/0011 case does not escalate yet.

## Observation

The ADR-019 workstream pattern materialised naturally, with none of
ADR-019/020's data-model code existing yet:

```
Spawn-Adopters-From-Hedl   [top-level workstream, multi-repo]
  |- bootstrap-lume         [child workstream, prose-form template]
  |- bootstrap-wyrd         [child workstream, same template, different seed]
```

Both children ran an identical sequence: create empty remote -> branch
protection -> install Hedl team tier -> sync to latest Hedl + migrate -> add
adopter requirements (pyproject.toml + uv.lock + .pymarkdown.json + README spec
links) -> PR#1 green -> operator-authored seed -> first product work item. The
template lives only in operator+session prose, in no `.work/` artefact.

## Premise correction (honest finding)

The operator's investigation brief (this 2026-05-29 session) stated the
2026-05-29 critique "recommended deferring WORK-0010 and WORK-0011 to Phase 2."
It did not. The critique
(`critique-2026-05-29-direction-and-progress.md`, lines 92-95) recommended the
opposite: **"Pull WORK-0010 (workstream data model), WORK-0011 (workstream
templates), WORK-0015 to the top of Phase 1."** Both are Phase 1 today, and
WORK-0011 closing is the v0.2.0 / phase-transition trigger. So the A/B/C menu's
shared premise (they are Phase-2-deferred) is off: option B ("promote to Phase
1") is moot — already there; option A ("keep at Phase 2") rests on a state that
does not exist. The actionable substance still resolves to C's spirit.

## The five questions, answered

1. **True workstream or lighter checklist?** For the *bootstrap-adopter* case
   specifically: a checklist. The sequence is linear, deterministic, and
   identical across Lume/Wyrd. A markdown template carries it at far lower cost
   than the recursive data model — the recursive model is over-engineered *for
   this case*. (That is not an argument against WORK-0010 in general; the
   workstream primitive earns its keep elsewhere. It is an argument that
   bootstrap-adopter does not need it.)

2. **Does N=2 validate ADR-019/020 as Phase 1?** It is consistent with the
   critique's call to keep them Phase 1, but it does not make the *data model*
   urgent. Numbers, not intuition: the recursive model's benefit over a prose
   template is machine-tracked nested state + cross-workstream coordination.
   That benefit is ~0 while one operator holds full context. It exceeds build
   cost (a multi-PR schema migration + gate/install changes) only when
   concurrently-active workstreams exceed what one operator tracks reliably
   (~5-7, the cognitive-load ceiling) **or** >1 operator needs shared
   machine-readable state (prose-in-session does not transfer). At N=2
   adopters / 1 operator, prose wins decisively.

3. **Does this stress ADR-021 (multi-repo, deferred)?** Coordinating 3 repos
   (Hedl + Lume + Wyrd) via prose works at N=3 / 1 operator. The
   coordination-failure point is the same threshold as Q2: when no single
   operator holds full context — >1 operator, or more concurrent repos than one
   person tracks. Evidence for ADR-021's eventual need; not yet a failure.

4. **Is bootstrap-adopter a codifiable template (ADR-020)?** Yes, and it should
   be authored now as prose (`docs/templates/bootstrap-adopter.md`) so the N=2
   learning does not evaporate. Data-form is a fold-in for WORK-0011 when it
   lands (ADR-020).

5. **Effect on the dogfood hypothesis (ADR-008)?** The dogfood is now testing
   Hedl against **two** real adopters in parallel, by accident. ADR-008's
   adopter-relevance question ("would another adopter want this?") is now
   answered by two real adopters at once rather than a hypothetical — over-
   satisfied ahead of schedule. Positive
   evidence that Hedl works on real consumer repos (the signal the direction
   critique said was missing).

## Decision — C (hybrid)

- **Codify bootstrap-adopter as a prose template now** —
  `docs/templates/bootstrap-adopter.md`, from the actual Lume/Wyrd sequence.
  Low cost, captures the learning, makes the next bootstrap repeatable.
- **WORK-0010/0011 stay where the critique put them (Phase 1).** No
  re-prioritisation — they are already prioritised; this is not a pivot. The
  Wyrd evidence is logged as support for keeping them, *and* as evidence that
  the prose template suffices for the bootstrap case until then.
- **Record the data-model-adoption threshold** (Q2/Q3's numeric answer) on
  WORK-0010 so the prose-vs-recursive question is decision-justified: adopt the
  recursive data model when concurrently-active workstreams exceed ~5-7, OR
  >1 concurrent operator needs shared state, OR a parallel-bootstrap-under-
  coordination-strain repeats. Below that, prose templates are the right tool.
- **WORK-0011 should fold in / supersede the prose template** when it ships
  workstream templates in data-form (ADR-020). Noted on the item.

Rejected: (A) as stated (wrong premise — they are not Phase 2); (B) promotion
(moot — already Phase 1, and a re-pivot is exactly what the critique warned
against).
