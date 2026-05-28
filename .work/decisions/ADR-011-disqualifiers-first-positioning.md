# ADR-011-disqualifiers-first-positioning — "Don't use Hedl if…" as primary positioning

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

The README opens with a "**Don't use Hedl if…**" section, before any pitch.
The disqualifiers (minimum set):

- Small / throwaway project where ceremony costs more than it saves.
- Solo developer who does not need a traceable engineering journey.
- Happy with native Claude Code flows; no need for a deterministic gate.
- Want zero Python dependency.

The gate (see [[ADR-002-tiered-adoption]]) is the uncontested
differentiator stated second. Comparison to alternatives is third (see
[[ADR-012-managed-competitive-lifecycle]]). What Hedl does *not* do is
fourth.

## Context

Pitching to people you cannot help corrodes the pitch for people you can
help. Self-selecting adopters trust the product faster, file more useful
feedback, and bounce less.

## Options considered

- Conventional README ("Hedl is a…") — rejected: makes every reader your
  target customer.
- Disqualifiers-first (chosen) — rare; effective; pairs with
  [[ADR-010-honesty-over-marketing]] to compound trust.

## Consequences

- Drafting any README change starts with the disqualifier section, not the
  pitch.
- If a disqualifier becomes false (e.g. Hedl finally has a non-Python
  install path) it is removed and announced as a real change, not a soft
  loosening.
- Comparison section (`docs/alternatives.md`) must exist and be honest;
  see [[ADR-012-managed-competitive-lifecycle]].
