# External-review framing gap: native-redundancy judged single-harness

**Date:** 2026-05-30
**Discovered during:** Phase-2 entry, reading external-2026-05-30-1 (third external review)
**Status:** Forensic record. Not a backlog item. Feeds the Unit B scope-narrowing
ADR and the "improved prompt" amendment to the external review (report.md §8).

The third external adversarial review (.work/reviews/external-2026-05-30-1/)
scored Hedl's native-platform redundancy 4/10 by comparing against Claude Code
natives only (Agent Teams, Dynamic Workflows, Outcomes, native skill activation,
.claudeignore). The same agent's verdict drove the §4 ADOPT/REJECT table.

Hedl's harness-agnostic intent is foundational and ADR-set-wide:

- ADR-001: "reach across harnesses (Claude Code today, others later)"
- ADR-011: "stdlib, LLM-agnostic, distributable tiered Skill"
- ADR-016: "NL routing through SKILL.md is the cross-harness fallback"
- ADR-019 (Status: Superseded — the recursive-workstream primitive was
  superseded by WORK-0027; the cross-harness portability rationale below
  survives the supersession): "workstream state is consumable from any
  agentskills.io-compatible harness, not lock-in to one vendor"
- ADR-021 (Status: Proposed — deferred to v1.x): distinguishes Hedl from
  Aider/Devin/Copilot Workspace explicitly on harness-coupling grounds
- ADR-033 (Status: Proposed): "model-agnostic gate enforcement"

Plus WORK-0047 (Phase 2 backlog): "harness-agnostic adoption — Hedl
works with GitHub Copilot, OpenCode, and other AI coding tools."

The review's framing is honest for today (WORK-0047 unbuilt; Hedl
operationally Claude-Code-only) but blind to the architectural intent
encoded across six ADRs. Future external reviews must record the
project's stated architectural intent (ADR-survey at setup) so the
native-redundancy agent compares against the right baseline.
