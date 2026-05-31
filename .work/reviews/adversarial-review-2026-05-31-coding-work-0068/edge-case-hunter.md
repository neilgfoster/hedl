# edge-case-hunter — WORK-0068 (gate-tier CI install fix)

**Run:** adversarial-review-2026-05-31-coding-work-0068
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** 022bdc6 (working tree, branch fix/gate-tier-ci-install)

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| SIGNIFICANT | Python 3.14 may be absent from setup-python's manifest → matrix leg fails. | am-i-done.yml:28. | REBUTTED — based on stale mid-2025 data; 3.14 is GA, Hedl's own CI already runs the 3.14 matrix green, and setup-python v6.2.0 (latest) supports it. |
| SIGNIFICANT | `python3` hardcoded in check_budget/check_template diverges from the setup-python `python`. | am_i_done.py:559-562,1147. | REBUTTED (not a regression) — setup-python puts both `python` and `python3` first on PATH pointing at the installed interpreter; under the prior `uv run`, `python3` likewise resolved to the active venv. Behaviour is equivalent; the change introduces no divergence. Pre-existing pattern, orthogonal. |
| MINOR | Test scanned only `run:`-prefixed lines → multi-line run blocks could evade it. | test_install.py. | FIXED — guard now scans all non-comment, non-blank lines. |
| MINOR | `pip install` without `--require-hashes` doesn't enforce the present hashes. | am-i-done.yml install step. | FIXED — `--require-hashes` added (verified installs clean). |
| MINOR | requirements-ci.txt drift not CI-enforced. | header. | NOTED — WORK-0062 scope. |
| MINOR | check_pr_template subprocess ImportError could mask as a template failure. | am_i_done.py:1147-1157. | NOTED — pre-existing/orthogonal; check_pr_template is stdlib-only, so no missing-import path under requirements-ci.txt. |

## Recommendations

Enforce hashes (done); harden the test guard (done); leave the interpreter-name and
drift items to their own scopes (no regression here).
