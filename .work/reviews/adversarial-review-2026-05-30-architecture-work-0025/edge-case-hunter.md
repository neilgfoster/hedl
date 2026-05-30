# edge-case-hunter — WORK-0025 review

**Run:** adversarial-review-2026-05-30-architecture-work-0025
**Model:** claude-opus-4-8
**Commit:** dba822f..883a12d

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| BLOCKING → resolved | Unhandled exception | open()/read with no try/except crashes the gate (PermissionError) | am_i_done.py `_read` | Resolved — OSError-wrapped, clean FAIL |
| SIGNIFICANT → resolved | False-green | missing template tree → silent skip | am_i_done.py | Resolved — framework-repo-scoped FAIL on missing tree |
| SIGNIFICANT → resolved | Type confusion | directory at guarded path → IsADirectoryError crash | am_i_done.py `_read` | Resolved — isfile guard |
| SIGNIFICANT → resolved | Broken symlink | dangling symlink mis-reported as missing | am_i_done.py `_read` | Resolved — lexists distinguishes "not a regular file" |
| SIGNIFICANT → resolved | TOCTOU | exists→open race | am_i_done.py `_read` | Resolved — OSError wrap covers it |
| MINOR → resolved | Vacuous pass | empty `_STATE_SYNC_GUARDED` passes with 0 comparisons | am_i_done.py | Resolved — explicit FAIL |
| MINOR → resolved | Test gaps | live-side-missing / dir / unreadable untested | test_am_i_done.py | Resolved — branch tests added |
| MINOR → accepted | CRLF | byte-compare treats CRLF ≠ LF | am_i_done.py | Accepted — intentional; both copies share checkout treatment |

## Recommendations

- All crash paths now FAIL cleanly rather than emitting a traceback. The new
  tests exercise each branch (directory-at-path, broken/escaping symlink,
  unreadable via scoped mock, missing tree, empty set).
