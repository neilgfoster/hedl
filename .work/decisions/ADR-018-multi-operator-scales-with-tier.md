# ADR-018-multi-operator-scales-with-tier — Multi-operator scales with tier

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Multi-operator support is not gated by tier. It scales with tier
complexity and the chosen state backend (per
[[ADR-022-pm-system-pluggability]]):

- **Gate-only**: trivially multi-operator — stateless. Each developer
  uses the gate on their own branches; no coordination needed.
- **Lightweight**: multi-operator via local mechanisms — assignee field
  on work items, per-assignee active items, `flock`-serialised state
  writes, claim/release lifecycle. The `.work/` JSON model is
  concurrent-safe.
- **Team**: multi-operator inherited from the chosen state backend
  (GitHub Issues today; Jira, Linear, others per
  [[ADR-022-pm-system-pluggability]]). Assignees, status transitions,
  comments, and locking are the backend's responsibility.

Tier transitions (handled by `install.py` per
[[ADR-003-deterministic-over-inference]]) preserve coordination state:
claims and assignees migrate coherently in both directions. File-level
isolation across concurrent work is enforced by `am_i_done.py --streams`
at merge time.

The principle "one work item at a time" (`CLAUDE.md` Principle 4) is
clarified as **one per operator**, not one per repo.

## Context

A staff-engineer adopter assumes Hedl handles parallel work because team
tier exists and `--streams` is documented. That assumption is only
honest if every tier has a coherent multi-operator story and tier
transitions don't lose coordination state. Treating multi-operator as a
team-tier-only capability would silently violate
[[ADR-008-framework-vs-lume-test]] — lightweight-tier adopters with
teams would hit pain Hedl doesn't acknowledge.

## Prior art

File-level locking (`flock`) is standard POSIX and already used in
`budget_manager.py`. Assignee-based work tracking is standard in every
PM tool. The pattern of "claim, work, release" is universal in
distributed task queues (Celery, RQ, Resque, GitHub Actions matrix
jobs). Per-operator state with merge-time conflict resolution is the
DVCS model itself.

Hedl applies these primitives at each tier; it is **not inventing**
multi-operator coordination, only consuming and combining well-known
patterns. What is uniquely Hedl: the **tier-graded** application —
gate-only adopters pay no coordination cost, lightweight adopters get
local mechanisms without a backend, team adopters inherit from a real
PM system — with state migrating coherently between tiers.

What would have to change for Hedl to delegate entirely: every adopter
would have to use a team-tier-equivalent backend (GitHub Issues / Jira
/ Linear) from day one. The lightweight tier exists precisely because
that assumption fails for many adopters.

## Options considered

- **Team-tier-only multi-operator** — rejected. Silent gap for
  lightweight-tier teams; violates
  [[ADR-008-framework-vs-lume-test]].
- **Add multi-operator only to lightweight, keep gate and team
  unchanged** — rejected. Incoherent across tiers; team-tier already
  has multi-operator semantics via its backend.
- **Tier-graded multi-operator with transition preservation** —
  chosen.

## Consequences

- Lightweight tier gains real implementation work: assignee field,
  `meta.active_items` keyed by assignee, `flock` writes, claim/release
  lifecycle, schema migration. Tracked as a backlog item.
- Team tier needs an audit to verify the GitHub Issues backend consumes
  assignee state correctly; future PM-backend adapters (per
  [[ADR-022-pm-system-pluggability]]) inherit the same contract.
  Tracked as a backlog item.
- `install.py` migration registry gains tier-transition migrations for
  coordination state. Tracked as a backlog item.
- Principle 4 wording in `CLAUDE.md` updates from "one work item at a
  time" to "one per operator" — tracked as a backlog item.
- Lightweight-tier solo adoption is unchanged — assignees default to
  the current operator; no ceremony imposed.
