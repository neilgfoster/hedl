# edge-case-hunter — WORK-0076 (.work/ cross-harness layer)

**Run:** adversarial-review-2026-05-31-architecture-work-0076
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** feat/work-state-cross-harness @ pre-commit working tree

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| BLOCKING | `check_dispatch` FAILs (not skips) without `.work/` (via `--check dispatch`/`--panel`); blanket "every check skips" overstated. | _load_dispatch_rules opens dispatch-rules.json; check_dispatch returns FAIL. | RESOLVED — claim scoped to the default run; check_dispatch named as the opt-in panel/team-tier exception (not in a gate-only default run). |
| SIGNIFICANT | `_append_gate_insight` creates `.work/insights/` when `[insights] enabled`, even gate-only — violates zero-`.work/`-impact. | am_i_done.py _append_gate_insight makedirs. | RESOLVED — guard added: no-op when `.work/` absent (cf. WORK-0002); tested. |
| SIGNIFICANT | `check_markdown_schemas` reads `.work/config/markdown-schemas.json`, omitted from the doc list + untested. | am_i_done.py:847. | RESOLVED — added to the doc list; tested by mocking the frozen `_SCHEMAS_FILE`. |
| SIGNIFICANT | Test weaker than the doc's "guarded by TestGateOnlyNoWorkDir" claim. | original 4-assertion test. | RESOLVED — expanded with schemas-skip + insight-no-op. |
| MINOR | `check_commands` redundant existence guard / TOCTOU window. | am_i_done.py:792-796. | NOTED — pre-existing, out of WORK-0076 scope. |

## Recommendation

Scope the claim to the default run; close the `_append_gate_insight` gap with a
real guard; document + test the schemas check. All applied.
