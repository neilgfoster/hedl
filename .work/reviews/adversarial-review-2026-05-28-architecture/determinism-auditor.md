# determinism-auditor — WORK-0030 review

**Run:** adversarial-review-2026-05-28-architecture
**Model:** claude-opus-4-8
**Commit:** 8811d78

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT | Single source of truth | `_GITHUB_PARSED_NAMES` duplicates classification that can drift from tiers.json | install.py:127-131, tiers.json | Upheld — FIXED via data-driven regression test tying predicate to tiers.json |
| SIGNIFICANT | Platform variance | byte comparison can report false DRIFT under git autocrlf | install.py:163,438 | Deferred — both files share one checkout's eol treatment; theoretical |
| MINOR | Dead reference | `CODEOWNERS` in set but not in tiers.json | install.py:130 | Resolved — kept (AC#1) and covered by the drift test |

## Recommendations

- Tie `_GITHUB_PARSED_NAMES` to the real projection inventory with a test (done).
- Consider a repo `.gitattributes` `eol=lf` if Windows contributors join (out of scope).
