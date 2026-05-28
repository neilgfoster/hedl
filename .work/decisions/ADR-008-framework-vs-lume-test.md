# ADR-008-framework-vs-lume-test — The Framework-vs-Lume test

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Every proposed Hedl change passes through one question:

> *Would this change narrow Hedl's use-case so far it is worthless to anyone
> except me?*

- **Yes** → it belongs in Lume (or another consumer), not in Hedl.
- **No** → it can land in Hedl, but **must be cherry-pickable**: a tier
  addition, optional module, or `hedl.toml` flag.

## Context

The maintainer is also Hedl's first heavy user. Without an explicit guard,
maintainer preferences calcify into framework requirements and Hedl becomes
the maintainer's personal OS — useless to anyone else. See
[[ADR-009-opinionated-defaults-configurable]] for the configurability rule
that makes "cherry-pickable" tractable.

## Options considered

- "Use judgement" (chosen by default elsewhere) — rejected: judgement drifts
  under reactive improvement (see [[ADR-005-self-improvement-human-gated]]).
- Hard ban on maintainer-driven change — rejected: that ban silences the
  primary signal source (real dogfood use).
- Explicit test, applied in review (chosen).

## Consequences

- Review checklist for any non-trivial Hedl change includes this question
  verbatim.
- "Cherry-pickable" is enforced: a feature that only works when 6 other
  features are also enabled fails the test.
- See [[ADR-013-existential-cycle-at-phase-boundaries]] — features that fail
  the question later can be culled, not grandfathered.
