# historian — ADR-037 (doing-it-wrong rules)

**Run:** adversarial-review-2026-05-31-architecture-adr-037
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** docs/doing-it-wrong-rules-adr @ pre-commit working tree

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| SIGNIFICANT | ADR-037 overstates that it "satisfies" ADR-035's reopen condition. ADR-035 has three conditions (a deterministic ADR-003-anti-pattern detector attempted first; a corpus; a content-aware scrub). doing-it-wrong is the general author-written-rule lane, not that specific detector. | ADR-035 reopen conditions; ADR-037 ADR-035 paragraph. | ACCEPTED — reworded: doing-it-wrong is the lane in which ADR-035's detector would live IF its own conditions are met; it does not by itself satisfy them. |
| — | Prior-art section satisfies ADR-017 (names linters/pre-commit/WORK-0028; what's different; why; delegate condition); attribution to Jacob/mcp-cli consistent with ADR-011/033. | ADR-037 Prior art. | OK. |
| — | Numbering 037 correct (035/036 latest; the rejected "ADR-034" is a non-file prose reference in ADR-013). | file listing. | OK. |
| — | Status vocabulary consistent with merged ADR-035/036 ("Proposed — recommends ..."). | ADR-035/036. | OK (revised recommendation wording). |

## Recommendation

Fix the ADR-035 "satisfies" overstatement; the rest is consistent. Applied.
