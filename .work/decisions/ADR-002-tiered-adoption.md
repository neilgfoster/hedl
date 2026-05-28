# ADR-002-tiered-adoption — Tiered adoption, default lightweight

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Hedl offers three install tiers — `gate`, `lightweight`, `team`. Default is
`lightweight`. The spec pipeline, phase-tracking, and team review panels are
strictly opt-in. The deterministic completion gate (`am_i_done.py`) is the
only mandatory artifact across all tiers.

## Context

An independent adversarial review confirmed Hedl's genuine differentiator is
the deterministic completion gate (see [[ADR-001-distribution-as-agent-skill]]
for the distribution mechanism that makes tiered adoption cheap). Rigid
pipelines fight the real-time flexibility most teams want. The choice is to
make ceremony cherry-pickable rather than make adoption a one-way door.

## Options considered

- Single all-in product — rejected: the review found ceremony was the friction
  most likely to make adopters bounce. Forcing it surrenders the
  best-of-class gate to spite.
- Two tiers (gate / full) — rejected: the lightweight middle (phases without
  parallel review) is the median consumer; we would push them to either floor
  or ceiling.
- Three tiers, default lightweight (chosen) — gate-only for adopters who just
  want the gate, lightweight as the median, team for organisations using the
  full review panel.

## Consequences

- `install.py --tier` is the authoritative path for tier changes; manual
  edits of projections are not supported.
- Lower-tier consumers must remain first-class — features that only function
  at `team` tier are restricted to `team` tier, not silently degraded.
- Marketing leads with the gate (see [[ADR-011-disqualifiers-first-positioning]]).
- See [[ADR-009-opinionated-defaults-configurable]] — tier choice is the
  largest such default.
