# edge-case-hunter — WORK-0030 review

**Run:** adversarial-review-2026-05-28-architecture
**Model:** claude-opus-4-8
**Commit:** 8811d78

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| BLOCKING | Data loss | copy=True overwrites a drifted regular target with no backup | install.py:163-167 | Rejected — by design; copies are projections of skill/hedl/, doctor reports the drift |
| BLOCKING | Migration | dry-run unlink-skip path | install.py:155-181 | Withdrawn by author of finding ("this IS correct", safe in dry_run) |
| SIGNIFICANT | False negative | closed `_GITHUB_PARSED_NAMES` misses future parsed files (FUNDING.yml, ISSUE_TEMPLATE) | install.py:127-131 | Upheld — mitigated by data-driven regression test |
| SIGNIFICANT | False negative | nested workflows depth / composite actions not handled | install.py:140-141 | Deferred — no such projection exists; speculative |
| SIGNIFICANT | False green | cmd_status reports symlinked GitHub-parsed file as `ok` | install.py:338-344 | Upheld — FIXED (status now flags DRIFT) |
| SIGNIFICANT | Concurrency | no install lock | install.py:309-312 | Deferred — pre-existing, out of scope |
| SIGNIFICANT | Dry-run | read_bytes() unguarded on permission-denied target | install.py:162-163 | Deferred — pre-existing copy-mode code |
| SIGNIFICANT | Error handling | doctor read_bytes() unguarded if source missing | install.py:431-442 | Deferred — matches file's existing no-try/except convention |
| MINOR | Audit | symlink->copy migration not distinguished in status string | install.py:155-181 | Deferred — cosmetic |
| MINOR | Windows | backslash targets break predicate | install.py:134-144 | Deferred — tiers.json targets are always POSIX |
| MINOR | Migration | cmd_migrate dry-run idempotency | install.py:386 | Out of scope — cmd_migrate untouched by this diff |

## Recommendations

- Fix cmd_status false green (done).
- Lock the predicate against tiers.json drift with a test (done).
