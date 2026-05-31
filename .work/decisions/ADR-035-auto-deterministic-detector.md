# ADR-035-auto-deterministic-detector — reject the LLM-classifier form

## Status

Proposed — 2026-05-31 — Phase 2 — recommends **Reject** (detector, with a
non-committed reopen condition) + **prove-or-cull** (reflect/contribute). The
full decision is in the Decision section below.

Drafted during an autonomous /iterate session while the operator was AFK, under
explicit delegated authority. Recorded **Proposed**; ratification is the PR merge
(no auto-merge). The mandatory existential challenge plus a determinism-auditor and
scope-auditor ran as independent steps; their findings are folded into this
revision. Records:
`.work/reviews/adversarial-review-2026-05-31-architecture-adr-035/`.

## Context

The question (Unit D of the Phase-2 strategic-compass bundle): should Hedl ship an
**auto-deterministic-detector** that mines `.work/insights/` for ADR-003
("deterministic over inference") violations and proposes candidate replacement
scripts? The Unit D spec required a **real-data investigation before the Status is
set**; findings are reported honestly below.

### Finding 1 — real data first (decisive)

The full insights corpus is `.work/insights/events.jsonl`: **682 events spanning
4 distinct days (2026-05-28 → 2026-05-31), and every one is a `gate_run`
telemetry event** written by the completion gate (`am_i_done.py:1666-1691`). Zero
`reviewer_fired` events; no other event type.

