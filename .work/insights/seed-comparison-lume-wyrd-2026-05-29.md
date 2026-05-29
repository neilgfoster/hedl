# Seed comparison: Lume vs Wyrd (bootstrap-adopter template, N=2)

**Date:** 2026-05-29
**Status:** Captured. Confirms the prior `dogfood-workstream-spawn-adopters`
decision (option C) at N=2. Five Hedl findings raised as work-item candidates
(WORK-0054..0058).

## Context

The bootstrap-adopter template (`docs/templates/bootstrap-adopter.md`, option C
from PR #58) was validated under two real adopters in one session: **Lume**
(AI-native IDP) and **Wyrd** (RPG/board-game AI runtime). One operator authored
both seed prompts in independent sessions; this Hedl-orchestration session
patched both for CI-green.

## What held under both (template invariants)

- File layout: `CLAUDE.md` + `.work/{context,work,session,phases/phase-0}`.
- Phase 0 as the scope-setting discovery phase.
- WS-TECH + WS-ARCH workstreams.
- "Deterministic over inference" as principle #1 — independently chosen in both.

## What diverged (healthy template flex)

| Dimension | Lume | Wyrd |
|-----------|------|------|
| Vision size | 247 lines / 14 backlog / 15-item DoD | 101 lines / 1 backlog / 4-item DoD |
| Start posture | sets `active_item` | leaves it null |
| Work-item prefix | `WORK` (default) | `WYRD` (custom) |
| Workstream variant added | `WS-REQ` | `WS-SPIKE` |
| Phase-0 name + branch conventions | own | own |

Divergence is healthy: the template is a skeleton, not a straitjacket. N=2
confirms it holds without forcing uniformity.

## Five Hedl findings (work-item candidates; code claims verified 2026-05-29)

- **C-1 (medium) — context.json `EDIT ME` survives the seed.** Placeholders
  survived BOTH seeds; the gate does not catch them, so both needed in-session
  patching after the seed PR. The bootstrap-adopter template should call out
  `context.json` as an explicit seed target with a "no EDIT ME remains" check.
  → WORK-0054.
- **C-2 (medium) — PR-template shape not surfaced to a new adopter.** Both seed
  PRs missed Hedl's required `PULL_REQUEST_TEMPLATE.md` sections. CLAUDE.md /
  SKILL.md should state the requirement, or install.py should print it as a
  next-step reminder. → WORK-0055.
- **W-1 (high) — `check_pr_template.py` hardcodes `WORK-\d+`.** VERIFIED:
  `check_pr_template.py:77` uses `re.search(r"\bWORK-\d+\b", ...)` and ignores
  `context.json.work_item_prefix`. Wyrd's prefix is `WYRD`, so its first product
  PR will FAIL the template check. Highest severity — adopter-blocking.
  → WORK-0056.
- **W-2 (medium) — branch-naming check is silently skipped in CI.** VERIFIED:
  `check_branch` returns `None` on a detached HEAD (`git branch --show-current`
  is empty on the CI merge-ref checkout), so the naming convention is enforced
  only on local runs, never in `--pr`/CI. Quiet rule erosion. → WORK-0057.
- **W-3 (low-medium) — WS-SPIKE is not in the canonical workstream set.**
  VERIFIED: standards.md lists only WS-PLAN/REQ/TECH/ARCH (WS-TECH's description
  already covers "spikes, proof-of-concept"). Wyrd uses WS-SPIKE. Decide:
  codify WS-SPIKE, document an adopter-extension contract, or push back to the
  canonical four (WS-TECH already covers spikes). → WORK-0058.

## Implications

**For the bootstrap-adopter template** (actioned in this PR):
- Step 7 explicitly names `.work/context.json` and adds a "verify no `EDIT ME`
  remains" check (C-1).
- Step 6 adds: use `.github/PULL_REQUEST_TEMPLATE.md` sections verbatim in the
  seed PR body (C-2).

**For the prior `dogfood-workstream-spawn-adopters` decision (C):**
- **N=2 confirmed:** the prose template held; per-adopter divergence is healthy.
- The case for WORK-0010 / WORK-0011 (recursive data model + templates) does
  **not** escalate yet. Prose suffices at N=2. (The data-model-adoption
  threshold on WORK-0010 stands unchanged.)
