# Quality

## Summary

The Python is, for a ~2.5-day-old single-author project, unusually disciplined: consistent stdlib-only style, dataclass-based result modelling, thorough error handling that distinguishes skip / pass / fail / "fail-closed", and a genuinely defensive posture (containment checks, atomic writes + flock, allow/deny-listed command execution). Type annotations are present throughout and the project runs `mypy --strict` with only a single `type: ignore` across the consumer scripts. The dominant quality risk is `am_i_done.py` at 1703 lines / ~20 check functions in one module — it is readable but monolithic and is the obvious refactor target. Tests are real (mock-based, behavior-asserting, ~410 test functions), not trivial, though coverage is lopsided: `am_i_done.py` and `install.py` are heavily tested while `budget_manager.py`'s concurrency machinery has only 7 tests. A handful of small consistency defects exist (a hardcoded reviewer list that has already drifted from the on-disk agent roster, hardcoded `"python3"` subprocess calls vs `sys.executable` elsewhere, a docstring/exit-code mismatch). Nothing here is structurally broken; the issues are size, a little duplication, and a couple of drift hazards.

## Strengths

- Clean result modelling and uniform check contract: every check returns `CheckResult` / `Optional[CheckResult]` with a consistent `(name, passed, message, detail)` shape, and `Report` derives `passed`/`failed`/`to_dict` from it (`skill/hedl/scripts/am_i_done.py:85-117`). The `Optional` return + `maybe_add` pattern cleanly encodes "not applicable → skip" vs "fail" (`am_i_done.py:1588-1647`).
- Error handling is deliberate and mostly fail-closed where it matters. The fresh-clone diff case surfaces a hard error instead of silently returning `[]` and skipping the security floor (`am_i_done.py:382-418`); the GitHub-issues read cap fails loudly rather than dropping live IDs (`am_i_done.py:533-543`); PR-thread/CI parse failures fail closed (`am_i_done.py:1087-1092`, `1206-1215`).
- Crash- and concurrency-safety in `budget_manager.py` is real, not cosmetic: `fcntl.flock` sidecar lock around read-modify-write (`budget_manager.py:151-162`), atomic `tempfile`+`os.replace`+`fsync` writes (`budget_manager.py:121-137`), and CORRUPT-vs-MISSING distinction that quarantines bad JSON instead of silently resetting (`budget_manager.py:104-148`).
- Strong path-containment discipline in `install.py`: `_resolve_contained` does a parents-membership check (not a string `startswith`) with a documented `follow` flag matching how each path is consumed, validated before any write (`install.py:275-340`). Tier-include flattening guards cycles and depth (`install.py:229-258`).
- Type quality is high for the age/size: `mypy --strict` enabled (`pyproject.toml:25-28`), one `type: ignore` in the consumer scripts (`record_insights.py:45`), and `Callable`/`Generator`/`cast` used correctly (`budget_manager.py:37-40,140`). A static AST test enforces the stdlib-only invariant without executing anything (`tests/test_stdlib_only.py:42-58`).
- Command execution is hardened with both an allow-list and an independent denylist re-checked at the call site (defense in depth even if a caller hands in a bad allow-list) plus shell-metachar rejection and bare-name enforcement (`am_i_done.py:180-303`).
- Security-relevant subtleties are handled correctly: the Dependabot template exemption keys off `is_bot is True` *and* a verified app login, explicitly refusing body/branch spoofing (`am_i_done.py:1112,1138`); the state-sync reader strips absolute paths from `OSError` messages to avoid leaking filesystem layout (`am_i_done.py:733-738`).

## Weaknesses