`record_insights.py` (the PostToolUse hook) only emits `reviewer_fired`, and only
for `Agent` tool invocations when `hedl.toml [insights] enabled=true`
(`.claude/scripts/record_insights.py:58-78`); it returns `None` for everything
else. (It does **not** write `gate_run` — that is the gate's own telemetry.) The
class of evidence a deterministic-detector needs — operations where LLM inference
was used for something a pure function could compute — is recorded **nowhere**.

**Candidate ADR-003 violations mineable from the corpus today: 0**, against the
spec's threshold of 5. The detector has no input to operate on; building it now is
building a miner for data that is not collected.

### Finding 2 — the LLM-classifier form is itself anti-ADR-003

The original framing was: a *classifier* (LLM inference) decides whether an
operation could be deterministic, and emits a deterministic script, so "ADR-003 is
honored at the artefact level." The determinism-auditor correctly rejected this as
a **loophole**: ADR-003 says "anything verifiable by a function is verified by a
function" — it governs the whole toolchain, not just final outputs. An
inference-using *author* of deterministic *enforcers* is still inference in the
enforcement path; the artefact-level argument would license LLM inference anywhere
as long as the last step is deterministic.

Crucially, **violation-detection can itself be deterministic.** WORK-0028 already
catches an ADR-003 violation class (doc-vs-code count drift) with regex +
arithmetic and no LLM. So the premise that a *classifier* must be an LLM is false.
The only ADR-003-respecting detector is a **deterministic pattern-matcher** that
greps for known anti-patterns (hardcoded lists where an authoritative source
exists, dict iteration without explicit sorting, timestamp-dependence in
determinism-critical paths) — an extension of WORK-0028, not an LLM judge.

### Finding 3 — reflect/contribute: zero landed PRs

The external review flagged reflect/contribute as a culling-candidate with zero
PRs landed end-to-end; confirmed first-hand (`git log --all` shows none). The
detector would extend exactly this plumbing. Extending a culling-candidate before
deciding its fate is incoherent.

What exists: `reflect.py` (193 lines, stdlib, no LLM) aggregates `events.jsonl` →
`metrics.json`; `contribute.py` (153 lines, stdlib, no LLM) is the self-PR egress
path, with a **path-prefix-only** privacy scrub (`contribute.py:89`) and no content
inspection.

### Finding 4 — safety (if ever built)

A generated/added detector script ships executable code into Hedl: it must pass
`am_i_done.py` + adversarial-review like any code, AND the contribute scrub must
extend from path-prefix to **content scanning** first, or the egress loop becomes a
vector for accidental adopter-source leakage (a secret inside a `skill/hedl/` file
passes the current path-only scrub).

### Finding 5 — harness-agnostic alignment

A deterministic detector would read stdlib JSON and emit stdlib Python, harness-
independent — aligning with ADR-036 DIRECTION-2 **if** ratified (ADR-036 is
Proposed). Under DIRECTION-1 the adopter draw is unclear.

### Finding 6 — goal-displacement

Today this would be **Hedl iterating on Hedl** with no adopter demand. Per the Unit
D guardrail ("if Hedl-only, defer until at least one adopter requests it"), that
alone is grounds not to build it — and, combined with Findings 1–2, grounds to
reject the proposed form outright rather than keep it as a standing deferral.

## Decision

### Auto-deterministic-detector (LLM-classifier form) — REJECTED

Rejected, not merely deferred: it has no corpus (0 candidates), no adopter demand
(Finding 6), and its core mechanism (an LLM classifier authoring enforcers) is
itself contrary to ADR-003 (Finding 2). A standing "deferred" entry with
open-ended conditions would just keep a zombie alive against the Phase-2 cutting
bias.

**Non-committed reopen condition.** This is a precondition list, not future work
anyone is committing to. The detector may be reconsidered only if *all* hold:

1. A **deterministic pattern-matcher** (extending WORK-0028, no LLM) is attempted
   first and shown to catch a meaningful share of real ADR-003 anti-patterns. If a
   deterministic detector suffices, no LLM detector is ever needed.
2. The corpus actually contains the evidence — which first requires instrumenting
   `record_insights.py` to capture inference-substitutable operations as a distinct
   event type, then reaching a non-trivial count. (Today: not collected; this
   instrumentation is itself unjustified absent demand, so it is named here as a
   precondition, not scheduled.)
3. An adopter (not the maintainer) requests it.

### Self-improvement loop (reflect.py + contribute.py) — prove-or-cull this phase

The Phase-2 DoD requires a decision DATE this phase, so this is decided here, not
deferred. The whole loop has landed zero PRs since inception. Therefore: the loop
must land **≥1 real end-to-end self-improvement PR before the Phase-2
`/phase-complete`**, or be **culled** at that boundary. No artificial split is made
to keep half of it alive: reflect.py's aggregation does not measure any reopen
condition above (the landed-PR count is a `git log` query; the new event type is
uncollected; the scrub is unrelated), so it earns no keep-by-default. It either
proves the loop or goes with it.

## Options considered

- **Accept and build the LLM-classifier detector** — rejected. No corpus, no
  demand, and the classifier mechanism is anti-ADR-003 (Finding 2).
- **Deferred-with-trigger** — rejected. Open-ended conditions on a no-demand,
  no-data, wrong-mechanism feature is a zombie; Phase 2 biases toward cutting.
- **Build a deterministic pattern-matcher now (extend WORK-0028)** — not now, but
  it is the *only* acceptable future form, and is the first reopen precondition.
  Not built today because there is no demand and the WORK-0028 detector already
  covers the one violation class with observed value.
- **Reject the LLM form + prove-or-cull the loop** — recommended. Forces the
  Phase-2 decision without building speculative inference machinery, and refuses
  the ADR-003 loophole.

## Prior art

Mandatory per [[ADR-017-adrs-existentially-challenged]]. Overlapping prior art for
"detect places where inference replaced a deterministic function, and enforce
deterministically":

- **Internal:** WORK-0028's drift detector (`check_doc_generated_facts`) already
  catches one ADR-003 violation class (doc-vs-code count drift) with regex +
  arithmetic, no LLM. It is the model any future detector must follow.
- **Static analysis / linters:** ruff, mypy, semgrep, AST-based custom checks —
  the established deterministic way to flag code anti-patterns. A pattern-matcher
  for ADR-003 anti-patterns (hardcoded lists where an authoritative source exists,
  dict iteration without explicit sort, timestamp-dependence) is squarely in this
  lane.
- **LLM-as-judge:** the pattern this ADR's *rejected* option would have used. Well
  known (e.g. eval harnesses), but it is the opposite of ADR-003 when placed in an
  enforcement path.

**What is different / what is uniquely Hedl:** nothing — and that is the point.
Detection of these anti-patterns is a *tractable, deterministic* problem in the
existing linter / WORK-0028 lane (WORK-0028 ships one such check today; the others
are Hedl-domain rules a deterministic matcher would add there, not new science).
There is no Hedl-unique reason to introduce an LLM classifier; doing so would be
strictly worse (anti-ADR-003, token cost, non-reproducible).

**Why the difference is worth the cost:** it is not, today — hence REJECT. If
demand ever appears, the deterministic pattern-matcher reuses the existing
linter/WORK-0028 lane rather than inventing anything.

**What would make Hedl delegate:** if ruff/semgrep (or an off-the-shelf rule
engine) can express the ADR-003 anti-patterns directly, Hedl should add rules to
those tools rather than ship its own detector at all.

## Consequences

- **No follow-up work item is drafted** (the spec requires one only "if
  Accepted"). The reopen preconditions and the loop's prove-or-cull date are
  recorded here and surfaced at the next `/phase-complete` existential cycle.
- ADR-005 (self-improvement, human-gated): its *principle* is untouched; only the
  *egress implementation* is on a prove-or-cull trigger — consistent with ADR-036's
  ADR-005 re-evaluation.
- Two pre-existing code findings surfaced by the panel are **out of scope for this
  docs-only ADR** and routed accordingly: reflect.py's determinism test masks
  dict-ordering via `sort_keys` (a future hardening item, only if the loop
  survives); and `record_insights.py` hardcodes the reviewer roster — already
  tracked as **WORK-0069**.

## Related

- [[ADR-003-deterministic-over-inference]] — the policy; its scope covers the whole toolchain, not just outputs.
- [[ADR-005-self-improvement-human-gated]] — the loop on a prove-or-cull trigger.
- `.work/decisions/ADR-036-phase-2-scope-narrowing.md` — deferred reflect/contribute to this unit.
- WORK-0028 — the deterministic drift detector; the model any future detector must follow.
- WORK-0069 — record_insights roster drift (the determinism-auditor's collection-layer finding).
- `.work/insights/events.jsonl` — the 682-event, gate-only corpus the investigation mined.
- `.work/reviews/adversarial-review-2026-05-31-architecture-adr-035/` — the existential + determinism + scope challenge.
