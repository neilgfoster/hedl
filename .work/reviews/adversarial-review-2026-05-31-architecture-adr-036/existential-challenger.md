# existential-challenger — ADR-036 (Phase-2 scope narrowing)

**Run:** adversarial-review-2026-05-31-architecture-adr-036
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** d1c789a (working tree, branch docs/phase-2-scope-narrowing-adr)

The mandatory existential challenge for ADR changes (Unit B spec; ADR-017). This
is the independent challenger record — the ADR must NOT pre-claim a passed
challenge; this file is it.

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| BLOCKING | Single-operator validation theatre: "Lume + Wyrd proved bootstrap-adopter (N=2 in 24h)" is one operator seeding two of their own practice repos, not two independent adoptions. | `.work/insights/seed-comparison-lume-wyrd-2026-05-29.md` — one operator authored both seeds. | ACCEPTED — pillar 4 reworded: no "proved"; honest single-operator caveat; promotion gated on an independent adopter. |
| BLOCKING | Goal displacement: DIRECTION-2 is the maintainer reasoning about Hedl in response to a bad competitive score, not adopter demand. Lume/Wyrd are the maintainer's repos. | `.work/insights/critique-2026-05-29-direction-and-progress.md` (zero consumer-driven items); ADR-008 test never exercised by an external adopter. | ACCEPTED — goal-displacement weighing rewritten to state this honestly; "adopter-serving" claim dropped in favour of "surface-reducing + portability-preserving, maintainer-decided." |
| BLOCKING | Vaporware positioning: the whole "harness-agnostic" differentiator rests on WORK-0047, which is unbuilt/backlog. Under "what exists today," the intersection of target harnesses is {Claude Code} and the 4/10 redundancy verdict stands. | ADR-036 admits WORK-0047 unbuilt; work.json WORK-0047 status=backlog. | ACCEPTED — positioning split into today-differentiator (work-item-aware gate binding, exists) vs roadmap-differentiator (harness-agnostic, needs WORK-0047); full WORK-0047 build gated on a feasibility spike (one real non-Claude projection). |
| SIGNIFICANT | "Conditional on Unit D" risks being a third deferral; Phase-2 DoD requires a decision DATE this phase. | phase-2.json: "every culling-candidate has a decision DATE this phase." | REBUTTED-with-clarification — Unit D is a committed unit in this same strategic-compass bundle, decided THIS phase (not open-ended). ADR now says so. |
| SIGNIFICANT | Self-validation: an ADR with a self-authored "Existential challenge" section that uniformly affirms the decision is theatre; it pre-claimed "full panel under .work/reviews/" that did not exist. | ADR-036 embedded section. | ACCEPTED — embedded section removed; challenge lives here; ADR references this file. |
| SIGNIFICANT | Process-over-product: a 200-line strategy ADR written while the broken adopter install (WORK-0068) remains unfixed; the ADR ships nothing, only describes future work. | report.md §2.3 (install broken 3 ways); WORK-0068 high. | PARTIALLY ACCEPTED — the operator deliberately sequenced strategy before fix-PRs; Unit C makes WORK-0068 + install the top of the backlog. ADR adds an explicit "this ADR ships no code; the install fix is the first execution item" note. Not a blocker to the decision artifact. |
| MINOR | Framing-gap insight file cited but not present on this branch. | branch visibility. | REBUTTED — insight is authored in sibling Unit A PR #76; the framing argument is restated self-contained in the ADR Context. |

## Recommendations

The decision (narrow to a focused, portable, work-item-aware gate) survives the
challenge, but only after the ADR stops overselling: drop the adopter-demand and
"proved" framings, separate the today-differentiator from the WORK-0047 bet, gate
the cross-harness build on a spike, and move this challenge out of the ADR body.
All applied in the revised ADR.
