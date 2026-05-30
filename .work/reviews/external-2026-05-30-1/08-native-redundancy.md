# Native-platform redundancy

External adversarial review. Dimension: NATIVE-PLATFORM REDUNDANCY (Hedl vs the
latest native Claude Code platform it extends). Repo inspected read-only at
`796639c6c926ba2535bac3a5474f5d2feb62cb28`. Date: 2026-05-30.

## Summary

Hedl is a Claude Code Agent Skill. The majority of its *mechanisms* are now
first-class native Claude Code primitives, and the most strategically important
overlap — the hand-rolled adversarial review panel — is squarely subsumed by
two native capabilities that shipped in the weeks before this review:

- **Agent teams** (native, requires v2.1.32+; experimental flag
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) — a lead session spawning specialist
  teammates in parallel with a shared task list and inter-agent messaging. The
  official docs ship *the exact two patterns Hedl hand-rolls*: a "parallel code
  review" with security / performance / test reviewers each on a distinct lens,
  and a "competing-hypotheses scientific debate" where teammates adversarially
  challenge each other. (code.claude.com/docs/en/agent-teams)
- **Dynamic Workflows** (research preview, dated 2026-05-28) — Claude writes
  orchestration scripts running "tens to hundreds of parallel subagents in a
  single session, checking its work before anything reaches you." This is the
  release the repo's own `docs/alternatives.md` flags.
- **Outcomes / rubric grader** (public beta, Managed Agents, 2026-05-12) — a
  separate grader in a fresh context window scores an artifact against a rubric
  and feeds gaps back for revision. This is the native form of "judge-panel."

Against that backdrop, Hedl's honest defensible core narrows to exactly what its
own `docs/alternatives.md` already concedes: the **deterministic, CI-symmetric,
work-item-aware completion gate** (`am_i_done.py`) and its `--streams` overlap
check. Those are NOT LLM orchestration — they are a deterministic exit-code
boundary that no native Claude Code feature provides. Everything that is
LLM-mediated routing, review, or orchestration is now redundant or partial.

Note the framework's self-assessment is unusually candid (it already classifies
the panel as "watchlisted / sharpened" and budget accounting as
"culling-candidate"). My independent finding is *harsher* on the panel: native
agent-teams does not merely "narrow" the panel's differentiator, it ships the
panel's headline use-cases verbatim. The residual value is the roster prompts +
the deterministic dispatch floor, not the orchestration.

## Feature-by-feature native mapping

