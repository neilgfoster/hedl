# ADR-025-iterate-drives-to-pr — /iterate drives end-to-end through PR-raised

## Status

Proposed — 2026-05-28 — Phase 1

Pending evaluation at the next phase boundary per
[[ADR-013-existential-cycle-at-phase-boundaries]]. Implementation is
tracked as WORK-0034.

## Decision

`/iterate` completes a work item from activation all the way through to a
PR that is open and merge-ready: local gate green, CI green,
adversarial-review verdict resolved, fix cycles completed, zero BLOCKING
findings remaining. The operator's only checkpoint is PR review at merge
time, structurally enforced by branch protection.

The steps between "implementation done" and "PR raised" (gate, adversarial
review, fix cycles, PR creation) are mechanical and require no operator
judgement, so `/iterate` performs them rather than stopping and waiting for
a separate command. `/pr-ready` remains independently invokable for driving
an existing branch through the PR cycle without a fresh implementation step.

## Context

Today `/iterate` stops at "implementation done" and the operator must
separately invoke `/pr-ready` (or a natural-language equivalent) for every
item. Across a phase that is dozens of identical manual prompts for steps
that carry no decision. Per [[ADR-003-deterministic-over-inference]]
(Principle 1), work that a deterministic controller can do should not be
gated on an operator prompt.

The genuine operator checkpoint is PR review at merge — and branch
protection already enforces it structurally, so collapsing the
implementation→PR handoff loses no control.

## Prior art

Task-to-PR automation is well established:

- Dependabot and Renovate open PRs autonomously on a trigger.
- Autonomous coding agents (Devin, Copilot Workspace, Cursor agents) run
  task → branch → PR without a manual handoff between phases.
- CI "ship" pipelines that build, test, and open a release PR in one run.

Hedl is **not inventing** task-to-PR flow. What is uniquely Hedl: each step
to PR is gated by a *deterministic* completion gate plus an adversarial
review panel as hard preconditions, and the stop point is structurally the
PR review (branch-protected), not an agent's self-assessed "done." What
would have to change to delegate: an agent runner that bakes in a
deterministic gate + adversarial panel as PR preconditions and stops at a
human review gate. None ships this combination today.

## Options considered

- **Keep the manual `/pr-ready` handoff** — rejected. Mechanical friction
  repeated per item; the prompt carries no judgement.
- **Drive fully autonomously through merge** — rejected. Removes the
  operator's PR-review checkpoint, which branch protection makes the correct
  and sufficient gate. Merging is a human decision.
- **Drive to PR-open and merge-ready, then stop for review** (chosen) —
  removes the mechanical prompts while preserving the one checkpoint that
  matters.

## Consequences

- `skill/hedl/commands/iterate.md` extends its flow through the `/pr-ready`
  controller loop after implementation; the stop point moves from
  "implementation done" to "PR open, awaiting operator review."
- Supervised mode is preserved and *extended*: `/iterate supervised` pauses
  at the existing intra-implementation checkpoints **and** at the
  intra-pr-ready checkpoints (gate result, review verdict, fix-cycle
  outcome). Pause semantics are not stripped.
- `/pr-ready` stays a first-class, independently invokable command.
- Fix cycles are bounded, not open-ended: `/iterate` inherits `/pr-ready`'s
  existing limit (max 3 review→fix cycles, then escalate via `/stuck`), so an
  unsupervised run cannot loop indefinitely on a BLOCKING finding it cannot
  resolve — it stops and surfaces to the operator. The autonomous flow never
  silently spins.
- Branch protection becomes load-bearing: it is the structural enforcement
  of the sole operator checkpoint. If it is absent, the checkpoint is only
  conventional. WORK-0034's implementation must therefore assert branch
  protection is active before driving autonomously to PR, or degrade to
  supervised — it must not rely on the protection being there by convention.
- The operator-handoff definition is unchanged: PR open, gate green, CI
  green, review resolved, zero BLOCKING — merge-ready.
