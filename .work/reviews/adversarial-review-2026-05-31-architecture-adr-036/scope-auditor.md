# scope-auditor — ADR-036 (Phase-2 scope narrowing)

**Run:** adversarial-review-2026-05-31-architecture-adr-036
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** d1c789a (working tree, branch docs/phase-2-scope-narrowing-adr)

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| BLOCKING | "Superseded → adopt MADR" is a material architectural decision (changes how all future ADRs are authored/validated) beyond Unit B's direction-pick scope. | ADR-036 drops table, ADR-schema row. | ACCEPTED — changed to "Superseded → replacement deferred; MADR is the recommended candidate, decided in a separate ADR/Unit-C item." No binding template change made here. |
| SIGNIFICANT | Embedded "Existential challenge" section duplicates the separate adversarial-review record (process bloat; conflates decision with validation). | ADR-036 embedded section. | ACCEPTED — section removed from ADR; challenge recorded in this run's existential-challenger.md; ADR references it. |
| SIGNIFICANT | Cited Unit A artifact not present. | branch visibility. | REBUTTED — authored in sibling PR #76; framing argument restated inline so the ADR is self-contained. |
| SIGNIFICANT | Pillar 5 "conditional on Unit D" is an asymmetric pre-emption: a yes from Unit D auto-promotes it to a required pillar. | ADR-036 pillar 5. | ACCEPTED — restructured to four guaranteed pillars + a separate "Deferred to Unit D" item; DIRECTION-2 is coherent without pillar 5. |
| MINOR | The drops table makes Unit C's disposition decisions rather than stating intent. | ADR-036 drops table vs Unit C consequence. | ACCEPTED — table reframed as DIRECTION-2's recommended dispositions that Unit C executes and records; final-disposition latitude noted. |
| MINOR | Consequences list README/alternatives.md updates as both consequence and out-of-scope. | ADR-036 consequences. | ACCEPTED — consequences split into immediate (Unit C) vs downstream (separate PRs). |

## Recommendations

Strip the binding MADR decision; externalize the challenge; reframe drops as
intent-for-Unit-C; restructure pillars to 4+1-deferred; split consequences by
horizon. All applied.
