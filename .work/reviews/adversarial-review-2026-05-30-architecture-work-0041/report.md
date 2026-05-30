# Adversarial Review — WORK-0041 (architecture)

**Log:** adversarial-review-2026-05-30-architecture-work-0041
**Session:** in-session
**Depth:** Standard (4-agent panel; security-sensitive gate code)
**Commit:** 4b1e43d..5021cd9

Panel: [security-auditor](security-auditor.md), [determinism-auditor](determinism-auditor.md),
[scope-auditor](scope-auditor.md), [edge-case-hunter](edge-case-hunter.md).
Validated via `am_i_done.py --check dispatch`. Scope: the Dependabot exemption in
the gate's PR-template check.
Verdict: **PASS** (two BLOCKINGs rebutted with reasoning; defensive tests added).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Security | PASS — exemption keyed off is_bot + a globally-unique app slug; not spoofable by a contributor |
| Determinism | PASS — empty finding set; exact membership + boolean, no inference |
| Scope | PASS — empty finding set; matches the ACs, three files |
| Edge cases | PASS after fix — fail-closed on null author / non-bool is_bot, both now tested |

## Strengths

- Removes real recurring friction (hand-rewriting every Dependabot PR body) while
  keeping human PRs fully enforced.
- Fails closed: anything but a verified Dependabot author runs the validator.

## Blocking Findings

Both raised by the panel; both **rebutted** (reasoning recorded):

- **security — "app/dependabot login is spoofable; register a colliding app".**
  Rebutted: GitHub App slugs are globally unique (the "dependabot" app is owned by
  GitHub; no attacker can present that slug), and `is_bot` reflects the
  GitHub-verified account type (not contributor-settable). So `is_bot AND login ∈
  {app/dependabot, dependabot[bot]}` reliably identifies Dependabot. App-ID
  pinning is marginally more robust but deviates from the AC's prescribed login
  method and would require hardcoding an unverified numeric ID — declined.
- **edge — subprocess.run has no try/except (FileNotFoundError).** Rebutted:
  pre-existing (predates this change); `python3` vanishing mid-run is near-
  impossible since am_i_done is itself python3. Not in WORK-0041's scope.

## Significant Findings

- **security — TOCTOU author-at-gate-vs-merge.** Rebutted: standard PR-gate
  semantics — the required check re-runs on every push (`synchronize`), tied to
  the head SHA; a branch transfer re-triggers it. Not introduced here.
- **security — is_bot not cryptographically verified (MITM); PR_BODY env size;
  audit-log granularity.** Pre-existing trust-model / patterns shared by all
  gh-based gate checks; not introduced here. Documented trust basis in the code.
- **edge — test gaps (null author, is_bot=1).** Fixed: defensive tests added
  (fail-closed), plus the dependabot[bot] login variant.

## Minor Findings

- gh code=0 + empty stdout treated as empty body → fails closed (safe). Noted.
- Renovate/other bots not exempt — correct per the AC (Dependabot-only).
- validator stderr not surfaced on failure — pre-existing, minor.

## Next Actions

PASS → operator handoff. Possible future hardening (not now): pin to Dependabot's
numeric App ID; widen to a documented verified-bot allowlist if Renovate is adopted.
