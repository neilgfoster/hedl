# security-auditor — WORK-0002 review

**Run:** adversarial-review-2026-05-30-architecture-work-0002
**Model:** claude-opus-4-8
**Commit:** 5889812..480a8ac

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → rebutted | TOCTOU | is_dir() guard not atomic with helper mkdir; concurrent .work delete recreates it | budget_manager.py guard + _atomic_write/_locked | Rebutted — far-fetched on a single-operator local CLI; hardening helpers breaks their auto-create contract |
| SIGNIFICANT → out-of-scope | Trust | REPO_ROOT from git rev-parse honours GIT_DIR/GIT_WORK_TREE | budget_manager.py REPO_ROOT | Pre-existing repo-wide; not introduced here |
| SIGNIFICANT → noted | Symlinked .work | is_dir follows symlinks | guard | Far-fetched; noted |
| MINOR → fixed | Exit code | no-op returns 0 on stdout, may mislead callers | guard | Fixed — message to stderr; exit 0 = not-applicable |
| MINOR → out-of-scope | Validation | record-panel lacks _AGENT_RE validation | cmd_record_panel | Pre-existing; possible follow-up |

## Recommendations

- The guard is read-only and prevents the reported .work creation in normal
  operation. Deeper helper-level hardening is disproportionate here; the
  pre-existing input-validation gaps are a separate hardening item.
