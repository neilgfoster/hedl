# Adversarial Review — architecture (ADR-037 doing-it-wrong rules)

**Log:** adversarial-review-2026-05-31-architecture-adr-037
**Session:** in-session
**Depth:** Standard (existential-challenger mandatory per ADR-017 + simplicity-enforcer + historian)
**Commit:** docs/doing-it-wrong-rules-adr @ pre-commit working tree

Panel: [existential-challenger](existential-challenger.md),
[simplicity-enforcer](simplicity-enforcer.md), [historian](historian.md).

Scope: `.work/decisions/ADR-037-doing-it-wrong-rules.md` (first draft proposed
building a minimal rules-framework MVP).

Verdict: **FAIL (first draft) → PASS (revised).** The panel convergently found the
framework MVP was premature accretion; the pattern is sound and adoptable today
via the existing `[verify]` mechanism. ADR rewritten to: adopt via `[verify]`,
defer the framework with a trigger.

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Anti-accretion / DIRECTION-2 (existential) | FAIL→PASS after rewrite — framework dropped; decision is now restraint + reuse |
| Simplicity (simplicity-enforcer) | FAIL→PASS — adopt via existing `[verify]`; no third mechanism; no discovery/contract |
| Demand justification (existential) | PASS after rewrite — framework deferred with an explicit rule-count/adopter trigger |
| Cross-ADR accuracy (historian) | PASS after fix — ADR-035 "satisfies" overstatement corrected |

## Strengths

- The pattern (deterministic, project-specific, evolving rules in the gate) is
  genuinely on-thesis (ADR-003) and from the gate's prior-art author (attributed).
- The insights→rule→gate compounding loop is a real DIRECTION-2 defensibility point.

## Blocking Findings

Two on the first draft; both resolved by the rewrite:

- **Framework-surface accretion vs DIRECTION-2** (existential) — a rule-dir +
  discovery + contract + runner is new parallel surface, exactly what DIRECTION-2
  forbids. RESOLVED: the framework is dropped; the pattern is adopted via the
  existing `[verify]` command path (zero new gate machinery), and any framework is
  deferred with a trigger.
- **Goal-displacement / no adopter demand** (existential) — Jacob's repos aren't
  Hedl adopters; Hedl has ~1 rule; value appears at 50-200. RESOLVED: no framework
  is built now; the cheap [verify] adoption serves the only real user (Hedl
  dogfood) and the trigger gates the framework on real demand.

## Significant Findings

- **`[verify]` already does this** (simplicity-enforcer) — a project rules script
  declared as one `[verify]` entry runs deterministically in the gate, reusing the
  WORK-0021-hardened command path. ADOPTED as the decision.
- **Over-specified contract / build-before-rules** (simplicity-enforcer) — a
  discovery protocol for ~1 rule is premature. RESOLVED: single script, no
  discovery, until the trigger.
- **Demand threshold not met; deferral theater; process-over-product**
  (existential) — RESOLVED: the framework is explicitly Deferred-with-trigger (not
  "accept + build later"); the cheap adoption is a small concrete follow-up; the
  ADR now records restraint, not a build.
- **Overstates "satisfies ADR-035 reopen"** (historian) — ADR-035 has three reopen
  conditions; doing-it-wrong is the general author-written-rule lane, not the
  specific ADR-003-anti-pattern detector + corpus + scrub. FIXED: reworded to "the
  lane in which ADR-035's detector would live, if its own conditions are met."

## Minor Findings

- **Phase discipline** (existential) — net-new capability mid-Phase-2 (cut-don't-
  build). Mitigated: zero-new-surface adoption + deferred framework; the only build
  is documenting a `[verify]` convention + 1-2 seed rules (a small follow-up).
- **New gate surface** (simplicity) — eliminated by reusing `[verify]`.

## Synthesis

The first draft fell into the trap the project's own memory names ("don't mint a
framework ADR; existential-challenger keeps FAILing those as accretion"). The
pattern is worth adopting, but the cheap path already exists. The rewrite keeps the
valuable parts (the pattern, the workflow, the attribution, the insights→rule→gate
loop) and drops the surface: adopt via `[verify]`, defer the framework with a
trigger, fix the ADR-035 overstatement. This is now a restraint decision.

## Next Actions

PASS (revised) → operator decision: keep as a (lean) ADR recording the
adopt-via-[verify]/defer-framework decision, OR downgrade to a backlog item per the
"prefer WORK item over process ADR" convention. Either way: a small follow-up to
document the `[verify]` rules convention + seed 1-2 rules; no framework until the
trigger.
