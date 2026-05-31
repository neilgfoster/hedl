# Adversarial Review — coding (WORK-0074 --streams hardening)

**Log:** adversarial-review-2026-05-31-coding-work-0074
**Session:** in-session
**Depth:** Standard (edge-case-hunter + scope-auditor)
**Commit:** feat/streams-hardening @ pre-commit working tree

Panel: [edge-case-hunter](edge-case-hunter.md), [scope-auditor](scope-auditor.md).

Scope: `check_streams` in `skill/hedl/scripts/am_i_done.py` (docstring + an
up-front dedup) and `skill/hedl/tests/test_am_i_done.py` (TestCheckStreamsRealGit).

Verdict: **CONDITIONAL → PASS after fixes.** 1 BLOCKING (test temp-dir leak) +
several SIGNIFICANT, all resolved or rebutted.

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Test robustness (edge-case-hunter) | PASS after fix — cleanup via addCleanup; duplicate test asserts message; comment corrected |
| Hardening genuineness (scope-auditor) | PASS — added explicit dedup (real edge-case fix); the rest is test+doc hardening of a sound impl |
| Scope containment (scope-auditor) | PASS — only check_streams docs/dedup + streams tests; alternatives.md left to WORK-0070 |

## Strengths

- Adds a non-mocked, real-git two-stream exercise (the sanctioned Lume+Wyrd
  equivalent) covering overlap→exit 1 and disjoint→exit 0 end-to-end.
- Documents the conservative, file-level refusal behaviour authoritatively in the
  docstring.

## Blocking Findings

- **Temp-dir leak if `_make_repo()` raises** (edge-case-hunter) — `mkdtemp()` ran
  before the `try/finally`. Resolved: switched to `self.addCleanup(shutil.rmtree,
  repo, ignore_errors=True)` registered immediately after `mkdtemp`, so cleanup is
  guaranteed even if a setup git command raises.

## Significant Findings

- **Duplicate causes redundant git I/O** (edge-case-hunter) — Resolved by a *real*
  hardening: `streams = list(dict.fromkeys(streams))` up front in check_streams
  (explicit dedup; one diff per unique branch; no reliance on dict-overwrite).
- **Duplicate test asserted only the exit code** (edge-case-hunter) — Resolved:
  now also asserts `"clean"` in output, pinning the correct code path.
- **Misleading "diffs in CWD" comment** (edge-case-hunter) — Resolved: corrected
  to explain the diff runs against REPO_ROOT, which am_i_done.py resolves at import
  via `git rev-parse --show-toplevel` from the process CWD — so `cwd=repo` is
  load-bearing.
- **`--check streams` with empty `--streams` exits 0** (edge-case-hunter) —
  REBUTTED (accepted behaviour): "no streams = nothing to validate" is intentional
  and already locked by `test_empty_streams_passes`.

## Minor Findings

- **`_git` capture hides setup git errors** (edge-case-hunter) — accepted; per-repo
  user config is set, and `check=True` surfaces the failing command.
- **No real-git origin/main fallback test** (edge-case-hunter) — the fallback path
  is already covered by the mock test `test_git_diff_failure_falls_back_to_origin`;
  a real-git version needs remote setup for marginal gain.
- **Dogfood via constructed equivalent, not live Lume+Wyrd** (scope-auditor) —
  honest per the "or equivalent" AC; acknowledged in the test docstring + PR.

## Synthesis

The audit confirmed check_streams was substantively sound, so "hardening" here is
(a) one real edge-case fix (explicit dedup), (b) authoritative documentation of the
refusal behaviour, and (c) a real-git regression suite that locks it. The BLOCKING
test-leak and the SIGNIFICANT test/comment issues are fixed; the accepted-behaviour
and out-of-scope items are recorded.

## Next Actions

PASS → fold the WORK-0074 (+ deferred WORK-0068/0061) state transition into the
delivering PR, raise it, await operator merge. No auto-merge.
