# WORK-0019 — The reported startup.sh printf RCE is a false positive

**Date:** 2026-05-28
**Author:** WORK-0019 implementation
**Work item:** WORK-0019
**Branch:** chore/startup-printf-guard

## Why this note exists

Repo-health 2026-05-28 (BLOCKING #6a, security-auditor) reported a printf
format-string injection (RCE) in `.claude/startup.sh`, claiming a
project-derived name is interpolated into a printf *format string* without
sanitisation, so a name containing `%s`/`%n` could control the format string.

Audit found the finding **not reproducible**. This note records the evidence
so the BLOCKING item can be closed honestly rather than by a fabricated fix.

## The actual code

`skill/hedl/integrations/claude-code/startup.sh` (symlinked to
`.claude/startup.sh`), line 8:

```bash
printf "║  %-36s ║\n" "$PROJECT_NAME — SESSION START"
```

The format string is the **literal** `"║  %-36s ║\n"`. `$PROJECT_NAME` is the
**data argument** consumed by `%-36s`. printf only interprets conversion
specifiers in its *first* argument (the format); specifiers appearing inside a
data argument are emitted verbatim. There is no path by which `PROJECT_NAME`
reaches the format-string position.

## Evidence

- **Empirical:** with `PROJECT_NAME='%n%n%s%s ATTACK'`, the script prints the
  specifiers literally (`║  %n%n%s%s ATTACK — SESSION START ║`) and exits 0 —
  no substitution, no crash.
- **Git history:** the printf line has had exactly one form since the initial
  commit (#1). It was never the vulnerable `printf "...$NAME..."` shape.
- **Surface:** the only dynamic shell interpolation in the script is
  `PROJECT_NAME` in that one safe printf. Every other dynamic section is a
  `python3 -c` block that keeps data inside Python.

The reviewer most likely pattern-matched "printf + interpolated variable"
without tracing argument vs format position.

## What this item delivered instead of a fix

- `skill/hedl/tests/test_startup_sh.py` — a regression guard that runs the real
  script against a `%n%n%s%s`-laden project name (and, in `full` mode, against
  specifier-laden work-item and session fields) and asserts every dynamic value
  renders literally with exit 0. A negative test
  (`test_guard_catches_vulnerable_printf_form`) rebuilds the script with the
  name moved into the format-string position and asserts the specifiers are no
  longer rendered literally — so the guard demonstrably distinguishes the safe
  form from the vulnerable one, in-repo and reproducibly, rather than by an
  asserted-but-unverified claim.
- **shellcheck (AC #3):** shellcheck is not installed in this environment and
  the `shellcheck-py` wheel could not be fetched (no network). Scope of the
  manual audit performed instead: the full script was read for shell-injection
  vectors (word-splitting, glob expansion, command substitution, and
  format-string position). The only dynamic shell interpolation is
  `PROJECT_NAME` in the one safe printf; no other shell issue was found. The
  format-string risk is now covered by the regression test. Wiring shellcheck
  into the gate for all shell scripts is out of scope here and is a candidate
  for a separate tooling item.

## A distinct risk class, explicitly out of scope

Every work-item and session field that startup.sh prints (title, status,
acceptance criteria, session entries) is emitted into the banner that an LLM
reads at session start. A process with `.work/` write access could craft those
fields as a **prompt-injection** payload against that LLM. This is a different
risk class from the reported printf RCE — it is not code execution and is not
what WORK-0019 covers. It is recorded here so a future reviewer does not
conflate it with the format-string finding; if it warrants attention it should
be filed as its own work item.
