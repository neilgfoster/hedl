# historian — Unit A (external-review framing-gap insight + report §8 amendment)

**Run:** adversarial-review-2026-05-31-requirements-unit-a
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** d1c789a (working tree, branch docs/external-review-framing-gap)

**Verdict contribution:** 2 SIGNIFICANT + 1 MINOR, all resolved by status annotation.

## Findings

| Severity | Finding | Evidence | Status |
|---|---|---|---|
| SIGNIFICANT | Insight cites ADR-019 as evidence of foundational harness-agnostic intent, but ADR-019 is Superseded. | `ADR-019` Status: "Superseded — 2026-05-30" (WORK-0027); standards.md supersession note. Portability rationale (ADR-019:88-89) survives the supersession (which targeted the recursive primitive, not portability). | RESOLVED — bullet now annotated "(Status: Superseded — ... the cross-harness portability rationale below survives the supersession)". |
| SIGNIFICANT | ADR-021 (Proposed — deferred to v1.x) listed among "foundational" intent without flagging deferred status. | `ADR-021` Status: "Proposed — deferred to v1.x"; ADR body: "captures two related ambitions without committing to either". | RESOLVED — bullet now annotated "(Status: Proposed — deferred to v1.x)". |
| MINOR | "foundational" mingles committed (001/011/016) with deferred (021/033/WORK-0047), creating ambiguity about what "foundational" means. | Insight body lines 13-26. | RESOLVED — per-ADR Status annotations now make committed-vs-deferred-vs-superseded explicit on the face of the list; ADR-033 ("Proposed") also annotated. |

## Recommendations

Distinguish committed intent (ADR-001/011/016, Accepted) from deferred/proposed
(ADR-021 deferred, ADR-033 Proposed) and superseded-but-surviving (ADR-019) on
the face of the citation list. Applied: each non-Accepted ADR now carries its
Status inline; the ADR-019 quote corrected to verbatim ("is consumable"). The
insight's thesis (intent encoded across the ADR set; honest-for-today but
blind-to-intent) is strengthened, not weakened, by the annotations.
