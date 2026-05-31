# determinism-auditor — ADR-035 (auto-deterministic-detector)

**Run:** adversarial-review-2026-05-31-architecture-adr-035
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** d1c789a (working tree, branch docs/auto-deterministic-detector-adr)

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| BLOCKING | The "ADR-003 honored at the artefact level, not the classifier level" argument is a loophole: it would license LLM inference throughout the toolchain so long as the final output is deterministic, contradicting ADR-003's "anything verifiable by a function is verified by a function". | ADR-003:9-12; ADR-035 recursion section. | ACCEPTED — the artefact-level blessing is removed. The ADR now states the LLM-classifier form is NOT ADR-003-compliant in spirit; the only acceptable detector form is a DETERMINISTIC pattern-matcher extending WORK-0028. |
| SIGNIFICANT | The ADR defers to an (implicit) LLM classifier without weighing the deterministic alternative — WORK-0028 already catches an ADR-003 violation class with regex+arithmetic, no LLM. | WORK-0028 drift detector. | ACCEPTED — deterministic pattern-matching added as the preferred (only acceptable) detector form in Options considered; the reopen condition requires it be explored first. |
| SIGNIFICANT | reflect.py determinism test uses sort_keys=True, masking dict-ordering; should assert byte-identical JSON across runs. | test_insights.py determinism test. | NOTED — code-quality finding about existing reflect.py, out of scope for this docs-only ADR; recorded for a future work item if reflect.py survives the prove-or-cull trigger. |
| SIGNIFICANT | record_insights.py hardcodes the reviewer roster (drift; omits existential-challenger) instead of deriving from skill/hedl/agents/. | record_insights.py:64-78; external review item 9. | NOTED — already tracked as WORK-0069; out of scope here, cross-referenced. |
| MINOR | reflect.py/contribute.py docstrings should state reproducibility explicitly. | reflect.py docstring. | NOTED — code, out of scope for docs-only ADR. |
| MINOR | The reopen trigger is silent on whether a future detector must be deterministic. | ADR trigger. | ACCEPTED — reopen condition now requires the deterministic form be attempted before any inference-based form is reconsidered. |

## Recommendations

Do not bless inference-authoring-of-enforcers; make the deterministic
pattern-matcher (extending WORK-0028) the only acceptable detector form and the
first thing explored if ever reopened. Applied. Code-level reflect.py/record_insights
findings routed to existing/future work items, not this docs PR.
