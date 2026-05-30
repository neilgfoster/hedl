# ADR-019-workstreams-as-unit-of-work — Workstreams as unit of tracked work

## Status

Superseded — 2026-05-30 — Phase 1 (was Accepted 2026-05-28, Phase 0)

Superseded by the canonical definition of "workstream" in
`skill/hedl/references/standards.md` (WORK-0027). In Hedl's shipped docs, state,
and routing, a **workstream** is one of the four fixed work classifications
(`WS-PLAN/REQ/TECH/ARCH`) — not the recursive primitive this ADR proposed. Two
live definitions of one word was the contradiction WORK-0027 resolved, and the
working four-category meaning won.

The recursive-container model below is **deferred, not rejected**: its
implementation is gated on demand (WORK-0010), and the 2026-05-29 dogfood insight
found prose templates outperform it below ~5-7 concurrent workstreams. If
WORK-0010 is ever built, a new ADR reintroduces the recursive primitive under a
name that does not collide with the work classification. The original decision is
preserved below for that context.

## Decision

A **workstream** is the unit of tracked work in Hedl. Properties:

- A workstream has a definition of done, a status, decisions, and a
  journey (per [[ADR-015-journey-capture-with-override]]).
- A workstream's items can themselves be workstreams — the structure is
  **recursive**. Depth is unlimited.
- A leaf-level workstream is what was previously called a "work item".
- A top-level workstream of release scope is what was previously called
  a "phase".

The single primitive replaces the current flat phase + work-item model.
Recursive composition handles every shape — Epic-of-Stories,
Story-with-Subtasks, single atomic deliverable.

Workstreams are storage-backend-agnostic. State lives wherever the
chosen backend places it (per
[[ADR-022-pm-system-pluggability]]).

Adoption is tier-graded and opt-in (per [[ADR-002-tiered-adoption]]):

- **Gate-only**: workstreams do not exist; no state.
- **Lightweight**: flat workstreams (leaves only) by default —
  equivalent to today's work items. Recursive composition is opt-in.
- **Team**: workstreams + backend-mediated coordination per
  [[ADR-018-multi-operator-scales-with-tier]].

## Context

The flat phase + work-item model handles single-phase work cleanly but
breaks down for any project where a unit of delivery decomposes
recursively (epic → stories → subtasks → bug-fixes). Without a
recursive primitive, Hedl either forces flattening (loses structure)
or invents parallel concepts at each level (proliferates terminology).
A single recursive primitive is simpler and matches how real
engineering work actually decomposes.

The terminology collapse (phase = top-level workstream, work item =
leaf workstream) removes two concepts and replaces them with one.
Existing ADRs reference these terms; a follow-up audit (tracked as a
backlog work item) brings their wording into alignment.

## Prior art

Recursive task decomposition is in every PM system — Jira
(epics/stories/subtasks/tasks), Linear
(projects/issues/sub-issues), GitHub Issues with the `gh-sub-issue`
extension, Asana, Notion, Scrum (epics/stories/sub-tasks). The user
explicitly invoked Scrum vocabulary. Hedl is **not inventing**
hierarchical task structures.

What is uniquely Hedl-workstreams, in combination with the other ADRs
in this series:

- Templates ([[ADR-020-workstream-templates]]) attached to a
  workstream type — most PM tools have types but no iteration
  templates.
- Deterministic gate at every workstream boundary (per
  [[ADR-014-security-quality-friction-aware]]) — most PM tools have
  status updates, not machine-validated completion.
- Journey capture (per [[ADR-015-journey-capture-with-override]]) at
  every workstream — most PM tools track what; Hedl-workstreams also
  track why.
- Cross-harness portability — workstream state is consumable from any
  agentskills.io-compatible harness, not lock-in to one vendor.

These four together are the existential justification; recursive task
trees alone would not earn Hedl's existence.

What would have to change for Hedl to delegate entirely: a PM system
that adds template-driven iteration, deterministic completion gates,
and journey capture as first-class features on top of recursive task
trees. None does today.

## Options considered

- **Keep phase + work-item flat model** — rejected. Forces structural
  decisions ("is this a phase or a work item?") that don't map to real
  work shapes.
- **Three-tier model** (phase / story / task, named explicitly) —
  rejected. Three fixed levels are arbitrary; some projects need two,
  some five.
- **Single recursive primitive** — chosen. Matches actual work shape;
  removes terminology; lets each project decide its depth.

## Consequences

- Existing `.work/work.json` schema migrates from
  `active`/`backlog`/`completed` arrays of flat items to a recursive
  tree of workstreams. Migration registry handles the conversion
  (per [[ADR-004-two-version-axes]] — `schema_version` increments).
- `.work/phases/` directory is conceptually subsumed; whether it
  retires or stays as the top-level-workstream namespace is an
  implementation decision deferred to the workstream-model work item.
- `CLAUDE.md`, `SKILL.md`, `tiers.md`, and ADRs that mention "phase"
  or "work item" will be brought into alignment via a follow-up audit
  pass (tracked as a backlog work item).
- Per [[ADR-015-journey-capture-with-override]], each workstream
  carries its own journey narrative. Recursive workstreams nest
  narratives.
- Per [[ADR-018-multi-operator-scales-with-tier]], assignees attach to
  leaf workstreams; recursive workstreams aggregate child assignments.
- Existing `WORK-0001`, `WORK-0002`, `WORK-0003` items continue to
  work unchanged — flat leaf workstreams remain the default for
  lightweight tier.
