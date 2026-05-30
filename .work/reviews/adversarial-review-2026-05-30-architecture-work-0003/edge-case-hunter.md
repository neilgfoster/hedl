# edge-case-hunter — WORK-0003 review

**Run:** adversarial-review-2026-05-30-architecture-work-0003
**Model:** claude-opus-4-8
**Commit:** 92ead87..f04e0c5

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → fixed | Doc accuracy | added 1→2 row said "Relocates"; code only writes hedl.toml when non-default, always drops the key | install.py:173,178; versioning.md | Fixed — row reworded + chaining note |
| MINOR → noted | Doc gap | multi-step chaining (unversioned→2 in one run) not stated | install.py cmd_migrate loop | Added a one-line note |
| MINOR → out-of-scope | Presentation | `not-installed` emitted as prose, not `[not-installed]` | install.py:781,794 | Pre-existing --doctor table; not the WORK-0003 defect |
| MINOR → out-of-scope | Semantics | `not-installed` triggers on absent context.json regardless of tier; doc says "gate-only" | install.py:780-781 | Pre-existing; future --doctor pass |
| MINOR → out-of-scope | Validation | non-integer schema_version silently read as unversioned | install.py _schema_ver_int | Pre-existing edge; future pass |

## Recommendations

- The one in-scope accuracy bug (the row I added) is fixed. The pre-existing
  `--doctor` status-table nuances are real but belong to a separate versioning.md
  / `--doctor` pass, not the schema_version/hedl.toml correction.
