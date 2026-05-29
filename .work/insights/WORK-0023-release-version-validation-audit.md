# WORK-0023 — Audit: next_version crashes on non-canonical --current-version

**Date:** 2026-05-29
**Author:** WORK-0023 implementation
**Work item:** WORK-0023
**Branch:** fix/release-version-validation

## Why this note exists

WORK-0023's AC1 requires an audit before any code change (audit-first per the
WORK-0019/WORK-0021 precedent), since the line numbers predate other edits.
This records what the audit found and the explicit fix-vs-guard decision.

## What was audited

`skill/hedl/scripts/release.py`, current line numbers:

- `next_version(current, bump)` (lines 92-99):
  ```python
  parts = current.split(".")
  major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
  ```
- `main()` (lines 123-153): the only `try/except` (lines 135-138) wraps
  `_load_phase_completed`. `next_version(args.current_version, bump)` is called
  at line 141, **outside** any try/except, and the result is printed as JSON at
  line 151.

## Findings — REAL (not a false positive)

`next_version` is unguarded against non-canonical `--current-version`:

- `"1.2"` -> `parts = ["1","2"]` -> `int(parts[2])` -> **IndexError**
- `"v1.2.3"` -> `int("v1")` -> **ValueError**
- `"1.2.3-rc1"` -> `int("3-rc1")` -> **ValueError**
- `""` -> `int("")` -> **ValueError**

Because the call sits outside `main()`'s try/except, the exception propagates as
an unhandled Python traceback to stderr, and **no JSON is printed at all** — a
caller piping stdout to a JSON parser gets empty stdout, a traceback on stderr,
and exit code 1. The existing `{"error": ...}` envelope (line 137) only covers
the work-json load, not version parsing.

## Decision — FIX (mirrors WORK-0021/0022, not WORK-0019)

Real unhandled crash -> fix with tests. `change_class` stays `fix`.

1. Add `_parse_version(current)` validating against a canonical `X.Y.Z` regex
   (three dot-separated non-negative integers; the only grammar release.py
   claims to support — see the module docstring "Current X.Y.Z version"). Raises
   `ValueError` with an actionable message naming the grammar.
2. `next_version` parses through `_parse_version` (single source of the regex).
3. `main()` validates `--current-version` immediately after `parse_args`,
   emitting the same `{"error": ...}` JSON envelope + non-zero exit on invalid
   input — so the failure is machine-readable, never a traceback.
4. Document the supported grammar adjacent to the script (module docstring +
   `_parse_version` docstring).

## Scope note

Only the canonical `X.Y.Z` core is supported (no `v` prefix, pre-release, or
build metadata). This matches release.py's stated contract and the consumer
version axis; broader PEP 440 / SemVer-2 support is not in scope and is not
implied by this fix.
