# simplicity-enforcer — ADR-036 (Phase-2 scope narrowing)

**Run:** adversarial-review-2026-05-31-architecture-adr-036
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** d1c789a (working tree, branch docs/phase-2-scope-narrowing-adr)

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| SIGNIFICANT | Five pillars for a "focused tool" is the framework surface relabeled; pillars 3/4/5 reintroduce scope the external review said to drop (ADOPT only gate + --streams). | ADR-036 Five pillars; report.md §4. | ACCEPTED — reframed as ONE thing (the work-item-aware gate) + its necessary substrate (.work/ is what makes it work-item-aware) + distribution (bootstrap/projections) + --streams; forensic plumbing demoted to deferred. The gate is the focus; the rest is in service of it. |
| SIGNIFICANT | Premature cross-harness abstraction: WORK-0047 projections committed before any second-harness adopter exists. | WORK-0047 unbuilt; zero non-Claude adopters. | ACCEPTED — full WORK-0047 build gated on a feasibility spike (one real projection) before promoting the whole multi-harness build; positioning preserved (gate is portable by design) without building the abstraction blind. |
| SIGNIFICANT | Disposition labels ("thinned", "trimmed", "kept") mask retention: of 5 REJECT features, only ~1 is cleanly culled. The ADR narrows the pitch, not the codebase. | ADR-036 drops table vs report.md §4. | ACCEPTED — added an honest "removed vs renamed" accounting; ADR states v0.2.0 narrows the positioning + culls budget_manager + panel-as-feature, with deeper codebase culls gated on /phase-complete. |
| MINOR | 205-line artifact over-built for a yes/no direction choice. | ADR-036 length. | PARTIALLY ACCEPTED — externalizing the challenge trims it; the repo's ADR house style is detailed (cf. ADR-008). Kept the decision-bearing content. |
| MINOR | Pillar 3 (.work/) ambiguous: a pillar yet "lean on native plan-mode/TodoWrite". | ADR-036 pillar 3. | ACCEPTED — clarified: .work/ is load-bearing for the work-item-aware gate (gate-only tier runs without it); native is fine for ad-hoc tracking. |

## Recommendations

Make the gate the singular focus and show the rest in service of it; gate the
cross-harness build on a spike; give an honest removed-vs-renamed count; clarify
.work/'s load-bearing role. All applied.
