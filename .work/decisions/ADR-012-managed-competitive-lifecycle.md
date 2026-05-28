# ADR-012-managed-competitive-lifecycle — Managed competitive lifecycle

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

`docs/alternatives.md` is a living, honest landscape map. Each entry has a
status field:

- `uniquely-hedl` — Hedl is the best option here.
- `watchlisted` — a competitor matches or exceeds; explicit improvement
  objective and measurement window attached.
- `culling-candidate` — window expired with no advance and no traction.
- `culled` — capability removed, delegated, or refactored out.

When `existential-challenger` flags that a competitor overlaps a Hedl
capability, that capability becomes `watchlisted` with:

- An explicit improvement objective.
- A measurement window (default: one phase).

At window's end, judge on two axes: *advancing materially?* and
*observable traction?*. Both **no** → cull. At least one **yes** → continue
and re-evaluate at next phase boundary.

## Context

Stagnation is fatal. Panic is not the trigger. A capability that a
competitor does better is not automatically lost — but it must earn its
continued existence on a defined timeline, not on hope. See
[[ADR-013-existential-cycle-at-phase-boundaries]] for the cadence.

## Options considered

- Ignore competitors — rejected: see [[ADR-010-honesty-over-marketing]].
- Cull on first overlap — rejected: panic-driven, throws away capabilities
  that could improve.
- Watchlist with bounded window (chosen).

## Consequences

- `docs/alternatives.md` exists from Phase 0.5 / 1 (see foundational items
  in the seed prompt).
- `existential-challenger` agent is promoted from review-library to a named
  agent (foundational item).
- Watchlist outcomes are public — culling is announced; so is "continuing
  because traction is real even if we haven't shipped the improvement yet."
