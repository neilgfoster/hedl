# historian — ADR-036 (Phase-2 scope narrowing)

**Run:** adversarial-review-2026-05-31-architecture-adr-036
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** d1c789a (working tree, branch docs/phase-2-scope-narrowing-adr)

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| SIGNIFICANT | Status "Accepted ... provisional, pending ratification" is not valid repo ADR vocabulary (Accepted/Proposed/Superseded/Deferred). | ADR-021 "Proposed — deferred to v1.x"; ADR-019 "Superseded". | ACCEPTED — Status changed to "Proposed" (recommended DIRECTION-2; ratification = merge). |
| SIGNIFICANT | Contradicts ADR-016, which preserves "NL routing through SKILL.md is the cross-harness fallback". ADR-036 said "drop the routing table". | ADR-016:20-22. | ACCEPTED — reworded: the NL-routing fallback is RETAINED per ADR-016; only the headline-feature pitch is dropped. No contradiction. |
| MINOR | ADR-008 cherry-pickable test is a per-change review gate, not a direction-level test; the alignment claim is loose. | ADR-008:9-16. | ACCEPTED — claim softened; ADR-011/013 cited as the more directly relevant gates; ADR-008 cited in spirit. |
| MINOR | ADR-005 is a principle (human-gated self-improvement); culling reflect/contribute supersedes the implementation, not the principle. | ADR-005. | ACCEPTED — reworded to "the one implementation is removed; the principle survives unless abandoned." |
| MINOR | ADR-032 numbering gap (031, then 033/034). | file listing. | NOTED — pre-existing cosmetic gap; 034 is the correct next number (highest existing is 033). |
| MINOR | ADR-011 disqualifiers may need reframing under focused-tool scope. | ADR-011. | NOTED — downstream README/disqualifier doc work; tracked as a Unit-C-adjacent consequence, not this docs-only ADR PR. |

## Recommendations

Use standard Status vocabulary; reconcile the SKILL.md disposition with ADR-016's
preserved fallback explicitly; soften the ADR-008 alignment to "spirit"; fix the
ADR-005 principle-vs-implementation precision. All applied.
