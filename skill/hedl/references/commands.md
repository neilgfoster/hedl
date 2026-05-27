# Command Reference Library

Detailed behavior for Hedl operations accessed on demand by the skill router.
The 4 core slash commands (`/start-session`, `/iterate`, `/adversarial-review`,
`/phase-complete`) have their own `.claude/commands/` files. Everything else is here.

---

## change-tier

Switch the installed tier. Blast radius: low (upgrade), medium (downgrade).

**Mandatory pattern — do not skip steps:**

1. **Run dry-run** — `python3 skill/hedl/scripts/install.py --tier <new_tier> --dry-run`
   Output shows exactly what will be added, removed, or archived. Read it.

2. **For downgrades: show delta and get explicit confirmation** — present the dry-run output to
   the operator. State the blast radius explicitly: "`.work/` will be archived (preserved, not
   deleted), the following projections will be removed: ...". Do not proceed without approval.

3. **For upgrades: confirm and apply** — upgrade dry-run output is low-risk; confirm once and apply.

4. **Apply** — `python3 skill/hedl/scripts/install.py --tier <new_tier>`
   The installer is idempotent. Re-running the same tier is safe.

5. **Verify** — `python3 skill/hedl/scripts/install.py --doctor`

**Never** change tiers by hand-editing symlinks, removing files directly, or modifying `.hedl-tier`.
The only supported path is `install.py`. See `skill/hedl/references/tiers.md` for tier capabilities.

---

## finish-task

Deterministic checklist. Do not skip steps. Do not use inference to assess pass/fail.

1. **Run tests** — run the test suite for the current work item. Report PASS or FAIL with specific output.
2. **Check acceptance criteria** — read `acceptance_criteria` from `.work/work.json` for the active item. For each criterion, assess deterministically (run a command, check a file, measure output). Report each as PASS or FAIL with evidence. Do NOT self-assess.
3. **Adversarial review** — run `/adversarial-review {task_type}`. Task type: requirements items → requirements; architecture/spike items → architecture; coding tasks → coding; infra tasks → infra. Do not mark complete if review returns FAIL. If CONDITIONAL: note findings, proceed, fix before phase-complete.
4. **If all PASS**: move item from `active` to `completed` in `.work/work.json`, set `status: complete`, `completed_date: today`. Update `.work/session.json`. Git commit: `[WORK-XXXX] title`. Show next item from backlog.
5. **If any FAIL**: list exactly what failed. Do not mark complete. Fix and re-run.
6. **Update session.json**: date, completed, decisions, next_item, blockers.

---

## change-direction

Use when a learning, blocker, or new insight means we should change course. This is not failure — it is the system working as designed.

**When to use**: a learning invalidates an assumption; something built isn't working as expected; a better approach discovered; operator wants to reprioritise; phase scope is wrong.

Steps:
1. **Capture the change** — answer: What triggered this? What are we changing? (scope, approach, phase sequence, future phase, core architecture) What is the new direction? What do we stop doing? What is the timeline impact?
2. **Record it** — add to `.work/phases/phases.json` `direction_changes` array: `{date, phase, trigger, change, stopped, approved_by: "the operator"}`. Write an ADR if it is an architecture change.
3. **Update affected files** — scope change: update `work.json` and `phase-{N}.json`; approach change: update work item; phase sequence change: update `phases.json` and affected phase files; architecture change: write ADR, update CLAUDE.md.
4. **Confirm** — output: `DIRECTION CHANGE RECORDED / Trigger / Changed / Stopped / Next action`. Then continue. Don't re-litigate.

---

## phase-status

Show the current state of the active phase. Run any time to reorient. Keep output under 400 tokens.

1. Read `.work/phases/phases.json` — identify current phase.
2. Read `.work/phases/phase-{N}.json`.
3. Read `.work/work.json` — find all items for this phase.

Output format:
```
PHASE {N}: {name} — {status}
GOAL: {goal}
DEFINITION OF DONE: [PASS/FAIL/UNKNOWN] {criterion} for each
ITEMS: ✅/🔄/⬜ WORK-XXXX: {title} ({status})
LEARNING GOALS: [ANSWERED/OPEN] {goal}
PHASE HEALTH: ON TRACK / AT RISK / BLOCKED
NEXT ACTION: {single sentence}
```

AT RISK if any item blocked >2 sessions. BLOCKED if active item stuck >3 attempts.

---

## promote-phase

Refine a draft phase definition before it becomes active. Apply real knowledge to replace assumptions.

