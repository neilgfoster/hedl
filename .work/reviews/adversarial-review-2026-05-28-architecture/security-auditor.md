# security-auditor — WORK-0030 review

**Run:** adversarial-review-2026-05-28-architecture
**Model:** claude-opus-4-8
**Commit:** 8811d78

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT | Supply chain | copying workflow YAML launders provenance; no digest pinning | install.py:166,177 | Rejected — symlink carried identical in-repo content risk; no new boundary |
| SIGNIFICANT | Path traversal | `proj["source"]` joined to SKILL_ROOT with no containment check | install.py:282 | Deferred — tracked by WORK-0020; tiers.json is repo-controlled; pre-existing |
| SIGNIFICANT | Path traversal | `proj["target"]` joined to repo with no containment check | install.py:283 | Deferred — tracked by WORK-0020; pre-existing |
| SIGNIFICANT | TOCTOU | doctor read between is_symlink() and read_bytes() | install.py:432-438 | Deferred — requires world-writable repo; pre-existing pattern |
| SIGNIFICANT | TOCTOU | unlink + copy2 window in _project_one | install.py:155-166 | Deferred — pre-existing code |
| MINOR | Audit | no SHA logged on copy | install.py:166,177 | Deferred — over-engineering for in-repo projection |
| MINOR | Windows | backslash target defeats predicate | install.py:138-144 | Deferred — tiers.json targets are POSIX |

## Recommendations

- No new security risk introduced by the copy-vs-symlink change itself.
- Containment enforcement is correctly tracked by WORK-0020, not this item.
