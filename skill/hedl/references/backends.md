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

## `.work/` as the cross-harness work-item layer (WORK-0076)

ADR-036 (DIRECTION-2) positions `.work/` as **"the substrate that makes the gate
work-item-aware"** — a work-item state layer, not a competing task tracker. Two
properties make it cross-harness:

- **Stdlib-readable, tool-independent (capability).** It is plain JSON on disk
  (`work.json`, `context.json`, `phases/*.json`), read with the standard library —
  no Hedl runtime or LLM in the read path. So *any* harness that can read a file
  could consume it; the gate (`am_i_done.py`) is itself one such stdlib reader.
  (Projecting Hedl into non-Claude harnesses is a separate, unbuilt item —
  WORK-0047; this is the layer's portability, not shipped multi-harness support.)
- **What makes the gate "work-item-aware" is what it reads from this layer:** the
  stale-WORK-ID check (`check_commands`) and the work-item read (`_load_work_items`)
  consult `work.json` (see Read paths below); `check_config` reads
  `.work/config/dispatch-rules.json`; `check_markdown_schemas` reads
  `.work/config/markdown-schemas.json`; `check_state_template_sync` guards the
  framework-config subset. The layer is the *input*; the gate is a consumer.
- **No lock-in — the gate-only tier's default run needs no `.work/`.** The gate
  tier projects no `.work/`, and every `.work/`-reading check in the **default
  run** skips cleanly when it is absent rather than failing: `check_config` → skip,
  `check_commands` → skip, `check_markdown_schemas` → skip, `check_state_template_sync`
  → skip (adopter layout), `_load_work_items_local` → empty set, and the gate's own
  `_append_gate_insight` no-ops without creating `.work/` (cf. `budget_manager`,
  WORK-0002). So an adopter runs the bare gate with zero `.work/` adoption; native
  plan-mode / TodoWrite / memory serve ad-hoc tracking. (`check_dispatch` is the
  one exception: it requires `dispatch-rules.json` and is opt-in via `--panel` /
  the team tier, never part of a gate-only default run.) Guarded by
  `TestGateOnlyNoWorkDir` in `test_am_i_done.py`.
- **Pluggable (ADR-022).** The same work-item layer is consumable via
  `[state] backend = "local-file"` (`.work/work.json`) or `"github-issues"` — the
  rest of this document audits the github-issues backend.

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

## Known limitations (deferred to WORK-0032)

The read path is shallow by design today; the adversarial review of WORK-0007
surfaced these, all rooted in the same gap — **identity is the issue title, and
the read is not scoped to Hedl-managed issues**. The fix is the `hedl:work`
label-scoped, paginated read that WORK-0032 owns.

- **Title-based identity / trust boundary.** A live WORK-ID is any open issue
  whose title matches `WORK-NNNN:`. Anyone who can open an issue can therefore
  inject a synthetic live ID (suppressing a stale-ID flag), and a non-Hedl issue
  that happens to match (`WORK-1234: customer ticket`) is mis-read as Hedl work.
  On a repo where untrusted users can open issues, do not rely on this backend
  until label-scoping lands. (Consistent with the gate's stance that the real
  untrusted-input control is fork/PR approval, not the gate — see WORK-0021.)
- **Completeness cap.** The read counts *all* open issues against the 1000 cap,
  not just WORK-issues; a repo with many non-Hedl open issues will hit the cap
  and the gate will FAIL the stale-ID check (loudly, by design — it cannot prove
  completeness). Label-scoping + pagination removes this.
- **Empty live set.** With zero open WORK-issues the github read returns an empty
  set with no error; unlike the local-file path, the stale-ID check is not
  skipped, so command-file WORK-ID references would all flag as stale.
- **`gh` stderr** is surfaced (truncated) in the gate output; it can carry the
  GitHub hostname / API error detail in CI logs.

Until WORK-0032 addresses these, the github-issues backend is suitable for
single-operator / trusted-issue repos and is not Hedl's own backend yet
(local-file remains the default; the dogfood migration is WORK-0033).

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
