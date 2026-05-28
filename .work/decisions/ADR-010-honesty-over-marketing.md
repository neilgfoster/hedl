# ADR-010-honesty-over-marketing — Honesty over marketing

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

No public claim ships without runnable, reproducible evidence. The
following are **banned** from README, CHANGELOG, PR descriptions, and
website copy:

- Percentage-gain claims without a runnable benchmark in the repo.
- Comparative superlatives ("the fastest," "the best," "most-loved").
- Vibes-grade testimonials.

**Encouraged**:

- "X enforces Y — see test Z."
- "Z run produced this artifact at `<link>`."
- "Here is what Hedl does *not* do."

## Context

Trust in developer tools compounds slowly and burns instantly. One
unverifiable claim corrodes every adjacent claim. See
[[ADR-011-disqualifiers-first-positioning]] for the positive expression of
this: leading with disqualifiers signals honesty before pitching anything.

## Options considered

- Standard marketing ("conversion-optimised landing") — rejected: see
  trust dynamics above.
- Pure docs, no positioning — rejected: adopters need to know what they're
  getting; absence of pitch is not honesty, it's poor communication.
- Evidence-bound claims only (chosen).

## Consequences

- Every claim links to a test, a script, or a runnable artifact in the repo.
- Reviewers can and should reject unverifiable claims with no further
  argument required.
- Reactive improvement (see [[ADR-005-self-improvement-human-gated]]) means
  evidence quality improves with use; honest copy is also less work because
  there is less to maintain.
