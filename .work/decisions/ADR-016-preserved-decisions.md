# ADR-016-preserved-decisions — Preserved decisions: do not "helpfully fix"

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

The items below are *intentional choices*, not defects. They have been
flagged as suspect by reviewers (human and agent) and the verdict in each
case is **keep as-is**. Future review that re-raises them should reference
this ADR and require new evidence to overturn.

## Preserved decisions

### 1. "Agents/commands duplicate native Claude Code features"

**False.** They are projected as native `.claude/agents/` and
`.claude/commands/` by `install.py` per `tiers.json` — they *are* the
native features. NL routing through `SKILL.md` is the cross-harness
fallback for harnesses that do not implement the native primitives. This
is progressive enhancement, not duplication.

### 2. "Seven-subagent reviews cost ~$0.20"

**Overstated.** The dispatcher (`dispatch-rules.json`) targets 3–4 agents
for typical diffs and caps at 5. The full panel of 8 (7 named agents today;
the 8th, `existential-challenger`, lands via WORK-0005) only runs on
`/repo-health`. Citing the cap as the typical case misrepresents the
common-path cost.

### 3. "Single squashed bootstrap commit / no build history"

**Intentional.** See [[ADR-006-pristine-repo-history]]. Adding a
`CHANGELOG-bootstrap.md` or reflating the scaffold history is explicitly
out of scope.

## Context

Reactive improvement plus thorough review will surface the same critiques
repeatedly. Recording the verdict once stops the cycle of "let me
helpfully address this" → "no, that was deliberate" rework.

## Consequences

- Future reviewers raising any of the above without new evidence can be
  pointed at this ADR with no further argument required.
- New evidence that overturns a verdict must be explicit and produces a new
  ADR (Status: Supersedes ADR-016 item N).
