# ADR-014-security-quality-friction-aware — Security and quality, friction-aware

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

Trust is built through demonstrable hygiene, not theatre.

- `security-auditor` runs **only** on code, config, and security-sensitive
  paths per current `dispatch-rules.json` — not blanket.
- Risk-based threat modelling at phase boundaries that introduce new attack
  surface; the standing discipline (gate + dispatched `security-auditor`)
  carries it otherwise.
- Public `SECURITY.md` mirrors what the gate actually enforces (SHA-pinned
  actions, hash-pinned deps, CodeQL, stdlib-only consumer scripts,
  `--streams` file isolation, privacy-scrubbed `/contribute`).
- README carries a one-line trust statement that points at `SECURITY.md`.

Lume (as an IDP) gets a stricter bar than Hedl (as a framework); they share
the floor.

## Context

Blanket security review is a noise factory — reviewers tune it out, real
findings get lost, and adoption friction grows without improving outcomes.
Targeted review on the surfaces that actually matter is both cheaper and
more honest about what was checked.

## Options considered

- All-paths `security-auditor` — rejected: noise, reviewer fatigue,
  diminishing returns.
- No `security-auditor` (rely on gate only) — rejected: gate verifies
  hygiene, not semantic security.
- Dispatched, risk-based (chosen).

## Consequences

- `dispatch-rules.json` is the authoritative routing config; changes there
  go through ADR-006-style historian review.
- See [[ADR-010-honesty-over-marketing]] — the trust statement on README
  must be runnable-verifiable.
- Adding new attack surface at a phase boundary triggers an explicit
  threat-modelling task; absence of new surface skips it.