1. Load `.work/phases/phase-{N}.json`, current phase retro, any direction_changes affecting this phase.
2. Review each section: definition_of_done (specific enough? criteria missing or irrelevant?), constraints (still right?), assumptions_to_validate (which answered? new ones?), learning_goals (right questions?).
3. Present a diff-style summary of proposed changes. **Wait for approval before writing.**
4. After approval: update `phase-{N}.json`, change status to "ready", log in `phases.json` transition_log.

---

## budget-status

Show current review panel budget tier, session usage, and deferral queue.

1. Run: `python3 .github/scripts/budget_manager.py` — shows tier, invocations used/cap, queue depth.
2. If queue has items: `python3 .github/scripts/budget_manager.py queue`
3. State: current tier and what it means for the next review, invocations remaining before tier downgrade, whether deferred reviews are waiting.

Tiers: FULL (<12 used), REDUCED (12-21, mandatory only), MINIMAL (22-27, scope-auditor only), DEFERRED (≥28, all queued).
Reset: `python3 .github/scripts/budget_manager.py reset` after Pro plan renewal (~12:30pm London).
Adjust thresholds: edit `.work/budget.json` → `config`.

---

## drain-review-queue

Process adversarial reviews deferred due to budget constraints. Run at the start of a fresh session.

1. `python3 .github/scripts/budget_manager.py queue` — if empty, stop.
2. Check tier: `python3 .github/scripts/budget_manager.py tier` — if DEFERRED/MINIMAL, ask whether to proceed or wait.
3. For each queued item (oldest first):
   a. State: "Running deferred review [entry.id]: PR #{pr} — {agents}"
   b. Get diff: `git fetch origin && git diff main...{branch} -- .`
   c. Run deferred agents via `/adversarial-review` (listed agents only, do not expand panel).
   d. Write findings to `.work/reviews/{entry.id}.json`.
   e. `python3 .github/scripts/budget_manager.py drain 1`
   f. `python3 .github/scripts/budget_manager.py record {N}`
   g. Re-check tier; if REDUCED or below, stop and report.
4. Report: items processed, items remaining, any BLOCKING findings (raise follow-up work item even if PR already merged).

---

## requirements

Structured requirements gathering. Token-efficient: ask once, listen, synthesise once.

1. Ask the operator a structured batch of questions (all at once — not drip-fed):
   ```
   A few questions about {capability}:
   1. Walk me through the ideal flow step by step.
   2. When something goes wrong mid-task, what should the user experience?
   3. How much should this decide autonomously vs. check with a human?
   4. What state must persist across sessions?
   5. What is the MOST IMPORTANT thing this must get right?
   ```
2. The operator answers.
3. Synthesise into `docs/spec/prd.md` using the sections from `skill/hedl/templates/prd-template.md`
   (Problem, Goals, Non-goals, Success criteria, Constraints, Open questions), formatted
   in MoSCoW. For a sub-feature, use `docs/spec/epics/epic-NNN.md` from `skill/hedl/templates/epic-template.md`.
4. End with: `DRAFT COMPLETE: docs/spec/prd.md / APPROVE — I'll mark complete / AMEND: {change} — I'll update`

Do not mark the work item complete until the operator explicitly approves.

---

## spike

Run a focused technology spike. Timeboxed. Produces a decision, not production code.

Rules: maximum 2 hours equivalent; output is conclusion + evidence, not working software; all spike code in `spikes/{name}/`; every spike ends with GO / NO-GO / MODIFY; verdict recorded as an ADR.

Steps:
1. **Frame the question** (no code) — "This spike answers: [question]." State GO vs NO-GO criteria. State what you will NOT investigate.
2. **Research first** — search for existing examples, known issues, others' conclusions. Document in `spikes/{name}/research.md`.
3. **Minimal implementation** — smallest thing that answers the question. No error handling beyond hypothesis testing. No abstractions.
4. **Test the hypothesis** — run it. Measure what matters.
5. **Write conclusion** — `spikes/{name}/conclusion.md` with: Question, Verdict (GO/NO-GO/MODIFY), Evidence, implications (If GO: what to adopt; If NO-GO: why and alternative; If MODIFY: what changes), Impact on plan.
6. **Record decision** — run new-decision flow to create ADR. Update affected phase files or assumptions.

Timebox: if going deeper than needed to answer the question — STOP. Write what you know. A partial answer with a clear "unknown" is better than scope creep.

---

