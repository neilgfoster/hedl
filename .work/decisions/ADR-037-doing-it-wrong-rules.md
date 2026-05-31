# ADR-037-doing-it-wrong-rules — project-specific gate rules

## Status

Proposed — 2026-05-31 — Phase 2 — recommends **adopt the pattern via the existing
`[verify]` mechanism; DEFER any rules-framework with a trigger.**

The mandatory existential challenge (ADR-017) ran independently and failed the
first draft (which proposed building a rules-framework MVP) as premature
accretion; this revision folds in that panel + simplicity-enforcer + historian.
Records: `.work/reviews/adversarial-review-2026-05-31-architecture-adr-037/`.
Ratification is the PR merge (no auto-merge).

## Context

Jacob (author of theshadow27/mcp-cli — the acknowledged prior-art origin of
Hedl's `am-i-done` gate, PRs #72/#74) shared a pattern that pairs with the gate
(captured verbatim in
`.work/insights/doing-it-wrong-rules-jacob-mcp-cli-2026-05-31.md`):

> a collection of rules scanned as a step of am-i-done, encoded as normal code …
> like lint, except project-specific and evolving … The best kind of change is
> "add a new doing-it-wrong rule to do X, then fix all the violations" … somewhere
> between 50-200 rules it just stops making mistakes … Project tooling >>> general
> tooling >>> prompt-only.

The pattern is on-thesis: ADR-003 (deterministic over inference — rules are plain
code, no LLM); WORK-0028's `check_doc_generated_facts` is already one such rule;
and it gives DIRECTION-2 (ADR-036) a real defensibility point — native AI review
*re-finds* the same issues every run, whereas a gate-enforced rule makes a finding
**permanent**, so the loop compounds (`.work/insights/` notices → a rule encodes →
the gate enforces → the panel stops re-finding it).

**But the adversarial panel was decisive about the shape:** building a rules
*framework* now (a rule-directory, a discovery mechanism, a rule-contract, a
dedicated runner) is exactly the framework-surface accretion DIRECTION-2 forbids,
and it is premature — the value Jacob describes appears at 50-200 rules; Hedl has
~1, and no external adopters. Crucially, Hedl already has the mechanism to adopt
the pattern at **zero new surface**: the `[verify]` declarative check runs an
arbitrary project-owned command in the gate, on the WORK-0021-hardened path. So a
project rules script declared as one `[verify]` entry *is* doing-it-wrong, today,
with nothing new built.

## Decision

1. **Adopt the pattern via `[verify]`.** A single project-owned rules script
   (e.g. `project_rules.py`, repo's choice) declared as one `[verify]` entry runs
   as a gate step. No new gate machinery, no directory-discovery, no rule-contract
   protocol, no new check name. Attributed to Jacob / theshadow27/mcp-cli
   (prior-art is non-negotiable for this project).
2. **Document the workflow** briefly: "add a rule → fix all current violations →
   it never repeats," fed by recurring adversarial-review findings and
   `.work/insights/` learnings.
3. **DEFER any rules-framework** (directory discovery, rule-registration contract,
   dedicated runner) with an explicit trigger — revisit only when **(a)** the
   single rules script holds ~10+ rules and one-file maintenance friction is
   actually felt, **OR (b)** an external adopter who cannot fork `am_i_done.py`
   requests extensibility. Until a trigger fires: no framework.

### Relationship to existing decisions

- **`[verify]`** is the chosen host; doing-it-wrong adds a *convention* for using
  it (a project rules script), not a new mechanism.
- **WORK-0028** stays; it is the built-in precedent. A future rule can move into
  the project script, or stay built-in — not required here.
- **ADR-035** is unchanged. doing-it-wrong is the general lane for author-written
  deterministic rules (it satisfies the "not an LLM classifier" spirit), but it
  does **not** by itself meet ADR-035's specific reopen conditions (a deterministic
  ADR-003-anti-pattern detector attempted first, a sufficient corpus, a
  content-aware scrub). It is simply where such a detector *would live* if those
  conditions are ever met.
- **WORK-0073** (split `am_i_done.py` into a `checks/` package) is unaffected — the
  `[verify]` path already exists; no new check is added.

## Options considered

- **Build a rules-framework MVP now (the first draft)** — rejected by the panel:
  premature accretion against DIRECTION-2 and the Phase-2 cut-don't-build bias;
  a discovery/contract/runner for ~1 rule is over-engineering; Hedl has no adopter
  asking for extensibility.
- **Do nothing** — rejected: the pattern is genuinely valuable and adoptable at
  zero cost; recording the decision also prevents a future contributor building
  the framework without the trigger.
- **Adopt via `[verify]` + defer the framework with a trigger** — recommended.
  Captures the pattern now, builds no surface, and gates the framework on real
  demand.
- **Downgrade this ADR to a backlog item** — a legitimate alternative given the
  project convention "prefer a WORK item over a process ADR." Left to the operator
  (see Consequences); kept as an ADR here because it records a capability/restraint
  decision (how project rules enter the gate, and an explicit defer-with-trigger),
  not a mere process convention.

## Prior art

Mandatory per [[ADR-017-adrs-existentially-challenged]].

- **theshadow27/mcp-cli (Jacob).** The "doing-it-wrong" pattern, the "add a rule →
  fix all violations" workflow, and the 50-200-rules observation are his — same
  author as the gate primitive Hedl already credits. Hedl is **not** inventing
  this.
- **Linters / static analysis** (ruff, mypy, semgrep, ESLint custom rules) — the
  "rules as code" lane. doing-it-wrong differs by being project-owned, bespoke,
  evolving in-repo, and bound into the work-item-aware completion gate.
- **`pre-commit`** — hook-runner plumbing; not project-specific rule authoring nor
  gate/work-item binding.
- **WORK-0028 (`check_doc_generated_facts`)** + **Hedl's `[verify]` mechanism** —
  Hedl's own precedents; this reuses `[verify]` rather than adding a mechanism.

**What is uniquely Hedl:** project-owned deterministic rules bound into the
work-item-aware gate, fed by the `.work/insights/` → rule → gate loop and by
codified adversarial-review findings, so review findings become permanent instead
of re-found. **Why worth it:** converts recurring re-found mistakes into one-time
fixes (Jacob's evidence). **What would make Hedl delegate:** if a linter/rule
engine can express the rules and wire into the gate as cleanly, run those instead —
the runner is thin; the rules and the gate binding are the point. (This is why no
new runner is built here: `[verify]` already is the thin runner.)

## Consequences

- **If ratified:** a small follow-up work item documents the `[verify]`-rules
  convention and seeds 1-2 real Hedl rules (candidates: the parenthetical
  count-drift pattern beside WORK-0028; a "review-record has required sections"
  rule). No framework. The framework's defer-trigger is recorded here and surfaced
  at `/phase-complete`.
- **Operator choice:** if you prefer the project's "WORK item over process ADR"
  convention, this can be dropped to a backlog item carrying the same decision +
  the Jacob attribution (the insight file already holds the evidence).
- **Security/trust:** a `[verify]` rules script is the same trust surface as the
  project's tests / other `[verify]` commands (WORK-0021 allow-list, no shell
  metachars, timeout, cwd containment); rules stay stdlib-only / no-network by
  convention.
- **Anti-accretion watch:** if the rules script does not accrue beyond the seed,
  the loop is not earning its keep — revisit at `/phase-complete`. The framework
  stays unbuilt until its trigger.
- **Goal-displacement check (honest):** this is a maintainer decision prompted by
  the gate author's suggestion, not external adopter demand. It is justified only
  because it builds *no* surface and serves Hedl's own dogfood; the framework
  (which would need adopter justification) is deferred.

## Related

- `.work/insights/doing-it-wrong-rules-jacob-mcp-cli-2026-05-31.md` — the source note.
- [[ADR-003-deterministic-over-inference]] — the policy this enforces, as code.
- [[ADR-035-auto-deterministic-detector]] — the lane its detector would live in (not satisfied here).
- [[ADR-036-phase-2-scope-narrowing]] — DIRECTION-2; this stays zero-surface to honour it.
- [[ADR-011-disqualifiers-first-positioning]], [[ADR-033-model-tiering]] — the bun + mcp-cli gate prior-art Hedl credits.
- WORK-0028 (built-in precedent) and WORK-0073 (checks/ split) — both unaffected.
