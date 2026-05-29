# Hedl

A disciplined engineering workflow distributed as an Agent Skill. Three opt-in tiers:

- **Gate-only** — drop `am_i_done.py` into any repo. Two-minute setup.
- **Lightweight** — gate + phase discipline + adversarial review + 5 slash commands.
- **Team** — lightweight + Claude Code integration, the parallel-worktree gate check, and a GitHub Issues read backend.

## What you get

- **Deterministic completion gate** — `.github/scripts/am_i_done.py` runs the same checks
  locally and in CI: clean tree, branch naming, PR-template validity, stale work-item IDs,
  lint, types, tests, unresolved review threads, Dependabot alerts. No inference; pass or fail.
- **Multi-agent adversarial review** — 8 named reviewer agents, a dispatcher that selects
  the minimal panel for a diff, and 18 composable reviewer prompts in the reference library.
- **Phase and work-item tracking** — `.work/` state files keep work to one item at a time,
  within the current phase.
- **Budget-aware reviews** — `budget_manager.py` tracks model-invocation budget per session
  and defers optional reviews to a queue when the tier drops.
- **Hooks** — post-edit linter and stop reminder, wired in `.claude/settings.json`.
- **CI** — SHA-pinned GitHub Actions: completion gate on every PR, CodeQL (Python + Actions),
  Dependabot.

## Adopt it

See [Getting started](docs/getting-started.md). Already using Hedl? Add yourself to
[ADOPTERS.md](ADOPTERS.md).

## Documentation

### Using Hedl

- [Getting started](docs/getting-started.md) -- installation, first use, adopter checklist
- [Bootstrap an adopter](docs/templates/bootstrap-adopter.md) -- the repeatable new-adopter-repo sequence
- [Tiers](skill/hedl/references/tiers.md) -- gate-only, lightweight, and team tier detail
- [Name and origin](docs/name.md) -- why "Hedl"
- [Adopters](ADOPTERS.md) -- projects using Hedl
- [Changelog](CHANGELOG.md)

### Commands and agents

- [Commands](docs/commands.md) -- five core slash commands and the gate
- [Commands reference](skill/hedl/references/commands.md) -- full behavior catalog
- [SKILL.md](skill/hedl/SKILL.md) -- natural-language routing table
- [Agents](docs/agents.md) -- named review agent roster
- [Review panels](docs/review-panels.md) -- running adversarial reviews
- [Review library](skill/hedl/references/review-library.md) -- composable reviewer prompts

### Standards and workflow

- [Standards](docs/standards.md) -- branch, commit, and PR conventions
- [Spec pipeline](docs/spec-pipeline.md) -- epic/PRD/task workflow
- [Team tier](docs/team-tier.md) -- Claude Code integration, worktree gate workflow, GitHub Issues backend
- [Self-improvement](docs/self-improvement.md) -- /reflect and /contribute flows
- [Versioning](docs/versioning.md) -- release and version policy
- [Alternatives](docs/alternatives.md) -- competitive landscape per ADR-012

### Spec templates

- [Epic template](docs/spec/epic-template.md)
- [PRD template](docs/spec/prd-template.md)
- [Task template](docs/spec/task-template.md)

## Requirements

- Python 3.11+
- `gh` CLI for PR-related checks (optional locally; skips gracefully)
- `pytest`, `ruff`, `pymarkdown` used by the gate when present (see `requirements-ci.txt`)
