# Alternatives

Living landscape map per ADR-012. Each Hedl capability maps to external
alternatives with one of four status values: uniquely-hedl, watchlisted,
culling-candidate, culled.

Watchlisted entries carry an improvement objective and a measurement
window. Re-evaluated at every phase boundary per ADR-013, and on meaningful
substrate releases per the proposed ADR-034 discipline (run manually until that
ADR lands).

Date: 2026-05-28 — Phase 1.

---

## Substrate impact assessments

Triggered re-evaluations when the underlying substrate ships a meaningful
release (proposed ADR-034). Each cites the release as trigger.

### Opus 4.8 — native multi-agent Workflows (2026-05-28)

Trigger: the Claude Code substrate shipped native multi-agent workflow
orchestration (dynamic fan-out / pipeline / parallel / judge-panel
"Workflows"). Impact:

- **Adversarial review panel** (watchlisted) — *sharpened*. The host now
  provides not just the subagent primitive but structured multi-agent
  orchestration — the judge-panel / parallel-review pattern Hedl hand-rolls. The
  panel's residual differentiator narrows to the deterministic dispatch floor +
  gate binding + the specific roster; the orchestration itself is now native.
- **Multi-operator coordination** (watchlisted) — *sharpened*. Native parallel
  workflows overlap the parallel-stream ambition; Hedl's defensible edge narrows
  to the gate-enforced `--streams` isolation (separately uniquely-hedl).
- **Proposed/deferred ADRs (021 orchestration, 031 parallel workstreams, 032 /
  WORK-0036 personas)** — *ratified*. With native orchestration available, the
  ADR-012 move is to delegate orchestration to the host (or CCPM / CrewAI) and
  wrap it with Hedl's gate + journey, not build Hedl-native equivalents. No new
  culls; the existing deferral/drop decisions hold and are reinforced.

Net: the release strengthens rather than threatens the
"discipline-substrate-on-top-of-someone-else's-orchestrator" positioning. No
status downgrades; two watchlist objectives sharpened.

---

## Deterministic completion gate (am_i_done.py)

**Status**: uniquely-hedl
**Hedl evidence**: `skill/hedl/scripts/am_i_done.py:1`; check list spans
`am_i_done.py:1-1300`; stack-agnostic dispatch via `hedl.toml` documented at
`skill/hedl/references/tiers.md:41-63`; same script runs locally and in CI per
`README.md:3-7`.
**Closest alternative(s)**:
- pre-commit (pre-commit.com)
- GitHub Actions matrix + required status checks
- task / just / Make declarative runners
- oven-sh/bun — `CLAUDE.md` (symlinked as `AGENTS.md`), the "Important
  Development Notes" completion instruction (the origin of the agent
  completion-gate idea: prose the agent is told to run before finishing, not a
  deterministic script)
**Prior art / origin**: the completion-gate *concept* is not Hedl's. It comes from
oven-sh/bun's `CLAUDE.md` (symlinked as `AGENTS.md`), whose "Important Development Notes"
instruct: "ONLY push up changes after running `bun bd test <file>` and ensuring your tests
pass", alongside a `claude/`-prefixed branch CI requirement — the direct inspiration for
`am_i_done`, via a contributor.
What remains Hedl-specific is the *deterministic* form: bun's gate is prose the agent is
trusted to follow (inference); Hedl packages the bundle as a single pass/fail: clean tree,
branch naming, PR-template validity, stale work-item IDs, unresolved review
threads, Dependabot alerts, *and* the consumer's lint/types/tests, with one
exit code, no LLM inference, same invocation in CI and on the desk. pre-commit
sits at the commit boundary, not the "am-I-done" boundary, and does not see
work-item state. CI status checks sit on the server, not at the desk. Hedl
binds them into one boundary that an agent can call and act on. The bundle —
not any single check — is the differentiator.

---

## Adversarial review panel (named agents + library prompts + dispatcher)

**Status**: watchlisted
**Hedl evidence**: 8 core agents in `.claude/agents/` and 18 reference prompts
in `skill/hedl/references/review-library.md`; dispatch model documented at
`skill/hedl/references/agents.md:17-39`; pattern-mandatory floor enforced via
`dispatch-rules.json` and verified by `am_i_done.py --check dispatch`.
**Closest alternative(s)**:
- Claude Code subagents (`.claude/agents/`) — native
- Claude Code native Workflows — multi-agent orchestration (judge panels,
  parallel fan-out), shipped 2026-05-28; see the substrate assessment above
