# determinism-auditor — WORK-0007 review

**Run:** adversarial-review-2026-05-30-architecture-work-0007
**Model:** claude-haiku-4-5
**Commit:** 5848141..6bb210a

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → reframed | Threshold | `>= _GITHUB_ISSUE_READ_LIMIT` is a magic-number cap; pagination would be fully deterministic | am_i_done.py | Accepted as safe-by-failing; pagination → WORK-0032 |
| MINOR → noted | Ordering | `gh issue list` order not contractually stable | am_i_done.py read path | No impact — consumer uses set membership; defensive sort optional |

## Recommendations

- The verdict is a deterministic function of backend state: same issues → same
  live-ID set; a capped read fails (never silently uses a partial set). No
  inference introduced. Pagination (WORK-0032) would make truncation impossible
  rather than a loud failure.
