# Repo-health — 2026-05-30 (Full panel, Phase-2 entry)

**Log:** repo-health-2026-05-30-full
**Session:** fresh (/start-session this session)
**Depth:** Full — 10 lenses run in parallel against a clean clone
**Commit:** 708ee36 (clone at /tmp, read-only; deleted after run)
**Distinct from:** `repo-health-2026-05-30/` which was only a targeted re-run of the
two Phase-1-triggering BLOCKINGs for DoD #4. This is the first full sweep at the
Phase-1 → Phase-2 boundary.

Panel: security-auditor, determinism-auditor, edge-case-hunter, scope-auditor,
simplicity-enforcer, historian, existential-challenger (7 core) + new-engineer,
performance-skeptic, quality-synthesizer (3 composable). Raw outputs are the
sibling `*.json` files. The four highest-impact findings were re-verified against
the clone before synthesis (see "Verified" tags).

---

## Verdict

**HEALTHY CORE, BLOCKED ADOPTION SURFACE.** The engineering substrate is strong
(quality-synthesizer mean ≈ 7.1/10; supply-chain 9, security 8, code 8). No
finding undermines the gate's integrity or the Phase-1 close. But the **adopter
install/run path is broken in three independent ways** — directly contradicting
Phase 2's stated goal ("Adoption readiness"). The most consequential findings are
documentation/packaging defects, not core-code bugs.

Historian returned zero ADR/requirement contradictions — the governance layer is
internally consistent.

---

## Dimension Scores

| Dimension | Score | Note |
|---|---|---|
| code_quality | 8 | typed, dataclass-based, AST-gated invariants |
| design_quality | 7 | coherent gate abstraction; monolithic 1703-line am_i_done.py |
| security | 8 | no shell=True, path containment, verified-author exemption |
| supply_chain | 9 | zero runtime deps, SHA-pinned, --frozen, CodeQL |
| utility_claude_code | 7 | real done-gate; value gated on adopting ceremony |
| accuracy | 6 | "every Phase-1 item reviewed" overstated: 16 of 30 have dedicated reviews |
| maintenance | 7 | disciplined; 10.7k md lines a load for a small team |
| utility_vs_complexity | 5 | ~4.7k LOC carries 29 ADRs + 8 agents at v0.1.0 |

---

## Blocking Findings

### Adopter readiness — the Phase-2 headline

1. **Gate fails on first run in an adopter repo.** `check_docs_index` has no
   adopter/framework guard (contrast `check_state_template_sync`,
   am_i_done.py:677, which returns None for adopters). It always runs
   (am_i_done.py:1623) and FAILs if any `docs/**/*.md` is unlinked from README.
   The lightweight tier projects `docs/spec/{prd,epic,task}-template.md`
   (tiers.json:36-38) into the adopter's `docs/`, which their README won't link.
   `getting-started.md:88-91` presents that exact gate command as the install
   verification step. **Verified.** New adopter's very first gate run goes red.

2. **Routed install commands don't resolve in an adopter repo (= WORK-0001).**
   SKILL.md routes status/doctor/tier/migrate/version to
   `skill/hedl/scripts/install.py` (SKILL.md:38,60-64) — the framework layout. In
   an adopter repo the skill lives under `.claude/skills/hedl/`, so the path is
   "No such file or directory". **Verified.** This is the open WORK-0001 bug,
   independently surfaced by the panel — strong corroboration it is real and
   currently broken.

3. **Manual-install docs contradict the tool.** `tiers.md:104` tells adopters to
   copy `skill/hedl` into `.claude/skills/Hedl/` and copy `.work/`, but
   install.py/tiers.json never create `.claude/skills/` — they project individual
   files. Casing also diverges (`Hedl` vs lowercase `hedl`). A newcomer builds a
   layout the tool never references.

> These three converge: **Phase 2 cannot claim "adoption readiness" until the
> install/run/doc path works end-to-end for a fresh adopter.** WORK-0001 covers
> (2); (1) and (3) are not yet ticketed and are equally adopter-blocking.

### Process verdicts — existential lens, operator decisions

