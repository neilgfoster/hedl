# Maintenance

Reviewer: independent external (adversarial). Target: Hedl, read-only clone at pinned
`796639c6c926ba2535bac3a5474f5d2feb62cb28`, location `/tmp/hedl-review-UKKLTd/hedl`.
All findings reproduced first-hand.

## Summary

Hedl is a one-author project, 3 days old, 73 commits, with an unusually disciplined
engineering substrate for its age: 413 tests, a real multi-Python-version CI gate that
genuinely runs ruff/mypy/pytest/pymarkdown (not a metadata stub), a stdlib-only
enforcement test, a versioning test suite, and an explicit, self-aware backlog. Velocity
is high but is iteration, not thrash: zero reverts, churn concentrated in state files
(`.work/work.json`) and docs rather than in core logic.

The headline maintenance risk is twofold. (1) Bus factor of 1 — 71 of 73 commits are a
single human; the other 2 are Dependabot. (2) A structural drift class the project itself
ships: the GitHub workflow files cannot be symlinked (GitHub forbids it), so they are real
copies of `skill/hedl/workflows/*`, and they have drifted (checkout v6.0.2 live vs v5.0.1
in the shipped template). A `--doctor` drift detector exists and would catch this, but it
is NOT wired into CI. So a project whose entire value proposition is a deterministic
completion gate ships a drifted copy of its own gate workflow, undetected by that gate.
The project knows: backlog item WORK-0062 documents these exact defects from a prior
external review and remains open.

Intrinsic maintenance score: **6/10**.

## Bus factor & author distribution (evidence)

`git shortlog -sne HEAD`:
```
    71  Neil Foster <1370457+neilgfoster@users.noreply.github.com>
     2  dependabot[bot] <...>
```
- 73 commits total (`git rev-list --count HEAD`). 71/73 = 97% one human; remaining 2 are
  automated dependency bumps (`0531caa` ruff, `b29a558` checkout).
- First commit `2026-05-28 00:10:40`, HEAD `2026-05-30 22:41:36` — a 2.5-day window.
- **Bus factor = 1.** No co-authors, no second reviewer identity, no `CODEOWNERS` with a
  second name (CODEOWNERS is referenced in `test_install.py:704` as a projected file but
  the live repo has a single maintainer). For a personal framework this is expected, but
  it is the dominant sustainability risk: every design decision, every ADR, and the entire
  mental model live with one person. The 33 ADRs and 164 markdown files mitigate
  knowledge-loss somewhat (the rationale is written down), but operational continuity has
  no redundancy.

## Velocity / churn (evidence)

Commits per day: 36 (05-28), 23 (05-29), 14 (05-30). Decelerating, not accelerating —
consistent with an initial build sprint settling down, not runaway thrash.

- **No reverts/rewrites**: `git log --oneline | grep -iE 'revert|rewrite|redo|undo'`
  returns nothing.
- **Churn is concentrated where churn is cheap** (`git log --name-only` frequency):
  `.work/work.json` 54, `.work/session.json` 27, `README.md` 14, `.work/context.json` 13.
  These are state/journal/doc files, expected to change every session. Core logic churns
  far less: `install.py` 8, `am_i_done.py` 8, `test_am_i_done.py` 9, `test_install.py` 10.
  Logic and its tests move together — healthy.
- No single source file shows pathological rewrite churn. This is iteration, not thrash.

## Drift findings (artifact vs source, file:line, with the actual diverging values)

Three real drifts, all in the "real copy" / "generated artifact" classes (symlinked paths
cannot drift and do not):

