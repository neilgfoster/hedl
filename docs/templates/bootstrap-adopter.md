# Bootstrap-adopter template

The repeatable sequence for standing up a new Hedl adopter repo, captured from
the Lume and Wyrd bootstraps (2026-05-29). This is the prose form of a
`bootstrap-adopter` workstream (ADR-019/020); it becomes a data-form workstream
template when WORK-0011 lands. Use it as a checklist — each adopter runs the
same steps with a different seed.

> Scope: this is operator documentation for onboarding an adopter. It is not
> projected into adopter repos.

## Sequence

1. **Create the empty remote.** `gh repo create <org>/<name> --private` (or
   public), clone it, branch from `main`.
2. **Branch protection.** Require 1 approving review and the `am_i_done` matrix
   checks on `main`. This is the structural operator checkpoint Hedl's
   `/iterate` flow relies on (ADR-025) — set it before any work lands.
3. **Install Hedl, team tier.**
   `python3 <hedl>/skill/hedl/scripts/install.py --tier team --copy --repo .`
   Until a packaged CLI exists (WORK-0045), this is invoked from a local Hedl
   checkout by path.
4. **Sync to latest Hedl + migrate.** Pull the Hedl checkout to the version you
   want, re-run the install at the same tier, then
   `install.py --migrate --repo .` if the state schema bumped. (`docs/upgrading.md`
   — WORK-0044 — will be the canonical reference for this step.)
5. **Add adopter requirements.** The gate expects these to exist; they are not
   yet auto-shipped (tracked by the manifest work, WORK-0050):
   - `pyproject.toml` + `uv.lock` — the workflow's Python/uv preconditions.
   - `.pymarkdown.json` — the markdown-lint config the gate's `markdown` check reads.
   - README spec links — link `docs/spec/*` so the gate's `docs-index` check
     (README-reachability) passes.
   The `.gitignore` protecting local-only insights artefacts is shipped
   automatically by the installer (WORK-0042) — no manual step.
6. **PR#1 green.** Open the install PR; drive `am_i_done` to green (it will flag
   the requirements above until step 5 is complete). Merge.
7. **Operator-authored seed.** Replace the `EDIT ME` placeholders in
   `.work/context.json`, `.work/work.json`, `.work/phases/phase-0.json` with the
   adopter's real project name, description, and first phase. (Today this is a
   second PR after install; WORK-0046 proposes `--project/--description` seed
   flags to fold it into PR#1.)
8. **First product work item.** Add the adopter's first real backlog item and
   begin `/iterate`.

## Known friction (and the backlog item addressing each)

| Step | Friction today | Tracked by |
|------|----------------|-----------|
| 3 | Invoked by path from a local Hedl checkout; no `pip install hedl` | WORK-0045 |
| 4 | Update workflow not discoverable; preserved-vs-overwritten unclear | WORK-0044, WORK-0043 |
| 5 | pyproject/uv.lock/.pymarkdown.json + README links are manual | WORK-0050 |
| 7 | `EDIT ME` placeholders force a two-PR adoption flow | WORK-0046 |

## When the prose template stops sufficing

This checklist is the right tool while one operator holds full context across a
handful of adopters. Move to the data-form workstream model (WORK-0010/0011)
when concurrently-active workstreams exceed ~5-7, OR more than one operator needs
shared machine-readable state, OR a parallel-bootstrap-under-coordination-strain
repeats. See `.work/insights/dogfood-workstream-spawn-adopters-2026-05-29.md`.
