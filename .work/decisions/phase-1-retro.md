# Phase 1 Retrospective — Discipline restoration

Date: 2026-05-30
Duration: 2026-05-28 → 2026-05-30

## What we built

30 Phase-1 items closed. By band:

- **BLOCKING (9):** the gate-on-main fixes (WORK-0029 schema, WORK-0030 real
  `.github/` files so CI actually runs), phase authoring (WORK-0016/0017), the
  security RCE band (WORK-0019 startup.sh, WORK-0020 SKILL_ROOT containment,
  WORK-0021 verify allow-list, WORK-0022 .hedl-tier/include guards, WORK-0023
  release.py validation), and the discipline tracker (WORK-0018).
- **GOVERNANCE (7):** WORK-0005 (existential-challenger → 8th named agent),
  WORK-0009 (Principle 4 = per-operator), WORK-0024 (state_backend → hedl.toml),
  WORK-0025 (.work/ vs work-state retain-and-guard), WORK-0026 (tier description),
  WORK-0027 (workstream double-definition; ADR-019 superseded), WORK-0028 (count
  drift + doc-facts detector).
- **BLIND-SPOT (2):** WORK-0002 (budget_manager gate-only), WORK-0003 (versioning.md).
- **POSITIONING (1):** WORK-0014 (README lead-with-disqualifiers per ADR-011/023).
- **normal/high/deferred (11):** WORK-0031 (/pr-ready 5th command), WORK-0034
  (/iterate→PR), WORK-0007 (github-issues audit + backends.md), WORK-0048
  (tiers.json guards), WORK-0041 (Dependabot template exemption), WORK-0037
  (ADOPTERS.md), WORK-0038/0039/0040 (Dependabot bumps), WORK-0042 (.gitignore).

## Definition of Done — final status

1. BLOCKING closed + gate green on main w/ required checks — **VERIFIED** (all 9
   BLOCKING incl. WORK-0018 complete; branch protection enforces the four
   `am_i_done` matrix contexts).
2. Security RCE fixes each with a fail-before regression test — **VERIFIED**
   (WORK-0019/0020/0021/0022/0023; tests in skill/hedl/tests/).
3. Every GOVERNANCE item closed, one source of truth — **VERIFIED** (zero
   GOVERNANCE items open).
4. WORK-0018 closed + repo-health re-run shows findings resolved — **VERIFIED**
   (.work/reviews/repo-health-2026-05-30/: goal-displacement + validation-theatre
   both resolved).
5. Every remaining item closed or reclassified-with-rationale — **VERIFIED**
   (7 items reclassified to Phase 2 with `reclassify_reason`; Phase-1 open = []).
6. Phase existential cycle recorded — **VERIFIED**
   (.work/reviews/phase-1-complete-2026-05-30/).
7. am_i_done passes — **VERIFIED** (gate green on the delivering branch).

## Learning goals — what we learned

- **LG1 (does leading with the gate change how the framework reads to a new
  adopter?)** — **Answered, qualified.** WORK-0014 repositioned the README
  (disqualifiers-first per ADR-011, gate as the differentiator); the new-engineer
  adversarial lens judged a newcomer unblocked within 30 minutes after fixes. This
  is a Claude proxy, not a live external adopter — treat as indicative, re-confirm
  with a real adopter.
- **LG2 (can WORK-0010's recursive-workstream model preserve solo/flat usage?)** —
  **UNANSWERED.** WORK-0010 was not built; ADR-019 (the recursive primitive) was
  superseded and the model deferred to Phase 2. The question is inherited by
  Phase 2, gated on WORK-0010 if/when demand activates it.
- **LG3 (does dogfooding github-issues on Hedl's own queue expose hidden gaps?)** —
  **UNANSWERED.** The backend was audited (WORK-0007) but not dogfooded;
  WORK-0032/0033 deferred to Phase 2. "Audited" ≠ "dogfooded." Inherited by Phase 2.

## What surprised us

- The work item that opened the phase as a generic tracker (WORK-0018) ended up
  measuring a genuine ratio flip: Python went from ~4,145 to 9,691 lines while
  process held ~3,358 — the process-over-product finding is substantively reversed.
- Two acceptance criteria were written against a misread of their own ADR: WORK-0014
  AC said "lead with the gate (ADR-011)" but ADR-011 mandates disqualifiers-first;
  WORK-0027's original recommendation (make the recursive model canonical) was the
  opposite of what the evidence supported. Both were caught and reconciled.
- The adversarial loop repeatedly earned its cost: panels caught real BLOCKING bugs
  the implementation missed (WORK-0048 binary-manifest crash, WORK-0007 read-cap,
  WORK-0002 incomplete mutating set, WORK-0014 dropped "Use Hedl if").

## What we'd do differently

- Honest accounting: surplus process was largely **justified/carried, not retired**.
  budget_manager and the recursive cluster were kept-deferred rather than cut, and
  the Lume bootstrap accreted 5 new ADR-class backlog items mid-phase. The
  discipline was preserved (gate green), but "retire surplus" (assumption 1) is only
  **partially validated**. Phase 2 must actually cut, not just defer.
- Watchlist verdicts should be recorded continuously, not scrambled at the boundary.
  Eight alternatives.md objectives had no verdict until /phase-complete forced them.
- AC writing: where an AC cites an ADR, verify the ADR actually says that before
  starting (two reconciliations this phase came from AC-vs-ADR misreads).

## Direction changes made during this phase

phases.json records none formally, but three boundary decisions are de-facto
direction calls (operator-approved at /phase-complete 2026-05-30):

- ADR-019 (recursive workstream) **superseded**; the four-category meaning is
  canonical (WORK-0027). The recursive cluster (WORK-0010/0011/ADR-031) is
  **deferred to Phase 2, not culled**.
- budget_manager **kept**, its culling-evidence window **extended to Phase 2**
  (despite the Phase-1 window closing with no rescue case).
- Watchlist (alternatives.md): self-improvement loop and multi-operator coordination
  are now explicit **culling-candidates** with a Phase-2 decision date.

## Impact on next phase

- Phase 2 **inherits LG2 and LG3 unanswered** — if the recursive model (WORK-0010)
  and github-issues dogfood (WORK-0032/0033) are activated, they answer them; if
  not, the learnings lapse with the deferral.
- Phase 2 carries a **standing anti-accretion watch**: the recursive cluster,
  budget_manager, and two culling-candidates all have Phase-2 decision dates. The
  phase should bias toward cutting deferred scaffolding over building it.
- Reclassified into Phase 2: WORK-0001, WORK-0010, WORK-0011, WORK-0015,
  WORK-0032, WORK-0033, WORK-0035 — each with a recorded `reclassify_reason`.

## Phase review verdict

Phase-1 existential cycle (.work/reviews/phase-1-complete-2026-05-30/, 5-agent
panel): **CONDITIONAL → resolved**. All conditional findings addressed before
transition — 7 items reclassified, watchlist verdicts recorded, repo-health re-run
persisted, WORK-0018 closed. The retro records LG2/LG3 as unanswered and
assumption 1 as partially validated, per the panel.
