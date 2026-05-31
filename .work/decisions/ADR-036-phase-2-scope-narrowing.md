# ADR-036-phase-2-scope-narrowing — narrow Hedl to a portable completion gate

## Status

Proposed — 2026-05-31 — Phase 2 — recommends **DIRECTION-2**.

Drafted during an autonomous /iterate session while the operator was AFK, under
explicit delegated authority ("proceed as far as possible using your own
judgement"). Recorded as **Proposed**, not Accepted: the operator's ratification
is the PR merge (no auto-merge). The mandatory existential challenge ran as an
independent step — see
`.work/reviews/adversarial-review-2026-05-31-architecture-adr-036/` — and its
findings are folded into this revision; this ADR does not self-certify a passed
challenge. If the operator prefers DIRECTION-1, this ADR is superseded before
merge and Unit C does not run.

## Context

Phase 2's goal is "Adoption readiness & deferred-bet resolution" — make Hedl
genuinely adoptable, and force the deferred cull-or-build decisions rather than
carry scaffolding further (`.work/phases/phase-2.json`; the phase "biases toward
cutting deferred scaffolding over building it").

The third external adversarial review (`.work/reviews/external-2026-05-30-1/`,
8-agent) returned a strategic verdict Phase 2 must reckon with:

- Intrinsic-quality sub-average **6.6/10**; competitive-defensibility sub-average
  **3.5/10**; overall **5.8/10** (report.md §3).
- Framework-level decision: **REJECT for adoption today.** ADOPT only the **gate
  bundle + `--streams`, packaged as a focused tool**, once the adopter install is
  fixed (report.md §4).
- Five capabilities marked **REJECT** against Claude Code natives / focused tools:
  adversarial-review panel orchestration, SKILL.md NL routing table, budget tier
  accounting, bespoke ADR schema, the self-improvement loop. Two **ADOPT** (gate,
  `--streams`).
- Strong 2026 competitors `alternatives.md` did not reference: Spec Kit (~107k★),
  OpenSpec (~51k★), BMAD (~48k★), Taskmaster (~27k★).
- The completion-gate concept is attributed to bun (upstream) and
  theshadow27/mcp-cli (direct origin) — PRs #72/#74. Loss of headline novelty.

**One framing correction the review did not make.** The native-redundancy agent
(4/10) scored Hedl against **Claude Code natives only**. Hedl's harness-agnostic
intent is design-encoded across the ADR set — ADR-001 (Accepted), ADR-011
(Accepted), ADR-016 (Accepted), ADR-019 (Superseded, portability rationale
survives), ADR-021 (Proposed, deferred), ADR-033 (Proposed) — plus WORK-0047.
Under *what the design intends*, a feature being native to Claude Code is not a
strike, because it is absent in Copilot / OpenCode / Cursor / Aider / Devin, so
redundancy should be scored against the *intersection* of native features across
target harnesses. (Recorded forensically in Unit A,
`.work/insights/external-review-framing-gap-2026-05-30.md`, delivered in sibling
PR #76.)

**But the correction has a hard limit, stated honestly:** WORK-0047 is unbuilt and
Hedl is operationally Claude-Code-only today. So *today* the target-harness set is
effectively {Claude Code}, the intersection IS Claude Code, and the review's 4/10
is correct for what an adopter sees now. The framing correction describes the
*design intent and the roadmap*, not a shipped differentiator. This ADR therefore
separates the two explicitly (see Decision).

Two coherent strategic directions follow. This ADR recommends one.

### DIRECTION-1 — stay framework

Defend the whole-framework framing against Spec Kit / OpenSpec / BMAD /
Taskmaster / Agent OS / Kiro. Requires substantial feature-parity work and a
differentiation story stronger than Spec Kit's 107k★ trajectory. Goal-displacement
risk: high. Aligned backlog: WORK-0010/0011 (recursive workstream model — deferred
per ADR-019 supersession; this direction un-gates them), WORK-0050/0051/0052
(manifest, GitHub Projects, schema validation), WORK-0035 (external review kit).

### DIRECTION-2 — narrow to a portable, work-item-aware completion gate

Concentrate on the genuinely additive primitives the review confirmed: the
deterministic work-item-aware completion gate + `--streams`, kept portable across
harnesses. Drop the whole-framework framing. Aligned backlog: WORK-0047
(harness-agnostic adoption), WORK-0068 (fix the broken gate-tier install),
WORK-0073 (split am_i_done.py into a checks/ package).

## Decision

**Recommend DIRECTION-2.** Position Hedl as **"a portable, work-item-aware
completion gate"** — one thing, with the substrate and distribution that make that
one thing real. Drop the whole-framework pitch.

### The one thing, and what serves it

The focus is the **gate**: `am_i_done.py`, stdlib-only, no LLM, single exit code,
binding work-item + PR-template + threads + dependabot into one no-inference
verdict — which the review confirmed no focused tool currently does (report.md §4,
gate row). Everything below is in service of that one thing, not a parallel
feature surface:

1. **The gate, portable.** Keep it stdlib-only and LLM-agnostic so it runs in any
   repo and any CI. Today's differentiator, and it exists now.
2. **`--streams`** — pre-merge cross-stream conflict refusal. An extension of the
   gate (refuse-to-merge on overlap). Honest caveat: never exercised by a second
   operator; Phase 2 must exercise it.
3. **`.work/` — the substrate that makes the gate work-item-aware.** It is not a
   competing tracker; it is what the gate reads to be work-item-aware. Load-bearing
   for that feature (the gate-only tier runs without it for adopters who want the
   bare gate; native plan-mode / TodoWrite remain fine for ad-hoc tracking).
4. **Bootstrap-adopter — how an adopter gets the gate into their repo.** The
   distribution path, not a separate product.

**Deferred (not a pillar): forensic-discipline plumbing**
(`.work/insights/`, reflect.py, contribute.py). Whether this stays at all is
**Unit D's** decision (auto-deterministic-detector ADR + reflect/contribute
cull-or-double-down), taken **this phase** as part of this same strategic-compass
bundle — satisfying the Phase-2 DoD's "decision DATE this phase" constraint. It is
explicitly *not* a pillar of DIRECTION-2; DIRECTION-2 is coherent whether or not
it survives.

### Today's differentiator vs the roadmap differentiator (honest split)

- **Today (exists, defensible now):** a work-item-aware deterministic gate that
  binds checks no focused tool binds, runnable locally and in CI symmetrically.
  This is the ADOPT the review already granted (conditional on the install fix).
- **Roadmap (does not exist; the bet):** *harness-agnostic* portability — the same
  gate projected to `.copilot/`, `.opencode/`, `.cursor/`, generic
  `instructions.md`. This is what answers "what's unique about Hedl?" against the
  crowded field and the bun/mcp-cli attribution, **but only once it ships.**

Because the roadmap differentiator is a bet on unbuilt work, DIRECTION-2 does
**not** commit to building the whole multi-harness projection blind. It commits
to: (a) keep the gate portable by design (free, already true), and (b) **gate the
full WORK-0047 build on a feasibility spike** — one real non-Claude projection
that passes its own gate — before promoting the entire cross-harness build. This
de-risks the abstraction the simplicity/existential challenge flagged.

### Recommended dispositions for the five REJECT'd features (Unit C executes/records)

These are DIRECTION-2's *intent*; Unit C makes and records the final dispositions
in each work item's notes. Honest accounting of removed-vs-renamed follows.

- **Adversarial-review panel orchestration → thin to the deterministic floor.**
  Native Agent Teams + Dynamic Workflows + Outcomes cover the Claude Code case;
  keep only `review-dispatcher` + `am_i_done.py --check dispatch` + gate binding.
  Stop pitching the panel as a headline feature.
- **Budget tier accounting (`budget_manager.py`) → cull.** Pre-existing
  culling-candidate; thresholds 12/22/28 unsourced; Pro-plan reset silent
  (report.md item 8). Replace with a single session-invocation counter, or remove.
- **Bespoke ADR / decision-log schema → supersede; replacement deferred.** Drop
  the bespoke schema's weight; **MADR is the recommended candidate**, but the
  template change is a separate decision (its own ADR / Unit-C item), not here.
- **SKILL.md NL routing table → retain fallback (per ADR-016); drop the pitch.**
  ADR-016 preserves NL routing through SKILL.md as the cross-harness fallback —
  that is **retained**. What DIRECTION-2 drops is the routing *table as a marketed
  feature* and the duplication of native skill activation. No ADR-016 contradiction.
- **Self-improvement loop (reflect/contribute) → deferred to Unit D.** Zero PRs
  landed end-to-end. Unit D decides cull-or-double-down this phase; this ADR does
  not pre-empt it.

**Removed vs renamed (honest count).** v0.2.0 narrows the *positioning* and the
*marketed surface* more than the codebase: cleanly culled = budget_manager (1);
replaced = bespoke ADR schema (1, replacement TBD); thinned-but-retained = panel
floor, SKILL.md fallback (2); deferred = reflect/contribute (1, Unit D). Deeper
codebase culls are gated on the /phase-complete existential cycle. DIRECTION-2 is
honestly a *positioning narrowing first*, with code culls following the decisions
it sets up — not a claim that most code is deleted in v0.2.0.

### ADRs touching affected features — re-evaluation

- **ADR-009 (opinionated defaults, configurable)** — survives. DIRECTION-2 removes
  *features and pitch*, not configurability.
- **ADR-005 (self-improvement, human-gated)** — the *principle* survives; only if
  Unit D culls reflect/contribute is the *one implementation* removed. The ADR
  itself is not superseded unless the principle is abandoned.
- **ADR-012 (native substrate)** — WORK-0065 (high) owns the
  gate-binding-vs-hand-rolled-orchestration re-eval; DIRECTION-2 is consistent
  (keep the gate; lean native for orchestration).
- **ADR-016 (preserved decisions)** — unchanged: the SKILL.md NL-routing fallback
  is retained; only its feature-pitch is dropped.

## Options considered

- **DIRECTION-1 (stay framework)** — rejected. Not defensible today against the
  2026 field (report.md §4) and dilutes the harness-agnostic intent under
  feature-parity pressure. It would need a differentiator stronger than Spec Kit's
  107k★ trajectory, which does not exist.
- **Do nothing / carry both** — rejected. Phase 2's stated bias is to cut deferred
  scaffolding; the ambiguity is what every Unit-C band decision needs resolved.
- **DIRECTION-2 (narrow to the gate)** — recommended. The only direction that gives
  a coherent answer to "what is unique about Hedl?" given the bun/mcp-cli
  attribution and the crowded field — *contingent on the roadmap differentiator
  shipping*, which is why the cross-harness build is spike-gated, not assumed.

## Honest risks and caveats (from the existential/simplicity challenge)

These are recorded so the operator ratifies with eyes open, not buried:

1. **This is a maintainer decision in response to a competitive score, not adopter
   demand.** Hedl has no independent external adopters today; Lume and Wyrd are the
   maintainer's own repos (one operator, two repos — *not* validation that the
   market wants a narrowed Hedl). The decision's merit is internal coherence and
   surface reduction, not adopter pull.
2. **The differentiator that makes DIRECTION-2 defensible is unbuilt.** If WORK-0047
   never ships a real second-harness projection, DIRECTION-2 collapses to "we have
   a good work-item-aware gate" — which is still a real, ADOPT-rated thing, but not
   uniquely defensible. The spike gate is the hedge.
3. **Bootstrap-adopter is unproven beyond the maintainer.** No "proved" claim is
   made; promoting it to a marketed capability waits on an independent adopter
   completing a bootstrap without session assistance.
4. **This ADR ships no code.** The review's actual BLOCKING finding was a broken
   adopter install (WORK-0068). The first *execution* item after this decision is
   the install fix, which Unit C places at the top of the backlog — the strategy
   must not become a substitute for fixing the install.

## Consequences

**Immediate (if ratified):** Unit C (a separate PR) reconciles the Phase-2 backlog
around the gate focus — promote WORK-0047 to high (build spike-gated as above);
make WORK-0068 + the install fix the top of the backlog; mark WORK-0010/0011
deferred-with-trigger; record the five dispositions above in each item's notes;
reframe WORK-0050/0051/0052 as adjacent (not v0.2.0 critical path).

**Phase boundary:** the next `/phase-complete` treats this decision as the
load-bearing input; the existential cycle evaluates whether the Phase-2 outcome
matched DIRECTION-2.

**Downstream (separate PRs, not this docs-only ADR and not Unit C's state edit):**
retire the whole-framework narrative from README / `alternatives.md`; reframe the
ADR-011 disqualifiers for the focused-tool scope; decide the ADR-schema
replacement (MADR candidate).

**If the operator picks DIRECTION-1 instead:** this ADR is superseded before merge;
WORK-0047 stays normal; the framework-feature backlog keeps its bands; and the
operator-decision rationale must cite specific differentiators stronger than Spec
Kit's 107k★ trajectory and state how the 3/10 competitive score reaches ≥6 over
Phase 2.

## Related

- [[ADR-008-framework-vs-lume-test]] — cited in spirit (it is a per-change gate, not
  a direction-level test); the cherry-pickable gate + `--streams` satisfy it.
- [[ADR-009-opinionated-defaults-configurable]] — survives; configurability ≠ feature-count.
- [[ADR-011-disqualifiers-first-positioning]] — the focused-tool positioning extends it; disqualifiers to be reframed downstream.
- [[ADR-016-preserved-decisions]] — SKILL.md NL-routing fallback retained; only the pitch dropped.
- [[ADR-021-beyond-single-repo-orchestration]] — deferred; not load-bearing for v0.2.0.
- `.work/insights/external-review-framing-gap-2026-05-30.md` — the framing correction (Unit A, PR #76).
- `.work/reviews/external-2026-05-30-1/report.md` §3–§4 — the verdict this ADR responds to.
- `.work/reviews/adversarial-review-2026-05-31-architecture-adr-036/` — the existential + panel challenge.
