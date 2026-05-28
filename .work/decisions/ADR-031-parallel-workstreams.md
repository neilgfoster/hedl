# ADR-031-parallel-workstreams — Dependency edges, gate-enforced parallel

## Status

Proposed — deferred — 2026-05-28 — Phase 1

Captured but **gated**: the manual existential review (per the WORK-0005
stopgap) rated this CONDITIONAL — genuine architecture, but the edge schema is
premature while its carrier (WORK-0010, recursive workstream data model) does
not yet exist and no real workload has demanded it. Held in the ADR-021 style:
recorded so the design is not lost, but it becomes a live decision only when
**WORK-0010 lands and a real Lume workload** can validate the edge fields. The
team-tier read path interacts with WORK-0007 (github-issues backend audit). The
build-vs-delegate choice (e.g. delegate the graph to CCPM, wrap with gate +
journey) stays open per [[ADR-012-managed-competitive-lifecycle]] and is
re-evaluated at each [[ADR-013-existential-cycle-at-phase-boundaries]] boundary
alongside the other Proposed ADRs (025-028).

## Decision

Workstreams (per [[ADR-019-workstreams-as-unit-of-work]]) gain dependency edges:
`depends_on`, `parallel`, and `conflicts_with`. Storage is tier-graded: the
lightweight tier stores edges in `.work/`; the team tier reads them from the
backend's native primitives (GitHub sub-issues, Jira parent/child — per
[[ADR-022-pm-system-pluggability]]). A **deterministic** orchestrator (graph
traversal, no LLM — per [[ADR-003-deterministic-over-inference]]) identifies
which items are parallelizable from the edges. File isolation across parallel
streams is gate-enforced by the existing `am_i_done.py --streams` check.

Scope is the **graph + identification only**. Autonomous dispatch/execution of
parallel streams is [[ADR-021-beyond-single-repo-orchestration]] (Deferred)
territory and is explicitly out of scope here.

## Context

Solo, flat, one-item-at-a-time work needs none of this. But real projects have
independent items that could run in parallel, and today there is no declared
way to say which. The `--streams` check already enforces file isolation across
parallel worktree branches; what is missing is the dependency graph that says
*what may run together* in the first place. Workstreams ([[ADR-019-workstreams-as-unit-of-work]])
are the natural carrier for those edges, and the data-model work to hold them
is already backlogged (WORK-0010).

## Prior art

Dependency graphs and parallel scheduling are deeply prior:

- CCPM — dependency-aware project management built for Claude Code.
- Make / Bazel / Nx — build systems whose entire job is a dependency DAG with
  parallel execution.
- Every PM tool — Jira/Linear "blocks/blocked-by", GitHub sub-issues.

Hedl is **not inventing** dependency edges or parallel scheduling. What is
uniquely Hedl: each parallel stream is **gate-validated** independently
(`am_i_done.py` per stream + `--streams` file-isolation), **journey-captured**
per stream, and the edges are **tier-graded** (local `.work/` vs backend-native
per [[ADR-022-pm-system-pluggability]]). Why worth the cost: the gate +
per-stream isolation is the safety property that makes parallel agent work
mergeable without conflict — that is Hedl's contribution, not the graph itself.
What would make Hedl delegate: if CCPM's dependency model and execution prove
good when actually used on a real project (Lume), the right move is to delegate
the graph/execution to CCPM and have Hedl wrap it with gate + journey, per
[[ADR-012-managed-competitive-lifecycle]] — not build a native scheduler. This
ADR therefore commits only to the **edge schema + deterministic identification +
gate-enforced isolation**, leaving build-vs-delegate open.

## Options considered

- **No dependency model; parallelism stays ad hoc** — rejected: there is no
  safe, declared way to identify what can run together.
- **Build a full Hedl-native orchestrator/scheduler now** — rejected/deferred:
  large surface, [[ADR-021-beyond-single-repo-orchestration]] territory, and
  likely better delegated (CCPM) than built.
- **Define edges + deterministic identification + gate-enforced isolation,
  defer execution/dispatch** (chosen) — minimal substrate that composes with the
  existing `--streams` check and leaves the build-vs-delegate choice for later.

## Consequences

- Depends on WORK-0010 (recursive workstream model) to hold `depends_on` /
  `parallel` / `conflicts_with`.
- The team-tier read-from-backend path interacts with WORK-0007 (backend audit)
  and [[ADR-022-pm-system-pluggability]].
- `--streams` already provides the file-isolation gate; no new gate check is
  required for the isolation property itself.
- Autonomous dispatch stays Deferred ([[ADR-021-beyond-single-repo-orchestration]]).
- Build-vs-delegate (e.g. CCPM) is decided later under
  [[ADR-012-managed-competitive-lifecycle]], ideally when Lume gives a real
  workload to evaluate against.
