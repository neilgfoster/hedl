# edge-case-hunter — WORK-0048 review

**Run:** adversarial-review-2026-05-30-architecture-work-0048
**Model:** claude-opus-4-8
**Commit:** 7b2cce4..b102b6b

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| BLOCKING → fixed | Uncaught exception | UnicodeDecodeError (binary file) is a ValueError, not OSError/JSONDecodeError → escaped → raw traceback | install.py _load_tiers | Fixed — open utf-8; `except ValueError`; test added |
| BLOCKING → fixed | Missing shape validation | valid JSON non-dict / no `tiers` key → caller crashes with TypeError/KeyError | install.py cmd_install:`tiers["tiers"]` | Fixed — shape guard → TiersConfigError; parametrised test |
| SIGNIFICANT → fixed | Inconsistent callers | _flatten_tier_key vs cmd_install disagree on bad shape | install.py | Fixed at the single chokepoint (_load_tiers guard) |
| SIGNIFICANT → fixed | Test gap | no binary / non-dict tests | test_install.py | Added |
| MINOR → fixed | Misleading message | PermissionError → "or not valid JSON" | _load_tiers | Fixed — split clauses |

## Recommendations

- Exception ordering verified: FileNotFoundError (specific) before OSError before
  ValueError. Post-fix, every malformed-manifest class exits cleanly.
