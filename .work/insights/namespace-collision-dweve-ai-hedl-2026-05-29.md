# Namespace collision: dweve-ai/hedl

**Date:** 2026-05-29
**Discovered during:** Lume bootstrap session
**Status:** Captured, not acted on. Rename/coexist question is a /phase-complete
decision, not an /iterate one.

## What was found

`dweve-ai/hedl` exists on GitHub: **Hierarchical Entity Data Language** — a Rust,
token-efficient JSON alternative for LLM applications. Snapshot at discovery:

- v2.0.0, ~73 stars, ~28 forks, Apache-2.0
- Footprint: MCP server + LSP + a published `hedl` crate on crates.io
- Active community traction in the same broad LLM-tooling ecosystem, despite a
  completely different problem domain (data-serialization language vs our
  disciplined Claude Code workflow).

## Implications

- **GitHub search collision** — their repo currently weights higher than ours.
- **crates.io `hedl` is taken** — no Rust-namespace path for us (not that we need
  one today).
- **PyPI `hedl` is still open** — directly relevant to the pip/pipx distribution
  work (WORK-0045): if that ADR is accepted, claim the name early before it goes.
- **No technical absorption value** — different domain entirely; nothing to learn
  from or integrate.

## Followups (flags for /phase-complete triage — NOT work items)

These are deliberately not backlogged. Surface them at the next phase boundary:

- `docs/name.md` gains an "Other projects named HEDL" section.
- ADR-007 (naming convention): revisit — either annotate `Status: Open question`
  or reaffirm with an explicit acknowledgment that coexistence with
  `dweve-ai/hedl` is the chosen path.
- `docs/alternatives.md` gets a namespace-collision watchlist entry.
- WORK-0045 (pip/pipx distribution) gets a "verify PyPI `hedl` still available;
  claim early" note.

## Honest take

This is the kind of finding Hedl is designed to surface forensically: capture it,
don't act on it yet. The rename question belongs at `/phase-complete`, not in an
`/iterate` loop. Given two days already spent naming this thing, the likely right
answer is **coexist and disambiguate** rather than restarting the naming exercise
— but that is the operator's call to make deliberately, with the collision on the
record.
