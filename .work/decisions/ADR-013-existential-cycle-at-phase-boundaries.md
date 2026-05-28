# ADR-013-existential-cycle-at-phase-boundaries — Existential cycle at phase boundaries

## Status

Accepted — 2026-05-28 — Phase 0

Amended 2026-05-29 (Phase 1): added a second trigger — meaningful substrate
releases — folding in the substrate-impact discipline that was briefly drafted
as a standalone ADR-034 and rejected by existential review as a second trigger
on this mechanism rather than a new decision.

## Decision

`/phase-complete` invokes `existential-challenger` against the current
state and produces a verdict for every named capability: *is it still
earning its keep?*. Removals are a first-class output of the cycle. No
feature is grandfathered.

The cycle has **two triggers**:

1. **Phase boundaries** (the primary cadence) — at `/phase-complete`, as above.
2. **Meaningful substrate releases** (off-cadence) — when the underlying
   substrate ships something Hedl users would care about (a model upgrade, a
   harness feature, an ecosystem-standard revision), run a **Substrate Impact
   Assessment**: re-evaluate each capability in `docs/alternatives.md` (status /
   improvement objective) and each Proposed or Deferred ADR (ratified / weakened
   / obsoleted), and propose amendments to any Accepted ADR the release touches.
   Output is a PR amending `docs/alternatives.md` and affected ADRs, citing the
   release as trigger. Triggered, not scheduled; the bar is "release notes that
   name new capabilities Hedl users would care about."

Both triggers run the same cull/retain machinery (per
[[ADR-012-managed-competitive-lifecycle]]); only the cadence differs. The
substrate trigger exists because vendors ship continuously while phases take
weeks, so competitive overlap would otherwise accumulate silently between
boundaries.

## Context

Reactive improvement (see [[ADR-005-self-improvement-human-gated]]) adds
capabilities. Without a counter-pressure, the framework only grows. The
counter-pressure is the existential cycle: a periodic, structured "why
does this exist?" pass.

## Options considered

- No periodic review — rejected: see growth-only dynamic above.
- Continuous review (every PR) — rejected: too noisy; review-fatigue
  produces rubber-stamp verdicts.
- Review at phase boundaries (chosen) — natural cadence, paired with
  `/phase-complete`, judgement informed by a full phase of usage.
- (Amendment) Substrate-release trigger as a *standalone* ADR-034 — rejected:
  it is a second trigger on this mechanism, not a new decision, so it is folded
  here. A fixed substrate-review cadence (e.g. monthly) was also rejected: it
  decouples the review from the actual change source.

## Consequences

- `existential-challenger` is a mandatory dispatch at `/phase-complete`.
  (Foundational item: promote it from the review library — see seed
  prompt.)
- Cull verdicts produce real changes: deletions, delegations, refactors.
- See [[ADR-012-managed-competitive-lifecycle]] — the existential cycle is
  where watchlist windows expire and judgement is rendered.
- The substrate trigger's shape was validated by a manual run against the
  2026-05-28 Opus 4.8 release (native multi-agent Workflows); see the
  substrate-impact assessment in `docs/alternatives.md`. A `/repo-health` or
  `/reflect` warning for "no substrate-impact assessment since the last
  meaningful release" is a reasonable future addition, not required here.
