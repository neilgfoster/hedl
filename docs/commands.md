# Command reference

Five core slash commands live in `.claude/commands/`. All other workflow operations
are accessible via natural language through the Hedl SKILL.md router.

**Full reference**: `skill/hedl/references/commands.md`

---

## Core slash commands

| Command | What it does |
|---------|--------------|
| `/start-session` | Loads context at session start: phase, active item, last session. |
| `/iterate [supervised]` | Work loop through to a merge-ready PR, then stops for operator review at merge time. |
| `/adversarial-review [type]` | Convenes a review panel for the current diff or target. |
| `/pr-ready` | Drives a branch to an operator-ready PR: gate → PR → CI → review → fix cycle. |
| `/phase-complete` | Validates the phase DoD, runs a final review, transitions to the next phase. |

Without Claude Code, invoke the same behaviors in natural language — the SKILL.md router
maps phrases like "finish this task", "raise PR", "I'm stuck" to the same flows.
See `skill/hedl/SKILL.md` for the full routing table.

---

## The completion gate

All "is it done?" judgements are deterministic, in `.github/scripts/am_i_done.py`:

```bash
python3 .github/scripts/am_i_done.py            # local checks
python3 .github/scripts/am_i_done.py --check git
python3 .github/scripts/am_i_done.py --pr 42    # + template, threads, dependabot
python3 .github/scripts/am_i_done.py --json     # machine-readable
```

Checks fail loudly when a tool is expected but missing:
ruff (if pyproject.toml present), mypy (if source dirs present), pytest (if tests dir present).
