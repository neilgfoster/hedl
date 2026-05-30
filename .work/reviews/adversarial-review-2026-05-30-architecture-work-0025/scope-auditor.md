# scope-auditor — WORK-0025 review

**Run:** adversarial-review-2026-05-30-architecture-work-0025
**Model:** claude-opus-4-8
**Commit:** dba822f..883a12d

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| BLOCKING → resolved | AC fidelity | AC4 ("fresh install reproduces .work/ from template") unmet — tests covered drift only | test_install.py | Resolved — reproduction test added |
| SIGNIFICANT → resolved | Hidden scope | AC2 reframed (eliminate → retain-and-guard) only in the commit message | .work/work.json WORK-0025 | Resolved — AC2 text reconciled + `reframe` field recorded |
| SIGNIFICANT → kept | Docs scope | getting-started.md documents the guard as well as the relationship | docs/getting-started.md | Kept — documenting the guard is part of AC1's "how install.py relates them" |
| MINOR → satisfied | AC1 completeness | quote the tiers.json projection line | docs/getting-started.md | Satisfied — the projection entry is quoted in the doc |

## Recommendations

- The reframe is a legitimate engineering call (deletion would break the
  projection model); recording it on the work item rather than reinterpreting
  silently was the required fix and is done.
- Cycle-2 re-review returned an empty finding set (all resolved).