These are not code defects; they are decisions the Phase-2 DoD ("cull-or-prove,
no third deferral") already forces. The panel argues for *cut now, at the start*:

4. **Adopter absence.** ADOPTERS.md lists one adopter (Hedl). Lume/Wyrd are
   in-session bootstraps, unlisted. Either list them or rename Phase 2 to match
   reality ("internal hardening + deferred-bet resolution").
5. **budget_manager** — culling-candidate with zero rescue cases, ~554 lines.
   Edge-case + simplicity independently flag bugs (fcntl crash, wrong-shape
   KeyError) and premature locking in the *same* module. Converging signal: cut it.
6. **ADR proliferation** — WORK-0050/0051/0052/0053 require a Proposed ADR before
   any code; WORK-0053 (reputation) tensions with ADR-003/ADR-025. Decide now;
   they crowd out WORK-0001 and WORK-0056.

## Significant Findings

### Code & correctness

Cross-cutting theme (security + edge-case + determinism): **regex/JSON from
config is fed to `re`/dict-subscripts without `re.error`/shape guards**, so a
malformed (PR-merged) config crashes the gate rather than FAILing cleanly.

- **dispatch-rules.json pattern → uncaught `re.error`** (am_i_done.py:415).
  re.search is outside the JSON-load try. **Verified.** Malformed pattern crashes
  the gate; catastrophic pattern hangs CI. *(Trust surface is repo-committed
  config, so exploit requires a merged change — robustness, not RCE.)*
- **markdown-schema regexes** (check_markdown_schema.py:180,205,220) — same
  pattern, schema-supplied, ReDoS-capable, no timeout.
- **PR body → subprocess env unbounded** (am_i_done.py:1144-1152) — 64KB
  attacker-controlled body, downstream `(.*?)`/DOTALL regexes.
- **fcntl unconditional import** (budget_manager.py:31) — **Verified.** Windows
  ImportError; breaks `check_budget` via subprocess. install.py *has* a Windows
  copy-mode guard, so Windows is an intended target → real gap. (Or declare
  Windows unsupported explicitly.)
- **Wrong-shape JSON crashes** — release.py `completed` as dict → AttributeError
  (release.py:149); budget get_tier/tier_description KeyError
  (budget_manager.py:189,201); check_markdown_schemas KeyError (am_i_done.py:864).
- **make/npm/pnpm in default verify allow-list** (am_i_done.py:181) —
  **Verified present.** Transitively executes committed Makefile/scripts. NOTE:
  this re-litigates the **WORK-0021 accepted decision** (defense-in-depth, real
  control is fork-approval) — recommend documenting, not re-fixing.

### Scope & process

- **Self-improvement loop** (reflect.py/contribute.py/docs, projected into
  lightweight tier) was built complete but is a CULLING-CANDIDATE with zero
  /contribute PRs — same cull-or-prove decision as budget_manager.
- **Watchlist verdict coupling is weak** — 6 of 8 Phase-1 objectives missed
  threshold; only 2 culled, 4 extended. The DoD's "no third deferral" needs a
  hard rule or it repeats.
- **Recursive workstream cluster** (WORK-0010/0011/ADR-031) — threshold (5-7
  concurrent workstreams) structurally unreachable at N=1 operator; cull.
- **WORK-0004** (Prior-art on ADR-001..016) and **WORK-0058** (WS-SPIKE
  one-liner) are process accretion; both align with the recorded user-preference
  to keep conventions in standards.md, not new/expanded process docs.
- **Performance:** nested subprocess fan-out in skill-meta check (~7 spawns + ~6
  git forks per gate run × CI matrix; am_i_done.py:1346) and per-file re-globbing
  in markdown-schema. Small absolute cost; cheap to fix.

## Minor Findings

See the per-agent `*.json` files. Recurring low-severity items: `events.jsonl`
unbounded (no rotation), missing `encoding='utf-8'` on install.py read_text (4
sites), non-atomic hedl.toml write, mixed-fence miscount, doc gaps (--migrate
/--version undocumented), tier-name inconsistency, 'tier' term overloaded
(adoption vs budget), agent-roster conflation in commands.md.

---

## Strengths

- Gate runs identically local + CI and self-validates its agent table
  (am_i_done.py:579).
- ~413 tests; stdlib-only invariant AST-gated (test_stdlib_only.py:42-58).
- Dependabot exemption keyed to verified author, not spoofable body
  (am_i_done.py:1112,1138).
- install.py path containment validated before any write
  (install.py:296-339).
- Zero runtime deps, SHA-pinned actions, weekly CodeQL.

---

## Next Actions

1. **Adoption-path triage first** — WORK-0001 (routed path) is the keystone;
   open two new items for the `check_docs_index` adopter-guard (finding #1) and
   the `tiers.md`/casing doc contradiction (finding #3). Phase 2's premise
   depends on these three landing before any adopter-facing UX work.
2. **Robustness cluster** — one item: wrap config-supplied regex + dict access
   in `re.error`/shape guards across am_i_done.py / check_markdown_schema.py /
   release.py / budget_manager.py (findings group above). Mechanical, high-value.
3. **Windows decision** — fix fcntl guard or declare Windows unsupported and add
   a startup check.
4. **Force the deferred-bet culls now, not at phase end** — budget_manager,
   self-improvement loop, recursive cluster, WORK-0004, WORK-0058. The DoD
   already mandates the decision; the panel's evidence supports *cut*.
5. **Do not re-fix** the make/npm allow-list — record it as a known
   defense-in-depth limitation (already decided in WORK-0021).
6. **Carry forward** the watch on net-new process (Significant from the 05-28 and
   targeted 05-30 reports) — accretion remains the dominant non-code risk.
