# Adversarial Review — architecture (ADR-036 Phase-2 scope narrowing)

**Log:** adversarial-review-2026-05-31-architecture-adr-036
**Session:** in-session
**Depth:** Standard (4-agent panel; existential-challenger mandatory for ADR per ADR-017)
**Commit:** d1c789a (working tree, branch docs/phase-2-scope-narrowing-adr)

Panel: [existential-challenger](existential-challenger.md) (mandatory),
[historian](historian.md), [scope-auditor](scope-auditor.md),
[simplicity-enforcer](simplicity-enforcer.md). The mandated existential-challenger
ran as an independent step; the ADR does not pre-claim a passed challenge.

Scope: `.work/decisions/ADR-036-phase-2-scope-narrowing.md` (Phase-2 strategic
direction; DIRECTION-1 vs DIRECTION-2).

Verdict: **CONDITIONAL → PASS after one revision cycle.** First pass surfaced 4
BLOCKING and (synthesized) 7 SIGNIFICANT — the per-agent logs hold additional
overlapping rows that this report dedupes; all addressed in the revised ADR
(decision unchanged, overselling removed).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Anti-goal-displacement (existential) | PASS after fix — adopter-demand framing dropped; honest "maintainer-decided in response to the review" recorded |
| Honest positioning (existential, simplicity) | PASS after fix — today-differentiator (gate binding) split from roadmap-differentiator (harness-agnostic / WORK-0047); cross-harness build gated on a spike |
| ADR consistency (historian) | PASS after fix — Status → Proposed; ADR-016 fallback reconciled; ADR-005/008 precision fixed |
| Scope containment (scope-auditor) | PASS after fix — binding MADR decision removed; challenge externalized; drops reframed as Unit-C intent |
| Genuine simplification (simplicity) | PASS after fix — reframed to one gate + substrate; honest removed-vs-renamed accounting |

## Strengths

- The core decision (narrow to a portable, work-item-aware completion gate; retire
  the whole-framework pitch) survives every challenge.
- The framing correction (harness-agnostic intent; intersection-of-natives) is a
  real and load-bearing rebuttal to the external review's single-harness 4/10.

## Blocking Findings

Four on first pass; all resolved in the revised ADR:

- **MADR adoption was a binding architectural decision** (scope-auditor) — beyond
  direction-picking. Resolved: MADR is now a recommended candidate, decided
  separately.
- **Vaporware positioning** (existential, simplicity) — differentiator bet on
  unbuilt WORK-0047. Resolved: today vs roadmap differentiator split; full build
  gated on a feasibility spike.
- **Single-operator validation theatre** (existential) — "Lume+Wyrd proved it" is
  one operator, two own-repos. Resolved: "proved" dropped; promotion gated on an
  independent adopter.
- **Goal displacement** (existential) — DIRECTION-2 is maintainer-decided in
  response to a competitive score, not adopter demand (existential-challenger.md
  marks this BLOCKING). Resolved: the adopter-serving claim was dropped; the ADR's
  goal-displacement weighing and "Honest risks" section state this plainly.

## Significant Findings

Synthesized to the seven below; all resolved. (The per-agent logs hold additional
overlapping rows — e.g. the same goal-displacement/positioning concern appears in
more than one agent's table — which this synthesis dedupes, so raw row counts
across the logs exceed these seven.)

- Self-validation — embedded challenge section removed; recorded separately
  (existential, scope-auditor).
- Process-over-product — ADR ships no code while install broken; mitigated by Unit
  C putting WORK-0068/install at top of backlog + an explicit note (existential).
- Status vocabulary — "Accepted provisional" → "Proposed" (historian).
- ADR-016 contradiction — NL-routing fallback retained; only the pitch dropped
  (historian).
- Five-pillars-isn't-focused — reframed to gate + substrate + deferred (simplicity).
- Premature cross-harness abstraction — gated on a spike (simplicity).
- Disposition labels mask retention — honest removed-vs-renamed accounting
  (simplicity).

## Minor Findings

- ADR-008 alignment softened to "spirit"; ADR-011/013 cited as the relevant gates
  (historian).
- ADR-005 principle-vs-implementation precision fixed (historian).
- ADR numbering: this ADR is **036** (034 is spoken-for by ADR-013's rejected
  "standalone ADR-034"; 035 is the sibling Unit D ADR); the 032 gap is cosmetic
  (historian).
- Pillar 3 (.work/) load-bearing role clarified (simplicity).
- Consequences split into immediate vs downstream (scope-auditor).
- Drops reframed as Unit-C intent, not final decisions (scope-auditor).
- "Unit D undefined" and "missing Unit A artifact" rebutted: both are committed
  units in this same operator-defined bundle; Unit A ships in sibling PR #76; the
  framing argument is restated inline (existential, scope-auditor).

## Synthesis

A strong, fair panel. The findings did not break the decision — they broke its
*marketing*. The revision keeps DIRECTION-2 as the recommendation while removing
every oversell the panel caught: no adopter-demand claim, no "proved", no
vaporware-as-fact, no binding side-decisions, standard Status vocabulary, and an
honest accounting of what is actually removed vs renamed. The decision is recorded
**Proposed** (not Accepted) because the operator is AFK and ratification is the
merge.

## Next Actions

PASS → commit the revised ADR + review records, raise PR, await operator
ratification (no auto-merge). Unit C is gated on this ADR's ratified outcome.
