# Accuracy (claims vs implementation)

Target: Hedl @ `796639c6c926ba2535bac3a5474f5d2feb62cb28`, read-only clone at
`/tmp/hedl-review-UKKLTd/hedl`. Canonical source `skill/hedl/`; `.github/scripts/`,
`.claude/agents/` are symlinks into it (verified: `ls -la .github/scripts/am_i_done.py`
-> `../../skill/hedl/scripts/am_i_done.py`).

## Summary

The substance of Hedl's headline claims holds up: every gate check named in the README
exists as a function in `am_i_done.py`; budget tiers and thresholds are accurate;
stdlib-only is true and test-enforced; mypy `--strict`, pytest `testpaths`, and Dependabot
config are all real. The defects are in **counts and line-number citations**, exactly where
docs go stale:

1. `docs/alternatives.md:50` cites the check list as `am_i_done.py:1-1300`; the file is
   **1703 lines** — the range is both wrong and too short.
2. All three `--streams` citations at `docs/alternatives.md:365-366` are stale by hundreds
   of lines (`check_streams` is at 1237 not 937-981; flag at 1580 not 1147; dispatch at
   1646-1647 not 1208-1209).
3. README:84 "8 named reviewer agents, a dispatcher" double-counts: there are **7 named
   reviewer agents + 1 dispatcher = 8 files total**, not 8 reviewers plus a 9th dispatcher.

A real behavioral divergence also undercuts the marquee "same checks locally and in CI"
claim: three checks (PR template, Dependabot, threads) are gated behind `--pr` and so do
**not** run on the default local path. CI is a strict superset of local, not identical.

## Claim verification table

