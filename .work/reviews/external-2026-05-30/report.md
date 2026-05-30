# External Adversarial Review — Hedl

**Date:** 2026-05-30
**Target:** https://github.com/neilgfoster/hedl @ `caa800e` (v0.1.0, tag `v0.1.0`)
**Method:** Read-only clone to `/tmp/hedl-review-clone` (no scripts executed). Swarm of 9 independent agents — 6 code-assessment + 3 web-enabled competitive/redundancy analysts — each scoring 0-10. Latest (2026) Claude Code, CCPM, spec-kit, OpenSpec, BMAD, Task Master, pre-commit/Danger/adr-tools docs consulted live.
**Repo facts:** 3 days old (first commit 2026-05-28), 68 commits, single human author (66) + dependabot (2), ~13.7k LOC incl. tests, stdlib-only runtime.

---

## Overall Summary

**Overall score: 5.6 / 10** (average of all 9 agents).
Sub-averages: **core quality dimensions 6.3** (quality, security, utility, accuracy, maintenance, supply-chain); **competitive defensibility 4.2** (frameworks, focused tools, native redundancy).

| # | Agent / Dimension | Score |
|---|---|---|
| 1 | Quality | 7 |
| 2 | Security | 7 |
| 3 | Utility | 4 |
| 4 | Accuracy | 8 |
| 5 | Maintenance | 5 |
| 6 | Supply-chain | 7 |
| 7 | Competitive — frameworks (CCPM, spec-kit, OpenSpec, BMAD, Task Master) | 4.5 |
| 8 | Competitive — focused tools (pre-commit, Danger, adr-tools, commitlint, gh-sub-issue, just) | 4.0 |
| 9 | Redundancy — native Claude Code (Skills, subagents, Workflows, Agent Teams, hooks, plugins) | 4.0 |
| | **Average** | **5.6** |

**Verdict in one line:** Hedl is engineered far above its 3-day age (honest docs, real tests, security-aware, no `shell=True`, SHA-pinned CI), but its *defensible surface is a single ~1700-line script*. The bundled deterministic completion gate, the pre-merge `--streams` overlap check, and the reversible tiered installer are genuinely not replicated elsewhere; **most of the surrounding framework is now redundant with native Claude Code primitives or out-competed on adoption.** Value beyond the author is asserted, not demonstrated (one dogfood-only adopter, flagship "invisible mode" unbuilt).

### Adopt / Reject — per identified tool or capability

**Keep (ADOPT, conditionally):**
- **Hedl deterministic completion gate (`am_i_done.py`)** — ADOPT. One inference-free pass/fail exit code over a work-item-aware bundle (clean tree, branch, PR template, stale WORK-IDs, lint/types/tests, unresolved threads, Dependabot), identical locally and in CI. No competitor or native feature ships this. *Condition:* configure GitHub branch protection with the correct check contexts (see Accuracy finding) or the gate is advisory only.
- **`--streams` pre-merge overlap check** — ADOPT. Uniquely Hedl: refuses to certify a stream done if its diff overlaps another declared stream *before* merge. Native Agent Teams explicitly does **not** do this.
- **Reversible, archive-on-downgrade tiered installer + LLM-agnostic gate-only drop-in** — ADOPT (niche). Native plugins do one-click install but not graduated reversible tiers; the gate-only tier works with no Claude Code and no LLM.

