# ADR-020-workstream-templates — Workstream templates as first-class

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

A **workstream template** describes the iteration pattern of a
workstream type — how it starts, what each iteration produces, and what
the final iteration delivers. Templates are markdown documents in
`skill/hedl/templates/workstreams/`. Two reference templates ship with
Hedl:

- **Existential review**: iteration 1 = identify capability +
  competitors; iterations 2..N = investigate each competitor; final
  iteration = report and culling decision (per
  [[ADR-012-managed-competitive-lifecycle]]).
- **Problem statement**: iteration 1 = broad problem + objective;
  iterations 2..N = discovery, planning, refinement; final iteration =
  deliverables (which may themselves spawn child workstreams per
  [[ADR-019-workstreams-as-unit-of-work]]).

For v0.2, templates are **prose-form**: a markdown file the agent reads
at workstream creation and follows. Templates do not yet execute as
state machinery. Promotion to executable templates (gate-enforced
iteration transitions) is deferred to a future version once prose-form
usage exposes the right contract.

Operators can author their own templates. Default templates are
overridable per [[ADR-009-opinionated-defaults-configurable]].

## Context

Most PM systems support task **types** (bug, feature, epic) but no
template for **how to iterate** within a type. The iteration pattern is
left to convention or memory. Templates make the iteration pattern
explicit, repeatable, and shareable. They also turn "what kind of work
is this?" into a useful prediction: an existential-review workstream
takes N+2 iterations; a problem-statement workstream unfolds into
deliverables; the agent can plan and pace accordingly.

## Prior art

Closest comparators: Jira's workflow schemes (state machines, but
per-project not per-template), Notion's database templates (form-level
only, no iteration semantics), GitHub Issue templates (initial-issue
form, nothing about iteration). None encode the iteration pattern
itself. Cookiecutter and Yeoman template **artifacts** at creation, not
iteration patterns. Hedl-workstream-templates are genuinely novel as a
first-class iteration-pattern concept in dev-tooling.

What would have to change for Hedl to delegate: a PM system that
allowed attaching an iteration playbook (not just a workflow state
machine) to a task type. None does today.

## Options considered

- **Prose templates only** — chosen for v0.2. Lightweight, ships
  immediately, exposes the contract through real use before being
  hardened.
- **Executable templates from day one** — rejected as YAGNI. The
  iteration contract isn't yet known well enough to encode as
  machinery; let real use shape it.
- **Templates as runtime state machines** (gate-enforced transitions)
  — deferred. The right shape will emerge from prose-form usage.

## Consequences

- `skill/hedl/templates/workstreams/` ships with at least two
  reference templates: existential-review and problem-statement.
- Workstream creation flow consults the chosen template at start; the
  agent follows the iteration pattern from the template.
- Adopter-authored templates live alongside the shipped ones; the path
  is configurable via `hedl.toml` per
  [[ADR-009-opinionated-defaults-configurable]].
- Promotion to executable templates is a future enhancement; not
  committed here.
- First concrete use of templates: the existential-review of Hedl
  itself (Step 8 of the bootstrap plan, where existential-challenger
  produces the initial `docs/alternatives.md`), and the
  problem-statement that bootstraps Lume. Both serve as real-world
  proving ground.
