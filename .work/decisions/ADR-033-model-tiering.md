# ADR-033-model-tiering — Heterogeneous model selection is gate-safe

## Status

Proposed — 2026-05-28 — Phase 1

**This is a hypothesis**: that Hedl's gate + adversarial review make cheaper
models safe for whole task classes. The reviewer half of the mapping is already
practice (see Context); the implementation/synthesis half is unvalidated.
Acceptance is **gated on evidence**, mirroring
[[ADR-028-external-reviews-cadence]]: the cheap prerequisite must land first —
record `model_used` in the gate-run insight event (and add it to `reflect.py`'s
allowed fields), then gather outcome data (ideally from a Lume bootstrap run).
Until that data exists this stays Proposed and is re-evaluated at each
[[ADR-013-existential-cycle-at-phase-boundaries]] boundary alongside the other
Proposed ADRs.

## Decision

Hedl's deterministic gate + adversarial review + scoped acceptance criteria make
per-task-class model selection a routine optimisation rather than a quality
gamble: the gate fails closed on the error classes it checks (schemas, lint,
types, tests) regardless of which model produced the work, and adversarial
review is the backstop for the semantic errors the gate cannot catch. The
framework therefore formalises a **deterministic default
model-per-task-class mapping** (configured in agent/persona frontmatter, with a
tier-level default; no LLM decides the model — per
[[ADR-003-deterministic-over-inference]]), empirically refined over time.
Recommended default mapping:

- Deterministic flows (gate, install, schemas): no model.
- Reviewers (named agents + library): Haiku-class default; Sonnet-class optional
  per agent frontmatter.
- Implementation (writing code): Sonnet-class default for `feat`; Haiku-class
  acceptable for `fix`/`docs`/`chore` where scope is tight.
- Synthesis (dispatcher, `/reflect` aggregation): Sonnet-class.
- Discovery (requirements, spike): Sonnet-class.

Per-agent/persona frontmatter overrides the default.

## Context

A recurring concern with LLM-driven workflows is cost. Hedl's discipline —
deterministic-over-inference for the substrate, gate enforcement at merge,
adversarial review per diff — shrinks the LLM *judgement* surface, which in turn
should let cheaper models handle more of the cycle safely. The hypothesis this
ADR puts up for evidence is that the framework becomes meaningfully usable with
non-frontier (including locally-hostable 7B-class) models for substantial
portions of the cycle; architectural reasoning and discovery still warrant
frontier models. This is a claim to be validated, not an established result.

This is not purely aspirational. An audit on 2026-05-28 found the reviewer tier
**already** heterogeneous: of seven named agents, four are Haiku-class
(determinism-auditor, historian, scope-auditor, simplicity-enforcer) and three
Sonnet-class (edge-case-hunter, review-dispatcher, security-auditor); the
reference library is 13 Haiku / 6 Sonnet. What is *missing* is (a) a model
contract for the implementation / synthesis / discovery flows (which currently
just inherit the main-loop model) and (b) insights tracking of which model ran
which task — the gate-run insight event does **not** record `model_used` today,
so the mapping cannot yet be validated empirically.

## Prior art

Cheaper-model viability under structure is well-studied:

- ReAct / chain-of-thought — structure improves smaller-model success rates.
- AutoGPT / BabyAGI — explored cheap-model autonomy with mixed, often poor
  results (open-ended, unstructured).
- LangChain tool-agents — explicit tools let smaller models succeed more than
  open-ended chat.

Hedl is **not inventing** model-tiering or cheap-model structuring. What is
uniquely Hedl: the deterministic gate catches its error classes (schemas, lint,
types, tests) **model-agnostically** — the same way no matter what produced the
diff — and adversarial review (itself model-dependent) is the semantic backstop.
So cheaper models are made *safer*, not *safe*: the residual risk is a
cheap-model semantic error that compiles, type-checks, and passes existing
tests, which the gate will not catch — that is managed by review and by
empirical refinement, not eliminated. The tier-graded operator model
([[ADR-018-multi-operator-scales-with-tier]]) is about operator coordination,
not models; this ADR *applies the same tier-graded configuration pattern* to
model selection (ADR-018 does not pre-authorise it). Why worth it: it converts
"use a cheap model and hope" into "use a cheap model, with the gate + review as
the floor and outcome data telling you where it is actually safe." What would
make Hedl delegate: nothing external pairs model-agnostic gate enforcement with
adversarial review as Hedl does; the mapping itself is mere config and is not a
moat.

## Options considered

- **Don't formalise — agents pick whatever model is convenient** — rejected:
  silent quality drift and no measurement.
- **Force a frontier model everywhere** — rejected: cost explosion negates the
  framework's value for many adopters and contradicts the audit reality that the
  reviewer tier already runs Haiku safely.
- **Default mapping + per-agent override + empirical refinement** (chosen) —
  formalises what reviewers already do, extends it to other flows, and gates the
  Accept decision on real outcome data.

## Consequences

- Agents/personas gain a documented default model class with frontmatter
  override (already partially present for reviewers; new for build/synthesis
  flows).
- The gate-run insight event (per [[ADR-005-self-improvement-human-gated]]'s
  insights mechanism) extends to record `model_used` per task event — **not
  instrumented today**, and `reflect.py`'s allowed-fields list would currently
  drop it. This is the prerequisite for validation and the cheapest next step (a
  small WORK item), independent of accepting this ADR.
- Once `model_used` is recorded, `/reflect` mining model+outcome data ("items
  closed with Haiku vs Sonnet; gate-failure rate by model") is a first concrete
  use case for [[ADR-026-iterate-consults-insights]]'s pattern surfacing — not
  something ADR-026 already commits to.
- [[ADR-022-pm-system-pluggability]] extends conceptually to
  *model-pluggability*: the adopter chooses model class per task; Hedl provides
  the contract and the gate/review floor.
- A strategic-positioning question follows (does Hedl become "the discipline
  substrate for agentic workflows on any model"?), but that is **out of scope
  for this ADR** — it is a v0.3/v1.0 product decision to be taken separately
  once evidence exists, not decided here. Recorded only as a pointer.
