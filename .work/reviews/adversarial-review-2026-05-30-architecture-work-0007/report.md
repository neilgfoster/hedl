# Adversarial Review — WORK-0007 (architecture)

**Log:** adversarial-review-2026-05-30-architecture-work-0007
**Session:** in-session
**Depth:** Standard (5-agent panel)
**Commit:** 5848141..6bb210a

Panel: [security-auditor](security-auditor.md), [determinism-auditor](determinism-auditor.md),
[scope-auditor](scope-auditor.md), [edge-case-hunter](edge-case-hunter.md),
[future-engineer](future-engineer.md).
Panel selected by review-dispatcher; validated via `am_i_done.py --check dispatch`.
Scope: the github-issues backend audit + the read-path hardening (`--limit` /
truncation), backends.md, the WORK-0059 deferral.
Verdict: **PASS** (CONDITIONAL on first pass; cheap real fixes applied, the rest
documented and deferred to WORK-0032).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Security | PASS with deferral — title-injection trust gap is the documented WORK-0032 build; read is opt-in/unused today; fork-approval is the control (WORK-0021) |
| Determinism | PASS — set membership (order-independent); capped read fails loud rather than guessing |
| Scope | PASS — audit + document + cheap fix matches the approved scope; AC2/AC3 → WORK-0059, read-hardening → WORK-0032 |
| Edge cases | PASS after fix — null-title crash fixed; cap completeness reframed honestly + deferred |
| Interface durability | PASS with deferral — label-scheme/identity durability folded into WORK-0032 |

## Strengths

- The audit correctly characterised the backend as shallow/read-only and named
  every gap; the review's findings largely confirm that characterisation.
- Deferral of the multi-operator build (WORK-0059) and the read hardening
  (WORK-0032) is explicit and tracked, not silent.

## Blocking Findings

None.

## Significant Findings

- **Title-based identity, no `hedl:work` filter** (security: injection; future-
  engineer: non-Hedl collision + breaking-change-later). Root cause of the
  cluster. Documented in backends.md "Known limitations"; the label-scoped read
  is added to WORK-0032's ACs. Low live risk: backend is opt-in and unused.
- **Cap counts all open issues → false failure at scale** (edge-case, future-
  engineer). Reframed: a capped unfiltered read cannot prove completeness, so
  failing loud is the safe gate behaviour; label-scoping + pagination (WORK-0032)
  removes it. Message corrected.
- **`--limit` raise = scope creep?** (scope-auditor) — rebutted: it fixes a gap
  the audit found (the silent 200-cap dropped live IDs); AC5 covers it.
- **AC4 uses a generic test** (scope-auditor, future-engineer) — rebutted:
  `--streams` is backend-agnostic (diffs git, not the backend), so
  `TestCheckStreams::test_overlap_fails` is the correct coverage; noted in
  backends.md.

## Minor Findings

Fixed: null-title `TypeError` crash (`issue.get("title") or ""`, + test).
Documented/deferred to WORK-0032: empty-live-set not skipped for the github
backend; `gh` stderr leakage. Noted, not fixed (pre-existing, low live risk):
zero-padding non-normalisation in `_WORK_ITEM_ID_RE` (shared with local-file;
Hedl IDs are 4-digit by convention); gh ordering (no impact — set membership).

## Next Actions

PASS → operator handoff. Read-path hardening (label-scoped + paginated read,
label application, empty-set/stderr handling) added to WORK-0032; multi-operator
assignee/claim layer is WORK-0059. No fix cycle outstanding.
