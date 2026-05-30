# security-auditor — WORK-0007 review

**Run:** adversarial-review-2026-05-30-architecture-work-0007
**Model:** claude-opus-4-8
**Commit:** 5848141..6bb210a

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → deferred | Trust boundary | attacker-controllable issue title can inject a synthetic live WORK-ID (suppress a stale-ID flag) | am_i_done.py `_load_work_items_github`; backends.md | Documented (Known limitations); label-scoped read → WORK-0032; opt-in/unused today |
| SIGNIFICANT → deferred | Trust boundary | `--state open` only + mutable issue state; closures can DoS the check | am_i_done.py read path | Documented; anchored by fork/PR approval (WORK-0021); folds into WORK-0032 |
| MINOR → deferred | Info disclosure | `gh` stderr surfaced (truncated) in gate output may leak hostname/API detail | am_i_done.py gh-failure path | Noted in backends.md; pre-existing; WORK-0032 |
| MINOR → noted | Resource | `json.loads` on unbounded `gh` output | am_i_done.py | Low risk (run() captures regardless); not fixed |
| MINOR → confirmed-safe | ReDoS | `_WORK_ITEM_ID_RE` is anchored, no backtracking amplification | am_i_done.py:469 | Non-finding |

## Recommendations

- The cluster (title identity + no label filter) is real but is the WORK-0032
  build, not a WORK-0007 defect; the backend is off by default and Hedl has not
  adopted it. Make `hedl:work` the identity filter as part of WORK-0032 so the
  switch is non-breaking on a then-still-small issue set.
