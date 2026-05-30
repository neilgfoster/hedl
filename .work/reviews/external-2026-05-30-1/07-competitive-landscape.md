# Competitive landscape

External adversarial review. Dimension: COMPETITIVE LANDSCAPE.
Target: Hedl @ `796639c6c926ba2535bac3a5474f5d2feb62cb28`.
All star/activity figures fetched via GitHub API or web search on 2026-05-30
unless noted. "Repo claims" = assertions in `docs/alternatives.md`; "verified"
= independently checked.

## Summary

Hedl positions itself as a "discipline substrate" that wraps someone else's
orchestrator (Claude Code) with a deterministic completion gate, an adversarial
review roster, phase/ADR/work-item discipline, and a reversible tiered install.
The honest read after independent verification: **Hedl competes in one of the
most crowded, fastest-moving open-source categories of 2026** (spec-driven /
AI-coding-workflow frameworks), where the leaders have 8k–107k stars and ship
weekly, while Hedl is an unreleased single-operator project whose own
`alternatives.md` already concedes 8 of 13 capabilities are "watchlisted" and 1
is a "culling-candidate."

The defensible core is narrow but real: (1) the **deterministic, tracker-aware,
LLM-agnostic completion gate** binding lint/types/tests + clean-tree + PR-template
+ stale-work-item + review-thread + Dependabot into one exit code that runs
identically local and CI; and (2) the **`--streams` gate-level overlap refusal
before push**. Almost everything else has a stronger, better-resourced focused
substitute. The framework-level pitch is the weakest layer: against spec-kit
(107k), BMAD (48k), OpenSpec (52k), Taskmaster (27k), and CCPM (8k), Hedl offers
no scale, no community, and no released distribution.

Crucially, the gate's named prior art (theshadow27/mcp-cli) has **2 stars** — so
while the repo is commendably honest about deriving the gate, the origin is not a
competitive threat; it's an obscure project. The real threat is convergence:
native Claude Code Agent Teams + Dynamic Workflows (confirmed shipping 2026) now
supply orchestration, and CCPM/spec-kit supply the workflow scaffolding, leaving
Hedl's moat as "the gate + the discipline bindings."

## A. Direct framework competitors

| Tool | URL | Stars / activity (2026-05-30) | What it does | vs Hedl | Verdict |
|---|---|---|---|---|---|
| GitHub Spec Kit | https://github.com/github/spec-kit | **107,179** ★, 9,486 forks, pushed 2026-05-30 (today), 431 open issues | Spec→Plan→Tasks→Implement SDD toolkit; 30+ agent integrations incl. Claude Code; GitHub-backed | Vastly larger, official, agent-agnostic, no lock-in. Covers the "structured workflow" pitch with massive reach. Has no deterministic gate or `--streams`. | REJECT-framework (use spec-kit for the workflow); Hedl can only compete as a gate layer *on top* |
| OpenSpec | https://github.com/Fission-AI/OpenSpec | **51,806** ★, pushed 2026-05-28 | Lightweight SDD: proposal→apply→archive state machine; brownfield delta markers (ADDED/MODIFIED/REMOVED); 20+ tools | Directly overlaps phase/work-item tracking and ADR discipline with a cleaner state machine and far more adoption | REJECT-framework for workflow scaffolding |
| BMAD-METHOD | https://github.com/bmad-code-org/BMAD-METHOD | **48,314** ★, 5,628 forks, pushed 2026-05-30 (today), 51 open issues | "Agile AI driven dev"; agent personas/roster, skills architecture, dev-loop automation, 42 platforms | Overlaps the *adversarial roster* and persona ideas at huge scale, with sub-agent teams and dev-loop automation | REJECT-framework for the roster/persona layer |
| Taskmaster (claude-task-master) | https://github.com/eyaltoledano/claude-task-master | **27,293** ★, 2,547 forks, pushed 2026-04-28 | Drop-in AI task management; PRD→tasks; multi-model (main/research/fallback); MCP | Overlaps work-tracking/phase decomposition; broad IDE support; far more mature | REJECT-framework for work decomposition |
| CCPM | https://github.com/automazeio/ccpm | **8,158** ★, 831 forks, pushed 2026-03-18, 4 open issues | GitHub-Issues + git-worktree parallel agent execution; deterministic script ops (status/standup/search) for zero-token state | The repo's named direct competitor. Issue-driven, worktree-parallel, GitHub-native, with its own deterministic no-LLM scripts — overlaps the multi-operator + work-tracking + "deterministic ops" pitch closely. Activity slowed (last push Mar 2026). | REJECT-framework for multi-operator/work-tracking; ADOPT-Hedl only for the gate binding |
| Agent OS | https://github.com/buildermethods/agent-os | **4,706** ★, pushed 2026-05-05 | Injects codebase standards + spec-writing for SDD | Overlaps "standards.md" + spec discipline; smaller but active | Comparable scale; REJECT-framework for standards injection |
| Amazon Kiro | https://kiro.dev/ | Commercial (AWS); succeeds Amazon Q Dev (new signups May 2026); not OSS-star-comparable | Agentic IDE; spec as source-of-truth (requirements/design/tasks .md); EARS notation; agent hooks on save/PR/repo events | Kiro's agent hooks + spec files overlap Hedl's hooks + phase artifacts, but Kiro is a full IDE with AWS backing; different distribution model | Out-of-scope as OSS but a strong category signal — the whole industry shipped this pattern |
| Claude Code Agent Teams + Dynamic Workflows (native) | https://code.claude.com/docs/en/agent-teams | First-party (Anthropic), shipping 2026 (experimental, default-off) | Team-lead session coordinates subagents; Dynamic Workflows fan-out tens–hundreds of parallel subagents, refute/converge ("judge panel" shape) | This is the substrate Hedl rides on AND its biggest convergence threat: native orchestration now does the fan-out/refute pattern Hedl hand-rolls | The host eating Hedl's orchestration layer; Hedl must retreat to gate + roster-as-content |

