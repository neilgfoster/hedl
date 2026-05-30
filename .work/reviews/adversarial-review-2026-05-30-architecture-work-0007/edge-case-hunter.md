# edge-case-hunter — WORK-0007 review

**Run:** adversarial-review-2026-05-30-architecture-work-0007
**Model:** claude-opus-4-8
**Commit:** 5848141..6bb210a

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → reframed | Cap boundary | `>=1000` fires on ALL open issues, not WORK-issues → false failure at scale | am_i_done.py | Reframed — capped read can't prove completeness; fail-loud is safe; fix = WORK-0032 |
| MINOR → fixed | Null title | `issue.get("title","")` returns None on null title → `re.match(None)` TypeError crash | am_i_done.py read loop | Fixed — `or ""`, + test |
| MINOR → deferred | Empty set | github backend with zero open WORK-issues isn't skipped → false stale flags | am_i_done.py:786-790 | Documented; WORK-0032 |
| MINOR → noted | Zero-padding | `WORK-12` vs `WORK-0012` treated as distinct | am_i_done.py:469 | Pre-existing, shared with local-file; Hedl IDs are 4-digit by convention |
| MINOR → noted | Duplicate IDs | two open issues with the same WORK-ID silently deduped | am_i_done.py read loop | Out of scope for the stale-ID check; noted |

## Recommendations

- The null-title crash was the one genuine must-fix (uncaught traceback in the
  gate); done. The cap false-failure is a completeness limitation of the
  unfiltered read, correctly handled by failing loud and deferred to WORK-0032.
