# "doing-it-wrong" project rules — pattern from Jacob (theshadow27/mcp-cli)

**Date:** 2026-05-31
**Source:** Jacob, author of theshadow27/mcp-cli — the acknowledged prior-art
origin of Hedl's `am-i-done` gate (PRs #72/#74; ADR-011, ADR-033). Shared
directly with the operator as a comment.
**Status:** External evidence feeding ADR-037.

## The note (verbatim)

> The other pattern I've found works quite well is doing-it-wrong which is
> basically a collection of rules that are scanned as a step of am-i-done,
> encoded as normal code in whatever language the project is in. Sort of like
> lint, except not limited to someone elses idea of code quality, project
> specific, evolve over time. They can encode quite complex
> preferences/requirements/learnings since it's just code.
>
> The best kind of changes are "add a new doing-it-wrong rule to do X, and then
> fix all the violations" claude will go off and work for a while, fix it, and
> then the issue never repeats.
>
> In some other repos I've noticed that somewhere between 50-200 rules (again,
> some very detailed), it just stops making mistakes. Implementations work the
> first time, and the reviewer comments are basically all "if in the future
> someone" which can be thrown out mechanically.
>
> Project tooling >>> general tooling >>> prompt-only (imo)

## Why it matters for Hedl

- Same author as the gate primitive itself — carries prior-art weight; adoption
  must be attributed (honesty/prior-art is non-negotiable for this project).
- Corroborates [[ADR-035-auto-deterministic-detector]] (just merged, #78): the
  *only* acceptable detector form is a deterministic pattern-matcher, not an LLM
  classifier. "doing-it-wrong" is that — author-written rules, gate-enforced.
- Generalizes WORK-0028's single built-in detector (`check_doc_generated_facts`)
  into an open, project-extensible rule set.
- Compounds Hedl's adversarial-review loop: a recurring panel finding becomes a
  permanent deterministic rule, so the panel stops re-finding it — the
  insights -> rule -> gate pipeline. This is the differentiation answer to the
  external review's "panel is redundant with native AI review" (native re-finds;
  Hedl makes findings permanent).
- Harness-agnostic (rules are just code run by the gate in any CI / AI tool) and
  on-thesis with ADR-003 — fits DIRECTION-2 (gate as the product).

## Caution

The value is in the *rules + workflow*, which accrue by use (50-200 over time),
not in a big framework built up front. The MVP must stay minimal or it becomes
the framework-surface accretion DIRECTION-2 warns against.