1. **Workflow checkout pin drift (CONFIRMED — security agent's flag is correct).**
   - Live `.github/workflows/am-i-done.yml:34` and `.github/workflows/codeql.yml:32`:
     `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2`
   - Shipped template `skill/hedl/workflows/am-i-done.yml:34` and
     `skill/hedl/workflows/codeql.yml:32`:
     `actions/checkout@93cb6efe18208431cddfb8368fd83d5badbf9bfd  # v5.0.1`
   - Direction: **live is NEWER than the shipped template.** Cause (verified via
     `git log`): Dependabot bumped only the live root file in `b29a558` ("Bump
     actions/checkout from 5.0.1 to 6.0.2 (#39)"); the projected template under
     `skill/hedl/workflows/` was last touched in `9b3c230` (WORK-0030) and was not
     bumped. Dependabot only sees the live `.github/` path, so this drift class will
     recur on every future action bump. Adopters who install Hedl get the stale v5.0.1
     workflow.
   - `git ls-files -s` confirms `.github/workflows/*.yml` are NOT mode 120000 (real
     files), while 32 other paths ARE symlinks — so the workflow files are exactly the
     copy class where drift is possible, as the brief stated.

2. **`requirements-ci.txt` generated-vs-source drift (CONFIRMED).**
   - `skill/hedl/requirements-ci.txt:322`: `ruff==0.15.14`
   - `pyproject.toml:11`: `ruff==0.15.15`; `uv.lock:119`:
     `{ name = "ruff", specifier = "==0.15.15" }`
   - The file header (`skill/hedl/requirements-ci.txt:1-3`) declares: "GENERATED — do not
     edit by hand. Source of truth: uv.lock ... Regenerate: uv export --only-group dev -o
     requirements-ci.txt". Cause (verified): Dependabot bump `0531caa` ("Bump ruff from
     0.15.14 to 0.15.15 (#42)") touched `pyproject.toml` and `uv.lock` but NOT
     `requirements-ci.txt` (`git show --name-only 0531caa` lists only those two). The
     generated file is stale relative to its own declared source.
   - Impact bounded: CI uses `uv sync --frozen` (uv.lock), so CI itself is correct;
     only the documented pip-fallback path (`pip install -r requirements-ci.txt`) gets
     the stale pin. Still a credibility problem for a determinism-selling project.

3. **No `uv export` / `requirements-ci` sync check anywhere.** `grep -rln 'uv export'`
   across tests/scripts/workflows finds nothing. The only `test_install.py:713` reference
   to `requirements-ci.txt` merely asserts it is classified as NOT GitHub-parsed
   (`test_predicate_false_for_workflow_invoked_and_other_paths`) — it does not compare its
   content to `uv.lock`. So drift #2 is structurally unguarded.

Non-drifts I verified equal (so the report is calibrated, not alarmist):
`.github/dependabot.yml` == `skill/hedl/workflows/dependabot.yml`, and
`.github/PULL_REQUEST_TEMPLATE.md` == `skill/hedl/workflows/PULL_REQUEST_TEMPLATE.md`
(`diff` exit 0 for both). `codeql-action` pins match across both copies
(`7211b7c...` v4.36.0).

## CI-enforced invariants (what CI actually runs vs what's claimed — be specific)

Two workflows exist: `.github/workflows/am-i-done.yml` and `codeql.yml`.

**What `am-i-done.yml` actually runs (verified by reading it + pyproject):**
- Triggers on `pull_request` only (`am-i-done.yml:4`). **No `push` trigger** — nothing
  runs the gate on direct pushes to `main`. (codeql.yml does run on push+schedule.)
- Matrix: Python 3.11/3.12/3.13/3.14 (`am-i-done.yml:25`), `fail-fast: false`,
  10-min timeout, minimal permissions, concurrency-cancel. Well-constructed.
- Steps: `uv sync --frozen --only-group dev` then
  `uv run python .github/scripts/am_i_done.py --pr "$PR_NUMBER"` (`am-i-done.yml:39-44`).
- The dev group (`pyproject.toml:7-12`) pins `mypy`, `pymarkdownlnt`, `pytest`, `ruff`.
  Because CI installs the dev group, those tools ARE on PATH, so the gate's
  conditionally-run checks — `lint` (ruff, `am_i_done.py:904`), `types` (mypy --strict,
  `:925`), `tests` (pytest, `:954`), `markdown` (pymarkdown, `:877`) — **genuinely
  execute in CI.** This refutes any claim that the gate is a metadata-only stub: it is a
  real lint+type+test+lint-docs gate across four Python versions.
- Also enforced in the same run (all unconditional or source-tree-gated): `git`,
  `branch`, `config`, `state-sync` (`:671` — byte-compares 4 guarded framework-config
  files), `commands` (stale WORK-ID), `schemas`, `skill-meta` (SKILL.md generated table
  vs `gen_skill_metadata.py --check`, `:1343`), `docs-index` (orphan-doc check, `:1362`),
  `doc-facts` (the source-derived documentation-fact drift detector, `:1469`), plus
  `template`, `dependabot`, `threads` because `--pr` is passed.

**The gap — claimed invariants that are NOT in CI:**
- **Workflow-copy drift is not gated.** The drift detector that WOULD catch drift #1
  lives in `install.py cmd_doctor` (`install.py:728`): for GitHub-parsed projections it
  does `target.read_bytes() != source.read_bytes()` and reports
  `"DRIFT (copy differs from source — re-run install)"` (`install.py:780-782`). This is
  exactly the right check. But `--doctor` is only reachable by manually running
  `install.py --doctor` (`install.py:1001`); it is NOT in `am_i_done.py`'s check list
  (`CLI_SPEC` choices at `:1301`) and NOT invoked by `am-i-done.yml`. **It is
  local-only.** A project selling a deterministic gate does not run its own
  shipped-artifact drift detector in CI — this is the single most important invariant gap.
- **`requirements-ci.txt` regeneration is not gated** (drift #2, see above).
- **`branch`-naming is effectively unenforced in CI**: `check_branch` returns None on
  detached HEAD (`am_i_done.py:343`), and CI checkout is detached, so the convention is
  not enforced on the PR head. (Tracked as WORK-0057 in the backlog.)
- `dependabot`/`threads` checks gracefully skip on 403 (`am_i_done.py:1010,1082`), so in a
  token-restricted CI they can pass-by-skip rather than enforce.

Net: CI enforces substantially more than "only 2 workflows" suggests, and far more than a
metadata stub — but the two invariants most relevant to THIS project's stated identity
(shipped-artifact / generated-file drift) are precisely the ones left local-only.

## Strengths / Weaknesses (file:line)

Strengths:
- **413 tests** across 12 files (`grep -rh 'def test_' skill/hedl/tests/*.py | wc -l`),
  weighted toward the load-bearing scripts: `test_am_i_done.py` 131, `test_install.py`
  114, `test_versioning.py` 43, `test_check_markdown_schema.py` 31.
- **Stdlib-only enforcement test** exists: `test_stdlib_only.py:42`
  `test_consumer_scripts_stdlib_only`, plus `test_schema_and_gen.py:357`
  `test_no_third_party_imports`. This protects the core promise (consumer scripts need no
  pip installs) at test time.
- **Versioning is tested as an invariant**, not just code: `test_versioning.py:71-75`
  asserts `install.py` version == `am_i_done.py` version == `pyproject.toml` version;
  `:318,324` assert context.json project-version semantics; semver bump logic tested
  `:244-300`.
- **Drift detectors are themselves tested**: `test_am_i_done.py:602`
  `test_drift_fails_and_names_file` (state-sync); `test_schema_and_gen.py:229-257` covers
  the SKILL.md generated-section check including the tampered/stale cases. The mechanisms
  that DO run in CI are well-covered.
- **Self-aware backlog**: WORK-0062 (`.work/work.json`) documents drifts #1 and #2
  verbatim with acceptance criteria demanding a CI filecmp + `uv export` diff. The project
  diagnosed its own maintenance defect from a prior external review.

Weaknesses:
- Bus factor 1 (see above).
- Drift detector exists but unwired (the core gap).
- **164 markdown files at 3 days old** (`git ls-files '*.md' | wc -l` = 164). 33 ADRs, a
  large `.work/reviews/` tree of generated panel artifacts, 8 `docs/` files plus
  `skill/hedl/references/`. The `docs-index` and `doc-facts` checks partially automate
  doc-consistency maintenance, but the sheer volume of hand-written narrative (ADRs,
  insights, retros) is a growing maintenance surface for one person. Doc churn is already
  visible (`docs/alternatives.md` 8 edits, `getting-started.md` 7, `tiers.md` 7).
- ADR numbering has gaps (024, 029, 030, 032 absent from `.work/decisions/`) — not
  necessarily a defect (numbers may be reserved/withdrawn) but undocumented; a reader
  cannot tell "withdrawn" from "lost".

## What would raise the score

1. **Wire drift detection into CI.** Add `install.py --doctor` (or a dedicated check) to
   `am-i-done.yml`, or add an `am_i_done.py` check that filecmp's
   `skill/hedl/workflows/*` against `.github/workflows/*` and `uv export`s against
   `requirements-ci.txt`. This closes drifts #1 and #2 permanently and makes the project
   live up to its own determinism claim. (Exactly WORK-0062's acceptance criteria.)
2. **Fix the two live drifts now** (bump template checkout to v6.0.2; regenerate
   `requirements-ci.txt`).
3. **Add a Dependabot config that also targets `skill/hedl/workflows/`** (or a post-bump
   step that re-projects), so action bumps don't reopen drift #1.
4. **Reduce bus-factor exposure**: a second maintainer or at minimum a documented
   "how to take over" runbook; an ADR-index that records withdrawn numbers.
5. Enforce branch-naming on the PR head in CI (resolve detached-HEAD skip; WORK-0057).

## Scores

- **Maintenance (intrinsic) score: 6/10** — For a 3-day-old, single-author project the
  testing discipline (413 tests, stdlib-only + versioning invariants, tested drift
  detectors), the genuinely-substantive multi-Python CI gate, zero reverts, and a
  self-aware backlog are well above the norm and pull strongly upward. Held back from
  higher by: bus factor 1 (no redundancy); the central irony that the shipped-artifact and
  generated-file drift detectors are local-only while three real drifts sit live in the
  tree at HEAD; and a 164-file doc surface maintained by one person. The drifts are minor
  in blast radius (CI itself uses uv.lock; adopters get a one-minor-version-stale workflow)
  but material to a project whose pitch is determinism. Not below 6 because the fix is
  known, scoped (WORK-0062), and small.
- **Competitive-defensibility: N/A** — maintenance-only dimension.

## Confidence and why

High. Every claim was reproduced directly: `git shortlog`/`rev-list`/`log` for authorship
and churn; `git ls-files -s` for symlink-vs-copy classification; `diff` and `grep` for the
exact diverging SHAs/versions with file:line; full read of `am_i_done.py` (1706 lines) and
`am-i-done.yml` plus `pyproject.toml` to trace which checks actually execute in CI; read of
`install.py cmd_doctor` to confirm the drift detector exists and is local-only; test counts
by `grep 'def test_'`. The one thing I could not do (read-only, no execution) is run the
gate to confirm runtime pass/fail — but the CI gating logic and tool availability are
established by reading, not inference.

## Not checked

- I did not execute any code (pytest/ruff/mypy/`am_i_done.py`/`install.py --doctor`) — the
  brief is read-only. So "CI passes today" is asserted from logic, not a run.
- I did not audit the full content of all 164 markdown files for internal consistency
  beyond what `doc-facts`/`docs-index` mechanically cover; the doc-maintenance-load finding
  is about volume/churn, not a line-by-line correctness audit.
- I did not verify GitHub branch-protection settings (server-side, not in the repo); the
  gate's effectiveness depends on required-status-checks being configured there, which I
  cannot see from the clone.
- I did not deep-audit `gen_skill_metadata.py` output vs SKILL.md byte-for-byte (the
  `skill-meta` check and its tests cover this; I confirmed the mechanism exists and is
  CI-run but did not independently recompute the table).
