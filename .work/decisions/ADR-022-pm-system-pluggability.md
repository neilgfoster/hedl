# ADR-022-pm-system-pluggability — PM-system pluggability

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Hedl does not compete with PM systems. It plugs into them. Workstream
state lives in a **pluggable backend**; Hedl's role is iteration +
deterministic gate + journey capture on top.

Supported backends and their identifiers:

- `none` — no PM tracking; gate-only adopters.
- `local-file` — local `.work/` JSON (default for lightweight tier).
- `github-issues` — GitHub Issues + sub-issues (default for team tier).
- `jira`, `linear`, `notion`, others — extensible via the backend
  adapter framework; not shipped initially.

The backend is the **system of record**. Hedl reads it, iterates over
it, writes status/journey updates back through it, and validates
completion via `am_i_done.py`. The backend's native semantics
(assignees, permissions, comments, history) are inherited.

Selection is operator-driven: `hedl.toml` declares `state_backend`;
`install.py` configures backend-specific projection (e.g.,
authentication, API endpoints). Tier transitions (per
[[ADR-018-multi-operator-scales-with-tier]]) preserve state by
migrating through the backend adapter.

## Context

A staff-engineer adopter on a team using Jira asks: "Do I have to
migrate off Jira to use Hedl?" The honest answer must be **no**. Hedl
that competes with Jira loses on adoption inertia alone. Hedl that
runs *on top of* Jira — projecting Jira tickets into iterable
workstreams while Jira remains the system of record — is the only
version of Hedl worth adopting at scale.

The state-backend abstraction already exists in `am_i_done.py`
(`state_backend = "local-file" | "github-issues"`). This ADR
generalises that pattern into an architectural commitment: any
PM-system-of-record can be a Hedl backend via an adapter.

## Prior art

Integration platforms (Zapier, n8n, Pipedream) connect arbitrary
backends but do not provide iteration discipline or deterministic
gates. Project-management aggregators (LinearB, Sleuth, Code Climate
Velocity) read PM systems for reporting but don't drive iteration.
Multi-backend task runners (Taskfile, Make, just) abstract over
execution but not over work tracking. PM-tool sync tools (Unito,
Hubstaff Tasks) mirror between PM systems but don't add an iteration
layer on top.

What is uniquely Hedl under this ADR: an **iteration-and-gate layer**
that is portable across PM substrates. The pluggability pattern is
standard; what differentiates is the layer above (templates per
[[ADR-020-workstream-templates]], gates per
[[ADR-014-security-quality-friction-aware]], journey per
[[ADR-015-journey-capture-with-override]]).

What would have to change for Hedl to delegate: a PM system that adds
template-driven iteration + deterministic completion gates as native
features. None does today; if one emerges, this ADR re-evaluates per
[[ADR-012-managed-competitive-lifecycle]].

## Options considered

- **Single backend (local-file only)** — rejected. Forces adopters off
  their existing PM systems; kills realistic adoption.
- **Compete with Jira/Linear** — rejected as a positioning choice.
  Adoption inertia is overwhelming; Hedl loses on every comparison.
- **Pluggable backends with `none` as a valid choice** — chosen. Hedl
  is the layer above; the backend is the operator's call.

## Consequences

- `state_backend` field in `hedl.toml` becomes a first-class
  configuration. `none` (gate-only) and `local-file` are no-adapter
  defaults; `github-issues` already implemented; others extensible.
- A **backend adapter contract** must be defined: read workstreams,
  write workstream state, list/claim/release, status transitions,
  comments/journey, authentication handshake. Adapters implement the
  contract; Hedl's flows consume it.
- `install.py` learns backend-specific projection (e.g., creating
  Jira custom fields, configuring webhook tokens). Backend selection
  at install time is reversible via tier transition.
- [[ADR-018-multi-operator-scales-with-tier]] multi-operator semantics
  are inherited from the backend at team tier.
- New backend adapters can be contributed via the `/contribute` flow
  (per [[ADR-005-self-improvement-human-gated]]). Each adapter must
  pass the gate and a backend-contract test suite.
- Hedl's strongest existential justification (per
  [[ADR-017-adrs-existentially-challenged]] and
  [[ADR-010-honesty-over-marketing]]) is grounded in this ADR: Hedl
  doesn't fight Jira; Hedl plugs into it.