- `am_i_done.py` is a 1703-line monolith holding ~20 `check_*` functions, the verify-allowlist engine, two state backends, the CLI spec, and an insights writer (`am_i_done.py:1-1703`). It is readable but well past a comfortable single-module size; the check functions are independent and would split cleanly into a `checks/` package. The self-assessment's own evidence line ("`am_i_done.py:1-1300`") undercounts the file by ~400 lines (`docs/alternatives.md:51-52`).
- Hardcoded reviewer roster that has already drifted. `record_insights.py:68-72` lists 7 reviewer names inline, but `skill/hedl/agents/` ships 8 — `existential-challenger` is missing from the list. So a fired `existential-challenger` agent is silently never recorded as a `reviewer_fired` insight. This is exactly the filesystem-drift class the project elsewhere builds a whole `check_doc_generated_facts` detector to prevent (`am_i_done.py:1467-1555`), but the insight recorder is not covered by it.
- Inconsistent interpreter invocation. `am_i_done.py` shells out with a hardcoded `"python3"` for the budget manager and PR-template subprocess (`am_i_done.py:559,562,1148`), whereas `gen_skill_metadata.py:54`, `check_markdown_schemas`/`check_skill_metadata` (`am_i_done.py:850,1346`) use `sys.executable`. On a system where the gate was launched as `python` (common in venvs/Windows) the hardcoded calls can pick a different/missing interpreter.
- Docstring/exit-code contract mismatch in `check_markdown_schema.py`: the module docstring says "Exits 0 when all validated files pass. Exits 1 when violations are found" (`check_markdown_schema.py:13-14`), but `main()` also returns 1 for "schemas file not found" and "schemas file malformed" (`check_markdown_schema.py:307-331`) — undocumented failure exits that a caller treating 1 as "violations found" would misread.
- Minor duplication. `_BRANCH_RE` is defined identically in two files (`budget_manager.py:280`, `integrations/.../stop_reminder.py:35`); the gh-auth-hint detection is centralized as `_GH_AUTH_HINTS` in `am_i_done.py:1160` but re-implemented as inline string checks in `stop_reminder.py:93`. For a stdlib-only, deliberately-no-shared-package design this is somewhat expected, but it is real drift surface.
- Stylistic inconsistency: function-local imports (`import json` at `stop_reminder.py:99`, `import subprocess` at `budget_manager.py:43`, `import datetime as _dt` at `am_i_done.py:1673`) sit alongside otherwise top-of-file import blocks. Harmless, but inconsistent with the rest of the codebase's conventions.
- Test-coverage breadth is lopsided. `test_am_i_done.py` (131 tests) and `test_install.py` (114) are thorough and assert real behavior via `mock.patch.object(M, "run", ...)` (e.g. `test_am_i_done.py:90-117`). But `budget_manager.py` — the file with the most concurrency/crash-safety surface — has only 7 tests (`test_budget_manager.py`), and there is no test that actually exercises the `flock`/atomic-write race path. The integration hook scripts under `integrations/claude-code/scripts/` have no dedicated unit tests in `tests/` beyond the insights recorder.

## What would raise the score

- Split `am_i_done.py` into a small `checks/` package (one module per logical group: vcs/dispatch/markdown/github/state) with a thin dispatcher + CLI in `am_i_done.py`. This alone removes the single biggest readability/maintainability liability.
- Derive the `record_insights.py` reviewer list from `skill/hedl/agents/*.md` (as `check_doc_generated_facts` already does) or add it to that drift detector, and fix the current missing-`existential-challenger` drift.
- Replace hardcoded `"python3"` with `sys.executable` in `am_i_done.py:559,562,1148` for consistency and venv/Windows robustness.
- Reconcile `check_markdown_schema.py`'s docstring with its actual exit codes (or use a distinct exit code, e.g. 2, for config errors as `am_i_done.py` already does for "nothing to validate").
- Add targeted tests for `budget_manager.py`'s lock/atomic-write/corruption-quarantine paths, and a couple of unit tests for the `posttooluse_lint.py` / `stop_reminder.py` hooks.
- De-duplicate `_BRANCH_RE` and the gh-auth-hint logic, accepting that a tiny shared helper module (still stdlib-only) is cheaper than the drift risk.

## Scores

- Quality (intrinsic code quality) score: 7/10 — disciplined, well-typed, genuinely defensive code; held back from higher by the 1700-line monolith, a live filesystem-drift defect in the reviewer list, and uneven test breadth.
- Competitive-defensibility score: N/A — quality-only agent.

## Confidence: high

First-hand read of all five largest scripts in full (`am_i_done.py`, `install.py`, `budget_manager.py`, `check_markdown_schema.py`, plus the integration hooks and `record_insights.py`), the test entry points, and the build config (`pyproject.toml`). Drift, duplication, and interpreter-invocation findings were each verified by direct grep against the tree (8 agent files on disk vs 7 in the list; two `_BRANCH_RE` definitions; three hardcoded `python3` call sites). The only reason this is not "very high" is that I did not read every test body or the two remaining mid-size scripts (`reflect.py`, `release.py`) in full.

## Not checked

- Runtime behavior: no script or test was executed, imported, or installed (read-only mandate). All "fail-closed"/"atomic"/"locked" claims are from reading the code, not observing it run; the `mypy --strict` / `ruff` clean state is asserted in config but not verified by running the tools.
- Full bodies of `reflect.py`, `release.py`, and `check_pr_template.py` (heads/structure only); the full bodies of most test files beyond `test_am_i_done.py` and `test_stdlib_only.py` (counted functions and spot-read assertions only).
- Markdown content, agent prompt quality, and non-Python tooling (out of dimension scope).
- Whether `gen_skill_metadata.py` output actually matches the committed `SKILL.md` (would require execution).
