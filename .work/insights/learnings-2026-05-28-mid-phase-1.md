# Mid-Phase-1 dogfood learnings — 2026-05-28

**Date:** 2026-05-28
**Author:** mid-Phase-1 dogfood session
**Scope:** cross-cutting observations from operating Hedl on Hedl, not tied to
any single WORK item.

These feed future `/reflect` mining (per [[ADR-026-iterate-consults-insights]])
and the Phase-1 `/phase-complete` retrospective. Each learning records framing,
evidence, and a disposition: *observation*, *already-captured*, or
*actionable-follow-up*.

## 1. Dogfood reveals what specs hide

Three structural bugs surfaced in the first hour of real use that weeks of
design did not: `.hedl-tier` shipped with a hardcoded developer absolute path
(WORK-0016), the `.github/` workflows were committed as symlinks GitHub cannot
follow (WORK-0030), and the gate on `main` was never actually enforced
(WORK-0029). Operational experience and specification rigour are orthogonal —
neither substitutes for the other.

**Disposition:** observation.

## 2. The framework can be honest about its own wrongness

WORK-0019 resolved as a *false positive* (the reported printf RCE was not
reproducible; audit-before-fix avoided a fabricated change). WORK-0029's
root-cause hypothesis was openly corrected by WORK-0030's investigation note.
Both corrections live in `.work/insights/`. This is
[[ADR-010-honesty-over-marketing]] validated in practice rather than asserted.

**Disposition:** observation.

## 3. Audit-first emerged from operation, not design

The audit-before-fix discipline was noticed while resolving WORK-0019, then
applied prospectively by amending WORK-0021/0022/0023's acceptance criteria
(PR #24) so a future agent inherits the framing without needing this session's
memory. The discipline was discovered by doing, not designed up front.

**Disposition:** already-captured as [[ADR-026-iterate-consults-insights]]
(Proposed) — `/iterate` consults insights for the nearest precedent.

## 4. CI not running for the early PRs was the single biggest learning

PRs #2 through #15 merged "green" while the gate workflow file was an
un-followable symlink — GitHub never created a check run, so the merge button
was wired to nothing. The structural bug was found and fixed in WORK-0030
(PR #16); `required_status_checks` now enforce the four-matrix gate
(`am_i_done (3.11)`–`(3.14)`) on every merge, confirmed via `gh api` check-runs
on subsequent PR heads. This is the structural moment worth flagging in the
v0.2.0 release notes: the gate only began actually gating at #16.

**Disposition:** observation.

## 5. ADR-017 cannot yet enforce on itself

ADRs 025–028 landed (PR #26) without a gate-enforced `existential-challenger`
review, because that agent is not yet promoted to a named agent (tracked by
WORK-0005). The discipline rule ([[ADR-017-adrs-existentially-challenged]])
exists ahead of its enforcement mechanism — a real gap, not just a backlog
ordering detail. (This session ran existential-challenger manually from the
review library on the ADR-025–028 PR, which is the stopgap this learning wants
to make explicit.)

**Disposition:** actionable-follow-up — amend WORK-0005's acceptance criteria
to require that, pending promotion, `existential-challenger` is invoked manually
on every `.work/decisions/*.md` write (operator responsibility, recorded in the
PR body); or accelerate WORK-0005 ahead of the remaining backlog.

## 6. The closeout-PR pattern is unanticipated overhead

Several completed WORK items produced two PRs — the fix, then a `chore`
closeout (e.g. WORK-0029 closed out in #15, WORK-0030 filed in #14). That
roughly doubles the merge count per item. It is genuinely unclear whether the
split adds signal (separating delivered work from bookkeeping) or is just
friction; it has not been evaluated against the alternative of folding the
state update into the fix PR (which this session has been doing).

**Disposition:** actionable-follow-up — propose ADR-029 (Proposed): evaluate
closeout-PR value vs overhead at the first `/phase-complete`; default decision
rule deferred to that boundary.

## 7. External review delivers genuinely different signal

The first external adversarial review (2026-05-28) found defects a self-hosted
`/repo-health` structurally *cannot* see, because the failing condition does not
exist in this repo — e.g. install.py's consumer-routing path (WORK-0001), which
only manifests in a consumer layout. Internal and external review are
complementary, not redundant.

**Disposition:** already-captured as [[ADR-028-external-reviews-cadence]]
(Proposed). External review #2 is due after the RCE trio closes (it now has,
with WORK-0021).

## 8. Insights notes are accumulating into a learnable substrate

Four resolution notes now exist (WORK-0019, WORK-0021, WORK-0029, WORK-0030),
plus this learnings file. They are becoming a corpus a future agent could
consult before activating a new item.

**Disposition:** already-captured as [[ADR-026-iterate-consults-insights]]
(Proposed); the consuming flow (read insights at activation) is still open work.

## 9. The biggest risk is the framework rationalising its own existence

Repo-health BLOCKING #4 (goal displacement — process outweighing shipped code)
remains true today: ~4050 lines of scripts + ~4034 lines of tests and 27 ADRs
against essentially one shipped capability (the deterministic gate). Dogfooding
produces real value but *defers* the existential judgement; it does not refute
it. The genuine test arrives when Lume bootstraps on Hedl and when an external
contributor adopts it. `docs/alternatives.md` must keep honest watchlist entries
that are allowed to become culling-candidates.

**Disposition:** observation; re-checked at every `/phase-complete` via
`existential-challenger` (per [[ADR-013-existential-cycle-at-phase-boundaries]]).

## 10. Discipline reduces decision load over time — but sample size is one

Early sessions needed extensive operator guidance; by mid-Phase-1 a terse
"merge / iterate" rhythm carries the loop for a solo operator. But no second
person has yet internalised the discipline. The framework-vs-Lume test
([[ADR-008-framework-vs-lume-test]]) — "would another adopter want this?" — is
only exercised when Lume bootstraps or when an external contributor opens a PR.
Both are ahead, not behind.

**Disposition:** observation.
