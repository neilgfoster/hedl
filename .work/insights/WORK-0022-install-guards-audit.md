# WORK-0022 — Audit: malformed .hedl-tier crash and includes-cycle are both real

**Date:** 2026-05-29
**Author:** WORK-0022 implementation
**Work item:** WORK-0022
**Branch:** fix/install-guards

## Why this note exists

WORK-0022's AC1 requires an audit before any code change (audit-first per the
WORK-0019/WORK-0021 precedent), because the line numbers in the repo-health
finding predate WORK-0016 and WORK-0020, which both edited `install.py`. This
records what the audit found and the explicit fix-vs-guard decision.

## What was audited

`install.py`, current line numbers (post WORK-0016/0020):

1. `.hedl-tier` (TIER_MARKER) JSON parsing — three sites:
   - `cmd_install:406` — `json.loads(marker.read_text()).get("tier")` wrapped in
     `try/except (json.JSONDecodeError, AttributeError): pass`. **Already
     guarded** (WORK-0016): a malformed marker is treated as "no current tier",
     i.e. a fresh install. Lenient-by-design; correct for install.
   - `cmd_status:490` — `data = json.loads(marker.read_text())`. **UNGUARDED.**
   - `cmd_doctor:608` — `data = json.loads(marker.read_text())`. **UNGUARDED.**

2. `includes` flattening — `_flatten_projections:174` and `_flatten_inits:184`
   recurse over `tier.get("includes", [])` with **no visited set / no cycle
   detection**.

## Findings — both REAL (not false positives)

- **Malformed `.hedl-tier` crash:** reachable via `install.py --status` and
  `install.py --doctor` with a hand-edited / truncated / wrong-type marker.
  `json.loads` raises `JSONDecodeError` straight to the top — a Python
  traceback, not an actionable message. `cmd_install` is already safe; only
  status/doctor crash.

- **`includes` cycle:** a `tiers.json` whose `includes` form a cycle (e.g.
  `team -> lightweight -> team`) makes `_flatten_projections` / `_flatten_inits`
  recurse without bound. Python raises `RecursionError` (stack overflow) rather
  than hanging — but it is an unhelpful traceback that never names the cycle.
  Reachable from `cmd_install`, `cmd_status`, and `cmd_doctor`, all of which
  flatten the bundled `tiers.json`; an adopter who hand-edits `tiers.json`, or a
  contributor who introduces a cycle, hits it.

## Decision — FIX both (mirrors WORK-0021, not WORK-0019)

Neither is a false positive, so the resolution is a fix with regression tests,
not a guard-only closeout. `change_class` stays `fix`.

1. Add a single corruption-aware reader `_read_tier_marker(marker)` returning
   `(tier, error_message)`; never raises on a malformed marker. `cmd_status` and
   `cmd_doctor` print the actionable message and exit non-zero; `cmd_install`
   reuses the reader for its existing lenient behaviour (malformed -> treat as
   fresh).
2. Add ordered-path cycle detection to `_flatten_projections` / `_flatten_inits`
   via a recursion `_path` argument; on revisit raise a clear error naming the
   cycle path, surfaced as a clean non-zero exit (not a traceback) in `main()`.

## Residual / accepted

- `_read_tier_marker` now treats a missing/non-string `tier` field as an error
  (previously `cmd_status` printed `tier: unknown` and continued). This is the
  intended AC outcome ("missing keys, wrong types produce an actionable error").
