# security-auditor — WORK-0025 review

**Run:** adversarial-review-2026-05-30-architecture-work-0025
**Model:** claude-opus-4-8
**Commit:** dba822f..883a12d

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → resolved | Path traversal | open() followed symlinks with no realpath containment | am_i_done.py `_read` | Resolved — realpath containment added on both roots |
| SIGNIFICANT → resolved | Resource | unbounded fh.read() (memory / device node) | am_i_done.py `_read` | Resolved — isfile guard + 1 MiB size cap |
| SIGNIFICANT → deferred-ok | Trust boundary | byte-equality can't defend against lockstep tampering of both copies | _STATE_SYNC_GUARDED | Deferred — branch protection / fork approval is the control (WORK-0021 stance); noted in docstring |
| MINOR → resolved | Info leak | `str(exc)` in the unreadable message embeds the absolute path | am_i_done.py `_read` (Copilot thread, PR #62) | Resolved — errno/strerror only |
| MINOR → resolved | Path handling | REPO_ROOT not realpath-canonicalised | am_i_done.py | Resolved — both roots realpath'd locally |

## Recommendations

- The check is read-only and never emits file contents, so exfiltration risk is
  low; the containment hardening nonetheless brings it to the gate-code bar set
  by WORK-0019/0020/0021.
- Follow-up: a shared contained-read helper across check_config and
  check_state_template_sync (codebase-wide; out of WORK-0025 scope).
