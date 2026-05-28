# ADR-006-pristine-repo-history — Repo history is intentionally pristine

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Hedl's git history begins with a single bootstrap commit. The scaffolding
history that produced it (the iterations, dead ends, and rebases) deliberately
exists nowhere in this repo. No `CHANGELOG-bootstrap.md`, no archived
`.work/` snapshot.

## Context

Bootstrapping a framework involves throwaway scaffolding. Carrying the
scaffolding's history in the framework's history would (a) confuse adopters
about what is supported, (b) couple the framework to its bootstrap's
particular choices, and (c) bloat the repo with content nobody can act on.

## Options considered

- Preserve the bootstrap branch — rejected: see (a)–(c) above. Also leaks
  pre-publication state that may include private decision-making.
- Squash and rebase but keep a CHANGELOG — rejected: a build CHANGELOG is
  half-information that invites "but why did you change X?" questions whose
  answers were intentionally discarded.
- Single bootstrap commit, no build CHANGELOG (chosen).

## Consequences

- Future contributors will not find a "history" to mine. The ADRs in this
  directory are the history.
- Reviewers seeing a one-commit history should not treat it as a defect.
  Recorded in [[ADR-016-preserved-decisions]] so this is not "helpfully fixed."
- Project CHANGELOG (consumer-facing, per `change_class`) is unrelated and
  begins now. See [[ADR-004-two-version-axes]].
