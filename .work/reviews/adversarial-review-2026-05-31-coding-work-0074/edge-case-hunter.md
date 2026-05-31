# edge-case-hunter — WORK-0074 (--streams hardening)

**Run:** adversarial-review-2026-05-31-coding-work-0074
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** feat/streams-hardening @ pre-commit working tree

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| BLOCKING | Temp-dir leak: `mkdtemp()` ran before the `try/finally`, so a `_make_repo` failure orphans the dir. | test_am_i_done.py TestCheckStreamsRealGit. | FIXED — `self.addCleanup(shutil.rmtree, repo, ignore_errors=True)` registered right after mkdtemp; try/finally removed. |
| SIGNIFICANT | Duplicate input → redundant git diff per duplicate (dedup was only an implicit dict-overwrite). | check_streams loop. | FIXED (real hardening) — `streams = list(dict.fromkeys(streams))` up front. |
| SIGNIFICANT | Duplicate-stream test asserted only returncode 0 — couldn't distinguish the right code path. | test_duplicate_stream_is_not_self_overlap. | FIXED — now asserts `"clean"` in output. |
| SIGNIFICANT | Comment "check_streams diffs in CWD" is imprecise: diff runs via REPO_ROOT (resolved at import from CWD by `git rev-parse --show-toplevel`); `cwd=repo` is load-bearing. | test _run_gate comment. | FIXED — comment corrected. |
| SIGNIFICANT | `--check streams` with empty `--streams` exits 0. | main() dispatch + check_streams guard. | REBUTTED — intentional ("no streams = nothing to validate"); locked by test_empty_streams_passes. |
| MINOR | `_git` capture_output hides git stderr on setup failure. | _git helper. | ACCEPTED — per-repo user config set; check=True surfaces the command. |
| MINOR | No real-git origin/main fallback test (shallow/detached CI). | tests. | NOTED — fallback covered by the mock test test_git_diff_failure_falls_back_to_origin; documented in the docstring. |

## Recommendations

Guarantee cleanup; dedup explicitly; pin the duplicate test; correct the comment.
All applied. Accepted-behaviour and mock-covered items recorded.
