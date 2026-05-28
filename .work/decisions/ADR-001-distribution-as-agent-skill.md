# ADR-001-distribution-as-agent-skill — Distribution = Agent Skill

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Hedl is distributed as a Claude Agent Skill. `skill/hedl/` is the single source
of truth. `.work/`, `.github/`, and `.claude/` in any consumer repo are
`install.py` *projections* of the skill — not authored content.

## Context

The product needs to (a) reach across harnesses (Claude Code today, others
later), (b) be installable with one command into an arbitrary repo, and (c)
remain coherent under updates — projections regenerate, authored state does
not.

## Options considered

- Distribute as a CLI tool / Python package — rejected: forces a runtime
  dependency on consumers and ties us to a single harness.
- Distribute as a repo template — rejected: forks the source-of-truth on day
  one; no migration story.
- Distribute as a Claude Agent Skill (chosen) — one symlinked directory in the
  consumer repo, deterministic projections via `install.py`, multi-harness
  reach as harnesses adopt the Skill spec.

## Consequences

- Every file outside `skill/hedl/` in a consumer repo is regenerable. Authored
  edits to projected files will be overwritten by `install.py`.
- Adding a new behaviour means: (1) author in `skill/hedl/`, (2) declare the
  projection in `tiers.json`, (3) update `install.py` if the projection
  shape is new. No three-of-these-is-the-source-of-truth ambiguity.
- See [[ADR-003-deterministic-over-inference]] for why projection is a script,
  not an LLM task.