**Reject in favour of native / focused tooling (with the native path to adopt):**
| Hedl capability | Decision | Adopt instead |
|---|---|---|
| Adversarial review panel + dispatcher | REJECT (orchestration) | **Native Dynamic Workflows / Agent Teams** (judge-panel & adversarial-verify are now native, 2026-05-28). Keep only the curated roster as native subagent definitions + the gate's deterministic dispatch floor. |
| `SKILL.md` 28-row NL routing table | REJECT | **Native skill auto-activation** from the SKILL.md `description` field (Hedl admits the table "risks going stale"). |
| Five slash commands (mechanism) | REJECT (mechanism) | **Native commands/skills** (commands merged into skills in 2026); native `/code-review`, `/security-review` cover mainstream review. Keep only the gate/phase flow content. |
| Hooks scripts (post-edit lint, stop reminder) | REJECT (as differentiators) | **Native hooks** + **pre-commit** (Dependabot now manages pre-commit pinning natively, 2026-03). Make each hook opt-in. |
| `budget_manager.py` tier accounting | REJECT | **Anthropic plan dashboards.** Self-declared culling-candidate; thresholds (12/22/28) unsourced, Pro reset silently negates the queue. |
| ADR six-line recipe | REJECT | **MADR template + adr-tools** (log4brains for a published site). Keep only spike→ADR workflow binding. |
| `check_pr_template.py` (154 LOC) | REJECT | **Danger ruleset or a GitHub Action**, unless the WORK-ID-staleness-vs-`work.json` check proves load-bearing. |
| Commit conventions (prose in `standards.md`) | REJECT | **commitlint / conventional-commits** (drives semver + changelog). |
| Multi-operator / GitHub Issues coordination | REJECT (compete) → fold | **gh-sub-issue (native sub-issues)** for hierarchy; **CCPM** or **native Agent Teams** for parallel issue execution. Position as "Hedl gate + CCPM/Teams," per Hedl's own ADR-012. |

---

## Detailed Findings

### 1. Quality — 7/10
**Above-average for a v0.1.0.** `am_i_done.py` is a clean 1703-line module (dataclasses `CheckResult`/`Report`, uniform `Optional[CheckResult]` skip contract, all subprocess calls list-form with timeouts, no `shell=True`). The gate is *genuinely* tested: 131 dedicated test methods (413 suite-wide) covering CI status classification, allowlist/denylist/metachar bypasses, byte-drift, symlink-escape, and Dependabot exemption edge cases. **Corrects the brief's premise:** the "scripts duplicated in 3 places" hazard is false — `.github/scripts/*` and `.claude/scripts/*` are git symlinks (mode 120000) into the single canonical `skill/hedl/` tree (independently confirmed: `am_i_done.py` md5-identical across paths, symlinked).
- *Gaps:* `main()` dispatch matrix (`am_i_done.py:1597-1662`) untested — a routing regression could silently drop a check; `check_branch/check_dispatch/check_budget/check_markdown/check_skill_metadata` have no direct tests; `_append_gate_insight` (`1665-1699`) swallows all exceptions with bare `except`; ruff config self-defeating (E501 ignored, `line-length=100` only feeds an un-run formatter); `[verify]/default` resolution copy-pasted across lint/types/tests; module trending toward a god-module (19 checks + backend + CLI + doc-parsing in one file).
- *To reach 8-9:* test the dispatch matrix + exit-code-2 path; add direct unit tests for the untested checks; fix or correct the ruff line-length config; extract the duplicated preamble.

### 2. Security — 7/10
**Unusually security-aware.** No `shell=True` anywhere; the only untrusted external input (PR body) crosses to the child via `env PR_BODY` not argv, NULs stripped (`1145-1152`). The `[verify]` surface is depth-constrained: `shlex.split`, metachar denylist, bare-name-only executable, interpreter/forwarder denylist (blocks python/bash/node/env/xargs/find/awk/eval), allowlist, cwd-escape check. `install.py` has real path-containment guards run *before* any write/delete (`_resolve_contained`, `_validate_tier_paths`, TOML-injection guard on backend name). Dependabot template exemption keys off GitHub-verified bot identity (`is True`), not spoofable PR body/branch. CI runs on `pull_request` (not `pull_request_target`), least-privilege, SHA-pinned, expression-injection-safe. Hooks fail-closed on missing `CLAUDE_PROJECT_DIR`.
- *Gaps:* `contribute.py`'s "privacy scrub" is a **filename-prefix check that reads no content** — cannot detect PII/secrets pasted into a `skill/hedl/` file, yet the docstring calls it a "privacy fail-closed scrub" (overstated). Team-tier `startup.sh` is unguarded bash trusting repo-committed `.work` JSON. The whole trust expansion (SessionStart shell + PostToolUse-on-every-edit + Stop) ships via a committed `settings.json` whose only safeguard is a comment asking reviewers to notice — no consent prompt, no checksum. `record_insights.py` is declared a team projection but **wired into no hook** (its privacy boundary is partly unreachable as shipped). The `[verify]` allowlist is honestly *not* an RCE boundary (pytest loads conftest, make runs Makefile from PR head) — but the "deterministic gate you trust" framing can lull operators into running it on untrusted forks; the real control is GitHub fork-approval, mentioned only in source comments.
- *To reach 8-9:* add a real content scrub (secret/PII regex over diff hunks); install-time consent for the team tier; harden `startup.sh`; wire or drop `record_insights.py`; surface the fork/untrusted-repo caveat in README/SKILL.md.