The three strongest direct competitors by scale/momentum: **spec-kit (107k)**,
**OpenSpec (52k)**, **BMAD-METHOD (48k)**. CCPM (8k) is the closest *architectural*
peer (deterministic no-LLM ops + parallel agents) and the one the repo correctly
identifies as its direct rival, but it is now the smallest and slowest-moving of
the named set.

## B. Focused substitutes per capability

| Hedl capability | Best focused tool | URL | Stars (2026-05-30) | ADOPT / REJECT + how |
|---|---|---|---|---|
| Deterministic completion gate (`am_i_done.py`, 1703 LoC) | pre-commit (for hook symmetry) + GitHub required status checks | https://github.com/pre-commit/pre-commit | 15,295 ★, pushed today | **ADOPT-Hedl.** No focused tool bundles clean-tree + PR-template validity + stale-WORK-ID-vs-`work.json` + unresolved-review-threads + Dependabot + lint/types/tests into ONE exit code with no LLM, tracker-aware, runnable identically local+CI. pre-commit gives hook symmetry but not the tracker-aware semantic checks. This is Hedl's strongest moat. |
| Task runner backing the gate | just / mise | https://github.com/casey/just (33,985 ★); https://github.com/jdx/mise (28,845 ★) | both active | **REJECT the dispatch layer.** Use `just`/`mise` tasks to define the per-stack commands instead of `hedl.toml` dispatch; Hedl keeps only the semantic glue. Lower maintenance than a bespoke dispatch format. |
| Git-hook plumbing | lefthook | https://github.com/evilmartians/lefthook | 8,301 ★, pushed today | REJECT bespoke hook wiring where a declarative hook manager suffices. |
| Adversarial review panel (8 agents + dispatcher + 18 prompts) | CodeRabbit / Greptile / PR-Agent (qodo) / native Claude Code Workflows | https://github.com/The-PR-Agent/pr-agent (11,412 ★, pushed today); Greptile/CodeRabbit commercial (CodeRabbit: 2M+ repos) | mixed | **REJECT for review *quality*; ADOPT-Hedl for the *deterministic dispatch floor only*.** Greptile indexes the whole repo (catches cross-file issues a diff-only roster misses); CodeRabbit has 2M+ repos installed. Native Workflows now do the refute/converge judge-panel shape. Hedl's residual edge is the gate-enforced "you must have run dispatch" floor, not the roster's intelligence. |
| Work / phase tracking (`.work/`) | GitHub Projects/Issues + CCPM, or Linear | https://github.com/automazeio/ccpm (8,158 ★); Linear (commercial) | — | **REJECT for tracking; ADOPT-Hedl only for the phase-boundary cull/retain binding.** GitHub Milestones/Linear cycles + CCPM cover scope tracking with real backends. Hedl's unique bit is binding phase completion to a forced existential-challenge + watchlist-expiry, which no tracker does — but that is a tiny sliver. |
| ADR / decision log | MADR template + adr-tools | https://github.com/adr/madr (2,233 ★, active); https://github.com/npryce/adr-tools (5,486 ★, **stale: last push 2024-04**) | — | **REJECT bespoke schema; adopt MADR.** Hedl's own doc commits to "adopt MADR or prove a feature adr-tools can't." adr-tools is effectively unmaintained (no push since Apr 2024), so don't depend on its CLI; vendor the MADR markdown template and keep Hedl's cross-link-to-`work.json` as the only differentiator. |
| ADR browsable site | log4brains | https://github.com/thomvaill/log4brains | 1,481 ★, **stale: last push 2024-12** | REJECT-this-substitute too — log4brains is low-traction and stale; not worth a dependency. ADOPT-Hedl's plain-markdown approach. |
| PR-template enforcement (`check_pr_template.py`) | Danger (JS/Ruby) + commitlint | https://github.com/danger/danger-js (5,475 ★); https://github.com/conventional-changelog/commitlint (18,562 ★, pushed today) | — | **REJECT unless local+CI symmetry proves a unique save.** Danger enforces PR structure server-side; commitlint enforces commit format. Hedl's only edge is checking WORK-ID staleness against local `work.json` *before* push. If that save isn't demonstrated, replace with a Danger ruleset configured from `hedl.toml`. |
| Multi-operator coordination (Team tier, `--streams`) | gh-sub-issue + CCPM worktrees | https://github.com/yahsan2/gh-sub-issue (116 ★) | — | Split: `--streams` overlap-refusal is **ADOPT-Hedl** (no focused tool refuses a "done" cert on pre-merge diff overlap). The rest of the team tier is **REJECT** — CCPM's worktree parallelism is more battle-tested. NOTE the repo cites `k1LoW/gh-sub-issue` which does **not exist**; the real tool is `yahsan2/gh-sub-issue` (116 ★). |
| Budget tier accounting (`budget_manager.py`) | Anthropic usage dashboards / nothing | — | — | **REJECT.** The repo itself marks this culling-candidate with unsourced 12/22/28 thresholds and a silent Pro-plan reset. Delete the tier machinery for a single invocation counter. |
| Hooks integration (SessionStart/PostToolUse/Stop) | Claude Code native hooks; pre-commit for post-edit lint | native; https://github.com/pre-commit/pre-commit | 15,295 ★ | **REJECT the bespoke scripts as default-on.** Post-edit lint belongs in pre-commit/native hooks; keep Hedl-specific session priming opt-in given the flagged security expansion. |
| Slash commands + NL routing | Claude Code native skill activation | native | — | **REJECT the routing table.** The host already routes phrases to skills; the table duplicates native behavior and risks staleness (the repo's own Phase-1 verdict: "not shrunk, EXTEND"). Keep only the flow definitions. |
| Self-improvement loop (reflect/contribute) | manual retro / git log | — | — | **REJECT until proven.** Repo's own Phase-1 verdict: zero `/contribute` PRs landed → demoted to culling-candidate. Mechanism without evidence. |

## Competitors the repo's alternatives.md missed

The repo's competitive map is thoughtful but has notable gaps, all of them
*larger and more current* than what it does cite:

1. **GitHub Spec Kit (107k ★)** — the single biggest entrant in the exact
   category Hedl plays in, GitHub-official, shipping daily. Not mentioned anywhere
   in `alternatives.md`. This is the most significant omission: Hedl maps itself
   against CCPM (8k) but ignores the 107k-star category leader.
2. **OpenSpec (52k ★)** — its proposal→apply→archive state machine directly
   competes with Hedl's phase tracking and ADR discipline, with a cleaner model
   and 13x the relevance signal. Unmentioned.
3. **BMAD-METHOD (48k ★)** — agent personas/roster + dev-loop automation overlaps
   Hedl's adversarial roster at scale. Unmentioned.
4. **Taskmaster (27k ★)** — work decomposition / PRD→tasks; the de-facto popular
   choice for AI task tracking. Unmentioned.
5. **Agent OS (4.7k ★)** — standards injection + spec writing, comparable in
   scale to Hedl's standards.md ambitions. Unmentioned.
6. **Amazon Kiro** — proves the spec-as-source-of-truth + agent-hooks pattern is
   now table stakes industry-wide, including from AWS. Unmentioned.
7. Focused-substitute gaps: **mise** (28k, task running), **lefthook** (8k, hook
   management), and **PR-Agent/qodo** (11k, OSS AI review) are all absent from the
   single-purpose alternatives, though just/danger/commitlint are covered.

The pattern: the repo benchmarks against the *architecturally similar but small*
peer (CCPM) and the *prior-art origin* (mcp-cli), but does not confront the
*category leaders* that would most threaten any adoption pitch.

## Corrections to repo's competitive claims

1. **gh-sub-issue attribution is wrong.** `alternatives.md:245,393` cite
   `k1LoW/gh-sub-issue`. That repo returns 404. The actual extension is
   `yahsan2/gh-sub-issue` (116 ★, last push 2025-10). Minor but a verifiable
   factual error in a doc that prides itself on cited evidence.
2. **adr-tools and log4brains are stale, not just "alternatives."** The doc
   treats adr-tools (last push **2024-04**) and log4brains (last push **2024-12**)
   as live competitors. Both are effectively unmaintained in 2026. This *helps*
   Hedl's ADR case (don't depend on a dead CLI) but the doc should say so rather
   than imply they are current.
