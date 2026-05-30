# security-auditor — WORK-0048 review

**Run:** adversarial-review-2026-05-30-architecture-work-0048
**Model:** claude-opus-4-8
**Commit:** 7b2cce4..b102b6b

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| MINOR → fixed | Info disclosure | `{exc}` in the OSError message can carry a kernel-supplied absolute path | install.py _load_tiers | Fixed — OSError clause uses `exc.strerror` |
| MINOR → fixed | Granularity | OSError (perms) grouped with JSON parse → conflated diagnostics | _load_tiers | Fixed — separate OSError vs ValueError clauses |
| MINOR → addressed | Trust boundary | non-dict JSON crashes callers past the TiersConfigError catch | install.py cmd_install | Addressed — shape guard raises TiersConfigError |

## Recommendations

- json.load is safe (no exec). TIERS_FILE in the message is the install's own
  path — actionable, not sensitive. Post-fix the full malformed-manifest surface
  exits cleanly.