| Hedl feature | Native Claude Code equivalent (docs URL) | Verdict | What to use natively if redundant |
|---|---|---|---|
| (1) SKILL.md natural-language routing table (`skill/hedl/SKILL.md:11-42`) | Native skill activation via `description` frontmatter; "Claude uses each subagent's/skill's description to decide when to delegate" (code.claude.com/docs/en/skills) | **REDUNDANT** | Put trigger phrases in the SKILL.md `description`; delete the 28-row routing table — the host already routes phrases to skills, and the table is a stale projection of that. |
| (2a) The 8 review agents as `.claude/agents/` files (name/description/tools/model frontmatter) | Native subagents — identical format; `tools`/`model` (incl. haiku) supported (code.claude.com/docs/en/sub-agents) | **PARTIAL** | The *file format and dispatch* are 100% native; keep the agents as native subagents. Additive part = the specific opinionated roster prompts. |
| (2b) Adversarial review *orchestration* (`/adversarial-review`, parallel panel, rebuttable findings, synthesized verdict) | **Agent teams** parallel-review + competing-hypotheses debate patterns (code.claude.com/docs/en/agent-teams); **Dynamic Workflows** 2026-05-28; **Outcomes** rubric grader 2026-05-12 | **REDUNDANT** | "Create an agent team to review this diff: one security reviewer, one scope, one edge-case…" — native spawns them in parallel, has them challenge each other, and synthesizes. Hedl's hand-rolled panel adds ceremony, not capability. |
| (3) The 5 slash commands in `.claude/commands/` (`/start-session`, `/iterate`, `/adversarial-review`, `/pr-ready`, `/phase-complete`) | Custom commands "merged into skills"; `.claude/commands/*.md` and `.claude/skills/*/SKILL.md` both create `/name` and work identically (code.claude.com/docs/en/skills) | **PARTIAL** | The `/command` *mechanism* is native and the existing files keep working. Additive = the flow *content* (the `commands.md` recipes). Mechanism redundant; content additive. |
| (4) Multi-agent review orchestration (dispatcher + budget-aware deferral + roster) | Agent teams + Dynamic Workflows (verified shipped: 2026-05-28 dynamic workflows; agent teams documented, experimental) | **REDUNDANT** (orchestration) | Delegate orchestration to native agent teams / dynamic workflows; the repo's own ADR-012 move ("wrap host orchestration with the gate, don't build Hedl-native") is correct. |
| (5) Hooks: SessionStart (`startup.sh`), PostToolUse Edit/Write lint, Stop reminder (`.claude/settings.json:8-40`) | Native hooks — SessionStart, PostToolUse (matcher `Edit\|Write`), Stop all native; same JSON schema Hedl uses; native also adds `SubagentStop`, `TeammateIdle`, `TaskCompleted`, `agent`/`prompt` hook types (code.claude.com/docs/en/hooks) | **PARTIAL** | The hook *primitive and events* are native (Hedl consumes them, doesn't extend them). Additive = the *specific scripts*. The Stop reminder is largely redundant with native auto-memory / the gate; the post-edit lint duplicates a `PostToolUse` everyone can write. |
| (6) `.claudeignore` (symlink to `skill/hedl/integrations/claude-code/claudeignore`) | Native `.claudeignore` / "Respect .gitignore" config exists but is documented as unreliable for secrets (theregister.com 2026-01-28; gh issues #2305, #30810) | **REDUNDANT** (mechanism) | The file is a thin native wrapper. For the secret-blocking intent, native guidance is `permissions.deny` in settings.json, not `.claudeignore`. Hedl adds no enforcement beyond the native (limited) behavior. |
| (7) Phase/work tracking (`.work/phases`, `.work/work.json`, `/phase-complete`) | Native plan mode, TodoWrite/shared task list, and **auto memory** (filesystem-based, dated 2026-04-23; CLAUDE.md memory) (code.claude.com/docs/en/memory, /interactive-mode#task-list) | **PARTIAL** | Native TodoWrite + memory track tasks/learnings; native does NOT enforce *gated phase transitions*. Additive = the `existential-challenger`-mandatory phase boundary + watchlist expiry binding. Tracking-as-data is redundant; transition *discipline* is additive. |
| (8) Budget tier accounting (`budget_manager.py`, FULL/REDUCED/MINIMAL/DEFERRED, 12/22/28 thresholds) | Native usage/cost surfaces: `/cost`, agent-team token-cost guidance (code.claude.com/docs/en/costs), API usage dashboards; native context-window visualization (code.claude.com/docs/en/context-window) | **REDUNDANT** | Use native `/cost` and plan dashboards. The thresholds are unsourced and the Pro reset is silent (the repo itself marks this culling-candidate). Drop the tier machinery for a single invocation counter or native cost display. |
| (9) Deterministic completion gate (`am_i_done.py`) + `--streams` overlap check | No native equivalent. Native has `prompt`/`agent` hooks and Outcomes, but all are LLM-mediated; none is a deterministic, CI-symmetric, single-exit-code, work-item-aware boundary | **ADDITIVE** | Keep. This is the defensible core. (Caveat: the deterministic CI-symmetric *concept* is prior art from theshadow27/mcp-cli per the repo's own honesty note; Hedl's additive part is the distributable, tracker-aware *packaging* and `--streams`.) |
| (extra) Plugin distribution / install.py tiers | Native **plugins + marketplace** (code.claude.com/docs/en/plugins-reference): plugins bundle skills+agents+hooks+MCP, user/project scope install, `/reload-plugins` | **PARTIAL** | Native plugins are the modern distribution channel and subsume the symlink-projection install model. Additive = the reversible, archive-on-downgrade *tier* contract (no native equivalent for "adopt only part"). Consider repackaging Hedl as a native plugin and keeping `install.py` only for tier projection. |
| (extra) Reflect/contribute self-improvement loop | Native auto memory (2026-04-23) learns across sessions; no native privacy-scoped contribution PR flow | **PARTIAL** | Native memory covers per-session learning. Additive = the privacy-scrubbed cross-repo *contribution* PR — but the repo concedes zero such PRs have landed (culling-candidate). |

## What is genuinely additive over native (the defensible core)

1. **The deterministic completion gate (`am_i_done.py`)** — feature (9). A
   single non-LLM exit code binding lint/types/tests + PR-template validity +
   stale work-item IDs + unresolved threads + Dependabot, run identically local
   and in CI. Native Claude Code has no deterministic gate; Outcomes/`agent`
   hooks are all inference. This is the one feature native genuinely does not do.
2. **`--streams` multi-stream overlap check** — refuses to certify a stream
   "done" if its diff overlaps another declared stream's diff, *before* push.
   Native agent-teams docs explicitly punt on this ("two teammates editing the
   same file leads to overwrites… break the work so each owns different files")
   — a prose best-practice, not an enforced gate. Genuinely additive.
3. **Gated phase-transition discipline** — feature (7), partial. The binding of
   phase completion to a mandatory existential-challenge + watchlist expiry is
   not something native TodoWrite/memory enforces. Additive, but thin: it is a
   convention layer, not a primitive.
4. **The reversible tiered install contract** — partial. "Adopt only the gate"
   with archive-on-downgrade has no native analog (native plugins are
   all-or-nothing per plugin).

Everything additive is *deterministic discipline*, not orchestration. That is
the correct and only defensible position against the native platform.

## What is now redundant and should be dropped in favor of native

- **The SKILL.md 28-row natural-language routing table** — pure duplication of
  native skill `description` activation. Move triggers into the description;
  delete the table. (The repo's own watchlist objective already says to shrink
  it; Phase-1 verdict was "EXTEND" because it was NOT shrunk — i.e. still owed.)
- **The hand-rolled review-panel orchestration** (`/adversarial-review`'s
  parallel dispatch + synthesis) — replace with native agent teams / dynamic
  workflows. Keep the 8 roster prompts as native subagent definitions (which
  agent-teams can spawn by name), drop the bespoke orchestration.
- **Budget tier accounting** (`budget_manager.py` tier machinery) — redundant
  with native `/cost` + dashboards; thresholds unsourced. The repo already calls
  this culling-candidate.
- **`.claudeignore`** as a Hedl-provided artifact — it is a thin native wrapper
  with known limits; for the secret-blocking intent use native `permissions.deny`.
- **The Stop-hook reminder** — low marginal value over native auto-memory + the
  gate; offer opt-in rather than default.

## What would raise the score

- **Repackage as a native plugin** (plugins-reference) so distribution rides the
  native marketplace; reserve `install.py` solely for the tier-projection
  contract that native lacks.
- **Bind the gate into native verification hooks** — wire `am_i_done.py` as a
  native `Stop` / `SubagentStop` / `TaskCompleted` hook (exit 2 to block), so the
  deterministic gate gates *native* orchestration. This makes Hedl the
  deterministic floor under agent teams rather than a parallel universe.
- **Re-express the roster as agent-team spawn definitions** and measure
  non-overlapping signal (the repo's own Phase-1 objective) so the roster earns
  its place above a generic native "review this diff."
- **Delete the routing table and budget tiers** and report the resulting
  surface-area reduction — the framework would then defend a smaller, sharper
  claim.

## Scores

- **Competitive-defensibility (vs native platform) score: 4/10** — Of ~12
  mapped features, the deterministic gate + `--streams` (2 features) are
  genuinely additive and strong; ~4 are partial (subagent format, command
  mechanism, phase discipline, tiered install, self-improvement); and ~5 are now
  redundant against native primitives that shipped *this month* (routing table,
  panel orchestration, budget tiers, `.claudeignore`, Stop reminder). The single
  most strategically-sold capability — the adversarial review panel — is the one
  native most clearly subsumed (agent-teams ships its exact use-cases). A
  framework whose headline differentiator is now native scores below the
  midpoint on defensibility. It is saved from a lower score by a real, narrow,
  deterministic core that native genuinely does not provide, and by the
  framework's own honest watchlisting.
- **Intrinsic-quality: N/A** — native-redundancy-only agent.

## Confidence and why

**High** on the native mappings: I verified subagents, hooks, skills,
agent-teams, plugins, memory, and outcomes against official `code.claude.com`
docs and dated Anthropic release notes (dynamic workflows 2026-05-28; multi-agent
orchestration + outcomes 2026-05-12; memory 2026-04-23). The agent-teams doc
containing Hedl's exact panel use-cases is direct, load-bearing evidence.
**Medium** on two points: (a) Dynamic Workflows is research-preview and
Max/Team/Enterprise-gated, so its availability to a given Hedl operator varies —
this slightly *reduces* immediate redundancy for solo/Pro users; (b) agent teams
are experimental (flag-gated), so the panel's orchestration redundancy is
"native exists but is beta," not "native is GA." Both caveats argue for PARTIAL
rather than hard REDUNDANT on the orchestration in the very near term, but the
trajectory is unambiguous.

## Not checked (native features I could not fully confirm from docs)

- Whether native hooks support `.claudeignore` *enforcement* improvements landed
  after 2026-01 (the reporting I found is from January 2026 and is negative; I
  did not find a docs page confirming a fix).
- Exact GA-vs-beta status of Dynamic Workflows and agent teams as of 2026-05-30
  (release notes say research-preview / experimental; I did not find a GA date).
- Whether native plugins support a tiered/partial-install contract — docs
  describe per-plugin user/project scope but I found no "install part of a
  plugin" feature, so I treated the tier contract as additive.
- Native `/cost` granularity for per-subagent invocation caps (I confirmed cost
  surfaces exist but not that they replicate Hedl's per-PR deferral semantics).

Sources:
- https://code.claude.com/docs/en/overview
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/agent-teams
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/plugins-reference
- https://code.claude.com/docs/en/memory
- https://releasebot.io/updates/anthropic/claude
- https://claude.com/blog/new-in-claude-managed-agents
- https://platform.claude.com/docs/en/managed-agents/define-outcomes
- https://www.theregister.com/2026/01/28/claude_code_ai_secrets_files/
