# Adversarial Review — requirements (Unit A)

**Log:** adversarial-review-2026-05-31-requirements-unit-a
**Session:** in-session
**Depth:** Standard (3-agent panel + deterministic evidence-check; docs-only diff)
**Commit:** d1c789a (working tree, branch docs/external-review-framing-gap)

Panel: [scope-auditor](scope-auditor.md), [historian](historian.md), plus an
evidence-check run deterministically by the orchestrator. Panel selected by
review-dispatcher (RUN: scope-auditor, evidence-checker, historian); validated
via `am_i_done.py --check dispatch`. evidence-checker has no subagent type, so
its role (verbatim-quote verification of the six cited ADRs + WORK-0047) was
executed deterministically by the orchestrator — more reliable than inference
for verbatim quotes.

Scope: `.work/insights/external-review-framing-gap-2026-05-30.md` + the
`.work/reviews/external-2026-05-30-1/report.md` §8 amendment (Unit A docs diff).

Verdict: **PASS** (CONDITIONAL on first pass; 2 SIGNIFICANT + 2 MINOR resolved in
the same branch).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Scope containment (scope-auditor) | PASS — forensic record + one-bullet amendment; no scope creep, no pre-deciding of Unit B |
| ADR-citation consistency (historian) | PASS after fix — ADR-019 (Superseded) and ADR-021/033 (Proposed/deferred) now annotated with Status |
| Quote fidelity (orchestrator evidence-check) | PASS after fix — all six citations verified; ADR-019 quote corrected to verbatim |

## Strengths

- Stays a forensic record: forward-references the Unit B scope-narrowing ADR
  without pre-deciding it (scope-auditor clean).
- The amendment is exactly one bullet folded into the §8 Setup block, matching
  the operator spec.
- After fix, the citation list distinguishes committed (ADR-001/011/016) from
  deferred/proposed (021/033) and superseded-but-surviving (019) on its face —
  sharpening the insight's own "intent vs realized" thesis.

## Blocking Findings

None.

## Significant Findings

Both raised on the first pass; both resolved in the same branch:

- **ADR-019 cited as live evidence, but it is Superseded** (historian) — ADR-019
  Status: "Superseded — 2026-05-30" (WORK-0027). Resolved: bullet annotated
  "(Status: Superseded — ... the cross-harness portability rationale below
  survives the supersession)". The supersession targeted the recursive-workstream
  primitive, not the portability rationale at ADR-019:88-89.
- **ADR-021 (Proposed — deferred to v1.x) presented as foundational** (historian)
  — Resolved: bullet annotated "(Status: Proposed — deferred to v1.x)".

## Minor Findings

- **"foundational" mingled committed and deferred** (historian) — Resolved:
  per-ADR Status annotations; ADR-033 ("Proposed") also annotated.
- **ADR-019 quote dropped "is"** (orchestrator evidence-check) — the quote read
  "workstream state consumable" vs the ADR's "workstream state is consumable".
  Resolved: corrected to verbatim.

## Next Actions

PASS → proceed to commit + PR (operator handoff; no auto-merge per operator
instruction). No findings remain open.
