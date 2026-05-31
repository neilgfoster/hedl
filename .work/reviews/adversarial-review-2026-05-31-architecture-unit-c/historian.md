# historian — Unit C (Phase-2 backlog reconciliation)

**Run:** adversarial-review-2026-05-31-architecture-unit-c
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** d1c789a (working tree, branch chore/phase-2-backlog-reconciliation)

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| BLOCKING | "Contingent on ADR-034/035, neither exist; ADR-034 folded into ADR-013." | reviewed `main`. | REBUTTED — ADR-036 (B)/ADR-035 (D) on sibling branches (PRs #77/#78). The folded-into-013 ADR-034 is the OLD rejected concept; my Unit B renumbered to 036 to avoid that collision. |
| BLOCKING | "Deferring WORK-0010/0011 pre-empts /phase-complete." | dogfood-2026-05-29 recommended pulling them to Phase 1. | REBUTTED — WORK-0010's existing reclassify_reason already records "operator decision at /phase-complete 2026-05-30: defer, not cull"; the 2026-05-29 Phase-1 rec was superseded by that later decision + ADR-019 supersession. My DEFERRED band is consistent, not pre-empting. |
| SIGNIFICANT | WORK-0075 gates completion on an external adopter event — un-completable in-phase (Principle 5). | WORK-0075 AC2. | ACCEPTED — rescoped: in-phase deliverable is the doc graduation; the "proven" marketing claim is a documented gate, not a completion criterion. |
| SIGNIFICANT | WORK-0050 demotion contradicts DIRECTION-2's distribution pillar. | WORK-0050 title vs band. | RETAINED — the operator's plan placed 0050 in the framework-feature direction; the note records it is distribution-adjacent but not the gate itself. |
| SIGNIFICANT | "No open items to supersede" asserted without an audit. | reconciliation_note. | ADDRESSED — the orphan audit was run (deterministically): no backlog item is about budget tier / panel orchestration / bespoke-ADR-schema / reflect-contribute expansion; those are code/scope owned by ADR-036/035 + /phase-complete. |

## Recommendations

Rescope WORK-0075 for phase-completability; confirm the WORK-0010/0011 deferral
against the recorded /phase-complete decision (it matches); keep the orphan-audit
claim only with the search behind it. Applied.