| Claim | Verdict | Evidence file:line | Correction if wrong |
|---|---|---|---|
| 1. `am_i_done.py` "runs the same checks locally and in CI" | **PARTIAL** | CI invokes `python .github/scripts/am_i_done.py --pr "$PR_NUMBER"` (`skill/hedl/workflows/am-i-done.yml:44`); same script via symlink. But `check_template`, `check_dependabot`, `check_pr_threads` are gated `and args.pr` (`am_i_done.py:1638-1642`). Local runs without `--pr` skip all three. | Claim should read "CI runs a superset; the `--pr`-only checks (PR template, Dependabot, threads) do not run locally unless `--pr` is passed." Same *script*, not same *check set* by default. |
| 2a. clean tree | PASS | `check_git()` `am_i_done.py:306` | — |
| 2b. branch naming | PASS | `check_branch()` `am_i_done.py:336` | — |
| 2c. PR-template validity | PASS | `check_template()` `am_i_done.py:1115` (delegates to `check_pr_template.py`) | — but `--pr`-gated (see claim 1) |
| 2d. stale work-item IDs | PASS | `check_commands()` `am_i_done.py:774` (docstring "Detect stale hardcoded work-item IDs in .claude/commands/") | Named `check_commands`, not an obvious `check_stale_*`; functionally present |
| 2e. lint | PASS | `check_lint()` `am_i_done.py:902` | — |
| 2f. types | PASS | `check_types()` `am_i_done.py:923` (runs `mypy --strict`) | — |
| 2g. tests | PASS | `check_tests()` `am_i_done.py:952` | — |
| 2h. unresolved review threads | PASS | `check_pr_threads()` `am_i_done.py:1049` | `--pr`-gated |
| 2i. Dependabot alerts | PASS | `check_dependabot()` `am_i_done.py:982` | `--pr`-gated |
| 2-extra. present-but-unclaimed checks | NOTE | `check_dispatch` (421), `check_budget` (554), `check_config` (579), `check_state_template_sync` (669), `check_markdown_schemas` (843), `check_markdown` (875), `check_skill_metadata` (1341), `check_docs_index` (1360), `check_doc_generated_facts` (1467), `check_ci` (1173), `check_streams` (1237) | README:81-83 lists 9 checks; the gate actually runs ~20. Under-claimed, not over-claimed (safe direction). |
| 3a. "8 named reviewer agents" + dispatcher | **FAIL** | `ls skill/hedl/agents/` = 8 files; one is `review-dispatcher.md`. agents.md:1 "Eight core agents"; agents.md:38 "review-dispatcher is the orchestrator... It is not itself reviewed; it reviews" | There are **7 reviewer agents + 1 dispatcher = 8 files**. README:84 phrasing implies 8 reviewers *and* a separate dispatcher (=9). Off by one. agents.md is self-consistent (8 incl. dispatcher) but contradicts README. |
| 3b. "18 composable reviewer prompts" | PASS | `grep -cE '^## ' skill/hedl/references/review-library.md` = **18** (agent-evaluator:12 ... quality-synthesizer:349) | Matches both README:84 and alternatives.md:89 |
| 4. check list spans `am_i_done.py:1-1300` (alternatives.md:50) | **FAIL** | `wc -l skill/hedl/scripts/am_i_done.py` = **1703** | Correct range is `am_i_done.py:1-1703` (or, for check defs specifically, ~306-1507). 1-1300 is stale/wrong. |
| 5a. `check_streams at am_i_done.py:937-981` (alternatives.md:365) | **FAIL** | `def check_streams` at `am_i_done.py:1237`; lines 937-981 are `check_types`/`check_tests` | Correct: `check_streams` at `am_i_done.py:1237` (body ~1237-1282). |
| 5b. CLI flag at `am_i_done.py:1147` (alternatives.md:366) | **FAIL** | `add_argument("--streams"...)` at `am_i_done.py:1580`; line 1147 is `check_template` subprocess setup | Correct: `--streams` declared at `am_i_done.py:1580`. |
| 5c. dispatch at `am_i_done.py:1208-1209` (alternatives.md:366) | **FAIL** | streams dispatch (`if only == "streams" or (streams and not only): maybe_add(check_streams(streams))`) at `am_i_done.py:1646-1647`; lines 1208-1209 are inside `check_ci` JSON parse | Correct: dispatch at `am_i_done.py:1646-1647`. |
| 6a. tiers FULL/REDUCED/MINIMAL/DEFERRED at `budget_manager.py:20-23` | PASS | docstring `budget_manager.py:20-23`; `get_tier` returns at 192/194/196/197 | tier-name definitions at 20-23 correct |
| 6b. tier logic at `budget_manager.py:187-189` | **PARTIAL** | `get_tier()` spans `budget_manager.py:186-197`; lines 187-189 are mid-function (`if budget is None`/`used =`/`cfg =`) not the threshold comparisons (191-196) | Imprecise: the tier-decision comparisons are at 191-196; thresholds themselves live in `DEFAULT_CONFIG` at 68-73. "187-189" points at function preamble. |
| 6c. thresholds 12/22/28 | PASS | `reduced_at: 12` (69), `minimal_at: 22` (71), `deferred_at: 28` (73) `budget_manager.py` | Values correct; in `DEFAULT_CONFIG`, user-overridable via `.work/budget.json` |
| 7. stdlib-only | PASS | All non-trivial imports across `skill/hedl/scripts/*.py` and `.claude/scripts/*.py` are stdlib (`shlex`, `tomllib`, `platform`, `fcntl`, `ast`, `__future__`). Enforced by `tests/test_stdlib_only.py` (static AST scan of 8 consumer scripts) | — |
| 8a. mypy `--strict` configured | PASS | `pyproject.toml:25-28` `[tool.mypy] strict = true`; `check_types` runs `mypy --strict` (`am_i_done.py:944`) | — |
| 8b. tests present, testpaths correct | PASS | `pyproject.toml:14-15` `testpaths = ["skill/hedl/tests"]`; 13 `test_*.py` files present in that dir | — |
| 8c. Dependabot config present | PASS | `.github/dependabot.yml` and canonical `skill/hedl/workflows/dependabot.yml` (622 bytes each) | — |
| 8d. CI workflow real file (not just symlink) | PASS | `.github/workflows/am-i-done.yml` is a real 1383-byte file; SHA-pinned actions (`actions/checkout@93cb6ef...`, `astral-sh/setup-uv@0880764...`); CodeQL at `codeql.yml` | — |

## Corrected factual errors found in the repo's own docs (explicit list)

