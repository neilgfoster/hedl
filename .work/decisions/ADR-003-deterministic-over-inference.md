# ADR-003-deterministic-over-inference — Deterministic over inference

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Tier management, status, doctor, gate, versioning, and migrations are
deterministic Python scripts. The LLM is used only for reasoning work
(planning, review judgement, narrative authorship). Anything verifiable by a
function is verified by a function.

## Context

LLMs are non-deterministic and untrustworthy as the source of truth for
"is the build done?", "what tier am I on?", or "did I project the right
files?" The gate is the product's differentiator; non-determinism in the gate
would undo the differentiator.

## Options considered

- LLM-driven gate ("ask the model if you're done") — rejected: this *is* the
  status quo we are trying to displace.
- Hybrid (LLM proposes, script verifies) — rejected at the gate; accepted
  elsewhere (e.g. `/iterate`, where the LLM proposes work and the gate
  verifies).
- Script-only for state-defining operations (chosen).

## Consequences

- Every state-defining operation has a script under `skill/hedl/scripts/`,
  exits non-zero on failure, and is callable from CI.
- Tier changes via `install.py` are deliberate friction — not a defect. See
  [[ADR-002-tiered-adoption]].
- LLM output that contradicts a script wins-loses to the script. The agent
  surfaces the conflict; it does not override.
- See [[ADR-014-security-quality-friction-aware]] — security checks are also
  deterministic (script-mediated), not "ask the model if this is safe."