## new-decision

Record an architecture decision. Run whenever a non-obvious choice is made.

1. Ask: "What is the decision in one sentence?"
2. Ask: "Why this over the alternatives?"
3. Ask: "What are the consequences?"

Create `.work/decisions/ADR-{NNN}-{slug}.md`:
```markdown
# ADR-{NNN} — {Title}
Date: {today} | Status: Accepted | Phase: {current phase}
## Decision
{one sentence}
## Context
{why this decision was needed}
## Options considered
- {option 1}: {why rejected or chosen}
## Consequences
{what this means going forward}
```

Update `.work/context.json` decisions array. Confirm: "Decision recorded as ADR-{NNN}."

---

## new-agent

Evaluate and optionally create a new adversarial review agent.

1. **State the hypothesis** — answer: What specific class of issue are we missing (concrete example)? What triggered this? If you cannot give a concrete example, stop.
2. **Run the evaluator** — instantiate the `agent-evaluator` from `skill/hedl/references/review-library.md`. Pass: proposed description + trigger. Evaluator returns APPROVE, EXTEND, or REJECT.
3. **Act on verdict**:
   - REJECT: do not create. Record reason so same proposal isn't re-evaluated without new evidence.
   - EXTEND: modify the identified existing agent file. PR as normal.
   - APPROVE: proceed.
4. **Write the agent** (APPROVE only) — create `.claude/agents/{name}.md`: frontmatter (`name`, `description`, `tools`, `model: haiku` unless reasoning-heavy), hostile system prompt with concrete checklist, standard finding JSON schema.
5. **Update indexes** — add to agent index in `skill/hedl/references/agents.md`; add dispatch rule to `review-dispatcher.md`; if deterministic-eligible, add to `dispatch-rules.json`; run `python3 .github/scripts/am_i_done.py --check config`.

---

## repo-health

Whole-repo independent health evaluation (distinct from `/adversarial-review` which reviews diffs).

**Run from a fresh session.** Session context skews findings.

Steps:
1. **Choose depth** — Standard (security-auditor, new-engineer, quality-synthesizer) or Full (all 6 core agents + composable reviewers from review-library.md). Use Standard for routine checks; Full for post-major-change or phase transitions.
2. **Clone repo** — `CLONE_DIR=$(mktemp -d -p /tmp); trap 'rm -rf "$CLONE_DIR"' EXIT; git -c core.hooksPath=/dev/null clone --no-local --filter=blob:none "$REPO_ROOT" "$CLONE_DIR/$REPO_NAME"`. Read from clone only.
3. **Convene panel** — instantiate agents from `.claude/agents/` (core 6) and from `review-library.md` (for Full depth).
4. **Run panel in parallel** — each agent reads `TARGET` independently.
5. **Validate + synthesise** — validate JSON schema per agent, then synthesise.
6. **Write output** — `RUN_DIR=".work/reviews/repo-health-{DATE}"`. Write one file per agent, then `report.md`.

---

## pr-raise

Raise a PR, run adversarial review, address all findings, hand to operator for sign-off.

1. Pre-flight: confirm not on main, active work item `status: complete`, run checks (typecheck/tests/lint), `git status` clean.
2. Draft PR: title `WORK-XXXX: <description>`, body filling all sections of `.github/PULL_REQUEST_TEMPLATE.md`.
3. Create: `gh pr create`. Record PR number.
4. Dispatch panel: run `review-dispatcher` agent with PR title + changed file list. Validate: `python3 .github/scripts/am_i_done.py --check dispatch --panel <agents>`. Add missing mandatory agents.
5. Run panel in parallel. Collect findings. One rebuttal round.
6. Post findings as PR comments (one per BLOCKING/SIGNIFICANT finding). Post summary comment.
7. Address each: valid → fix, commit, push, reply with SHA; invalid → specific rebuttal citing evidence.
8. Post final comment: "All findings addressed."
9. Tell operator PR is ready. Wait. When signalled: check new threads, handle like BLOCKING findings. Confirm ready to merge when all resolved. Do not merge.

---

## pr-ready

Controller loop: branch → operator-ready PR. Runs gate → adversarial review → fix cycles.

Stops only when: `am_i_done.py --pr N` exits 0 AND `am_i_done.py --pr N --check ci` exits 0 AND zero BLOCKING findings from adversarial review. Maximum 3 full review cycles, then `/stuck`.

