# Getting started

Three tiers — gate-only in 2 minutes, full lightweight in 5, team with GitHub Issues when
you need shared state. The installer is a single Python script; no network access, no sudo.

**Prerequisites**: Python 3.11+, git. Claude Code for slash commands and named agents (optional).

---

## Install

From your project root, point the installer at this skill directory:

```bash
python3 /path/to/hedl/skill/hedl/scripts/install.py --tier lightweight
```

If you have already cloned this repo and are inside it:

```bash
python3 skill/hedl/scripts/install.py --tier lightweight
```

### Tier comparison

| Tier | What you get | Time |
|------|-------------|------|
| `gate` | Deterministic gate + CI workflow + PR template | ~2 min |
| `lightweight` | Gate + `.work/` state + 5 slash commands + 7 agents + spec templates | ~5 min |
| `team` | Lightweight + Claude Code hooks + GitHub Issues guidance | ~5 min |

Preview before installing:

```bash
python3 skill/hedl/scripts/install.py --tier lightweight --dry-run
```

Check what was installed:

```bash
python3 skill/hedl/scripts/install.py --status
python3 skill/hedl/scripts/install.py --doctor
```

---

## First-time setup (lightweight or team)

The installer copies a template `.work/` directory. Edit three files with your project's content:

- **`.work/context.json`** — set `meta.project` to your project name
- **`.work/phases/phase-0.json`** — replace `goal`, `definition_of_done`, `constraints`
- **`.work/work.json`** — replace the example item with your real backlog

---

## The daily loop

```text
/start-session      # orient: phase, active item, last session
/iterate supervised # work one item at a time
"finish this task"  # acceptance criteria + adversarial review + commit
"raise PR"          # pr-ready + pr-raise with template and CI
/phase-complete     # when all DoD criteria verified
```

All behaviors are accessible via natural language — see `skill/hedl/SKILL.md` for the
full routing table. Slash commands are the Claude Code shorthand for the same flows.

Before declaring any task done:

```bash
python3 .github/scripts/am_i_done.py
python3 .github/scripts/am_i_done.py --pr 42   # when a PR is open
```

---

## Verify the installation

```bash
pytest skill/hedl/tests/ -q                        # gate script tests
python3 .github/scripts/am_i_done.py               # gate: local checks
python3 skill/hedl/scripts/install.py --doctor     # projection health
```

---

## Team tier

For GitHub Issues backend and parallel worktrees:

```bash
python3 skill/hedl/scripts/install.py --tier team
```

See `docs/team-tier.md` or `skill/hedl/references/tiers.md` for configuration.

---

## Stack-agnostic verification

Hedl is not a Python-only gate. The implementation is Python (a runtime dependency),
but the checks it runs are declarative. Add a `hedl.toml` at the repo root to tell
the gate what to run:

```toml
[gate]
timeout = 120   # default per-command timeout (seconds)
# A [verify] command may only invoke an allow-listed executable. Default:
# pytest, mypy, ruff, npm, pnpm, make. Add bare names for your stack (additive,
# and no path separators or shell metacharacters). See references/tiers.md.
allowed_commands = ["golangci-lint", "tsc", "go", "playwright"]

[verify]
lint  = "golangci-lint run"
types = "tsc --noEmit"
test  = "go test ./..."
build = "npm run build"

[verify.e2e]    # long form: per-command overrides
cmd     = "playwright test"
timeout = 600
cwd     = "e2e"
```

With no `hedl.toml`, the gate auto-detects Python projects (via `pyproject.toml`,
`ruff.toml`, or `tests/`) and runs ruff/mypy/pytest. With `hedl.toml` present it
runs exactly the declared checks — undeclared standard checks are skipped, not
Python-defaulted. Commands run with `shell=False` (no shell interpretation; shell
metacharacters are rejected) and the executable must be in the allow-list above;
wrap complex pipelines in a script.

---

## Developing Hedl

This section is for contributors editing Hedl itself — not for consumers who adopt it.

**Prerequisites**: [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip.
Consumers need only `python3` — uv is a Hedl dev/CI tool, not an adoption requirement.

### With uv (recommended)

```bash
uv sync              # install pinned dev deps into .venv from uv.lock
uv run pytest skill/hedl/tests/ -q
uv run python .github/scripts/am_i_done.py
```

`uv.lock` is the canonical source of truth. After updating `pyproject.toml` dep versions,
run `uv lock` to regenerate the lock, then `uv export --only-group dev -o requirements-ci.txt`
to keep the pip fallback in sync.

### With pip (fallback)

```bash
pip install -r requirements-ci.txt
pytest skill/hedl/tests/ -q
python3 .github/scripts/am_i_done.py
```

`requirements-ci.txt` is generated from `uv.lock` — do not edit it by hand.

---

## Review panels

`/adversarial-review [task-type]` convenes a panel for the current diff.
Panel composition quick reference: `docs/review-panels.md`.
Full agent library: `skill/hedl/references/review-library.md`.
