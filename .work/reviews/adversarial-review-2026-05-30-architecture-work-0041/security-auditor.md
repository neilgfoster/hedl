# security-auditor — WORK-0041 review

**Run:** adversarial-review-2026-05-30-architecture-work-0041
**Model:** claude-opus-4-8
**Commit:** 4b1e43d..5021cd9

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| BLOCKING → rebutted | Trust boundary | "app/dependabot" login spoofable via a colliding GitHub App | am_i_done.py _DEPENDABOT_LOGINS / check_template | Rebutted — App slugs are globally unique; "dependabot" owned by GitHub; is_bot is GitHub-verified |
| BLOCKING → rebutted | TOCTOU | author at gate time vs merge time | check_template | Rebutted — required check re-runs on synchronize, tied to head SHA |
| SIGNIFICANT → noted | Trust model | is_bot not cryptographically verified (MITM) | check_template | Pre-existing gate trust model (TLS + gh); documented |
| SIGNIFICANT → noted | Injection | PR_BODY env has no size limit | check_template (pre-existing) | Pre-existing; not introduced |
| SIGNIFICANT → noted | Audit | exemption not logged distinctly in insights | _append_gate_insight | Message says "authored by Dependabot"; insight detail is a pre-existing pattern |
| SIGNIFICANT → addressed | Logic | `is True` correct but is_bot=1 untested | check_template | Test added (is_bot=1 not exempt) |

## Recommendations

- Login+is_bot is a safe identity basis (slug uniqueness + verified account type);
  documented in the code. App-ID pinning is optional future hardening (needs a
  verified numeric ID; deviates from the AC's login method).