1. **`docs/alternatives.md:50`** — "check list spans `am_i_done.py:1-1300`". File is **1703 lines**. Correct to `1-1703`.
2. **`docs/alternatives.md:365`** — "`check_streams` at `am_i_done.py:937-981`". Actual: **`am_i_done.py:1237`** (937-981 is `check_types`/`check_tests`).
3. **`docs/alternatives.md:366`** — "CLI flag declared at `am_i_done.py:1147`". Actual: **`am_i_done.py:1580`** (1147 is inside `check_template`).
4. **`docs/alternatives.md:366`** — "dispatch at `am_i_done.py:1208-1209`". Actual: **`am_i_done.py:1646-1647`** (1208-1209 is inside `check_ci`).
5. **`README.md:84`** — "8 named reviewer agents, a dispatcher". Actual: **7 reviewer agents + 1 dispatcher = 8 files**; the dispatcher is one of the eight, not additional. (agents.md:1 is correct: "Eight core agents".)
6. **`docs/alternatives.md:265-266`** — tier-name + threshold logic "at `budget_manager.py:20-23,187-189`". The `:20-23` (tier names, docstring) is right; `:187-189` points at `get_tier` preamble, not the threshold comparisons (191-196) or the threshold values (`DEFAULT_CONFIG` 68-73). Minor mis-cite.
7. **`README.md:43-45` / `:81-83`** — "runs the same checks locally and in CI ... clean tree, branch naming, PR template, stale work-item IDs, lint, types, tests, unresolved review threads, Dependabot." Three of these (PR template, Dependabot, threads) are `--pr`-gated and skip on the default local path; should be qualified.

## Strengths / Weaknesses

Strengths: every claimed gate check genuinely exists as a discrete function; the gate is
in fact under-claimed (runs ~20 checks vs 9 advertised). stdlib-only is real and protected
by a test. mypy strict, testpaths, Dependabot, SHA-pinned actions all verifiable. Symlink
single-source-of-truth (`skill/hedl/` canonical) is real, so local and CI run literally the
same file.

Weaknesses: docs carry stale line numbers in the one entry (`--streams`) the project itself
markets as "uniquely-hedl" — every single line cite there is wrong. The "1-1300" range is
wrong. The agent count is off by one in the README and contradicts agents.md. The "same
checks locally and in CI" headline overstates: CI is a superset because of `--pr` gating.

## What would raise the score

- Fix the four stale `am_i_done.py` line numbers in `alternatives.md:50,365,366` (the
  `--streams` block especially — it is the flagship differentiator and 100% wrong).
- Reword README:84 to "7 reviewer agents + 1 dispatcher (8 files)" or "8 core agents
  including the dispatcher," matching agents.md:1.
- Qualify README:43-45/81-83 to note the `--pr`-gated checks do not run on the bare local
  invocation, or have the local path auto-detect a PR.
- Consider a doc-facts test that asserts cited line numbers resolve to the named symbol
  (there is already `check_doc_generated_facts` at `am_i_done.py:1467` — extend it to cover
  these citations).

## Scores

- Accuracy (intrinsic) score: **6.5/10** — Core feature claims are substantively true and
  the implementation is, if anything, more capable than advertised (under-claimed checks,
  test-enforced stdlib invariant). But the doc citations are riddled with stale line numbers
  precisely in the headline "uniquely-hedl" entry (all 3 `--streams` cites wrong, the range
  cite wrong), the agent count is off by one and self-contradictory across README/agents.md,
  and the flagship "identical locally and in CI" claim is a superset relationship, not
  identity. These are exactly the defects an adversarial accuracy review must penalize.
- Competitive-defensibility: **N/A** — accuracy-only agent.

## Confidence and why

High. Every verdict is first-hand: line numbers from `sed`/`grep` on the pinned checkout,
counts from `wc -l`/`grep -c`/`ls`, config from reading `pyproject.toml`, divergence from
reading the workflow YAML and the `main()` dispatch. The only judgment call is claim 3 (8
agents): the file count (8) is objective; whether README's phrasing is "wrong" depends on
reading "8 named reviewer agents, a dispatcher" as 8+1 — which is the natural reading and
contradicts agents.md's "eight core agents [including the dispatcher]."

## Not checked

- Runtime behavior of any check (READ-ONLY; no execution).
- Whether `check_pr_template.py` / Dependabot GraphQL logic is *correct*, only that the
  functions exist and are wired in.
- Truth of the prior-art / origin attribution claims (mcp-cli, bun) — out of scope for
  implementation-accuracy; not verifiable without fetching external repos.
- Non-headline docs (getting-started, team-tier, etc.) line cites beyond those enumerated.
- `tiers.md` line cites (e.g. `:163-165`, `:41-63`) — not in the assigned claim set.
