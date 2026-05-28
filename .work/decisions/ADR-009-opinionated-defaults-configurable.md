# ADR-009-opinionated-defaults-configurable — Opinionated defaults, configurable

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Hedl ships the maintainer's preferences as **defaults**. Anything
*mandatory* must independently justify itself (security, correctness,
gate behaviour). Configurability lives in `hedl.toml`.

## Context

A framework with no opinions is shapeless and gets no traction. A framework
that forces its opinions on every consumer is narrow and gets no adoption.
The middle path: have opinions, ship them as defaults, leave an escape
hatch.

## Options considered

- No defaults (config required) — rejected: install-day friction kills
  adoption.
- Mandatory opinions (no `hedl.toml` flags) — rejected: indistinguishable
  from "personal OS," fails [[ADR-008-framework-vs-lume-test]].
- Opinionated defaults plus `hedl.toml` overrides (chosen).

## Consequences

- When a maintainer reflex turns into "Hedl should require this," ask first:
  should it be a default instead? Default is the safer landing zone.
- Mandatory behaviours must trace to a tangible justification — gate
  determinism, security, schema integrity. "Because I prefer it" is not a
  justification for mandatory.
- `hedl.toml` is the public API for overrides. Adding a new mandatory
  behaviour without an override is a deliberate, justified decision.
