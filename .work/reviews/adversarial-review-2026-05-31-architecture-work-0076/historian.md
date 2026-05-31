# historian — WORK-0076 (.work/ cross-harness layer)

**Run:** adversarial-review-2026-05-31-architecture-work-0076
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** feat/work-state-cross-harness @ pre-commit working tree

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| SIGNIFICANT | Misattribution: doc said "Under DIRECTION-2 (ADR-036), .work/ is positioned as harness-agnostic"; ADR-036 calls .work/ "the substrate that makes the gate work-item-aware" and reserves "harness-agnostic" for the gate/roadmap (WORK-0047). | ADR-036 pillar 3 vs backends.md. | RESOLVED — doc now quotes ADR-036 accurately; the cross-harness/stdlib-readable property is framed as the doc's own capability claim, not ADR-036 calling .work/ harness-agnostic. |
| — | ADR-022 pluggability, WORK-0002 budget no-op, and the per-check read claims (check_commands/work.json, check_config/dispatch-rules, check_state_template_sync) verified accurate. | am_i_done.py; ADR-022; WORK-0002. | OK. |
| — | No duplication/contradiction with the existing WORK-0007 github-issues audit; the section precedes it cleanly. | backends.md. | OK. |

## Recommendation

Fix the ADR-036 attribution; separate capability from deployed breadth. Applied.