- CCPM (github.com/automazeio/ccpm) — parallel agents per issue
**Why watchlisted**: Claude Code already supplies the subagent primitive Hedl
uses — and, as of the Opus 4.8 release, native multi-agent Workflow
orchestration (the judge-panel / parallel-review shape Hedl hand-rolls). What
Hedl adds is (a) a named opinionated roster covering orthogonal adversarial
axes, (b) a deterministic dispatch floor enforced by the gate, and (c) a
budget-aware deferral path. None of those primitives is unique on its own, and
the orchestration is now native — so the roster's signal must justify itself
even more sharply. The roster's value depends on whether each agent actually
catches things a generic "review this diff" subagent would miss. That is
not yet measured. CCPM ships its own multi-agent workflow and may
converge on similar coverage with less ceremony.
**Improvement objective**: Across the next phase, record for each named
agent how often it produces at least one BLOCKING or SIGNIFICANT finding
that the diff's other agents did not raise. Any core agent below a
documented threshold of non-overlapping signal becomes a culling-candidate
in its own right. Numeric threshold to be set by the operator at the start
of the measurement window — not invented here.
**Measurement window**: end of Phase 1.

---

## Phase-based work tracking (.work/phases, .work/work.json, /phase-complete)

**Status**: uniquely-hedl
**Hedl evidence**: phase state schema in `.work/phases/`; `/phase-complete`
behavior documented at `skill/hedl/references/commands.md` (the dedicated
`.claude/commands/phase-complete.md` file owns the flow); mandatory
existential cycle binding per ADR-013 section "Consequences".
**Closest alternative(s)**:
- GitHub Milestones
- Linear / Jira / Notion cycles
- CCPM epics/issues
**Why uniquely-hedl**: Milestones and PM-tool cycles track scope but do not
enforce *transition discipline* — entry into the next phase is a human button
press, not a gated artifact. Hedl's phase boundary is the only place
`existential-challenger` is mandatory (ADR-013) and the only place watchlist
windows expire (ADR-012). The differentiator is the binding of phase
completion to a structured cull/retain decision, not the phase concept itself.
If that binding is later moved into a pluggable PM backend (ADR-022), this
entry must be re-evaluated.

---

## Tiered adoption (gate-only / lightweight / team) with install.py projections

**Status**: uniquely-hedl
**Hedl evidence**: tier definitions in `skill/hedl/references/tiers.md:1-211`;
deterministic projection management via `skill/hedl/scripts/install.py`
(`--tier`, `--status`, `--doctor`, `--migrate`, `--dry-run`);
SKILL.md "Division of labour" section forbids manual symlink edits
(`skill/hedl/SKILL.md:82-86`).
**Closest alternative(s)**:
- pre-commit + a README listing optional add-ons
- CCPM's all-in-one install
- generic dotfile / template repos
**Why uniquely-hedl**: The tier concept itself is unremarkable. What is
unusual is that the tiers correspond to a *deterministic, reversible,
archive-on-downgrade installer* — the operator can move between tiers and
the framework's view of installed state remains consistent. No competitor
ships that primitive because no competitor sells "adopt only the part you
need" as a structured contract. This will become culling-candidate if Phase
1 adopters skip tiers entirely and install everything by hand anyway —
which would mean the tier abstraction is for us, not them.

---

## Slash commands + natural-language routing (SKILL.md)

**Status**: watchlisted
**Hedl evidence**: routing table at `skill/hedl/SKILL.md:12-42`; four core
commands in `.claude/commands/`; full behavior catalog in
`skill/hedl/references/commands.md`.
**Closest alternative(s)**:
- Claude Code native slash commands and skill activation
- Cursor / Continue / Cline command palettes
**Why watchlisted**: Claude Code already routes phrases to skills natively.
Hedl's routing table is a *projection* of skill activation that the host
already does. The genuine Hedl-specific content is *what each command does*
(the flows in `commands.md`), not the routing mechanism. The routing table
risks duplicating native behavior and going stale relative to it.
**Improvement objective**: Over the next phase, audit whether each entry in
the routing table provides behavior that the host's native activation
cannot reach. Rows that just restate native activation get removed; the
table shrinks to genuinely-Hedl flows.
**Measurement window**: end of Phase 1.

---

## Self-improvement loop (insights -> reflect -> contribute, Layer A/B/C)

