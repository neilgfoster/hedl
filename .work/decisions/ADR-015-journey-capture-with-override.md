# ADR-015-journey-capture-with-override — Journey capture as feature, with override

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Phase narrative — *problem / objective / DoD / steps / why* — is generated
by `/phase-complete`. Iteration log is appended by `/iterate`. The default
template is the maintainer's framework, opinionated.

**The template path is overridable via `hedl.toml`.** Adopters who want a
different journey shape swap it. `/reflect` mines the journey alongside
`.work/insights/`.

## Context

A traceable engineering journey is one of Hedl's value propositions, but
"my preferred narrative shape" is not universally true. Per
[[ADR-009-opinionated-defaults-configurable]], opinions ship as defaults
with escape hatches.

## Options considered

- Fixed template, no override — rejected: fails
  [[ADR-008-framework-vs-lume-test]] (narrows Hedl to maintainer-likes-it).
- No template, free-form — rejected: gives back the value proposition.
- Default template, `hedl.toml` override (chosen).

## Consequences

- Default template lives under `skill/hedl/templates/` (or equivalent),
  projected by `install.py`. Editing the projection in a consumer is
  unsupported; overriding via `hedl.toml` is.
- `/reflect` reads journey artifacts via the same path resolution — does
  not hard-code the default location.
- New template fields are additive; removing fields is a `schema_version`
  bump (see [[ADR-004-two-version-axes]]).
