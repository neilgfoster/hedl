# WORK-0021 — Audit: the [verify] cmd RCE is real, but narrower than reported

**Date:** 2026-05-28
**Author:** WORK-0021 implementation
**Work item:** WORK-0021
**Branch:** fix/verify-cmd-allowlist

## Why this note exists

WORK-0021's acceptance criteria require an audit before any code change
(audit-first per the WORK-0019 precedent). This records what the audit found
and the explicit fix-vs-guard decision. Unlike WORK-0019 (a false positive
closed with a guard), WORK-0021's audit confirms a **real** vulnerability —
so the resolution is a fix, not a guard. It is the counterpart outcome.

## What was audited

`_run_declared_check` in `.github/scripts/am_i_done.py:169-203` — the code
that executes `[verify.<name>]` commands declared in `hedl.toml`. All
`[verify]` paths route through it: the standard keys `lint`/`types`/`test`
(via `check_lint`/`check_types`/`check_tests` when `[verify]` is present)
and any extra keys (via `main()`'s extra-check loop).

## Findings

Already safe (the ticket's framing partly overtaken by the current code):

- `shlex.split(cmd_str)` (line 188) parses the command; `run()` (line 140)
  invokes `subprocess.run(cmd, ...)` with a **list** and no `shell=True`.
- So shell metacharacters (`;`, `|`, `&`, `$()`, backticks, globs, redirects)
  are **not** interpreted by a shell. The ticket's "require cmd be a list,
  execute without shell=True" is already implemented.

The real gap (genuine RCE vector):

- `shutil.which(cmd[0])` (line 195) only checks the executable exists **on
  PATH**. It does **not** constrain *which* executable runs.
- Therefore any `[verify]` entry can execute an arbitrary program with
  arbitrary args, e.g. `cmd = "python -c '<arbitrary code>'"`,
  `cmd = "bash -c '<...>'"`, `cmd = "node -e '<...>'"`, or `rm -rf <path>`.
  No shell is needed — these are valid argv vectors.

Threat model:

- `hedl.toml` is committed to the repo. The gate runs on the PR head in CI,
  so a malicious or compromised PR that adds a `[verify]` entry obtains
  **code execution in CI** (and on any operator who runs the gate locally on
  that branch). This is a supply-chain / CI-RCE vector, not merely a
  local-footgun.

## Decision: FIX

The missing executable allow-list is a real hole. Resolution is a code fix
(constrain `cmd[0]` to an allow-list), with regression tests and adversarial
review — not the WORK-0019 guard-only pattern. `change_class` stays `fix`.

Design (default allow-list contents + operator-extension config contract) was
confirmed with the operator before implementation, because it introduces an
operator-facing `hedl.toml` contract and could affect consumer repos that
already declare `[verify]` entries.

## Implemented design

- Default allow-list (operator's informed choice): `pytest, mypy, ruff, npm,
  pnpm, make`. Extend via `[gate] allowed_commands` (additive; entries with a
  path separator, a shell metacharacter, or a denylisted interpreter/forwarder
  name are ignored).
- `cmd[0]` must be a **bare name** (no path) — closes the absolute-/relative-path
  bypass without breaking project-local tools resolved via PATH (`.venv/bin`,
  `node_modules/.bin`).
- Shell metacharacters (`; & | < > $`, backtick, newline, CR, NUL, tab) are
  rejected outright; `cwd` (long form) must stay within the repo.
- An interpreter/forwarder denylist (sh, bash, python, node, env, xargs, ...)
  is enforced in both `_verify_allowlist` and `_run_declared_check`.

## Important reframing (from the adversarial security review)

This allow-list is **defense in depth, not a complete RCE control**. An allowed
runner can still execute committed repo content — `pytest` loads `conftest.py`,
`make` runs the `Makefile`, `npm`/`pnpm` run `package.json` scripts. No
command allow-list that includes a real test runner can close that. What it
*does* close is the trivial one-line inline vector (`python -c '...'` straight
from `hedl.toml`). The real control for untrusted contributions is GitHub's
"require approval to run workflows for outside/first-time contributors" — the
allow-list is not a substitute and the docs (references/tiers.md) say so. The
two-cycle review caught three terminal-symlink-class bypasses in the first
implementation (absolute-path, planted binary, extension interpreters); the
final design closes the concrete ones and documents the inherent residual.
