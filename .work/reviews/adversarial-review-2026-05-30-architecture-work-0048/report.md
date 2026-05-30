# Adversarial Review — WORK-0048 (architecture)

**Log:** adversarial-review-2026-05-30-architecture-work-0048
**Session:** in-session
**Depth:** Standard (4-agent panel; gate-adjacent script)
**Commit:** 7b2cce4..b102b6b

Panel: [security-auditor](security-auditor.md), [determinism-auditor](determinism-auditor.md),
[scope-auditor](scope-auditor.md), [edge-case-hunter](edge-case-hunter.md).
Validated via `am_i_done.py --check dispatch`. Scope: `_load_tiers` error handling
in install.py.
Verdict: **PASS** (CONDITIONAL on first pass; two BLOCKING traceback paths fixed).

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Security | PASS — no exec; error text trimmed (OSError uses strerror, not path repr) |
| Determinism | PASS — deterministic exit; only the message text varies (acceptable for install-time) |
| Scope | PASS — install.py + test only; reuses WORK-0022's TiersConfigError |
| Edge cases | PASS after fix — binary (UnicodeDecodeError) and wrong-shape manifests now exit cleanly |

## Strengths

- Reuses the established TiersConfigError clean-exit path (caught in main()).
- After the fix, every malformed-manifest class (missing, unreadable, invalid
  JSON, non-UTF-8, valid-but-wrong-shape) exits cleanly with no traceback.

## Blocking Findings

Both raised by edge-case-hunter; both fixed in b102b6b:

- **UnicodeDecodeError escaped.** A binary tiers.json raises UnicodeDecodeError
  (a ValueError, not OSError/JSONDecodeError), bypassing the original clauses →
  raw traceback. Fixed: open as utf-8; `except ValueError` covers JSONDecodeError
  + UnicodeDecodeError. Test added.
- **Valid JSON, wrong shape.** `[]`/`42`/dict-without-`tiers` parsed, then crashed
  a caller (`tiers["tiers"]`) with an uncaught TypeError/KeyError. Fixed: shape
  guard raising TiersConfigError. Test added (parametrised).

## Significant Findings

- **Inconsistent caller shape handling** (edge-case) — addressed by the shape
  guard in `_load_tiers` (single chokepoint; all callers get a clean error).
- **Missing test coverage** for binary / non-dict (edge-case) — added.

## Minor Findings

- **PermissionError message "or not valid JSON" misleading** (security, edge-case)
  — fixed by splitting OSError vs ValueError clauses.
- **`{exc}` path leak / determinism of message text** (security, determinism) —
  OSError clause now uses `exc.strerror`; the ValueError clause's `{exc}` is a
  parse position, not a path. TIERS_FILE in the message is the install's own
  path (actionable, not sensitive).

## Next Actions

PASS → operator handoff. No fix cycle outstanding.
