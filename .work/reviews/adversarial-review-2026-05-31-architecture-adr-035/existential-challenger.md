# existential-challenger — ADR-035 (auto-deterministic-detector)

**Run:** adversarial-review-2026-05-31-architecture-adr-035
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** d1c789a (working tree, branch docs/auto-deterministic-detector-adr)

Mandatory existential challenge for ADR changes (Unit D spec; ADR-017),
independent of the ADR draft.

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| BLOCKING | The "keep reflect.py as trigger-condition (2)'s measurement substrate" rationale is false — reflect.py aggregates gate telemetry; it does not measure landed-PR count (a git query), the uncollected new event type, or the privacy scrub. | reflect.py aggregate() handles gate_run/reviewer_fired only. | ACCEPTED — false rationale removed; reflect/contribute folded into one honest prove-or-cull decision. |
| SIGNIFICANT | Goal-displacement / zombie-deferral: the ADR concedes the detector is "Hedl iterating on Hedl, no adopter demand" — its own rejection criterion — yet outputs DEFERRED, keeping it alive with non-time-bounded conditions. | ADR finding 6; phase-2 cutting bias. | ACCEPTED — detector decision changed to REJECTED with a non-committed reopen condition. |
| SIGNIFICANT | Quiet work creation: trigger-1 requires instrumenting record_insights.py for a new event type, but the ADR claims "no follow-up work item." | ADR trigger-1 vs consequences. | ACCEPTED — instrumentation + deterministic-detector exploration are now stated as preconditions nobody is committing to; no hidden work. |
| SIGNIFICANT | Process-over-product: a long ADR to say "not now." | ADR length. | PARTIALLY ACCEPTED — the ADR format is operator-mandated for Unit D (findings-in-Context + Status). Trimmed where possible; the investigation record has standalone value (first honest measurement of the corpus). |
| MINOR | Factual error: record_insights.py does not emit gate_run; gate_run is written by am_i_done.py. | am_i_done.py:1666-1691; record_insights.py:58-78 emits reviewer_fired only. | ACCEPTED — attribution corrected. |

## Recommendations

Reject (not defer) the detector given no demand and no corpus; stop using a false
measurement-substrate claim to avoid culling; decide reflect/contribute as one
honest prove-or-cull; fix the gate_run attribution. All applied.
