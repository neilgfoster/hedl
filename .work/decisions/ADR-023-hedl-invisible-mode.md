# ADR-023-hedl-invisible-mode — Hedl invisible mode

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Hedl supports an **invisible mode** in which all Hedl artifacts
(`.work/`, `.hedl-tier`, the `.github/` projections, the `.claude/`
projections, `hedl.toml` if used) are gitignored at install time and
never tracked. The operator's actual deliverable (code, docs, PRs)
commits normally to the repo; Hedl's machinery stays local-only.

`install.py --invisible <tier>` is the entry point: it performs a
normal tier install **and** inserts a delimited Hedl block
(`# >>> hedl >>>` ... `# <<< hedl <<<`) into `.gitignore`. The reverse
mode `install.py --make-visible` removes the block, lifting Hedl
artifacts into the repo proper for team-wide adoption.

State persistence in invisible mode is local-only by default. Pairing
invisible mode with an external PM backend (per
[[ADR-022-pm-system-pluggability]]) is how operators preserve work
across machines without exposing Hedl to teammates.

## Context

An individual engineer may want Hedl's iteration discipline and
deterministic gate without requiring the rest of their team to adopt
anything. Without invisible mode, that conversation is "convince the
team to commit Hedl artifacts into our repo" — a political lift that
kills most personal-tool adoption.

Invisible mode collapses that adoption funnel: the engineer is the
only required stakeholder. This validates
[[ADR-008-framework-vs-lume-test]] from a different angle — Hedl
serves solo adopters embedded in non-Hedl teams without forcing Hedl
on those teams.

## Prior art

The pattern of "personal local overlay on a shared repo" is
widespread:

- `nvm` and `pyenv` — installed centrally, repo-level markers
  (`.nvmrc`, `.python-version`) optional and often gitignored when
  personal.
- `direnv` — `.envrc` can be gitignored for personal use.
- Local `.git/hooks/` — never committed.
- VS Code workspace settings — `.vscode/` can be either committed or
  personal.
- Personal task trackers (Things, Bear, Linear personal) layered over
  team trackers.

Hedl is **not inventing** the pattern. What is uniquely Hedl under
this ADR: the deterministic gate + workstream discipline + journey
capture applied as a personal overlay, optionally backed by the team's
PM system (per [[ADR-022-pm-system-pluggability]]). The closest
comparator is "personal git hooks + personal task tracker" — Hedl is
the integrated version.

What would have to change for Hedl to delegate: an integrated personal
overlay that bundles gate-equivalent + task-tracking + journey-capture
on top of an arbitrary PM system. None exists today.

## Options considered

- **Always-visible install only** — rejected. Forces team adoption
  whenever an individual wants Hedl; fails
  [[ADR-008-framework-vs-lume-test]] for solo adopters on shared
  teams.
- **Two separate install code paths (visible/invisible)** — rejected.
  Fragmentation; doubles maintenance.
- **Single install with `--invisible` and reverse `--make-visible`
  mode** — chosen.

## Consequences

- `install.py` learns `--invisible <tier>` and `--make-visible` flags;
  gains responsibility for managing a delimited block in `.gitignore`
  (additive, idempotent, never touches other rules).
- **CI gate does NOT run on team CI in invisible mode** — the
  operator's local gate is the only validation of their work. The
  trade-off is recorded explicitly in install output and docs:
  invisible mode trades CI enforcement for non-intrusiveness.
- State is per-machine unless paired with an external PM backend (per
  [[ADR-022-pm-system-pluggability]]). The recommended pattern for
  cross-machine invisible-mode work is `--invisible` +
  `state_backend: github-issues` (or Jira/Linear/Notion).
- README adds an explicit "Use Hedl if..." qualifier — *"you want
  personal iteration discipline + a deterministic gate on your own
  work without requiring your team to adopt anything new."* This is
  the strongest qualifier next to the existing disqualifiers (per
  [[ADR-011-disqualifiers-first-positioning]]).
- Adoption funnel: invisible adoption → use over time → propose team
  adoption via `install.py --make-visible` + a PR. The transition is
  one command.
- The skill must be installable from a path outside the project's repo
  (e.g., `~/tools/hedl/skill/hedl/`) so the operator's repo does not
  need to contain the skill source. `install.py --skill-from <path>`
  or equivalent is required.
