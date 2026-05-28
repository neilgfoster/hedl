---
description: Disciplined engineering workflow — deterministic completion gate, adversarial review, phase discipline, work tracking. Activated by: "start a session", "what should I work on", "continue", "review this", "am I done", "finish this task", "raise a PR", "switch to next phase", "I'm stuck", "let's plan", "record a decision", "spike on", "change direction", "what's the status", "budget", "repo health", "scope check", "drain the queue", "switch to team tier", "what tier am I on", "check my hedl install", "change tier", "reflect on usage", "contribute improvement", "self-improve", "propose improvement".
---

# Hedl

A disciplined engineering workflow with a deterministic completion gate, adversarial review,
and phase-based work tracking. Three tiers — drop in just the gate, add lightweight specs,
or use GitHub Issues with parallel execution.

## Natural language routing

| What the user says | Behavior |
|--------------------|----------|
| "start", "start session", "good morning", "what are we working on" | Run the start-session flow |
| "what next", "next task", "continue", "keep going", "iterate" | Run the iterate flow |
| "review this", "check my work", "adversarial review", "review the diff" | Run /adversarial-review |
| "am I done", "is this done", "check completion", "run the gate" | Run `python3 .github/scripts/am_i_done.py` |
| "finish this", "mark complete", "close this task", "finish task" | Run the finish-task flow |
| "phase status", "where are we", "what's the progress", "phase health" | Show current phase DoD status |
| "phase complete", "done with phase", "close the phase", "next phase" | Run /phase-complete |
| "I'm stuck", "blocked", "can't proceed", "going in circles" | Run the stuck escalation flow |
| "change direction", "pivot", "change course", "new priority" | Run the change-direction flow |
| "let's plan", "requirements for", "what should we build" | Run the requirements flow |
| "spike on", "evaluate", "should we use", "tech evaluation" | Run the spike flow |
| "record decision", "ADR", "architecture decision", "new decision" | Run the new-decision flow |
| "budget", "how many tokens", "review budget", "budget status" | Run `python3 .github/scripts/budget_manager.py` |
| "repo health", "health check", "how is the project" | Run the repo-health flow |
| "raise PR", "create PR", "open PR", "submit PR" | Run the pr-raise flow |
| "PR ready", "check PR", "pre-PR", "is the PR ready" | Run `/pr-ready` (the pr-ready flow) |
| "drain queue", "process deferred reviews", "deferred reviews" | Run the drain-review-queue flow |
| "scope check", "is this in scope", "scope drift" | Run the scope-check flow |
| "phase status", "promote phase", "promote next phase" | Run the promote-phase flow |
| "new agent", "add reviewer", "create agent" | Run the new-agent flow |
| "switch to team tier", "upgrade to team", "enable parallel execution" | Run change-tier flow → `install.py --tier team` |
| "downgrade to lightweight", "drop the GitHub backend" | Run change-tier flow → `install.py --tier lightweight` |
| "go gate-only", "strip back to just the gate" | Run change-tier flow → `install.py --tier gate` |
| "what tier am I on", "show install state" | Run `python3 skill/hedl/scripts/install.py --status` |
| "check my hedl install", "is the install healthy" | Run `python3 skill/hedl/scripts/install.py --doctor` |
| "reflect on usage", "aggregate insights", "what's hedl doing", "self-improve" | Run the reflect flow (aggregate + synthesise proposals) |
| "contribute improvement", "propose improvement", "upstream this", "open self-improvement PR" | Run the contribute flow (scrub → classify → implement → gate → PR) |

For detailed behavior of any flow, load `skill/hedl/references/commands.md`.
For composable reviewer prompts (extended panel), load `skill/hedl/references/review-library.md`.
For tiered adoption guidance, load `skill/hedl/references/tiers.md`.

## Division of labour — mandatory rule

Every Hedl operation is classified before acting. No exceptions.

<!-- GENERATED: deterministic-ops START -->
> _Do not edit this section — generated from script `--schema` output._
> _To update: change the script's `CLI_SPEC` and run `python3 skill/hedl/scripts/gen_skill_metadata.py`._

**DETERMINISTIC — always invoke the script, never reason through it:**

