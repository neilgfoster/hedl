# existential-challenger — Phase-1 boundary review

**Run:** phase-1-complete-2026-05-30
**Model:** claude-opus-4-8
**Commit:** caa800e

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| BLOCKING | Watchlist accountability | ~8 alternatives.md objectives "measuring at Phase-1 boundary" have zero recorded verdicts | docs/alternatives.md (multiple "Measurement window: end of Phase 1") | Operator decision: record verdicts or defer the re-eval |
| BLOCKING | Uncut culling-candidate | budget_manager's rescue-case evidence window closed with no case shown | alternatives.md culling-candidate entry; budget_manager.py (~554 lines) | Operator decision: cull vs keep+defer |
| SIGNIFICANT | Dead-weight cluster | recursive cluster (WORK-0010/0011/ADR-031) gated on the unbuilt, demand-gated model (ADR-019 superseded; threshold never hit) | work.json WORK-0010/0011; ADR-031 | Operator decision: cull vs defer-to-Phase-2 |
| SIGNIFICANT | Deferral as displacement | WORK-0035 (external review kit) net-new, not in sanctioned exceptions | work.json WORK-0035 | Reclassify Phase 2 |
| SIGNIFICANT (accept) | Ratio improved | process-to-code ratio genuinely flipped (Python ~2.9x process text) | scripts/ + tests/ vs decisions/ + references/ | Goal-displacement substantively resolved |
| MINOR (accept) | Goal met | core restoration real (gate runs in CI, RCE fixed, ADRs reconciled) | work.json completed[] | Carry — phase goal met once blockers cleared |

## Recommendations

- The restoration goal is met; close cleanly by FORCING the deferred decisions
  (cull vs carry the recursive cluster + budget_manager, record watchlist verdicts)
  rather than carrying them silently — carrying them is the displacement Phase 1
  was meant to unwind.
