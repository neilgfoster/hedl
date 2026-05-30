# future-engineer — WORK-0007 review

**Run:** adversarial-review-2026-05-30-architecture-work-0007
**Model:** claude-haiku-4-5
**Commit:** 5848141..6bb210a

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → deferred | Interface coupling | identity bound to issue TITLE, not the `hedl:work` label; switching later is a breaking read-path change on a populated tracker | am_i_done.py:469,540-545; backends.md | Deferred to WORK-0032 with an explicit "label from day one" AC so the switch is non-breaking |
| SIGNIFICANT → deferred | Schema versioning | label scheme has no version marker / migration story | backends.md label table | Folded into WORK-0032 (apply scheme + version at creation) |
| MINOR → deferred | Label cardinality | `priority-band:<value>` is free-form → label proliferation | backends.md | WORK-0032 (enumerate or keep in body) |
| MINOR → deferred | Scale | unpaginated 1000 cap counts all repo issues | am_i_done.py | WORK-0032 (label-scope + paginate) |

## Recommendations

- The painful-later coupling (title identity) is real; the mitigation is to make
  `hedl:work` the identity filter as part of the migration that first populates
  issues (WORK-0032), before any repo accumulates title-only issues. Captured in
  WORK-0032's ACs and backends.md.