**Status**: watchlisted
**Hedl evidence**: `/reflect` flow at `skill/hedl/references/commands.md:270-281`;
`/contribute` flow at `commands.md:285-311`; aggregation script
`.github/scripts/reflect.py`; scrub/classify in `.github/scripts/contribute.py`.
**Closest alternative(s)**:
- DORA / SPACE metrics tooling
- Plain `git log` + a human retrospective
- LLM-driven retros built ad-hoc in the host
**Why watchlisted**: The privacy-scoped local-metrics aggregation (no source,
no PII, only Hedl metadata — `commands.md:281`) is genuinely distinctive
and is bound to the framework's own structural rules (scrub rejects any
file outside `skill/hedl/`). But the *value* of the loop depends entirely on
whether the aggregated metrics produce proposals an operator actually
adopts. Until at least one `/contribute` PR lands from a `/reflect` cycle,
this is mechanism without evidence.
**Improvement objective**: Land at least one merged self-improvement PR
originating from a `/reflect`-generated proposal, end-to-end, including the
privacy scrub. Zero such PRs by the window's end demotes this to
culling-candidate.
**Measurement window**: end of Phase 1.

---

## ADR / decision log discipline

**Status**: watchlisted
**Hedl evidence**: `new-decision` flow at `skill/hedl/references/commands.md:168-190`;
existing ADRs in `.work/decisions/`; ADR template embedded in the flow text
rather than as a file in `skill/hedl/templates/`.
**Closest alternative(s)**:
- adr-tools (npryce/adr-tools)
- log4brains
- MADR template (adr.github.io)
**Why watchlisted**: All three alternatives do this. adr-tools provides
`adr new`, supersession links, and an index; log4brains provides a
browsable site; MADR provides a richer template. Hedl's ADR flow is a
six-line shell-free recipe that produces a minimal file. The only Hedl-
specific element is that ADR creation is wired into the broader workflow
(spike verdicts, direction changes). That binding is the differentiator,
not the ADR mechanics themselves.
**Improvement objective**: Either (a) adopt MADR-style sections as the
project template and credit upstream, removing the bespoke six-line schema,
or (b) demonstrate a specific Hedl ADR feature (e.g. cross-link to
`work.json`, automatic phase tagging) that adr-tools cannot replicate. Pick
one of these before the window closes; both options are improvements.
**Measurement window**: end of Phase 1.

---

## Multi-operator coordination (assignees/claims, GitHub Issues backend)

**Status**: watchlisted
**Hedl evidence**: Team tier section at `skill/hedl/references/tiers.md:116-167`;
backend configuration shape at `tiers.md:131-141`; gate-enforced per-stream
file scoping at `tiers.md:163-165`.
**Closest alternative(s)**:
- GitHub Issues + `gh-sub-issue` (k1LoW/gh-sub-issue)
- CCPM (github.com/automazeio/ccpm) — already issue-driven with parallel agents
- Linear / Jira workflows
**Why watchlisted**: CCPM is the direct competitor: issue-driven, subagent-
parallel, GitHub-native — and the Opus 4.8 native Workflow orchestration now
supplies the parallel-execution primitive itself. Hedl's pitch above both rests
on the *gate-enforced file scoping at merge* (`--streams`, separately
uniquely-hedl) and on tier-inheritance with the lower tiers — both of which
need to actually be exercised to be credible. Today the team tier is described,
not battle-tested; the orchestration layer is now best treated as delegated.
**Improvement objective**: Either run at least one multi-stream cycle on a
real repository and document an instance where the gate's `--streams` check
caught an overlap CCPM-style coordination would have missed, or fold the
team tier story to "Hedl plus CCPM" and stop competing on this axis.
**Measurement window**: end of Phase 1.

---

## Budget tier accounting (budget_manager.py)

**Status**: culling-candidate
**Hedl evidence**: tier names FULL / REDUCED / MINIMAL / DEFERRED at
`skill/hedl/scripts/budget_manager.py:20-23,187-189`; thresholds documented at
`skill/hedl/references/commands.md:103`; CLI surface in SKILL.md generated
table at `skill/hedl/SKILL.md:65-73`.
**Closest alternative(s)**:
- Anthropic API usage dashboards / plan-level quotas
- Just running fewer reviewers when you notice it's slow
**Why culling-candidate**: The thresholds (12/22/28) are unsourced — they
appear without provenance and are user-tunable, which means they encode no
shared knowledge. The deferral queue exists primarily to keep the named
agents below an invocation cap that Anthropic does not surface to the
framework, and that Pro-plan renewal at ~12:30pm London (`commands.md:104`)
silently resets anyway. This is local bookkeeping shadowing a system the
operator can already observe. The mechanism is real; the *value* is
unproven.
**Improvement objective** (carryover from a prior implicit window): Show one
concrete case where the deferral queue prevented a useful review from being
skipped — i.e. the queued review was drained, ran, and produced a finding
that mattered. Absent that case by the next phase boundary, retire to a
single-counter "agent invocations this session" display and delete the tier
machinery.
**Measurement window**: end of Phase 1.

