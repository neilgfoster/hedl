# Review personas

Seven core agents live as named files in `.claude/agents/`. Nineteen additional reviewer
prompts are available as composable reference prompts in
`skill/hedl/references/review-library.md`. The dispatcher reads the reference
library on demand to instantiate non-core reviewers.

`/adversarial-review` and `/repo-health` convene panels. The dispatcher picks the
minimal set for a given diff and the completion gate enforces a mandatory floor
(see [review-panels.md](review-panels.md)).

To add a new named agent, use the new-agent flow (see SKILL.md or
`skill/hedl/references/commands.md`).

---

## Dispatch model

Three selection mechanisms — all deliberate:

1. **Pattern-mandatory** (`dispatch-rules.json`): `security-auditor` and `historian`
   are required whenever specific file patterns match (Python, shell, workflows,
   agent files, ADRs, phase files). Deterministic — no dispatcher judgment involved.

2. **Always-required** (`dispatch-rules.json` `always_required`): `scope-auditor`
   runs on every review. Cheapest agent, highest signal.

3. **Dispatcher-selected** (`review-dispatcher.md`): `edge-case-hunter` and
   `simplicity-enforcer` are selected by the dispatcher based on diff content.
   Their triggers are context-dependent (logic branches, new abstractions) and
   cannot be expressed as file-pattern rules.

`review-dispatcher` is the orchestrator — it reads the diff and selects the panel.
It is not itself reviewed; it reviews.

Reference library agents (see table below) are instantiated on demand by the
dispatcher from `skill/hedl/references/review-library.md`. None duplicate the 7
core agents — they cover orthogonal risk categories.

---

## Core agents (named files in `.claude/agents/`)

| Agent | Model | Role |
|-------|-------|------|
| `review-dispatcher` | Sonnet | Reads a diff and selects the minimal sufficient panel |
| `scope-auditor` | Haiku | Finds work exceeding the current phase; always required |
| `security-auditor` | Sonnet | Injection, auth gaps, secrets, trust boundaries, blast radius |
| `historian` | Haiku | Decisions contradicting ADRs, prior requirements, or principles |
| `simplicity-enforcer` | Haiku | Over-engineering, premature abstraction, needless code |
| `edge-case-hunter` | Sonnet | Inputs, states, and sequences that break assumptions |
| `determinism-auditor` | Haiku | LLM inference replacing deterministic functions (Principle 1) |

---

## Reference library (`skill/hedl/references/review-library.md`)

Composable prompts instantiated on demand. The dispatcher reads this file and
passes the relevant prompt + scope context to a sub-agent call.

| Agent | Model | When dispatched |
|-------|-------|----------------|
| `agent-evaluator` | Haiku | New agent being proposed |
| `ambiguity-hunter` | Haiku | Requirements, specs, acceptance criteria being reviewed |
| `assumption-challenger` | Haiku | Phase or planning review |
| `chaos-engineer` | Sonnet | Infrastructure, config, or operational design |
| `claude-code-scout` | Haiku | Slash commands, hooks, or agents being built |
| `contradiction-finder` | Haiku | Requirements review alongside existing specs |
| `cost-analyst` | Haiku | Cloud resources or model usage in the diff |
| `devil-advocate` | Sonnet | Significant architectural decision |
| `drift-detector` | Haiku | Self-review when `.work/reviews/` has 5+ records |
| `evidence-checker` | Haiku | Phase completion review |
| `existential-challenger` | Sonnet | Self-review or phase transition |
| `future-engineer` | Haiku | Interfaces, schemas, or data formats external systems consume |
| `model-optimizer` | Haiku | Any agent definition or model routing config changed |
| `new-engineer` | Haiku | New public APIs, commands, or comprehensibility review |
| `operator` | Haiku | Infrastructure, runbooks, or operational config |
| `oss-scout` | Sonnet | New components or capabilities designed from scratch |
| `performance-skeptic` | Haiku | Python code with loops, API calls, or LLM invocations |
| `project-scout` | Sonnet | Scope expansion or phase boundary self-review |
| `quality-synthesizer` | Sonnet | Repo-health review (counterbalances adversarial agents) |
