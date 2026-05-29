# Hedl Adoption Tiers

Three tiers — drop in just the gate, add lightweight specs, or use GitHub Issues with
parallel execution. Each tier is a superset of the previous. Users opt up only when
the work warrants it.

---

## Tier 1 — Gate-only

**What it is**: just `am_i_done.py` and the review panel. Drop into any repo.
**Setup time**: under 2 minutes.
**Files added to your repo**: zero framework files — just `.github/scripts/am_i_done.py`
and optionally `.github/scripts/budget_manager.py`.

**What you get**:
- Binary pass/fail gate before declaring any task done (stack-agnostic — declare
  your verify commands in `hedl.toml`; Python is the bundled default profile, not
  a constraint on the consumer's stack)
- SHA-pinned GitHub Actions workflow with CodeQL
- Dispatch rule validation (mandatory reviewer floor from diff)
- PR template check

**How to install**:
```bash
curl -O https://raw.githubusercontent.com/neilgfoster/hedl/main/skill/hedl/scripts/am_i_done.py
# Place in your .github/scripts/ directory
```

> **Note:** `.github/scripts/am_i_done.py` in this repo is a symlink. The real file is
> `skill/hedl/scripts/am_i_done.py` — use that path for `curl` or any zip-export / Windows workflow
> that does not follow symlinks.

**Usage**:
```bash
python3 .github/scripts/am_i_done.py            # local checks
python3 .github/scripts/am_i_done.py --pr 42    # + PR template, threads, dependabot
```

**Stack-agnostic verification** (optional):
Add a `hedl.toml` at the repo root to declare your verification commands.
With no `hedl.toml` and a Python project present, the gate runs ruff/mypy/pytest
automatically. With `hedl.toml` the gate runs exactly what you declare:

```toml
[gate]
timeout = 120   # default per-command timeout (seconds)

# Security (WORK-0021): a [verify] command may only invoke an allow-listed
# executable, named bare (no path), with no shell metacharacters. Default:
#   pytest, mypy, ruff, npm, pnpm, make
# Extend with bare names for your stack. allowed_commands is additive and
# constrained: an entry is ignored if it has a path separator, a shell
# metacharacter, or names an interpreter/forwarder (python, sh, bash, node,
# env, xargs, find, ...) — so you cannot re-open inline code via config.
allowed_commands = ["golangci-lint", "tsc", "go", "playwright"]

[verify]
lint  = "golangci-lint run"
types = "tsc --noEmit"
test  = "go test ./..."
build = "npm run build"

[verify.e2e]    # long form for per-command overrides
cmd     = "playwright test"
timeout = 600
cwd     = "e2e"
```

Commands are parsed with `shlex.split` and run as argv with `shell=False` — no
shell interpretation, and shell metacharacters (`; | & $`, backticks, `< >`) are
rejected outright. The executable must be a bare name in the allow-list (default
set plus any `[gate] allowed_commands` you add); a path or a non-listed tool
fails with a clear message. Wrap complex pipelines in a script.

This allow-list is **defense in depth, not a complete RCE control.** It closes
the trivial inline vector (a one-line `python -c '...'` straight from
`hedl.toml`), but an allowed runner can still execute committed repo content —
`pytest` loads `conftest.py`, `make` runs the `Makefile`, `npm`/`pnpm` run
`package.json` scripts. For untrusted contributions the real control is the CI
setting *"require approval to run workflows for outside / first-time
contributors"*; the allow-list is not a substitute for it. The gate's
implementation being Python is a runtime dependency only, not a constraint on the
consumer's stack.

---

## Tier 2 — Lightweight (recommended starting point)

**What it is**: Gate-only + local-file state (`.work/`) + the 5 core slash commands.
**Setup time**: under 5 minutes.
**Files added to your repo**: `.work/` directory (state), `.claude/commands/` (5 commands).

**What you get**: everything from Tier 1, plus:
- Phase discipline (`phase-0.json`, `work.json`)
- Session context (`/start-session`, `/iterate`)
- Adversarial review gate (`/adversarial-review`)
- Phase transition (`/phase-complete`)
- All 15 command behaviors via natural language (from `skill/hedl/references/commands.md`)
- 7 core adversarial reviewers as named agents
- 19 additional reviewer prompts via `skill/hedl/references/review-library.md`

**How to install**:
Copy `skill/hedl/` into your project's `.claude/skills/Hedl/` (or symlink it).
Copy the `.work/` state directory. Initialize:
```bash
# Edit .work/context.json to set your project name
# Edit .work/phases/phase-0.json with your real Phase 0
# Edit .work/work.json with your real backlog
```

**Spec pipeline** (optional, add when needed):
Lightweight PRD → epic → task flow:
1. PRD lives in `docs/spec/prd.md` — copy from `skill/hedl/templates/prd-template.md` or generate
   via the requirements flow
2. Epics map to phase items in `phase-{N}.json` — copy from `skill/hedl/templates/epic-template.md`
3. Tasks are work items in `work.json`
4. No new tooling — the existing state backend handles it

```
skill/hedl/templates/         # canonical template source (inside the skill)
  prd-template.md             # copy to docs/spec/prd.md and fill in
  epic-template.md            # copy to docs/spec/epics/epic-NNN.md
  task-template.md            # tasks go in work.json, not spec files

docs/spec/                    # adopter's spec files (templates symlinked from skill)
  prd-template.md             # -> skill/hedl/templates/prd-template.md
  epic-template.md            # -> skill/hedl/templates/epic-template.md
  task-template.md            # -> skill/hedl/templates/task-template.md
  prd.md                      # your project's PRD (create from template)
  epics/
    epic-001.md               # one file per epic (create from template)
```

---

## Tier 3 — Team (GitHub Issues backend + parallel execution)

**What it is**: Tier 2 + GitHub Issues as the authoritative state source + parallel worktrees.

### GitHub Issues backend

Replaces `.work/work.json` as the source of truth for work items. Benefits:
- Recoverable state (no local JSON corruption risk)
- Audit trail (issue events, comments, assignment history)
- Handoff between agents and humans
- Native integration with GitHub Projects for roadmap views

State interface: the gate (`am_i_done.py`) reads from whichever backend is configured.
The local-file backend remains fully functional without `gh` — Tier 3 is additive.

Backend configuration (add to `hedl.toml`, per ADR-022):
```toml
[state]
backend = "github-issues"

[state_backend.github-issues]
repo = "owner/repo"
label_prefix = "work"
phase_label = "phase-{N}"
```

When `backend` is `local-file` (the default), the existing `.work/work.json` is used.
`install.py --migrate` relocates any legacy `.work/context.json` `state_backend` value into `hedl.toml`.

### Parallel worktree execution

Multiple agents work in parallel, each in an isolated git worktree. The gate runs at
the worktree merge point — not per commit.

Pattern:
```bash
# Create a worktree for each parallel stream
git worktree add .worktrees/stream-A feat/stream-A
git worktree add .worktrees/stream-B feat/stream-B

# Each stream runs am_i_done.py before merging
python3 .github/scripts/am_i_done.py  # from within .worktrees/stream-A

# Merge only on clean gate exit
git merge feat/stream-A  # only if gate passed
```

**Correctness guarantee**: strict per-stream file scoping enforced by the gate, not by
"check git status and wait." The gate validates that each stream's diff does not overlap
with parallel streams. Parallel writes to the same file are a gate violation, not a warning.

**Economics**: gate runs at merge, not per commit. The dispatcher's Haiku-by-default economics
apply to stream-level reviews — one review panel per stream merge, not per commit.

---

## Changing tiers

Always change tiers by re-running `install.py` — never by hand-editing symlinks, removing
files directly, or modifying `.hedl-tier`. Manual changes are not reproducible and break the
installer's view of installation state.

### Upgrade (low blast radius)

Adds only the missing projections. Existing projections and user-modified files are untouched.
`.work/` is preserved.

```bash
# Preview what will be added:
python3 skill/hedl/scripts/install.py --tier team --dry-run
# Apply:
python3 skill/hedl/scripts/install.py --tier team
```

### Downgrade (medium blast radius)

Removes projections that the lower tier does not include. `.work/` is archived — never
deleted — to `.work/archive/<timestamp>/`. **Always preview first and get explicit
confirmation before applying.**

```bash
# Show exactly what will be removed and archived:
python3 skill/hedl/scripts/install.py --tier gate --dry-run
# Review the output, then apply with explicit confirmation:
python3 skill/hedl/scripts/install.py --tier gate
```

The archived state is under `.work/archive/` and can be restored manually. Re-running
`install.py --tier lightweight` after a gate downgrade will skip `.work/` initialisation
(directory already exists from the archive step) — restore the desired state from the
archive subdirectory manually if needed.

### Idempotent re-run

Running `install.py --tier <current_tier>` verifies projections and restores any that are
missing or broken. Use `--doctor` to check health without making any changes.
