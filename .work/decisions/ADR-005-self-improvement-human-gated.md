# ADR-005-self-improvement-human-gated — Self-improvement loop is human-gated

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

`/contribute` raises PRs against Hedl from consumer-side friction.
Branch protection on `main` plus required reviewer approval is the human
gate. `/contribute` is privacy fail-closed: it emits framework-only diffs
and refuses to include consumer code, prompts, or `.work/` content.

## Context

A self-improving framework that can merge its own PRs is a runaway system.
A self-improving framework that *cannot* receive friction reports from real
use is dead on arrival. The middle path: the loop exists, but a human signs
every merge.

## Options considered

- Auto-merge on green CI — rejected: removes the only check on a system whose
  improvements judge themselves.
- Manual PR drafting (no `/contribute` flow) — rejected: high friction kills
  the loop in practice; reactive improvement only works if reporting is
  cheap.
- `/contribute` flow plus branch protection (chosen).

## Consequences

- `main` has branch protection and required-review configured.
- `/contribute` privacy scrub is part of the gate, not advisory. A
  `/contribute` PR that includes consumer content is a security defect.
- Hedl improves reactively, not on a roadmap. See
  [[ADR-013-existential-cycle-at-phase-boundaries]] for the
  earn-your-keep counter-pressure.
