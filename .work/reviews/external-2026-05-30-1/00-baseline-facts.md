# Baseline facts (recorded before any agent claims)

Recorded: 2026-05-30. All facts below come from a read-only full-history clone of
`https://github.com/neilgfoster/hedl.git` to a scratch dir. No code was run, installed, or imported.

## Pinned ref
- Default branch: `origin/main`
- Pinned commit SHA: `796639c6c926ba2535bac3a5474f5d2feb62cb28`
- `git describe --tags`: `v0.1.0-69-g796639c`
- Only tag in repo: `v0.1.0`

## Repo age / size
- First commit: 2026-05-28 00:10:40 +0100
- Last commit (at pin): 2026-05-30 22:41:36 +0100
- Repo age: ~2.5 days
- Commit count (HEAD): 73
- Tracked files: 275 (164 `.md`, 55 `.json`, 34 `.py`, 6 `.yml`, others)
- Python LOC (tracked .py): 13,714 total (incl. tests)
- Markdown LOC (tracked .md): 11,094 total

## Author distribution (`git shortlog -sne HEAD`)
- Neil Foster <1370457+neilgfoster@users.noreply.github.com> — 71 commits
- dependabot[bot] — 2 commits
- Bus factor: 1 (single human author)

## Symlinks vs copies (`git ls-files -s`, mode 120000 = symlink)
The canonical source tree is `skill/hedl/`. The repo-root operational dirs are git **symlinks**
into it (real symlinks, mode 120000 — NOT duplicated copies). Verified symlinks include:
- `.claude/agents/*.md` -> `skill/hedl/agents/*.md` (8)
- `.claude/commands/*.md` -> `skill/hedl/commands/*.md` (5)
- `.claude/scripts/*.py`, `.claude/settings.json`, `.claude/startup.sh`
- `.github/scripts/*.py` (7) -> `skill/hedl/scripts/*.py`
- `docs/agents.md`, `docs/standards.md`, `docs/spec/*-template.md`
- `.claudeignore`, `requirements-ci.txt`
Implication: any "duplication/drift between .claude and skill" claim must account for these
being symlinks, not copies. Drift is only possible where a file is a real copy, not a symlink.

## Supply chain (baseline)
- No `[project].dependencies` in `pyproject.toml` — no runtime third-party deps (stdlib-only claim consistent so far).
- Dev deps pinned exactly in pyproject `[dependency-groups].dev`: mypy==2.1.0, pymarkdownlnt==0.9.37, pytest==9.0.3, ruff==0.15.15.
- `uv.lock` present (25 locked packages); `skill/hedl/requirements-ci.txt` is `uv export`-generated with `--hash=sha256:` pins.
- GitHub Actions are SHA-pinned with version comments (actions/checkout@de0fac2…  # v6.0.2, astral-sh/setup-uv@0880764…  # v8.1.0, github/codeql-action@7211b7c…  # v4.36.0).
- Only 2 workflows present: `am-i-done.yml`, `codeql.yml`. (No standalone pytest/ruff/mypy CI workflow file — to be probed by Maintenance/Supply-chain agents: does the gate workflow run the test suite?)

## Headline features claimed (README.md, for Accuracy cross-check)
1. Deterministic completion gate — `am_i_done.py` runs identical checks locally + CI (clean tree, branch naming, PR-template, stale work-item IDs, lint, types, tests, unresolved threads, Dependabot).
2. Multi-agent adversarial review — 8 named agents + dispatcher + 18 reference reviewer prompts.
3. Phase / work-item tracking — `.work/` state files.
4. Budget-aware reviews — `budget_manager.py` (the repo's own alternatives.md marks this culling-candidate).
5. Hooks — post-edit linter + stop reminder via `.claude/settings.json`.
6. CI — SHA-pinned actions, gate on PRs, CodeQL, Dependabot.
7. Tiered install — gate-only / lightweight / team via `install.py` (reversible projections).
8. Multi-stream conflict detection — `am_i_done.py --streams`.
9. (Planned, NOT built) invisible mode (ADR-023, WORK-0013); GitHub Issues backend write-back (WORK-0012, read-only today).

## Self-assessment present
`docs/alternatives.md` is the repo's own adversarial competitive map (status values: uniquely-hedl /
watchlisted / culling-candidate / culled), with Phase-1 boundary verdicts dated 2026-05-30.
Agents must VERIFY OR REFUTE its file:line citations against code — not echo it.
