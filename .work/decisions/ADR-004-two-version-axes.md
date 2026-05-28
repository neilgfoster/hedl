# ADR-004-two-version-axes — Two version axes, kept separate

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Hedl exposes two distinct version axes:

1. **Hedl's own version** — semver, tracked alongside `schema_version` and
   driven by migrations under `skill/hedl/scripts/install.py`.
2. **The consumer project's version** — driven by `change_class` on each work
   item, computed and bumped at `/phase-complete`.

They never share a number. They never share a release.

## Context

A framework that bumps its consumers' versions is broken. A consumer that
bumps the framework is impossible. Conflating the two leaks one product's
release cadence into the other's.

## Options considered

- Single shared semver — rejected: incoherent (whose semver is it?).
- Calendar versioning on one side — rejected: complicates migrations, which
  need ordering, not dates.
- Two independent axes (chosen) — Hedl semver with explicit migrations,
  consumer phase→release via `change_class`.

## Consequences

- Hedl's `schema_version` is stored separately from the consumer's
  `project_version`. See [[ADR-003-deterministic-over-inference]] —
  migrations are scripted, not inferred.
- Consumers can upgrade Hedl without bumping their own version, and vice
  versa.
- A Hedl breaking change requires a `schema_version` increment plus a
  migration. There is no "soft" Hedl bump.