### 3. Utility — 4/10
**The honest low score.** The one genuinely useful primitive (gate with byte-identical local+CI execution + one exit code) is real and modestly differentiated from the loose pre-commit + required-status-checks teams already run. But for a generic adopter the *individual* checks are a thin wrapper — Hedl's own `alternatives.md` concedes "the bundle, not any single check, is the differentiator." The Hedl-specific checks (WORK-ID staleness, dispatch floor, `--streams`) only pay off if you also swallow the `.work/` ceremony, 8-agent roster, ADR discipline, and budget tiers.
- *Evidence against utility:* `ADOPTERS.md` lists exactly one adopter (Hedl itself); the internal critique states "the engine has only ever run on itself," end-user-facing capability count = 2; the flagship **invisible-mode use case is unbuilt** (WORK-0013, backlog) and the README downgrades it to "intent, not a current capability"; the README itself tells solo devs not to bother; gate-only is not truly minimal (projects `budget_manager.py` + a pinned `requirements-ci.txt` pulling the pymarkdown chain); ~half the gate's distinctive value needs `gh` CLI + GitHub auth; native Workflows (Opus 4.8) erode the review-panel/multi-operator value that justifies the heavier tiers.
- *To raise:* land one external adopter; document a concrete gate/`--streams` "save" that pre-commit+CI would miss; ship invisible mode; make gate-only literally minimal; retire budget tiers.

### 4. Accuracy — 8/10 (highest)
**Documentation is honest and headline claims hold under code cross-check.** All nine README gate checks map to real implemented functions (`check_git:306`, `check_branch:336`, `check_template:1115`, `check_commands:774`, `check_lint:902`, `check_types:923`, `check_tests:952`, `check_pr_threads:1049`, `check_dependabot:982`). CI runs the same script with SHA-pinned actions (independently confirmed). "GitHub-issues backend, read-only today" is precisely accurate; `backends.md` is candid about its trust hole and 1000-issue cap, and the code matches. Verifiable counts (8 agents / 18 prompts / 5 commands) check out and are *self-policed* by `check_doc_generated_facts`. "Planned, not built" features trace to real backlog items — no vaporware presented as real.
- *Defects:* `docs/self-improvement.md:103-105` ships a branch-protection command using `contexts: ["am-i-done"]`, but the matrix publishes `am_i_done (3.11)`..`(3.14)` — **contradicting the project's own WORK-0029 finding**, leaving the gate either bypassable or merges wedged. The README headline ("decides whether a task is actually done", "no inference") never discloses the gate is *advisory until branch protection is wired correctly* — the exact validation-theatre WORK-0029 found let red-on-main PRs merge green. Minor: the verdict path has a best-effort side effect (`_append_gate_insight` writes `events.jsonl`), and the gate actually runs ~16 checks vs the 9 headlined (framework-only checks silently skip in adopter installs).
- *To reach 9:* fix the branch-protection context names; add a one-line "advisory until branch protection" caveat to the README headline.

