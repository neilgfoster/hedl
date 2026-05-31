# Adversarial Review — coding (WORK-0061 docs-index adopter skip)

**Log:** adversarial-review-2026-05-31-coding-work-0061
**Session:** in-session
**Depth:** Standard (edge-case-hunter; small, pattern-mirroring gate-check change)
**Commit:** main-HEAD (working tree, branch fix/docs-index-adopter-skip)

Panel: [edge-case-hunter](edge-case-hunter.md).

Scope: `check_docs_index()` in `skill/hedl/scripts/am_i_done.py` + test fixtures.
Fix: skip docs-index in adopter repos (no `skill/hedl/` at root), mirroring
`check_state_template_sync`'s guard (WORK-0061 AC option a).

Verdict: **PASS** (1 test-isolation nit applied; the rest are pre-existing,
pattern-wide, or AC-sanctioned design choices, recorded as follow-ups).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Guard correctness | PASS — mirrors the established check_state_template_sync guard; consistent with the nearest analog |
| Test coverage | PASS — skip-in-adopter + enforced-in-framework added; existing docs-index fixtures updated with the framework marker |
| Test isolation | PASS after fix — `_run` now uses `mock.patch.object` (matches test_docs_index.py) |

## Blocking Findings

None.

## Significant Findings

- **Discriminator edge cases — monorepo/submodule false-positive + sparse-checkout
  false-negative** (edge-case-hunter) — REBUTTED as pre-existing/pattern-wide:
  `check_state_template_sync` uses the identical `os.path.isdir(REPO_ROOT/skill/hedl)`
  guard and shares these exact edge cases. WORK-0061's AC required "the same guard";
  using a different signal would create inconsistency (see next). Not introduced here.
- **Discriminator inconsistency — check_skill_metadata uses a different signal**
  (edge-case-hunter) — REAL but pre-existing: the file has 2-3 framework-vs-adopter
  signals. Centralizing into one `_is_framework_repo()` across docs-index +
  state-sync + skill-meta is a clean follow-up for **WORK-0073** (the am_i_done split
  into a checks/ package), not WORK-0061 scope. Recorded.
- **No `--check docs-index` exit-code test in adopter layout** (edge-case-hunter) —
  the exit-2 ("nothing to validate") on an isolated skipped check is pre-existing
  semantics shared by every Optional check; orthogonal to WORK-0061. The full gate in
  an adopter repo still runs its other checks normally. Noted.

## Minor Findings

- **Adopter loses orphan-doc protection** (edge-case-hunter, option b) — the work
  item explicitly sanctioned option (a) (skip entirely); docs-index reachability from
  README is a framework-curation invariant, not a convention Hedl's gate should impose
  on an adopter's own docs. Trade-off recorded: if adopters want it, the path is a
  hedl.toml `[verify.docs-index]` opt-in or the narrower (b) exemption — a future
  enhancement, not this fix.
- **Test isolation** (edge-case-hunter) — FIXED: `_run` uses `mock.patch.object` as a
  context manager.

## Synthesis

A small, correct fix that mirrors the established adopter-skip pattern. The
substantive findings all point at one pre-existing issue — the framework-vs-adopter
discriminator is duplicated and has monorepo/sparse-checkout edge cases — which is
genuinely worth fixing but belongs in WORK-0073's centralization, not in a
single-check fix that the AC told to match the existing guard. Applied the
test-isolation improvement.

## Next Actions

PASS → commit + PR (no auto-merge). Follow-up recorded for WORK-0073: centralize the
framework-repo discriminator across docs-index / state-sync / skill-meta.
