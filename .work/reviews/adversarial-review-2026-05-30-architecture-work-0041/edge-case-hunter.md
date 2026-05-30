# edge-case-hunter — WORK-0041 review

**Run:** adversarial-review-2026-05-30-architecture-work-0041
**Model:** claude-opus-4-8
**Commit:** 4b1e43d..5021cd9

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| BLOCKING → rebutted | Unhandled exception | subprocess.run (validator) has no try/except | check_template (pre-existing) | Rebutted — pre-existing; python3 vanishing mid-run is near-impossible (am_i_done is python3) |
| SIGNIFICANT → noted | Empty stdout | gh code=0 + empty out → empty body → validator fails | check_template | Fail-closed (safe); distinction is cosmetic |
| SIGNIFICANT → fixed | Test gap | null author untested | test | Test added (fail-closed) |
| SIGNIFICANT → fixed | Test gap | is_bot=1 (non-bool) untested | test | Test added (not exempt) |
| MINOR → noted | Other bots | renovate[bot] etc. not exempt | _DEPENDABOT_LOGINS | Correct per the AC (Dependabot-only) |
| MINOR → noted | stderr | validator stderr dropped on failure | check_template (pre-existing) | Pre-existing, minor |

## Recommendations

- The exemption fails closed for every non-Dependabot/non-bot/missing-author case,
  now covered by tests. The dependabot[bot] login variant is also tested.
