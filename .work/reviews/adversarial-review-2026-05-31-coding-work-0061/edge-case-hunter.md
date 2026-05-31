# edge-case-hunter — WORK-0061 (docs-index adopter skip)

**Run:** adversarial-review-2026-05-31-coding-work-0061
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** main-HEAD (working tree, branch fix/docs-index-adopter-skip)

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| SIGNIFICANT | Monorepo/submodule false-positive: REPO_ROOT at a parent without skill/hedl/ → docs-index silently skipped in an embedded framework checkout. | am_i_done.py:1376. | REBUTTED (pre-existing) — identical to check_state_template_sync's guard; shared edge case, not introduced here. Follow-up: WORK-0073 centralization. |
| SIGNIFICANT | Sparse-checkout false-negative: framework repo without skill/hedl/ in the worktree → guard fires, docs-index skipped silently. | am_i_done.py:1376. | REBUTTED (pre-existing) — same shared guard. Follow-up: WORK-0073. |
| SIGNIFICANT | Discriminator inconsistency: check_skill_metadata guards on a different signal (_GEN_METADATA presence) than docs-index/state-sync (skill/hedl/ dir). | am_i_done.py:1343 vs 1376. | ACCEPTED as a real pre-existing issue; out of WORK-0061 scope. Recorded as a WORK-0073 follow-up: one `_is_framework_repo()` for all three. |
| SIGNIFICANT | No test for `--check docs-index` exit-2 in adopter layout. | runner ~1633-1663. | NOTED — exit-2 on an isolated skipped check is pre-existing, shared by all Optional checks; orthogonal. Full-gate adopter behaviour unaffected. |
| MINOR | Adopter loses orphan-doc protection (option b would exempt only docs/spec/*-template.md). | am_i_done.py:1376-1377. | DESIGN CHOICE — work item sanctioned option (a); docs-index is a framework-curation invariant. Trade-off + opt-in path recorded. |
| MINOR | Test isolation: `_run` used manual try/finally instead of mock.patch.object. | test_am_i_done.py. | FIXED — now uses `mock.patch.object` context manager. |

## Recommendations

Keep the consistent guard (matching state-sync) for this fix; centralize the
framework-repo discriminator in WORK-0073; fix test isolation (done). Consider a
hedl.toml opt-in for adopter orphan-doc protection if demand appears.
