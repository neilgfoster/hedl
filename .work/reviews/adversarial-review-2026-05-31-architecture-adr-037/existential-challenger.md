# existential-challenger — ADR-037 (doing-it-wrong rules)

**Run:** adversarial-review-2026-05-31-architecture-adr-037
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** docs/doing-it-wrong-rules-adr @ pre-commit working tree

Mandatory challenge for ADR changes (ADR-017).

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| BLOCKING | A rule-dir + discovery + contract + runner is framework-surface accretion — DIRECTION-2 forbids parallel feature surface. | ADR-036 DIRECTION-2; ADR-037 Shape items 1-4. | ACCEPTED — framework dropped; pattern adopted via existing `[verify]`; framework Deferred-with-trigger. |
| BLOCKING | Goal-displacement: sole evidence is Jacob's other repos; Hedl has no external adopters; "adopter-serving" overstated. | ADR-036 honest-risk 1; phase-2.json cut-don't-build bias. | ACCEPTED — no framework built now; cheap adoption serves Hedl dogfood; trigger gates the framework on real demand. |
| SIGNIFICANT | Demand threshold unmet: value at 50-200 rules; Hedl has ~1. | Jacob's note; WORK-0028 is the one rule. | ACCEPTED — single-script adoption now; directory/discovery deferred until ~10+ rules. |
| SIGNIFICANT | "Accept + build MVP via follow-up" is deferral theater (punts scope to an unchallenged item). | ADR-037 Decision/Consequences. | ACCEPTED — reframed to an explicit Deferred-with-trigger for the framework; the only near-term build is a small, concrete [verify]-convention doc + seed rules. |
| SIGNIFICANT | Process-over-product: a chat idea became insight + 164-line ADR + review records + no shipped code; project memory says prefer WORK item over process ADR. | memory: prefer-standards-or-workitem-over-process-adr. | PARTIALLY ACCEPTED — ADR trimmed and reframed to a capability/restraint decision; operator offered the downgrade-to-backlog-item option. |
| MINOR | Phase discipline: net-new capability mid-Phase-2. | phase-2.json. | MITIGATED — zero-new-surface adoption + deferred framework; if it grows, revisit at /phase-complete. |

## Recommendation

Defer the framework; adopt the pattern the zero-surface way ([verify]); gate the
framework on ~10+ rules or an external adopter request. Applied in the rewrite.
