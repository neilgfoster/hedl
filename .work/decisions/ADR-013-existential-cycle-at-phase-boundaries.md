# ADR-013-existential-cycle-at-phase-boundaries — Existential cycle at phase boundaries

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

`/phase-complete` invokes `existential-challenger` against the current
state and produces a verdict for every named capability: *is it still
earning its keep?*. Removals are a first-class output of the cycle. No
feature is grandfathered.

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

## Consequences

- `existential-challenger` is a mandatory dispatch at `/phase-complete`.
  (Foundational item: promote it from the review library — see seed
  prompt.)
- Cull verdicts produce real changes: deletions, delegations, refactors.
- See [[ADR-012-managed-competitive-lifecycle]] — the existential cycle is
  where watchlist windows expire and judgement is rendered.
