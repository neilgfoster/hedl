# State backends

Hedl reads its work-item state from a pluggable backend, selected by
`hedl.toml` (ADR-022):

```toml
[state]
backend = "local-file"   # default; or "github-issues"
```

`local-file` reads `.work/work.json`. `github-issues` reads GitHub Issues via
the `gh` CLI. This document is the WORK-0007 audit of the `github-issues`
backend: what is wired and working, what is not yet built, and the label scheme
proposed for the migration (WORK-0032/0033).

---

## Read paths (what the gate consults)

| Consumer | Backend call | Expected schema | Status |
|---|---|---|---|
| stale-WORK-ID check (`check_commands`) | `gh issue list --state open --json number,title --limit 1000` | issue titles formatted `WORK-NNNN: <desc>`; open issues are live items | **wired and working** |

Selection and config:

- `_state_backend()` reads `[state] backend` from `hedl.toml` (default
  `local-file`). `install.py` writes it (`_set_hedl_state_backend`), guarded by
  `_validate_backend_name` (rejects anything but `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`),
  and a schema 1→2 migration relocates a legacy `state_backend` from
  `context.json` into `hedl.toml`.
- `_load_work_items()` dispatches to `_load_work_items_github()` or
  `_load_work_items_local()`. Both return `(live_ids, error_or_None)`; a read
  error propagates as a gate FAIL rather than a silent empty set.
- The github read is capped at `_GITHUB_ISSUE_READ_LIMIT` (1000). Hitting the cap
  is a loud FAIL (the read may be truncated), not a silent partial set — a
  truncated read would let a stale WORK-ID slip past the gate.

What the read path does **not** do today: it reads `number,title` only. It does
**not** read `assignees`, labels, state-reason, or any field beyond the title
ID. Hedl's "view" of github-issues state is currently just the set of live
WORK-IDs.

---

## Write paths (what needs to exist — not yet built)

The `github-issues` backend is **read-only today**. Nothing writes issue state.
The following write paths are required for a full team-tier backend and are
**not built**:

| Write path | Trigger | Status |
|---|---|---|
| Status transition (open → closed) | `/finish-task`, PR merge (`Fixes #N`) | **not built** |
| Assignee read into Hedl state | claim/release, `/iterate` selection | **not built** (gap AC2) |
| Concurrent-claim detection | two operators claim one issue | **not built** (gap AC3) |
| Phase close-out | `/phase-complete` | **not built** |
| Label application on item creation | migration / new item | **not built** (scheme below) |

These gaps are tracked as backlog (WORK-0032 migration, WORK-0033 dogfood, and
WORK-0059 for the multi-operator read layer — assignees + concurrent-claim
detection). They are deferred deliberately: Hedl has not migrated its own queue
to github-issues yet, and there is no current multi-operator user, so building
the claim/assignee layer now would be speculative (WORK-0007 audit decision,
2026-05-30).

---

## File-level conflict across operator PRs

Independent of the state backend, `am_i_done.py --streams <branchA,branchB,...>`
diffs each branch against `main` and FAILs if any file is touched by more than
one stream. This is how parallel-operator work is kept from colliding at merge
time; it is backend-agnostic (it reads git, not the backend). Covered by a
regression test (`TestCheckStreams`).

---

## Proposed label scheme (AC9 — open for refinement in WORK-0032)

When the migration creates issues, map Hedl metadata to labels:

| Hedl field | Label |
|---|---|
| `phase` | `phase-N` |
| `change_class` | `change-class:<feat\|fix\|refactor\|docs\|chore\|spike>` |
| `workstream` | `workstream:WS-<PLAN\|REQ\|TECH\|ARCH>` |
| `priority_band` | `priority-band:<value>` |
| scope marker | `hedl:work` (identifies Hedl-managed issues) |

The historical `WORK-NNNN` ID is preserved in the issue **title** (`WORK-NNNN:
<desc>`) so commits and ADRs that cite it keep resolving. The `hedl:work` label
lets the read path filter to Hedl-managed issues once a repo mixes Hedl work
with ordinary issues (a refinement for WORK-0032; today the read matches on the
title pattern alone).
