# ADR-028-external-reviews-cadence — External reviews at a defined cadence

## Status

Proposed — 2026-05-28 — Phase 1

Pending evaluation at the next phase boundary per
[[ADR-013-existential-cycle-at-phase-boundaries]]. Explicitly gated: hold at
Proposed until external reviews #2 and #3 have run and demonstrated the
pattern is real before formalising to Accepted.

## Decision

External adversarial reviews (performed with consumer-context the
self-hosted repo lacks, by a reviewer outside the repo's own tooling) run on
a defined cadence rather than ad hoc: after a batch of BLOCKING fixes, after
governance closures, and before `/phase-complete`. Their outputs are
captured in-repo under `.work/reviews/external-<date>/` and reconciled into
the backlog.

## Context

The 2026-05-28 external review surfaced defects a self-hosted `/repo-health`
run structurally **cannot** find, because the failing condition does not
exist in this repo — for example the consumer-layout install-path issues
(WORK-0001), the gate-only-tier `.work/` creation (WORK-0002), and the
spec-vs-code drift (WORK-0003). A self-review is blind to anything that only
manifests in a consumer context. That argues for external review as a
recurring discipline, not a one-off. But it is a single data point so far;
committing to a mandatory cadence on one observation would be premature,
hence Proposed-and-gated.

## Prior art

Scheduled external review is standard in security and assurance:

- Periodic third-party penetration tests / security audits on a cadence.
- SOC 2 / ISO 27001 periodic external assessments.
- Scheduled third-party code and dependency audits.

Hedl is **not inventing** external-review cadence. What is uniquely Hedl:
the external adversarial review is formalised as a phase-discipline artifact
stored in-repo (`.work/reviews/external-<date>/`) that feeds directly into
backlog reconciliation, the same channel the internal panel uses — external
review becomes part of the iteration loop, not a detached compliance event.
What would have to change to delegate: an external-audit service whose output
lands as structured, in-repo, backlog-reconcilable findings on a trigger. The
audit services exist; the in-loop reconciliation contract does not.

## Options considered

- **Ad-hoc external reviews only** — rejected. Blind spots persist
  unpredictably between reviews; the cadence is what guarantees coverage.
- **Continuous external review** — rejected. Cost and reviewer-sourcing make
  it impractical, and it would dilute into rubber-stamping.
- **Scheduled at defined triggers** (chosen) — after BLOCKING batches, after
  governance closures, pre-`/phase-complete`. Held at Proposed until two more
  reviews confirm the value before it becomes mandatory.

## Consequences

- Proposes trigger points (post-BLOCKING-batch, post-governance, pre-phase
  boundary) and a storage convention: `.work/reviews/external-<date>/`. These
  specifics are themselves **provisional** on the evidence gate — reviews #2
  and #3 must validate that this schedule (not just "external review in the
  abstract") surfaces real defects. They are recorded as a starting point, not
  a decided cadence, to avoid pre-committing structure on a single observation.
- External findings are reconciled into the backlog the same way the
  2026-05-28 review was (see `meta.reconciliation_note` in `.work/work.json`).
- Open questions deferred until the gate clears: who sources/performs the
  external review, and how its cost is justified per cadence.
- Decision is **conditional on evidence**: reviews #2 and #3 must demonstrate
  the pattern surfaces real, otherwise-invisible defects before this is
  promoted from Proposed to Accepted.