---

## PR-template enforcement (check_pr_template.py)

**Status**: watchlisted
**Hedl evidence**: `.github/scripts/check_pr_template.py`; required sections
listed at `skill/hedl/references/standards.md` PR section; bound into the
gate via `am_i_done.py`.
**Closest alternative(s)**:
- conventional-commits / commitlint
- GitHub PR template + branch-protection required reviewers
- danger.js / danger-python
**Why watchlisted**: GitHub renders the template; danger enforces structure;
commitlint enforces commit format. The Hedl-specific value is that
`am_i_done.py` reads the live PR via `gh` and applies the same checks the
operator runs locally — one tool, one exit code. That is genuine. But the
*rules being checked* (Summary, Work item, Type, Changes, Validation) are
not Hedl-specific and could be a Danger ruleset or a GitHub Action with
equivalent enforcement.
**Improvement objective**: Either show that the local+CI symmetry has
caught a class of error a server-only check could not (e.g. WORK-ID staleness
detected against `.work/work.json` before push), or replace
`check_pr_template.py` with a published Danger / Action and just *configure*
it from `hedl.toml`.
**Measurement window**: end of Phase 1.

---

## Hooks-driven Claude Code integration (SessionStart, PostToolUse, Stop)

**Status**: watchlisted
**Hedl evidence**: hook wiring at `.claude/settings.json:9-37` (SessionStart
`.claude/startup.sh`, PostToolUse Edit/Write `.claude/scripts/posttooluse_lint.py`,
Stop `.claude/scripts/stop_reminder.py`).
**Closest alternative(s)**:
- Claude Code native hooks (the same primitive Hedl uses)
- pre-commit for the post-edit lint case
**Why watchlisted**: Hedl is consuming the host's hook primitive; the
question is whether the specific scripts wired in provide enough value to
justify the security expansion they incur (the `_comment_security` in the
settings file flags this explicitly at `.claude/settings.json:2`). The
post-edit lint and stop reminder are useful but not differentiated.
**Improvement objective**: For each of the three hooks, capture in the
session log at least one instance per phase where the hook output changed
operator behavior. Any hook that does not clear that bar at window's end
is removed from the default install and offered as opt-in.
**Measurement window**: end of Phase 1.

---

## Workstream templates (existential-review, problem-statement)

**Status**: watchlisted
**Hedl evidence**: ADR-020 at `.work/decisions/ADR-020-workstream-templates.md`
and the work item to ship them in `.work/work.json:168-180`.
**Closest alternative(s)**:
- A prose runbook in a wiki
- LangGraph / promptflow style explicit graphs (heavier; different problem)
- Notion or Obsidian templates for the same iteration pattern
**Why watchlisted**: The templates do not exist yet as files in
`skill/hedl/templates/workstreams/` (verified by directory listing — only
`epic-template.md`, `prd-template.md`, `task-template.md` are present). A
capability whose evidence is "we plan to ship this" cannot be uniquely
Hedl. The concept (iteration-pattern templates consumed by a workflow) is
plausibly differentiated but is not yet shipped.
**Improvement objective**: Land both templates as real files under
`skill/hedl/templates/workstreams/` and have the first existential-review
template *be the workstream that produced this document*. If the templates
have not shipped by the window's end, this entry moves to culling-candidate
and the ADR is reconsidered.
**Measurement window**: end of Phase 1.

---

## Multi-stream conflict detection (am_i_done.py --streams)

**Status**: uniquely-hedl
**Hedl evidence**: `check_streams` at
`skill/hedl/scripts/am_i_done.py:937-981`; CLI flag declared at `am_i_done.py:1147`;
dispatch at `am_i_done.py:1208-1209`; tier-3 narrative at
`skill/hedl/references/tiers.md:163-165`.
**Closest alternative(s)**:
- `git merge` conflict detection at merge time
- CCPM's coordination (assumes humans don't overlap; no gate-level enforcement)
- branch-protection rules requiring linear history
**Why uniquely-hedl**: The closest tools detect overlap *at merge*. Hedl's
gate refuses to certify a stream as "done" if its diff overlaps another
declared stream's diff — failure before push, not after. That is a
narrowly-defined, concretely-implemented, demonstrably-different check.
Note: differentiation is the *gate-level enforcement before merge*; this
entry must be re-evaluated if a competitor lands the same primitive.

---

## Summary table

