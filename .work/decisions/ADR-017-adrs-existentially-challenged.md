# ADR-017-adrs-existentially-challenged — ADRs are existentially challenged

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Every new ADR must include a `Prior art` section (or its equivalent inside
`Options considered`) that names existing standards, conventions, or
practices it overlaps. If overlap exists, the ADR must answer three
questions:

- What is genuinely different about Hedl's version?
- Why is the difference worth the cost of being non-standard?
- What would have to change for Hedl to delegate to the existing thing
  instead?

Where no overlap exists, the ADR states that explicitly.
`existential-challenger` will be added to
`.work/config/dispatch-rules.json` as a mandatory reviewer for any
`.work/decisions/*.md` write so the check is gate-enforced rather than
aspirational. This requires promoting `existential-challenger` from the
review library to a named agent first; the promotion is tracked as a
backlog work item.

## Context

ADRs are cheap to write and load-bearing once written. Without an
upstream existential check, the framework drifts toward Hedl-specific
labels for things that already have well-known names. The result is
inflated cognitive load and silent contradiction with
[[ADR-010-honesty-over-marketing]].

[[ADR-012-managed-competitive-lifecycle]] handles capabilities under
competitive pressure once they exist;
[[ADR-013-existential-cycle-at-phase-boundaries]] runs an existential
review at phase boundaries. Both act *after* an ADR has been written.
This ADR is the upstream filter that prevents capabilities from being
added without justification in the first place.

## Prior art

The pattern of "justify the existence of every architectural decision"
is not novel; it is a long-standing practice in software architecture
literature (Michael Nygard's original ADR template explicitly asks
"what other patterns were considered"). What is uniquely Hedl here:

- The `Prior art` section is **mandatory and gate-enforced**, not
  optional. Most ADR practice treats the analysis as best-effort.
- Enforcement via a dedicated review agent (`existential-challenger`)
  on every ADR write closes the discipline loop deterministically.

What would have to change for Hedl to delegate: an ADR template / tool
that bakes in mandatory prior-art analysis with automated review
enforcement. None ship this in the open-source ecosystem today.

## Options considered

- **No upstream check, rely on phase-boundary review only** — rejected.
  The ADR is already load-bearing by the time
  [[ADR-013-existential-cycle-at-phase-boundaries]] reaches it.
  Catching unjustified decisions earlier costs less.
- **`existential-challenger` as advisory reviewer** — rejected. Without
  gate enforcement, the discipline is aspirational and decays.
- **Per-ADR `Prior art` requirement with `existential-challenger` as
  mandatory reviewer** — chosen.

## Consequences

- New ADRs take longer to write — one additional section to fill.
- ADRs become more defensible and easier to surface in
  `docs/alternatives.md` (per
  [[ADR-012-managed-competitive-lifecycle]]).
- Most ADRs will explicitly acknowledge they are applying an existing
  pattern. This is good — it is honest about not inventing.
- `existential-challenger` must be promoted from
  `skill/hedl/references/review-library.md` to a named agent at
  `.claude/agents/existential-challenger.md` (mirroring how
  `determinism-auditor` was promoted previously). Promotion is tracked
  as a backlog work item.
- After promotion, `.work/config/dispatch-rules.json` adds
  `existential-challenger` as mandatory for any `.work/decisions/*.md`
  write.
- ADR-001 through ADR-016 do not currently include `Prior art`
  annotations. A retrospective audit work item is created to bring
  them into compliance; ADR-017 does not block on the audit.
