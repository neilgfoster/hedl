# security-auditor — WORK-0068 (gate-tier CI install fix)

**Run:** adversarial-review-2026-05-31-coding-work-0068
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** 022bdc6 (working tree, branch fix/gate-tier-ci-install)

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| SIGNIFICANT | New action `actions/setup-python` widens the trusted-action surface; no in-repo audit trail of SHA resolution. | am-i-done.yml:36. | PARTIALLY ACCEPTED — pinned by full SHA + version comment per the repo's existing convention (checkout/setup-uv/codeql are pinned the same way, none with a separate audit trail). SHA resolved from the v6.2.0 git tag ref via the GitHub API. A repo-wide SHA-provenance doc is a broader practice, not WORK-0068 scope. |
| SIGNIFICANT | Checkout SHA divergence: shipped v5.0.1 vs Hedl-live v6.0.2. | am-i-done.yml:34 vs .github/workflows/am-i-done.yml:34. | REBUTTED (out-of-scope) — pre-existing drift owned by WORK-0062; surgical-change principle, not touched. |
| MINOR | requirements-ci.txt IS hash-pinned (== + sha256) — no reproducibility regression vs uv.lock. | requirements-ci.txt. | NOTED — confirms the fix is reproducible. |
| MINOR | Add `--require-hashes` / `--no-deps` so hashes are enforced, not just present. | am-i-done.yml install step. | ACCEPTED (`--require-hashes`) — verified `pip install --require-hashes -r requirements-ci.txt` exits 0 in a throwaway venv; applied. `--no-deps` not added (the closure is complete; --require-hashes already locks integrity). |
| MINOR | requirements-ci.txt drift not CI-enforced. | header comment. | NOTED — WORK-0062 scope. |
| MINOR | PR_NUMBER env-var injection guard retained (safe, unchanged). | am-i-done.yml. | OK. |

## Recommendations

Enforce the hashes (`--require-hashes`) — applied. Leave checkout-SHA sync + the
drift-guard to WORK-0062.