### 5. Maintenance — 5/10
**Strong hygiene, fatal bus factor.** 413 test functions, 4-version Python matrix (3.11-3.14), pinned dev deps + `uv.lock` + Dependabot, stdlib-only invariant test, deterministic `release.py` (semver from change_class, no LLM), honest self-assessment. Script duplication is well-engineered (symlinks, single source).
- *Live defect:* GitHub Actions workflow files **cannot** be symlinks (GitHub requirement) and have **already drifted** — `.github/workflows/` pins `actions/checkout` v6.0.2 (dependabot PR #39) but the shipped `skill/hedl/workflows/` templates still pin v5.0.1. A drift detector exists (`install.py --doctor`, with a test) but is **not wired into CI**, so a project selling a deterministic gate ships drifted copies of its own gate workflow undetected.
- *Other:* bus factor = 1 (66/68 commits one author); no `CONTRIBUTING.md`, no issue/PR templates despite courting adopters; self-improvement loop unproven (zero reflect/contribute PRs ever landed — its own Phase-1 bar); 3-day velocity (36/23/9) too thin to read; heavy governance-to-code ratio (33 ADRs, 18 insights, ~15 review dirs) that only the single author can keep coherent.
- *To raise:* add a CI filecmp test asserting `.github/workflows/*` == `skill/hedl/workflows/*`; add `CONTRIBUTING.md` explaining the symlink/projection model; land one end-to-end self-improvement PR or scope it down.

### 6. Supply-chain — 7/10
**Genuinely strong posture.** Every Action full-SHA-pinned with version comments (no floating tags) in both root and adopter-projected workflows; Dependabot covers uv/pip/actions; CodeQL scans python + actions; CI installs from frozen `uv.lock`. **The install mechanism is the standout: `install.py` is stdlib-only and fetches nothing remote (symlink/copy only); neither `startup.sh` curls anything** — an adopter pulls in zero network-fetched code at install time. `test_stdlib_only.py` statically (AST) enforces the zero-dependency invariant.
- *Gaps:* `requirements-ci.txt` (adopter pip fallback) has **silently drifted** from its declared source of truth — pins `ruff==0.15.14` while `uv.lock`/`pyproject.toml` pin `0.15.15` (dependabot PR #42 bumped the lock, the "GENERATED/in-sync" file was never regenerated); no test enforces the sync. Adopter workflow copies pin older `actions/checkout` v5.0.1 vs root v6.0.2. `test_stdlib_only.py` omits the three team-tier hook scripts that actually execute on an adopter's machine. The self-review scored supply-chain 9 and missed the ruff drift.
- *To reach 9:* add a CI `uv export` diff against `requirements-ci.txt`; sync adopter workflow SHAs to root + add an equality test; extend the stdlib-only test to the hook scripts.

### 7. Competitive — AI-coding frameworks — defensibility 4.5/10
Researched live (2026): **CCPM** (~8.2k★, the closest direct competitor: PRD→epic→issue, GitHub Issues as DB, git-worktree parallel agents, 14 deterministic bash scripts) — but its bash does status/standup, **not** a single inference-free done verdict bound to CI; **spec-kit** (~107k★, GitHub-official, category leader), **BMAD-METHOD** (~43k★, 12+ personas), **OpenSpec** (~27k★, propose→apply→archive), **Task Master** (~25k★, MCP-native, 36 tools). All five dwarf Hedl on adoption and own the 2026 "spec-driven development" narrative; **all verify via LLM, none ships a deterministic CI-symmetric completion gate** — that is Hedl's one decisive, narrow win. Hedl loses on adoption, spec-authoring depth, persona richness, MCP integration, and portability. The moat is a single ~1700-line cloneable script with unproven value.
- *Recommendation:* keep the gate + `--streams`; do **not** out-build spec-kit/OpenSpec/BMAD/Task Master — position Hedl as the deterministic done-gate that layers *under/alongside* them ("spec-kit for specs, Hedl for the completion verdict"; "Hedl gate + CCPM coordination").

### 8. Competitive — focused single-purpose tools — defensibility 4.0/10
Hedl's README concedes "for most Hedl capabilities a focused tool already does that one thing," and per-piece that concession is correct: **pre-commit** owns commit-time lint (Dependabot now manages its pinning natively); **Danger** owns PR-structure (`check_pr_template.py` is 154 LOC reimplementing a Danger rule — Hedl's own docs set the objective to replace it); **adr-tools/log4brains/MADR** own ADR mechanics (supersession graph, published site, standard template) that Hedl's six-line recipe lacks; **commitlint** owns commit conventions + the semver/changelog pipeline (Hedl doesn't really compete); **gh-sub-issue** owns issue hierarchy via native GitHub sub-issues; **just/Taskfile/make** own the task-runner entrypoint. Hedl's non-redundant residue: the *bundle* behind one exit code, `--streams`, and the reversible installer.
- *Factual error found in Hedl's own docs:* `alternatives.md` attributes `gh-sub-issue` to **k1LoW** — the maintained extensions are **yahsan2/gh-sub-issue** and **agbiotech/gh-sub-issue** (k1LoW ships gh-wait / gh-pr-reviews). Fix the misattribution.
- *Recommendation:* if a team wants only one piece, use the focused tool — exactly what the README already says. Keep Hedl only for the bundle.