| Capability | Status | Closest alternative |
|---|---|---|
| Deterministic completion gate (am_i_done.py) | uniquely-hedl | pre-commit / CI status checks |
| Adversarial review panel | watchlisted | Claude Code subagents; CCPM |
| Phase-based work tracking | uniquely-hedl | GitHub Milestones; Linear cycles |
| Tiered adoption + install.py projections | uniquely-hedl | pre-commit + ad-hoc add-ons |
| Slash commands + natural-language routing | watchlisted | Claude Code native skill activation |
| Self-improvement loop (reflect/contribute) | watchlisted | DORA/SPACE; manual retros |
| ADR / decision log discipline | watchlisted | adr-tools; log4brains; MADR |
| Multi-operator coordination | watchlisted | CCPM; gh-sub-issue |
| Budget tier accounting (budget_manager.py) | culling-candidate | API dashboards; do nothing |
| PR-template enforcement | watchlisted | Danger; commitlint; GH template |
| Hooks-driven Claude Code integration | watchlisted | Claude Code native hooks; pre-commit |
| Workstream templates | watchlisted | Wiki runbooks; Notion templates |
| Multi-stream conflict detection (--streams) | uniquely-hedl | git merge; branch protection |

---

## Disqualifier story

Three capabilities are genuinely Hedl-specific today and earn their place
on cited evidence: the bundled completion gate, the tiered install with a
reversible projection model, and the gate-enforced multi-stream overlap
check. The phase-tracking capability is uniquely-hedl in its current form
but is the most likely to lose that status if ADR-022's PM-pluggability
lands — that is acceptable and expected.

Eight capabilities are watchlisted with concrete, falsifiable improvement
objectives all measuring at the Phase 1 boundary: the review panel must
demonstrate non-overlapping signal per agent; the routing table must
shrink to genuinely-Hedl flows; the self-improvement loop must land at
least one PR end-to-end; ADR discipline must either adopt MADR or
demonstrate a feature adr-tools cannot replicate; multi-operator
coordination must show a real `--streams` save or fold to CCPM; PR-template
enforcement must justify local+CI symmetry or be replaced by Danger;
hooks must each show one behavior-changing instance per phase; workstream
templates must actually ship as files.

One capability — budget tier accounting — is honestly a culling-candidate
already. The thresholds are unsourced, the Pro-plan reset is silent, and
no recorded case shows the queue rescuing a useful review from being
skipped. If Phase 1 closes without that case, the tier machinery is cut
and a single-counter display takes its place.

This document is re-evaluated at every phase boundary per ADR-013.

## Phase-1 boundary verdicts (2026-05-30)

Per ADR-013, the watchlist objectives (measurement window: end of Phase 1) were
forced at the Phase-1 close. Verdicts:

- **Adversarial review panel** (non-overlapping signal per agent) — **RETAIN**:
  ~11 Phase-1 runs show distinct per-lens findings (edge-case-hunter caught crashes
  security/scope missed); re-confirm rigor in Phase 2.
- **ADR / decision-log discipline** (MADR, or a feature adr-tools can't replicate) —
  **RETAIN**: ADR-017 existential-challenge + supersede-via-historian (WORK-0027) is
  not an adr-tools feature.
- **PR-template enforcement** (justify local+CI symmetry or replace with Danger) —
  **RETAIN**: the same check runs locally and in CI; WORK-0041 refined it.
- **Routing table (SKILL.md)** (shrink to genuinely-Hedl flows) — **EXTEND to
  Phase 2**: not shrunk in Phase 1.
- **Hooks** (one behavior-changing instance per hook per phase) — **EXTEND to
  Phase 2**: not rigorously demonstrated per-hook.
- **Budget tier accounting** (show one rescued-deferral case) — **EXTEND to Phase 2**
  (operator decision): Phase-1 window closed with no case; kept rather than cut,
  window extended to the Phase-2 boundary.
- **Self-improvement loop** (land ≥1 /contribute PR end-to-end) —
  **CULLING-CANDIDATE**: zero such PRs by window end; per the stated rule, demoted;
  decide cull-or-prove in Phase 2.
- **Multi-operator coordination** (a real `--streams` save or fold to CCPM) —
  **CULLING-CANDIDATE**: no real multi-operator save (single operator); carried by
  WORK-0006/0059, decide in Phase 2.
- **Workstream templates** (ship both templates as real files) — **EXTEND to
  Phase 2**: not shipped (WORK-0011 deferred); prose `docs/templates/bootstrap-adopter.md`
  serves below the threshold.

Two items (self-improvement loop, multi-operator coordination) are now explicit
culling-candidates carried with a Phase-2 decision date; the rest retain or extend.
