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

The gate (see [[ADR-002-tiered-adoption]]) is the primary
differentiator stated second — its *concept* is prior art (see Prior art);
what is differentiated is the deterministic, CI-symmetric, work-item-aware
*script* form, not the idea of a completion gate. Comparison to alternatives is third (see
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

## Prior art

The completion-gate concept is not original to Hedl. It comes from
[oven-sh/bun](https://github.com/oven-sh/bun)'s `CLAUDE.md` (symlinked as
`AGENTS.md`), whose "Important Development Notes" instruct: "ONLY push up changes
after running `bun bd test <file>` and ensuring your tests pass", alongside a
`claude/`-prefixed branch CI requirement. That is the direct
inspiration for `am_i_done` (reached Hedl via a contributor). bun's gate is
prose the agent is trusted to follow; Hedl's refinement is the *deterministic*
script form (no inference; one exit code; run identically in CI; work-item
aware). Per [[ADR-010-honesty-over-marketing]], this origin must be
acknowledged wherever the gate is described as a differentiator.

## Amendment — 2026-05-30 (Phase 2)

"Uncontested differentiator" softened to "primary differentiator" with explicit
bun prior-art (above), per the operator principle that unacknowledged prior art
is theft. WORK-0066.

