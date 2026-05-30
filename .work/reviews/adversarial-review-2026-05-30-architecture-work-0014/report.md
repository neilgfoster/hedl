# Adversarial Review — WORK-0014 (architecture)

**Log:** adversarial-review-2026-05-30-architecture-work-0014
**Session:** in-session
**Depth:** Standard (docs/positioning; 3-agent panel)
**Commit:** 80c0e38

Panel: [historian](historian.md), [scope-auditor](scope-auditor.md),
[new-engineer](new-engineer.md). Validated via `am_i_done.py --check dispatch`.
Scope: README + getting-started positioning rewrite.
Verdict: **PASS** (one BLOCKING fixed: the dropped "Use Hedl if" section restored).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| ADR consistency | PASS after fix — ADR-011 order (disqualifiers-first) + ADR-023 "Use Hedl if" both present; claims honest (ADR-010) |
| Scope | PASS — two files; AC1/AC2 reconciled, reframe recorded |
| Newcomer clarity | PASS after fix — product defined up front; "iteration layer" glossed |

## Strengths

- Honest positioning: invisible mode and github-issues write-back both stated as
  planned/not-built; no marketing claims.
- Leads with disqualifiers per the Accepted ADR rather than the AC's misquote.

## Blocking Findings

- **historian / scope — "Use Hedl if" section dropped.** ADR-011 mandates "Don't
  use Hedl if" first AND ADR-023 mandates an explicit "Use Hedl if" qualifier; the
  restructure kept the former but deleted the latter. **Fixed:** re-added "Use
  Hedl if" (incl. the invisible-mode case, flagged planned). Both sections present.

## Significant Findings

- **new-engineer — disqualifiers land before the product is defined.** Fixed: a
  neutral one-line definition (gate + iteration-layer) now opens, before "Don't
  use Hedl if" (still ADR-011-compliant — a definition, not a pitch).
- **new-engineer — "iteration layer" undefined jargon.** Fixed: glossed on first
  use ("the per-task work → validate → done loop").
- **scope — AC1/AC2 reconciliation not recorded.** Done at the completion
  transition (reframe field), per the standards.md fold-into-PR step.

## Minor Findings

- **new-engineer — README didn't state github-issues is write-unsupported.** Fixed:
  now "read-only today; write-back planned, WORK-0012" in both places.
- invisible-mode "planned, not built" wording praised as exemplary (no action).
- getting-started anchor link works on GitHub (no action).
- alternatives.md not edited — confirmed (only README + getting-started touched).

## Next Actions

PASS → operator handoff. No fix cycle outstanding.
