# Hedl

Hedl is an **iteration layer** for AI-assisted coding — the per-task work → validate →
done loop — built around a **deterministic completion gate**: a script that decides, by
identical checks locally and in CI, whether a task is actually done. Opt-in adversarial
review and phase discipline layer around that gate. It sits on top of whatever issue
tracker you already use, not in place of it. Distributed as an Agent Skill.

## Don't use Hedl if

- it's a small or throwaway project where the ceremony costs more than it saves.
- you're a solo developer who doesn't need a traceable engineering journey.
- you're happy with native Claude Code flows and don't need a deterministic gate.
- you want zero Python dependency.
- you only need one of Hedl's pieces in isolation — for each, the
  [alternatives](docs/alternatives.md) (Danger, adr-tools, CCPM, native agent workflows)
  may serve you better.
- you want a full project-management system — Hedl is a thin iteration layer, not a
  replacement for Jira, Linear, or GitHub Projects.

## Use Hedl if

- you want a deterministic "am I done?" check on AI-generated work, identical locally
  and in CI, with no inference in the verdict.
- you want adversarial review and phase discipline as **opt-in** layers, not a framework
  you must adopt whole.
- you want it to plug into your existing PM tool (local files, or GitHub Issues today)
  rather than replace it.
- _(planned)_ you want the gate's discipline on a repo you don't own — an **invisible
  mode** (ADR-023) is designed for exactly that, though the `install.py` flag is not yet
  built (WORK-0013); see "What Hedl doesn't do" below.

## The gate

Hedl's completion gate is **not original**. A single deterministic command that decides
whether a change is done — run identically by the pre-commit hook and in CI — comes directly
from [theshadow27/mcp-cli](https://github.com/theshadow27/mcp-cli), which has shipped an
`am-i-done` script since before Hedl existed: "the same command the pre-commit hook and CI
both run, so a local pass means a green PR". Hedl took the name and the design from it. The
older, upstream idea — "run the checks before you finish", as agent prose — is
[oven-sh/bun](https://github.com/oven-sh/bun)'s (`CLAUDE.md` / `AGENTS.md`).

`am_i_done.py` runs the same pass/fail checks locally and in CI — clean tree, branch naming,
PR template, stale work-item IDs, lint, types, tests, unresolved review threads, Dependabot
alerts. No inference; the script decides, not the agent; a task is done when the gate says so.

What Hedl adds over mcp-cli's gate is only the **packaging**: a stdlib-Python, LLM-agnostic,
drop-in gate (no JS/bun toolchain) distributed as an opt-in tiered **Skill** so *other* repos
can adopt it, plus a work-item/PR-aware check bundle (stale work-item IDs, PR-template
validity, unresolved threads, Dependabot) tied to a tracker. The deterministic, CI-symmetric
core is mcp-cli's. Everything else is opt-in scaffolding around the gate. See
[Alternatives](docs/alternatives.md).

Three opt-in tiers:

- **Gate-only** — drop `am_i_done.py` into any repo. Two-minute setup.
- **Lightweight** — gate + phase discipline + adversarial review + 5 slash commands.
- **Team** — lightweight + Claude Code integration, the parallel-worktree gate check, and
  a GitHub Issues backend (read-only today; write-back planned, WORK-0012).

## Alternatives

For most Hedl capabilities a focused tool already does that one thing. What is genuinely
Hedl-specific today — the work-item-aware gate bundle (the deterministic gate itself is
prior art, see below), the tiered and reversible install, and the `--streams` overlap
check — and the alternative for every other piece are catalogued in
[docs/alternatives.md](docs/alternatives.md).

## What Hedl doesn't do

Hedl is an **iteration layer**, not a project-management system — it plugs into your PM
tool (local `.work/` files, or a GitHub Issues backend, read-only today with write-back
planned in WORK-0012) rather than replacing it. An **invisible mode** — installing into a
repo you don't own, keeping Hedl's artifacts
out of the committed tree (at the cost of the CI gate not running on your PRs) — is
recorded in ADR-023 but **planned, not yet built**: the `install.py` flag is Phase-2 work
(WORK-0013), so treat it as intent, not a current capability.

## What you get

- **Deterministic completion gate** — `.github/scripts/am_i_done.py` runs the same checks
  locally and in CI: clean tree, branch naming, PR-template validity, stale work-item IDs,
  lint, types, tests, unresolved review threads, Dependabot alerts. No inference; pass or fail.
- **Multi-agent adversarial review** — 8 named reviewer agents, a dispatcher that selects
  the minimal panel for a diff, and 18 composable reviewer prompts in the reference library.
- **Phase and work-item tracking** — `.work/` state files keep work to one item per operator
  at a time, within the current phase.
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
- [State backends](skill/hedl/references/backends.md) -- local-file vs github-issues, read/write paths
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