Phases: 1. Local gate → 2. Create/update PR + PR gate → 3. Dependabot check → 4. CI gate → 5. Adversarial review → 6. Fix cycle (if FAIL) → 7. Operator handoff.

For each BLOCKING finding: post PR comment, fix or rebut, resolve thread. After all findings addressed: re-run local gate + CI gate before returning to review.

---

## scope-check

Review everything created or modified this session against the active phase scope.

Scope source: union of `phase-{N}.json` constraints + `definition_of_done`, active work item `acceptance_criteria`, ADRs with explicit carve-outs.

Steps:
1. Load active phase from `.work/context.json`.
2. List changed files: `git diff --name-only` against branch base.
3. For each file: map to work item (WORK-XXXX) if any; assess IN SCOPE or OUT OF SCOPE against phase constraints and acceptance criteria.
4. For each OUT OF SCOPE: recommend DELETE, DEFER (target phase + work item to create), or RECORD-AS-ADR.
5. Output: **SCOPE: CLEAN** or **SCOPE: DRIFT**.

If SCOPE: DRIFT — do not commit until resolved or recorded.

---

## reflect

Aggregate local usage insights and synthesise improvement proposals. Requires `[insights] enabled = true` in `hedl.toml`.

1. **Aggregate** — `python3 .github/scripts/reflect.py --work-dir .work`
   Reads `.work/insights/events.jsonl`; writes `.work/insights/metrics.json`. Pure arithmetic — no LLM. Exit 2 if no events exist.

2. **Synthesise** — pass `metrics.json` to the existing agents (`existential-challenger`, `drift-detector`, `agent-evaluator`) with the prompt: "Here are Hedl usage metrics. Identify the highest-leverage improvement and write a structured proposal." Each agent writes a JSON proposal to `.work/insights/proposals/`.

3. **Review proposals** — read `.work/insights/proposals/`; select one to act on. Proposals are input to `/contribute`, not automatic actions.

**Privacy**: only Hedl metadata is recorded (timestamps, check names, pass/fail counts, reviewer names, command names). No source code, file paths, commit messages, or PII. See `docs/self-improvement.md`.

---

## contribute

Turn a Layer-B proposal into an upstream PR using Hedl's own workflow. Structural rule: opens a PR, never merges.

**Pre-flight** — a proposal from `/reflect` must exist in `.work/insights/proposals/`. Operator selects one.

1. **Privacy scrub** — before any push:
   ```bash
   git diff main...HEAD --name-only | xargs python3 .github/scripts/contribute.py scrub --diff-files
   ```
   Any file outside `skill/hedl/` is a hard rejection. Do not proceed if scrub fails.

2. **Semver classify** — determine the implied Hedl version bump:
   ```bash
   python3 .github/scripts/contribute.py classify --change-type <signal>
   ```
   See `docs/versioning.md` for the full classification table. Valid signals: `new-reviewer`, `new-tier`, `new-check`, `new-command`, `new-optional-config` (minor); `hedl-toml-schema-break`, `work-state-schema-break`, `gate-exit-code-change`, `tier-layout-break`, `command-removed`, `agent-removed` (major); anything else (patch).

3. **Implement on branch** — follow the normal spec → implement → gate loop applied to the selected proposal.

4. **Gate** — run `am_i_done.py`; all checks must pass.

5. **Confirm remote push** — always prompt the operator before any `gh pr create`. Show: branch, scrub result, implied bump, PR title draft. Do not push without explicit approval.

6. **Open PR** — `gh pr create` against the upstream Hedl repo's `main` branch.

7. **Do not merge** — the `/contribute` flow ends after PR creation. Merging requires a human reviewer. Branch protection on `main` enforces this. See `docs/self-improvement.md` for the `gh api` setup command.

---

## stuck

Structured escalation when going in circles or blocked.

1. **Diagnose** — answer: What exactly am I trying to do? What have I tried? What specifically is not working? How many attempts?
2. **Check the obvious** — is this in scope (run scope-check)? Is there a clarifying acceptance criterion? Is there an ADR covering this? Does an OSS tool already solve this?
3. **Escalation path**:
   - After 2 failed attempts: try a different approach entirely. State the alternative before starting.
   - After 3: write a minimal reproduction. Check if the acceptance criterion is actually testable.
   - After 4: surface as blocker in `.work/session.json`. Move to next work item. Flag for operator in next session.
4. **Never do when stuck**: expand scope to work around the problem, delete tests to make them pass, mark an item complete with known failures, spend >4 attempts on the same approach.
