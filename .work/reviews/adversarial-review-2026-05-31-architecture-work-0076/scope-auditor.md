# scope-auditor — WORK-0076 (.work/ cross-harness layer)

**Run:** adversarial-review-2026-05-31-architecture-work-0076
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** feat/work-state-cross-harness @ pre-commit working tree

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| — | No accretion: extends backends.md (no new doc); documents real, verifiable behaviour; ADR-036/022-sourced. | backends.md new section. | OK. |
| — | One consolidating test (relying on existing per-check skip tests) is appropriately minimal for AC2, not under-delivery. | TestGateOnlyNoWorkDir. | OK. |
| — | No scope creep: only backends.md + test (+ the insight guard, which makes AC2 true); no unbuilt-harness commitments (those are WORK-0047). | diff. | OK. |
| MINOR | Listing Copilot/OpenCode/Cursor as readers could imply deployed breadth. | backends.md harness list. | RESOLVED — reworded to capability ("any harness that can read a file could consume it"), with WORK-0047 named as the unbuilt projection work. |

## Recommendation

In scope and minimal; keep the harness framing as capability, not deployed
support. Applied.