### 9. Redundancy vs native Claude Code — unique value remaining 4.0/10
**The most important finding for a plugin/extension.** Verified against current (2026) Claude Code docs: a majority of Hedl's surface is now native.
- **Adversarial panel → native Dynamic Workflows** (research preview): orchestrates subagents from a rerunnable JS script, explicitly supports judge-panel / "adversarially review each other's findings," bundled `/deep-research` "votes on each claim." This *is* the dispatcher+panel shape Hedl hand-rolls in prose. **Native Agent Teams** add a documented parallel PR-review (security/perf/coverage) + competing-hypotheses debate, with `TaskCompleted`/`TeammateIdle` exit-code-2 blocking hooks.
- **Routing table → native skill auto-activation** from the SKILL.md `description` (Hedl admits this is "a projection the host already does").
- **Slash commands → native** (commands merged into skills in 2026; `.claude/commands/*.md` and `.claude/skills/*/SKILL.md` both create `/cmd`); native `/code-review`, `/security-review` cover mainstream review.
- **Hooks → literally the native primitive**; Hedl just wires three scripts; native Stop exit-code-2 already forces continued work.
- **Tiered install → native plugins** bundle skills+agents+hooks+commands for one-click install; Hedl's reversible *graduated* tiers + LLM-agnostic gate-only drop-in are the only additive part.
- **Genuinely survives:** the deterministic no-inference completion gate (sees work-item state native gates do not), the pre-merge `--streams` overlap check (Agent Teams explicitly does **not** prevent overlap), and the reversible installer.
- *Recommendation (paste-ready, for the operator's Hedl session — repo is read-only here):*
  > Per ADR-012/ADR-034, run a substrate re-evaluation against now-GA native Dynamic Workflows (judge-panel/adversarial-verify, saveable `/commands`) and Agent Teams (`TaskCompleted`/`TeammateIdle` blocking hooks). Downgrade the slash-command routing-table and hooks-integration entries toward culling-candidate unless each row/script proves non-native value this phase, and rewrite the review-panel entry to position Hedl as gate-binding + a curated subagent roster on top of native orchestration rather than a hand-rolled orchestrator.

---

## How native tooling could be adopted (consolidated)
1. **Orchestration:** delegate the review panel to native Dynamic Workflows / Agent Teams; repackage the 8 reviewer prompts as native subagent definitions a workflow calls; keep only `am_i_done.py --check dispatch` as the deterministic floor.
2. **Routing/commands:** delete redundant routing rows; rely on native skill activation + native `/code-review` `/security-review`; reserve Hedl commands for the gate/phase loop.
3. **Hooks:** treat as opt-in convenience over native hooks + pre-commit.
4. **Per-piece substitution:** Danger (PR template), MADR+adr-tools (ADR), commitlint (commits), gh-sub-issue (hierarchy), just/Taskfile (entrypoint), Anthropic dashboards (budget — cut `budget_manager.py`).
5. **Distribution:** offer Hedl as a native plugin for the "whole thing" case; keep the reversible installer only for the graduated-tier and LLM-agnostic gate-only stories.

---

## Independently verified during this review
- 3-way script "duplication" is **symlinks**, single source of truth (md5-identical, mode 120000) — corrects the brief's premise.
- GitHub Actions are **SHA-pinned** with version comments across root + adopter workflows.
- `am_i_done.py` = **1703 lines**, ~20 real `check_*` functions backing every headline claim.
- **Live workflow drift** (root v6.0.2 vs shipped template v5.0.1) and **`requirements-ci.txt` ruff drift** (0.15.14 vs 0.15.15) reproduced.

---

## Appendix A — Exact prompt executed (verbatim, mandatory)

```
An independent adversarial evaluation of https://github.com/neilgfoster/hedl
Clone it somewhere safe without running scripts and then unleash a swarm of agents to assess the following: Quality, security, utility, accuracy, maintanance, supply-chain risks.
Identify competing projects and assess advantages and disadvantages against those projects.
If the project represents tooling/plugin/extension on existing projects, assess utility and redudancy again projects it supports (referencing latest documentation to ensure assessment is up-to-date)

Output:
A 1-page detailed and comprehensive markdown ~/source/hedl/.work/reviews/external-2026-05-30/ which includes the full details of agents findings, plus an overall summary. Each should score findings on a scale of 0 to 10, with the overall summary being the average. Overall summary should include an adopt or reject decision based on each identified tool/project. If overlaps with existing tooling/projects, identify how native tooling could be adopted.

Mandatory:
Include this exact prompt in the report as a reference to what was executed.
Provide an improved prompt to use next time in order to improve the quality of the adversarial review going forwards.
The improved prompt must include this same mandatory section, with the exact same requirements.
```

---

## Appendix B — Improved prompt for next time (mandatory)

```
Conduct an independent, adversarial external review of <REPO_URL> at a pinned ref.

Setup (no side effects on the target):
- Clone read-only to a scratch dir with FULL history (no --depth); never run, install, or import any of its code. Read-only shell inspection only (cat/find/grep/git log/git ls-files -s).
- Record up front: pinned commit SHA + tag, repo age, commit count, author distribution (git shortlog -sne), and whether paths are symlinks vs copies (git ls-files -s) BEFORE asserting any duplication/drift claim.

Swarm (each agent independent, must cite file:line, must NOT echo the repo's own self-assessment — read it, then verify or refute against code):
- Six code dimensions: Quality, Security, Utility, Accuracy (claims-vs-implementation cross-check of every headline feature), Maintenance (bus factor, drift between shipped artifacts and source, CI-enforced invariants), Supply-chain (SHA-pinning, lockfile-vs-manifest drift, remote fetches at install/runtime, what an adopter actually executes).
- Competitive landscape (web-enabled, cite 2026 docs + star counts/activity): direct framework competitors AND focused single-purpose substitutes for each individual capability.
- Native-platform redundancy: for a plugin/extension, map EACH feature to the latest native capability of the platform it extends; state what is now redundant vs genuinely additive.

Scoring & calibration:
- Each agent scores 0-10, calibrated and adversarial (10 exceptional, 5 adequate, 0 unacceptable), with concrete evidence and a "what would raise the score" recommendation.
- Distinguish quality scores from competitive-defensibility scores; report both sub-averages and the overall average, and state explicitly which agents feed the overall average.
- Every claim must be independently reproducible from the cited evidence; flag and CORRECT any factual errors found in the target's own docs.

Output:
A detailed, comprehensive markdown report at <OUTPUT_DIR> with: per-agent findings (summary, strengths, weaknesses with file:line, recommendation, score), an overall summary scoring 0-10 (the average of the agents), an explicit ADOPT or REJECT decision per identified tool/project/capability, and — where Hedl overlaps existing or native tooling — the specific native/focused tool to adopt instead and how. Include a short "independently verified" section listing claims you reproduced first-hand. Add a confidence level and list anything not checked (e.g. runtime behavior, since scripts were not executed).

Mandatory:
Include this exact prompt in the report as a reference to what was executed.
Provide an improved prompt to use next time in order to improve the quality of the adversarial review going forwards.
The improved prompt must include this same mandatory section, with the exact same requirements.
```

---
*Generated by an independent 9-agent adversarial swarm. Scripts were never executed; findings are static-analysis + live-doc based. Runtime behavior of the gate was not observed and should be confirmed separately.*