3. **The named gate prior art is not a competitive threat.** The doc is admirably
   honest that the gate derives from theshadow27/mcp-cli — but that repo has
   **2 stars**. Framing it as the "direct origin" is correct for attribution;
   readers should not infer it is an alternative anyone would adopt instead.
4. **The native-orchestration claim is verified and, if anything, understated.**
   The doc's "Opus 4.8 native Workflows" assessment is accurate: Claude Code Agent
   Teams (team-lead + subagents) and Dynamic Workflows (fan-out + refute/converge)
   are confirmed shipping in 2026. This is a larger threat to the review-panel and
   multi-operator capabilities than the doc's "sharpened, no downgrade" framing
   admits — native fan-out + refute *is* the judge-panel pattern.
5. **CCPM is mischaracterized as purely "humans don't overlap, no gate."**
   (`alternatives.md:371`). CCPM does ship deterministic no-LLM scripts and
   worktree isolation that materially reduce overlap; Hedl's edge is the
   *pre-push refusal*, not that CCPM has "no" coordination. The distinction is
   real but narrower than stated.

## What would raise the score

- **Ship and get adoption.** Defensibility is currently theoretical: zero
  released distribution, single operator, no external stars to verify. One
  external adopter repo running the gate in CI would move this more than any
  feature.
