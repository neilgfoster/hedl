# new-engineer — WORK-0014 review

**Run:** adversarial-review-2026-05-30-architecture-work-0014
**Model:** claude-haiku-4-5
**Commit:** 80c0e38

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → fixed | Orientation | disqualifiers precede any definition of the product | README.md opening | Fixed — neutral one-line definition now opens (ADR-011-compatible) |
| SIGNIFICANT → fixed | Jargon | "iteration layer" load-bearing but undefined | README.md / getting-started.md | Fixed — glossed on first use |
| MINOR → fixed | Accuracy | "GitHub Issues read backend" didn't state writes unsupported | README.md | Fixed — "read-only today; write-back planned, WORK-0012" |
| MINOR → no action | Availability | invisible-mode "planned, not built" wording | README.md | Exemplary as-is |
| MINOR → no action | Links | getting-started → README anchor | getting-started.md | Works on GitHub |

## Recommendations

- After the fixes a newcomer reads what Hedl is, then who it's for/not, then the
  gate — unblocked well within 30 minutes. Optional future polish: a half-sentence
  on the gate's payoff (stops premature "done").
