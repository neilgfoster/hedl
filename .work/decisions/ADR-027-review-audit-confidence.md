# ADR-027-review-audit-confidence — Review findings carry audit confidence

## Status

Proposed — 2026-05-28 — Phase 1

Pending evaluation at the next phase boundary per
[[ADR-013-existential-cycle-at-phase-boundaries]].

## Decision

`/repo-health` and `/adversarial-review` outputs carry a per-finding
confidence (or `verification_needed`) indicator. For a BLOCKING finding
marked low-confidence, the default downstream behaviour is **audit before
fix**: confirm the finding is reproducible before writing any code, and if
it is not, resolve it with a regression guard plus an evidence note rather
than a fabricated change.

## Context

The 2026-05-28 review run produced findings of both kinds. WORK-0019's
BLOCKING "printf RCE" was non-reproducible — a false positive that, taken at
face value, would have shipped a fix for a non-bug. WORK-0020's BLOCKING was
real, and the first fix attempt contained three terminal-symlink bypasses
that only a second adversarial pass caught. Reviewers are fallible in both
directions: they raise findings that are not real and they miss holes in
proposed fixes. A flat "BLOCKING" with no confidence signal gives downstream
consumers no basis for how much trust to extend, so every consumer must
either over-trust (and ship false-positive fixes) or re-audit everything
(and lose the triage value of severity).

## Prior art

Static-analysis tooling already separates severity from confidence:

- Coverity reports impact **and** a confidence/likelihood.
- CodeQL queries carry `precision` (high/medium/low) alongside severity.
- Semgrep rules carry a `confidence` metadata field.
- SARIF supports `rank`/precision so consumers can rank by trustworthiness.

Hedl is **not inventing** confidence-on-findings. What is uniquely Hedl: the
indicator is wired to a concrete behavioural protocol — low-confidence
BLOCKING triggers a mandatory audit-first step in `/iterate` (per
[[ADR-026-iterate-consults-insights]]) — rather than being a passive sort
key. What would have to change to delegate: a review tool emitting calibrated
confidence **and** a workflow engine that branches behaviour on it (audit
gate before fix). The emit half is common; the branch-behaviour half is the
Hedl-specific piece.

## Options considered

- **Treat all findings as equally authoritative** — rejected. WORK-0019
  shows this ships fixes for non-bugs.
- **Drop BLOCKING findings that cannot be auto-verified** — rejected. Loses
  real signal (many real bugs are not mechanically verifiable up front).
- **Annotate confidence and define an audit-first protocol for
  low-confidence BLOCKING findings** (chosen) — keeps the signal, calibrates
  trust, and makes the WORK-0019 audit-first response the default rather than
  an operator's manual instinct.

## Consequences

- Reviewer agent prompts and the structured output they return gain a
  confidence / `verification_needed` field; the review-output markdown schema
  in `.work/config/markdown-schemas.json` may need a corresponding required
  field.
- `/iterate` (per [[ADR-026-iterate-consults-insights]]) consumes the
  indicator: low-confidence BLOCKING → audit-first by default. This is the
  *base* trigger (confidence alone). A matching false-positive precedent from
  [[ADR-026-iterate-consults-insights]] only *strengthens* that signal; it
  does not override or replace this default.
- Confidence must be calibrated to be useful; an uncalibrated field is noise.
  The two 2026-05-28 cases (one false positive, one real-but-incompletely
  fixed) are the initial calibration anchors.
- Does not change the deterministic gate (`am_i_done.py` stays binary,
  inference-free per [[ADR-003-deterministic-over-inference]]); this concerns
  the adversarial-review layer only.
