# Hedl

A disciplined Claude Code workflow with a deterministic completion gate, adversarial
review, and phase-based work tracking. Distributed as a Skill — one directory to
install, tiered adoption from gate-only to full team workflow.

---

## How to work on this project

Five core slash commands:

```text
/start-session        # orient: phase, active item, last session
/iterate              # autonomous work loop
/iterate supervised   # pause before each item (use this by default)
/adversarial-review   # convene review panel on demand
/pr-ready             # drive a branch to an operator-ready PR
/phase-complete       # validate DoD, write retro, transition phase
```

Everything else activates via natural language — "finish this task", "raise PR",
"what's the status?", "run a spike on X", "I need to change direction".
The SKILL.md router (`skill/hedl/SKILL.md`) maps phrases to behaviors.
Full behavior catalog: `skill/hedl/references/commands.md`.

Completion gate: `.github/scripts/am_i_done.py` — run before declaring any task done.

---

## Core principles — never violate

1. **Deterministic over inference** — if a function can do it, don't use an LLM.
2. **Validation loops** — every agent output is validated before downstream work proceeds.
3. **Token efficiency** — compress context; escalate models only when needed.
4. **One work item at a time** — finish and validate before starting the next.
5. **Phase discipline** — nothing built outside the current phase scope.

---

## Coding behaviour

Applies to every operator on this project — human or agent.

### Think before coding

- State assumptions explicitly before starting. If multiple interpretations exist, surface them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- Stop and name what is confusing rather than guessing forward.

### Minimum code

- Implement exactly what the acceptance criteria require. Nothing more.
- No abstractions for single-use code. No configurability that wasn't asked for.
- No error handling for scenarios the calling code makes structurally impossible. Do add error handling at system boundaries.
- If you wrote 200 lines and it could be 50, rewrite it.

### Surgical changes

- Touch only files the work item requires. Match existing style even when you'd write it differently.
- Don't clean up adjacent code, comments, or formatting that isn't broken.
- If you notice unrelated dead code, mention it in the PR — don't delete it.
- Every changed line should trace to the active work item or a direct dependency of it.

### Verify before declaring done

- Success = acceptance criteria satisfied + `am_i_done.py` passes.
- Define the check before implementing, not after.
- Run the project's verification suite. If you can't run it, say so explicitly.

---

## Vocabulary

- **Blast radius** — the maximum damage a tool call could do if it goes wrong.
  Levels: `none` (read-only), `low` (writes within the workspace), `medium`
  (mutates `.work/` state or pushes commits), `high` (touches `main`, deploys,
  or external systems). High always requires human approval.
- **Validation loop** — the four-step pattern `act → validate → refine →
  escalate` applied to every agent output before downstream work proceeds.
- **MoSCoW** — Must / Should / Could / Won't prioritisation used in
  requirements docs.
- **Scaffolding** — code or process that exists temporarily to enable a phase
  and is expected to be replaced or retired at a phase boundary.

---

## Current state

- Phase: 1 — Discipline restoration (see `.work/phases/phase-1.json`)
- Active item: check `.work/work.json` → `meta.active_item`

---

## Security — non-negotiable

Every privileged tool call: identity → permission → blast radius → validation → execution.

Blast radius classification (see Vocabulary). High blast radius always requires
human approval.

Never write to `.work/phases/` directly — use `/phase-complete`.

---

## Context compaction — preserve these

When compacting, always preserve:

- The active work item ID and its acceptance criteria
- List of files modified in this session
- Any pending adversarial review findings not yet addressed
- Any operator instructions given in this session

---

## Reference docs

@skill/hedl/references/standards.md