- **Confront the category leaders.** Add spec-kit / OpenSpec / BMAD / Taskmaster
  to `alternatives.md` and articulate the "gate layer on top of spec-kit" wedge
  explicitly. The strongest honest position is "Hedl is the deterministic gate
  and stream-isolation you bolt onto spec-kit/CCPM," not "Hedl is a framework."
- **Collapse the weak layers into focused tools.** Cut budget tiers; move dispatch
  to just/mise; move post-edit lint to pre-commit; adopt MADR; replace the routing
  table with native activation. This shrinks the surface to the 2 defensible
  capabilities and removes maintenance the field already maintains better.
- **Prove the two moats empirically.** Document one real `--streams` save and one
  WORK-ID-staleness catch the server-only checks missed. Both are claimed; neither
  is demonstrated (per the repo's own Phase-1 verdicts).
- **Decouple from the host's roadmap.** As native Agent Teams/Workflows mature,
  the review panel's only durable value is the *deterministic dispatch floor*
  bound to the gate — lean into that, stop competing on orchestration.

## Scores

- **Competitive-defensibility score: 3/10.** Justification: Two genuinely
  defensible primitives (the tracker-aware deterministic gate bundle; the
  `--streams` pre-push overlap refusal) keep this off the floor — neither has an
  exact focused substitute, and both are concretely implemented. But the
  framework-level pitch is indefensible against the verified field: spec-kit
  (107k), OpenSpec (52k), BMAD (48k), Taskmaster (27k) and even CCPM (8k) all
  dwarf an unreleased, single-operator project, and the host (Claude Code) is
  natively absorbing the orchestration layer. 9 of 13 capabilities have a
  stronger focused substitute or are the repo's own watchlist/culling candidates.
  The moat is real but thin and narrowing; defensibility rests almost entirely on
  the gate, which the repo honestly admits is derived prior art. A project this
  small in a category this crowded is structurally hard to defend, and the repo's
  own competitive map omits every leader that matters.
- **Intrinsic-quality: N/A** — competitive-only agent.

## Confidence and why

**High confidence** on competitor existence and star/activity figures: fetched
live via GitHub API on 2026-05-30 (spec-kit 107,179; OpenSpec 51,806; BMAD
48,314; Taskmaster 27,293; CCPM 8,158; pre-commit 15,295; commitlint 18,562;
just 33,985; mise 28,845; etc.). High confidence the native Claude Code
orchestration (Agent Teams + Dynamic Workflows) is real (official docs + multiple
2026 sources). **Medium confidence** on the precise boundary of Hedl's gate
uniqueness — verified by reading file sizes/structure read-only, not by running.
**Lower confidence** on commercial tools' exact reach (CodeRabbit/Greptile/Kiro
report self-published or marketing figures, not star-comparable).

## Not checked

- Exact star *velocity* (stars/week) for any repo — only absolute counts and last
  push date were verified.
- CodeRabbit "2M+ repos" and "13M+ PRs" are vendor marketing claims, not
  independently verified.
- Kiro has no comparable OSS star metric; pricing/usage figures are from reviews,
  not AWS primary docs verified here.
- `superagent-ai/conductor` and `coder/conductor` both returned 404; "conductor"
  as a named competitor could not be located at the guessed paths and was not
  pursued further.
- Hedl's own star count / adoption: the repo is at a pinned local commit with no
  public GitHub metrics available to this review.