| Operation | Invocation |
|-----------|------------|
| Run applicable checks (all, or one with --check) | `python3 .github/scripts/am_i_done.py` |
| Install or change the Hedl tier | `python3 skill/hedl/scripts/install.py --tier {gate\|lightweight\|team}` |
| Show installed tier and projection state | `python3 skill/hedl/scripts/install.py --status` |
| Verify all projections are healthy and report schema compatibility | `python3 skill/hedl/scripts/install.py --doctor` |
| Apply pending schema migrations to .work/context.json | `python3 skill/hedl/scripts/install.py --migrate` |
| Print Hedl version | `python3 skill/hedl/scripts/install.py --version` |
| Show full budget status including tier, usage, and queue depth | `python3 .github/scripts/budget_manager.py` |
| Print current budget tier name only | `python3 .github/scripts/budget_manager.py tier` |
| Record N agent invocations used | `python3 .github/scripts/budget_manager.py record N` |
| Reset session invocation counter, archive current session | `python3 .github/scripts/budget_manager.py reset` |
| Add agents to the deferral queue for a PR | `python3 .github/scripts/budget_manager.py defer --pr N --branch BRANCH --agents AGENTS` |
| Show all items in the deferral queue | `python3 .github/scripts/budget_manager.py queue` |
| Remove first N items from the deferral queue | `python3 .github/scripts/budget_manager.py drain [N]` |
| Record which agents ran on a PR for rotation tracking | `python3 .github/scripts/budget_manager.py record-panel --pr N --agents AGENTS` |
| List optional agents not run recently - candidates for next panel | `python3 .github/scripts/budget_manager.py suggest-rotation --optional OPTIONAL` |
| Compute bump and group items for a phase | `python3 .github/scripts/release.py --work-json WORK_JSON --phase N` |
| Aggregate events.jsonl into metrics.json | `python3 .github/scripts/reflect.py` |
| Verify diff only touches skill/hedl/ framework files | `python3 .github/scripts/contribute.py scrub` |
| Classify a change type against the Hedl semver contract | `python3 .github/scripts/contribute.py classify --change-type CHANGE_TYPE` |
<!-- GENERATED: deterministic-ops END -->

**REASONING — LLM only (no deterministic answer exists):**
Writing PRDs, decomposing epics, synthesising review findings, planning, change-direction decisions.

**Forbidden:** manually creating or removing symlinks, editing `.work/` state files directly,
modifying `.hedl-tier` by hand, or applying tier changes by any means other than `install.py`.
Manual changes are not reproducible, not validated, and break the installer's view of
installation state.

---

## Claude Code integration (optional)

When used with Claude Code, five slash commands are available as aliases for common flows:

- `/start-session` — orient at session start
- `/iterate [supervised]` — work loop (autonomous or supervised)
- `/adversarial-review [type]` — convene review panel
- `/pr-ready` — drive a branch to an operator-ready PR
- `/phase-complete` — validate phase DoD and transition

Without Claude Code, invoke the same behaviors by describing them in natural language
(see routing table above). The flows are defined in `skill/hedl/references/commands.md`
and work with any agent that reads this file.

## Completion gate

```bash
python3 .github/scripts/am_i_done.py            # local checks
python3 .github/scripts/am_i_done.py --pr 42    # + PR template, threads, CI
python3 .github/scripts/am_i_done.py --json     # machine-readable
```

The gate is stack-agnostic. Declare your verification commands in a `hedl.toml`
at the repo root and the gate runs them instead of the Python defaults:

```toml
[gate]
timeout = 120          # default per-command timeout (seconds)

[verify]
lint  = "golangci-lint run"
types = "tsc --noEmit"
test  = "go test ./..."
build = "npm run build"

[verify.e2e]           # long form: per-command overrides
cmd     = "playwright test"
timeout = 600
cwd     = "e2e"
```

With no `hedl.toml` the gate detects Python projects (via `pyproject.toml`,
`ruff.toml`, or `tests/`) and runs ruff/mypy/pytest automatically. The gate's
implementation is Python — that is a runtime dependency only, not a constraint
on the consumer's stack.

## Tiers

**Gate-only** — add `.github/scripts/am_i_done.py` to any repo. Two-minute setup.
**Lightweight** — add `.work/` state files and the 5 core slash commands.
**Team** — add GitHub Issues backend and worktree parallel execution (see `references/tiers.md`).
