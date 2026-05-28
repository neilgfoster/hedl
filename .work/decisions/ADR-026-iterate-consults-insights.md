# ADR-026-iterate-consults-insights — /iterate consults insights for precedent

## Status

Proposed — 2026-05-28 — Phase 1

Pending evaluation at the next phase boundary per
[[ADR-013-existential-cycle-at-phase-boundaries]].

## Decision

When `/iterate` activates a backlog item, it reads `.work/insights/` for
completed-work resolution notes whose patterns match the new item (e.g.
RCE-class findings, count-drift fixes, false-positive resolutions) and
surfaces the nearest precedent to the operator/agent before work begins.
The aim is that a lesson learned on one item does not depend on operator
memory to reach the next item that needs it.

## Context

WORK-0019 (a reported RCE) turned out to be a false positive; auditing
first saved a fabricated fix. The lesson was carried forward only because
the operator manually amended WORK-0021/0022/0023's acceptance criteria
with audit-first guidance — a step that worked but does not scale and
depends entirely on someone remembering the prior item. WORK-0020, by
contrast, was a *confirmed* vulnerability; the pair shows precedent cuts
both ways and is worth surfacing automatically. Without an automatic
consult, every future agent re-derives (or misses) the same lesson.

## Prior art

Surfacing related prior work is common:

- Jira "linked issues" / "related issues"; Linear's related-work links.
- GitHub Copilot and similar tools recommending similar PRs/code.
- Case-based reasoning and nearest-neighbour retrieval in expert systems.

The closest comparator is **internal**, not external: Hedl's own
`/reflect`, which already owns `.work/insights/` (it mines
`events.jsonl` today). Honest prior-art analysis per
[[ADR-017-adrs-existentially-challenged]] must name it. What is
genuinely different from "just extend `/reflect`": the mining of insight
notes *belongs* in `/reflect`; the decision this ADR actually makes is the
*inject-at-activation timing inside the iteration loop* — surfacing the
matched precedent into the working agent's context at the moment an item
is activated, not as a separate report. Why worth a distinct decision: the
timing is what makes the precedent act on the work rather than sit in a
log. What would have to change for Hedl to delegate / consolidate: if the
phase-boundary review judges the inject-at-activation delta too thin to
stand alone, this folds into `/reflect` (extend it to mine notes) plus a
one-line `/iterate` orient step — and should be consolidated rather than
kept as a peer ADR.

Against external tools, Hedl is **not inventing** related-work surfacing.
The external delta: the consult is deterministic and file-based, injected
at work-activation rather than offered as a search, feeding a concrete
behavioural default (audit-first for matching findings, per
[[ADR-027-review-audit-confidence]]). The linking half exists in PM tools;
the inject-at-activation half does not.

## Options considered

- **Rely on operator memory** — rejected. WORK-0019's lesson reached
  WORK-0021 only by a manual, non-scaling amendment.
- **Embed precedent in each item's AC by hand** — partial; this is exactly
  the manual WORK-0019 → WORK-0021/0022/0023 amendment. Works once, does not
  generalise, and rots as items change.
- **Fold entirely into `/reflect`** (no separate decision) — a live
  consolidation candidate. `/reflect` already owns the insights directory;
  the only delta this ADR adds is activation-time injection. If that delta
  is judged too thin at the phase boundary, this ADR consolidates into a
  `/reflect` extension and is retired.
- **Automatic insights consult at activation** (chosen, pending the above) —
  generalises the manual amendment into a loop step. Depends on extending
  `/reflect` to mine `.work/insights/*.md`, not only `events.jsonl`.

## Consequences

- `/iterate`'s orient step gains a read of `.work/insights/` with a matching
  heuristic (tags/keywords on items vs notes). The match must be cheap and
  high-precision; a noisy consult would be ignored and become theatre.
- Suggests a light tagging convention on insight notes and/or work items so
  matches are deterministic rather than fuzzy.
- Relates to [[ADR-027-review-audit-confidence]]: a low-confidence BLOCKING
  finding plus a matching false-positive precedent is the strongest trigger
  for audit-first.
- Candidate `/reflect` extension: mine insight notes for recurring patterns,
  not just event counts.
