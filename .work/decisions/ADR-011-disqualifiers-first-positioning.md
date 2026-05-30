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

The gate (see [[ADR-002-tiered-adoption]]) is stated second, but it is **not
original** (see Prior art): the name `am_i_done` and the deterministic, CI-symmetric
design come from theshadow27/mcp-cli. What is Hedl-specific is the *packaging* — a
stdlib, LLM-agnostic, distributable tiered Skill with a tracker-aware check bundle —
not the gate itself. Comparison to alternatives is third (see
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

Hedl's completion gate is derivative, and both sources must be named.

**Direct origin — [theshadow27/mcp-cli](https://github.com/theshadow27/mcp-cli)** (created
2026-03-02, predating Hedl; MIT). It ships an `am-i-done` script (`scripts/am-i-done.ts`,
package script `am-i-done`) its `CLAUDE.md` describes as "the **single command** for checking
whether work is done — run it before committing" and "the **same command the pre-commit hook
and CI both run**, so a local pass means a green PR"; `ci.yml`, `pre-commit`, and `pre-push`
all invoke it. Hedl took both the **name** and the **deterministic, CI-symmetric design** from
there.

**Upstream concept — [oven-sh/bun](https://github.com/oven-sh/bun)** (`CLAUDE.md`/`AGENTS.md`,
"Important Development Notes"): "ONLY push up changes after running `bun bd test <file>` and
ensuring your tests pass", with a `claude/`-branch CI rule — the "run the checks before you
finish" idea, in prose.

Because mcp-cli already had the deterministic, CI-symmetric gate, that property is **not**
Hedl's differentiator. Hedl's genuine residual is only the *packaging*: a stdlib-Python,
LLM-agnostic, drop-in gate distributed as an opt-in tiered Skill for other repos, with a
work-item/PR-aware check bundle tied to a tracker. Per [[ADR-010-honesty-over-marketing]],
both origins must be acknowledged wherever the gate is described. (Attribute the projects,
not individuals.)

## Amendment — 2026-05-30 (Phase 2)

"Uncontested differentiator" softened to "primary differentiator" with explicit
bun prior-art (above), per the operator principle that unacknowledged prior art
is theft. WORK-0066.

## Amendment 2 — 2026-05-30 (Phase 2)

Prior art corrected: theshadow27/mcp-cli identified as the DIRECT origin of `am_i_done` (the
name + the deterministic, CI-symmetric design), with bun as the upstream concept. The earlier
claim (Amendment 1 / WORK-0066) that the deterministic, CI-symmetric form was Hedl's
contribution was itself unattributed prior art — mcp-cli had it first. Hedl's claim re-scoped
to packaging only. Project attributed, not the individual. WORK-0067.

