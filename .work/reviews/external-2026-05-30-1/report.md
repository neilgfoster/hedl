# Hedl — Independent Adversarial External Review

**Target:** `https://github.com/neilgfoster/hedl.git`
**Pinned ref:** `796639c6c926ba2535bac3a5474f5d2feb62cb28` (origin/main, `git describe` = `v0.1.0-69-g796639c`, only tag `v0.1.0`)
**Review date:** 2026-05-30
**Method:** Read-only full-history clone to a scratch dir. No repo code was run, installed, or imported. Eight independent adversarial agents (six intrinsic-code dimensions + two competitive dimensions), each citing `file:line`, each instructed to verify/refute the repo's own self-assessment (`docs/alternatives.md`) rather than echo it. Findings below were spot-reproduced first-hand by the orchestrator (see "Independently verified").
**Overall confidence:** Medium-high on intrinsic code findings (full read of the five largest scripts, drift/line-number claims reproduced by direct grep); Medium on competitive/native findings (web-sourced star counts and native-feature availability are point-in-time and some native features are beta/flag-gated).

Full baseline: `00-baseline-facts.md`. Full per-agent detail: `01`–`08-*.md` in this directory.

---

## 1. Snapshot (recorded before any claim)

- **Age:** ~2.5 days (first commit 2026-05-28 00:10, pin 2026-05-30 22:41).
- **Commits:** 73. **Tracked files:** 275 (164 `.md`, 55 `.json`, 34 `.py`). **Python LOC:** ~13.7k incl. tests. **Markdown LOC:** ~11.1k.
- **Author distribution (`git shortlog -sne`):** Neil Foster — 71; dependabot — 2. **Bus factor: 1.**
- **Symlinks vs copies:** canonical source is `skill/hedl/`. Repo-root `.claude/` and `.github/scripts/` are real git **symlinks** (mode 120000) into it — drift there is impossible. Drift IS possible in real copies: `skill/hedl/workflows/*.yml` (the projected template adopters install) vs the live `.github/workflows/*.yml`, and generated `requirements-ci.txt` vs `uv.lock`. Both are currently drifted (below).
- **What it is:** a Claude Code "Agent Skill" — an opt-in iteration layer around a deterministic completion gate (`am_i_done.py`), plus an adversarial review roster, phase/work-item tracking, tiered reversible install, and Claude Code hook wiring.

---

## 2. Per-agent findings

Scores are 0–10, calibrated (10 exceptional, 5 adequate, 0 unacceptable). Six agents score **intrinsic quality**; two score **competitive defensibility**. Both sub-averages and the overall are in §3.

### 2.1 Quality — 7/10 (intrinsic) · [`01-quality.md`]
**Summary:** The Python is better than the repo's age suggests — real concurrency/crash safety, genuine path containment, fail-closed error discipline. Held back by one oversized monolith and a live filesystem drift the project's own tooling is built to prevent.
**Strengths:** flock + atomic tempfile/`os.replace`/fsync + corrupt-vs-missing quarantine in `budget_manager.py:104-162`; parents-membership path containment (not string `startswith`) validated before writes in `install.py:275-340`; fail-closed on the security floor (`am_i_done.py:382-418`, `533-543`).
**Weaknesses:** `record_insights.py:68-72` hardcodes 7 reviewer names and silently omits `existential-challenger` — the exact doc/code drift the project elsewhere builds checks to catch; `am_i_done.py` is a 1703-line monolith (~20 checks + two backends + CLI + insights writer).
**Raise the score:** split `am_i_done.py` into a check-registry package; derive the insights reviewer list from the agents directory instead of hardcoding.

### 2.2 Security — 8/10 (intrinsic) · [`02-security.md`]
**Summary:** Strong defensive posture for code adopters execute. No BLOCKING or HIGH issue. No `shell=True`, no `os.system`/`eval`/`exec`/`pickle`/`yaml.load`/`tarfile`, no network egress; all subprocess calls use argv lists; inputs regex-validated before reaching `gh`/`git`; workflows least-privilege, SHA-pinned, no `pull_request_target`; CodeQL covers python+actions.
**Weaknesses (all MEDIUM/LOW):** committed `settings.json:9-37` auto-runs three hook scripts every session and auto-allows `Write(.claude/agents/*)` (`:4`) — the `_comment_security` note (`:2`) is honest but is a convention, not an enforced control, so a future malicious hook commit runs unprompted in the operator's session; the `contribute.py` privacy "scrub" is **path-prefix only** (`contribute.py:89`, `f.startswith("skill/hedl/")`) and never inspects diff *content*, so adopter source/secrets placed in a file under `skill/hedl/` would pass; projected-workflow SHA drift (LOW, see Supply-chain).
**Raise the score:** add content-level scanning (or an explicit "paths-only" disclaimer) to the scrub; document the hook trust model as a required adopter review step.

### 2.3 Utility — 5/10 (intrinsic) · [`03-utility.md`]
**Summary:** The core gate is genuinely useful and well-built, but the **adopter's first install is broken in three independently verified ways**, and a real slice of the pitch is backlog vaporware.
**Weaknesses:** the shipped gate-tier CI workflow runs `uv sync --frozen --only-group dev` (`skill/hedl/workflows/am-i-done.yml:41`) but the gate tier projects neither `uv.lock` nor the `pyproject` dev group — only `requirements-ci.txt` (`tiers.json:12,16`) — breaking the "local pass = green PR" promise (`README.md:39-41`); `check_docs_index` has no adopter guard and always runs (`am_i_done.py:1360-1422,1623`), failing a vanilla lightweight install (project's own WORK-0061); adoption is one self-referential `ADOPTERS.md:8` row against a 2.5-day single-author repo; "invisible mode" (WORK-0013) sits in the "Use Hedl if" list (`README.md:29-31`) and GitHub write-back (WORK-0012) in the team pitch (`README.md:59`) — both unbuilt.
**Verdict:** A real team should **not** adopt Hedl today. Re-evaluate once install is fixed and a second, non-author adopter exists.
**Raise the score:** make a fresh adopter repo pass the gate out of the box; ship or remove the planned-but-absent features from the pitch.

### 2.4 Accuracy (claims vs implementation) — 6.5/10 (intrinsic) · [`04-accuracy.md`]
**Summary:** Headline mechanisms exist and mostly do what's claimed (stdlib-only ✔, mypy `--strict` ✔, Dependabot ✔, ~20 checks vs 9 advertised — under-claimed if anything), but the **self-assessment's own file:line citations are substantially stale**, including on the flagship feature. 24 claims checked: 18 PASS, 5 FAIL, 3 PARTIAL.
**Most significant corrected errors in the repo's docs:**
1. `docs/alternatives.md:365-366` — the entire `--streams` evidence block (Hedl's flagship "uniquely-hedl" feature) is wrong: `check_streams` is at `am_i_done.py:1237` (not 937-981); `--streams` is declared at `:1580` (not 1147); dispatch at `:1646-1647` (not 1208-1209). Lines 937-981 are actually test-candidate code.
2. `docs/alternatives.md:50` — "check list spans `am_i_done.py:1-1300`"; the file is **1703 lines**.
3. `README.md:84` "8 named reviewer agents, a dispatcher" double-counts: 8 files exist in `skill/hedl/agents/`, one of which IS the dispatcher (`review-dispatcher.md`) → 7 reviewers + 1 dispatcher.
**Also:** "runs the same checks locally and in CI" is a **superset**, not identity — `check_template`/`check_dependabot`/`check_pr_threads` are `--pr`-gated (`am_i_done.py:1638-1643`) and skip on the default local run; CI runs `--pr` across a 3.11–3.14 matrix.
**Raise the score:** regenerate/lint the alternatives.md citations against current line numbers (a CI invariant the project could enforce); reword the "same checks" claim to "superset; CI runs the PR-only checks too."

### 2.5 Maintenance — 6/10 (intrinsic) · [`05-maintenance.md`]
**Summary:** Substantive CI and strong written rationale (33 ADRs), but bus factor 1 and a drift-detector that doesn't run where it matters.
**Bus factor:** 1 (71/73 commits one human). Velocity decelerating (36/23/14 per day), zero reverts, churn concentrated in state/doc files — healthy iteration, not thrash.
**CI-enforced invariants:** the gate workflow genuinely runs ruff/mypy/pytest/pymarkdown across Python 3.11–3.14 (not a stub). **Gap:** `install.py cmd_doctor` (`install.py:780`) byte-compares shipped copies against source and reports DRIFT, but `--doctor` is **not** in `am_i_done.py`'s check list and **not** invoked by `am-i-done.yml` — so the project ships a drifted copy of its own gate workflow that its own gate never checks. No `uv export` sync check exists either.
**Drift confirmed (actual values, both already in backlog WORK-0062):** (1) `actions/checkout` — live pins `de0fac2…` v6.0.2, shipped template `skill/hedl/workflows/*` pins `93cb6ef…` v5.0.1 (Dependabot bump touched only the live copy); (2) `requirements-ci.txt:322` pins `ruff==0.15.14` while `pyproject.toml:11`/`uv.lock:119` pin `0.15.15` (generated file not regenerated).
**Raise the score:** add the drift/`uv export` checks to the CI gate; add a second maintainer/reviewer.

### 2.6 Supply-chain — 7/10 (intrinsic) · [`06-supply-chain.md`]
**Summary:** Clean trust surface — no network fetch at install or runtime; everything pinned — undercut by hand-maintained sync between source and projected artifacts that is currently broken.
**What an adopter executes:** `install.py` is stdlib-only and makes **zero** network calls (only probe is `shutil.which("gh")`, `install.py:602`); every subprocess across shipped scripts is `git`/`gh` against the adopter's own remote. No urllib/requests/httpx/pip-install/uv-add/git-clone anywhere.
**SHA-pinning:** all 10 `uses:` are full 40-char SHAs — none unpinned. But `actions/checkout` is pinned to two different SHAs (live v6.0.2 vs shipped v5.0.1 — the artifact adopters install is a version behind).
**Lockfile/manifest:** drift confirmed (`requirements-ci.txt` ruff 0.15.14 vs uv.lock/pyproject 0.15.15), refuting that file's own "in sync with uv.lock" header. CI uses `uv sync --frozen` so CI is unaffected, but an adopter using the documented `pip install -r requirements-ci.txt` fallback gets the wrong toolchain version. All 24 packages otherwise fully hash-pinned; Dependabot covers uv + pip + github-actions.
**Raise the score:** add a CI step asserting `requirements-ci.txt` == `uv export` output and that shipped-vs-live workflow SHAs match (i.e. wire `--doctor` into CI).

### 2.7 Competitive landscape — 3/10 (competitive-defensibility) · [`07-competitive-landscape.md`]
**Summary:** Two genuinely defensible primitives keep it off the floor, but the framework-level pitch is weak: an unreleased, single-operator project in one of 2026's most crowded categories, benchmarked in its own docs only against small/similar rivals while ignoring every category leader.
**Strongest direct competitors (GitHub API, 2026-05-30):** GitHub Spec Kit — 107,179★, pushed same day (GitHub-official category leader); OpenSpec (Fission-AI) — 51,806★; BMAD-METHOD — 48,314★. The repo's own named rival CCPM is 8,158★ and slowing (last push 2026-03-18).
**REJECT-for-a-focused-tool:** budget tier accounting → delete (repo's own culling-candidate); bespoke ADR schema → adopt MADR template (`adr/madr`, ~2.2k★; note `adr-tools`/`log4brains` stale since 2024).
**Competitors the repo's alternatives.md MISSED:** spec-kit, OpenSpec, BMAD, Taskmaster (~27k★), Agent OS (~4.7k★), Amazon Kiro.
**Correction to repo's competitive claims:** `docs/alternatives.md` cites `k1LoW/gh-sub-issue` which 404s — the real tool is `yahsan2/gh-sub-issue` (~116★). The named gate prior art `theshadow27/mcp-cli` has ~2★ (an attribution source, not a competitive threat).
**Raise the score:** benchmark honestly against the category leaders; concentrate the pitch on the gate bundle + `--streams`, drop the whole-framework framing.

### 2.8 Native-platform redundancy — 4/10 (competitive-defensibility) · [`08-native-redundancy.md`]
**Summary:** Of 12 features mapped to current Claude Code native capability: **REDUNDANT 5, ADDITIVE 2, PARTIAL 5.** The feature Hedl sells hardest is the one native most fully subsumes.
**Most defensible (additive):** the deterministic, CI-symmetric, work-item-aware completion gate + `--streams` — no native capability is a non-LLM single-exit-code gate; native Outcomes and agent/prompt hooks are inference-mediated, and agent-teams docs explicitly leave cross-stream file overlap as prose best-practice, not an enforced gate.
**Most redundant:** the adversarial review panel orchestration — native **Agent Teams** ships Hedl's exact use-cases (parallel security/perf/test split; adversarial competing-hypotheses debate), and **Dynamic Workflows** (2026-05-28) + **Outcomes** rubric grading (2026-05-12) cover fan-out and judge-panel. Also redundant: SKILL.md routing table (native skill activation), budget tiers, `.claudeignore`.
**Caveat (lowers confidence to medium):** Dynamic Workflows is research-preview (Max/Team/Enterprise) and agent teams are flag-gated, so for solo/Pro operators the redundancy is "native exists but beta," not GA.
**Raise the score:** drop the routing table and panel orchestration to thin wrappers over native; keep only the deterministic dispatch floor + gate binding.

---

## 3. Overall scoring

| Agent | Dimension type | Score |
|---|---|---|
| Quality | intrinsic | 7.0 |
| Security | intrinsic | 8.0 |
| Utility | intrinsic | 5.0 |
| Accuracy | intrinsic | 6.5 |
| Maintenance | intrinsic | 6.0 |
| Supply-chain | intrinsic | 7.0 |
| Competitive landscape | competitive-defensibility | 3.0 |
| Native-platform redundancy | competitive-defensibility | 4.0 |

- **Intrinsic-quality sub-average (6 agents):** (7+8+5+6.5+6+7)/6 = **6.6/10**
- **Competitive-defensibility sub-average (2 agents):** (3+4)/2 = **3.5/10**
- **Overall average (all 8 agents feed it):** (7+8+5+6.5+6+7+3+4)/8 = **5.8/10**

**Which agents feed the overall:** all eight, weighted equally. The two competitive agents pull the overall down ~0.8 below the intrinsic sub-average; this is the intended adversarial signal — the code is solidly built, but its *defensibility* against native Claude Code and the 2026 framework field is weak.

**One-line characterization:** A well-engineered, candidly-documented, single-author 2.5-day-old skill whose intrinsic code quality (6.6) substantially outruns its competitive defensibility (3.5); genuinely additive only at the gate bundle and `--streams`, with a currently-broken adopter install.

---

## 4. ADOPT / REJECT decisions per capability

"ADOPT" = keep Hedl's version (genuinely additive/defensible). "REJECT" = use the named native or focused tool instead.

| Capability | Decision | Use instead / condition |
|---|---|---|
| Deterministic completion gate (`am_i_done.py`, work-item-aware bundle) | **ADOPT (conditional)** | Genuinely additive vs native + focused tools (pre-commit/just only run checks; none bind work-item + PR-template + threads + dependabot into one no-inference exit code). **Condition:** fix the broken adopter install (WORK-0061) and the `uv sync` vs projected-files mismatch first. Credit mcp-cli for the gate origin (already done). |
| Multi-stream conflict detection (`--streams`) | **ADOPT** | Uniquely additive (pre-merge overlap refusal; native agent-teams leaves this as prose). Caveat: unproven — never exercised by a second operator. |
| Adversarial review panel orchestration | **REJECT** | Native **Agent Teams** + **Dynamic Workflows** + **Outcomes** for orchestration/judging; **CodeRabbit / Greptile / PR-Agent (qodo)** for hosted review. Keep ONLY Hedl's deterministic dispatch floor + gate binding. |
| SKILL.md natural-language routing table | **REJECT** | Native skill activation already routes phrases. Keep the per-command *flows*, drop the routing table. |
| Budget tier accounting (`budget_manager.py`) | **REJECT** | Delete (repo's own culling-candidate; thresholds 12/22/28 are unsourced and the Pro-plan reset is silent). Replace with a single "invocations this session" counter. |
| ADR / decision-log bespoke schema | **REJECT** | Adopt the **MADR** template (`adr/madr`); keep only Hedl's workflow binding (phase-tagging, supersede-via-historian). Do not depend on `adr-tools`/`log4brains` CLIs (stale since 2024). |
| Phase / work-item tracking (`.work/`) | **ADOPT (partial)** | Additive transition-discipline binding, but overlaps native plan mode / TodoWrite / memory for the tracking mechanics. Keep the gated phase boundary; lean on native for the rest. |
| Tiered reversible install (`install.py`) | **ADOPT (partial)** | The reversible/archive-on-downgrade projection model is unusual and additive — but worthless until the projected tier actually produces a passing adopter repo. Fix install first. |
| PR-template enforcement (`check_pr_template.py`) | **ADOPT (borderline)** | Justified only by the local+CI symmetry. If you can't show a class of error a server-only check misses, REJECT for **danger-python** / a GitHub Action. |
| Hooks (SessionStart/PostToolUse/Stop) | **ADOPT (partial)** | Native hooks are the same primitive. Keep the post-edit lint; make undifferentiated hooks opt-in (per the repo's own unmet improvement objective). |
| Self-improvement loop (reflect/contribute) | **REJECT / defer** | Repo's own culling-candidate (zero PRs landed end-to-end). The path-prefix-only scrub also needs content scanning before this is trustworthy. |

**Framework-level decision: REJECT for adoption *today*.** The whole-framework pitch is not defensible against the 2026 field and the host platform, and the adopter install is broken. The **gate bundle + `--streams`, packaged as a focused tool**, is the only part worth conditional ADOPT once the install and drift issues are fixed.

---

## 5. Independently verified (reproduced first-hand by the orchestrator)

Reproduced via read-only `grep`/`sed`/`wc`/`git` on the pinned clone — not taken from agent reports:

1. `am_i_done.py` is **1703 lines** (`wc -l`), refuting `docs/alternatives.md:50` "1-1300".
2. `check_streams` is defined at `am_i_done.py:1237`; the `--streams` arg at `:1580`; lines 937-981 are test-candidate code — refuting `docs/alternatives.md:365-366` (937-981 / 1147).
3. `skill/hedl/agents/` contains **8 files**, one being `review-dispatcher.md` → 7 reviewers + 1 dispatcher.
4. **Ruff drift:** `requirements-ci.txt:322` = `ruff==0.15.14`; `pyproject.toml:11` and `uv.lock:119` = `0.15.15`.
5. **Checkout SHA drift:** `.github/workflows/*` = `de0fac2…` (v6.0.2); `skill/hedl/workflows/*` = `93cb6ef…` (v5.0.1).
6. **stdlib-only confirmed:** no third-party imports in `skill/hedl/scripts/*.py` (only `glob`, `shlex`, `platform`, `__future__`, and other stdlib).
7. **CI runs the real gate:** `am-i-done.yml:41,44` runs `uv sync --frozen --only-group dev` then `am_i_done.py --pr` across a 3.11–3.14 matrix. `check_template`/`check_dependabot`/`check_pr_threads` are `--pr`-gated at `am_i_done.py:1638-1643` (so "same checks local+CI" is a superset).
8. **Budget thresholds:** `budget_manager.py:69-73` → reduced_at 12, minimal_at 22, deferred_at 28 (user-tunable, unsourced).
9. **Insights drift:** `record_insights.py:69-71` lists 7 names including `review-dispatcher` but omits `existential-challenger` — so that agent's insights are never recorded.
10. **Privacy scrub is path-only:** `contribute.py:89` — `violations = [f for f in diff_files if not f.startswith(FRAMEWORK_PREFIX)]`; no content inspection.
11. **Symlinks:** `git ls-files -s` confirms `.claude/*` and `.github/scripts/*` are mode 120000 symlinks into `skill/hedl/`, while `skill/hedl/workflows/*` are real copies (hence the drift in #5 is possible).

---

## 6. Confidence and what was NOT checked

**Confidence:** Medium-high overall. Intrinsic findings rest on full reads of the largest scripts and were spot-reproduced. Competitive star counts and native-feature availability are point-in-time (2026-05-30) and partly beta/flag-gated.

**Not checked (out of scope by the read-only constraint, or unverifiable here):**
- **Runtime behavior** — no script, test, hook, or workflow was executed. We did not confirm `am_i_done.py` actually exits non-zero on a dirty tree, that `install.py --doctor` truly reports the drift, or that the test suite passes. All behavioral claims are from reading source.
- The **CI run history** on GitHub (whether the gate is green on `main`) — only the workflow definitions were read.
- **Dynamic completeness** of CodeQL results (we confirmed config coverage, not findings).
- **Star counts / "last pushed" dates** for some smaller competitors were not all individually re-fetched; treat sub-5k figures as approximate.
- Native Claude Code features behind preview/flags (Dynamic Workflows, Agent Teams) were verified from docs, not exercised, so the "redundant" verdict assumes GA parity that may not yet hold for Pro/solo operators.
- We did not audit every one of the 164 markdown files or all 33 ADRs — sampling focused on claim-bearing docs.

---

## 7. Reference: the exact prompt executed

> Conduct an independent, adversarial external review of <REPO_URL> at a pinned ref.
>
> Setup (no side effects on the target):
> - Clone read-only to a scratch dir with FULL history (no --depth); never run, install, or import any of its code. Read-only shell inspection only (cat/find/grep/git log/git ls-files -s).
> - Record up front: pinned commit SHA + tag, repo age, commit count, author distribution (git shortlog -sne), and whether paths are symlinks vs copies (git ls-files -s) BEFORE asserting any duplication/drift claim.
>
> Swarm (each agent independent, must cite file:line, must NOT echo the repo's own self-assessment — read it, then verify or refute against code):
> - Six code dimensions: Quality, Security, Utility, Accuracy (claims-vs-implementation cross-check of every headline feature), Maintenance (bus factor, drift between shipped artifacts and source, CI-enforced invariants), Supply-chain (SHA-pinning, lockfile-vs-manifest drift, remote fetches at install/runtime, what an adopter actually executes).
> - Competitive landscape (web-enabled, cite 2026 docs + star counts/activity): direct framework competitors AND focused single-purpose substitutes for each individual capability.
> - Native-platform redundancy: for a plugin/extension, map EACH feature to the latest native capability of the platform it extends; state what is now redundant vs genuinely additive.
>
> Scoring & calibration:
> - Each agent scores 0-10, calibrated and adversarial (10 exceptional, 5 adequate, 0 unacceptable), with concrete evidence and a "what would raise the score" recommendation.
> - Distinguish quality scores from competitive-defensibility scores; report both sub-averages and the overall average, and state explicitly which agents feed the overall average.
> - Every claim must be independently reproducible from the cited evidence; flag and CORRECT any factual errors found in the target's own docs.
>
> Output:
> A detailed, comprehensive markdown report at ~/source/hedl/.work/reviews/external-2026-05-30-1/ with: per-agent findings (summary, strengths, weaknesses with file:line, recommendation, score), an overall summary scoring 0-10 (the average of the agents), an explicit ADOPT or REJECT decision per identified tool/project/capability, and — where Hedl overlaps existing or native tooling — the specific native/focused tool to adopt instead and how. Include a short "independently verified" section listing claims you reproduced first-hand. Add a confidence level and list anything not checked (e.g. runtime behavior, since scripts were not executed).
>
> Mandatory:
> Include this exact prompt in the report as a reference to what was executed.
> Provide an improved prompt to use next time in order to improve the quality of the adversarial review going forwards.
> The improved prompt must include this same mandatory section, with the exact same requirements.

*(`<REPO_URL>` resolved to `https://github.com/neilgfoster/hedl.git`, pinned at `796639c6c926ba2535bac3a5474f5d2feb62cb28`.)*

---

## 8. Improved prompt for next time

> Conduct an independent, adversarial external review of <REPO_URL> at a pinned ref.
>
> **Setup (no side effects on the target):**
> - Clone read-only to a scratch dir with FULL history (no `--depth`); never run, install, or import any of its code. Read-only shell inspection only (cat/find/grep/git log/git ls-files -s).
> - Record up front, in a committed `00-baseline-facts.md` BEFORE any agent runs: pinned commit SHA + `git describe` + all tags; repo age (first + pinned commit dates); commit count; author distribution (`git shortlog -sne`) and resulting bus factor; symlinks-vs-copies map (`git ls-files -s`, flag mode 120000) identifying exactly which paths CAN drift (real copies) vs cannot (symlinks); the runtime/dev dependency surface; and a verbatim list of every headline feature claim with its doc citation, to be used as the Accuracy agent's checklist.
>
> **Swarm (each agent independent; every claim MUST cite `file:line` and be reproduced first-hand; each MUST read the repo's own self-assessment and then verify or REFUTE it against code, never echo it):**
> - Six code dimensions: Quality, Security, Utility, Accuracy (claims-vs-implementation cross-check of EVERY headline feature, INCLUDING re-verifying every `file:line` citation in the repo's own docs and CORRECTING stale line numbers/counts), Maintenance (bus factor, drift between shipped/projected artifacts and source — diff the actual values, CI-enforced invariants — trace which checks run in CI vs local-only), Supply-chain (SHA-pinning audit of every `uses:`, lockfile-vs-manifest-vs-generated-requirements drift with exact versions, remote fetches at install/runtime, and a step-by-step trace of what an adopter actually executes).
> - Competitive landscape (web-enabled, cite 2026 docs + GitHub-API star counts + last-push dates): direct framework competitors AND focused single-purpose substitutes for each individual capability. REQUIRED: independently find at least the current category leaders by star count, not only the competitors the repo names; verify every competitor URL resolves (flag 404s) and report each one's stars/last-push so stale tools are not recommended.
> - Native-platform redundancy: for a plugin/extension, map EACH feature to the LATEST native capability of the platform it extends (cite official docs + changelog with dates); classify REDUNDANT / ADDITIVE / PARTIAL; and explicitly note when a "native equivalent" is beta/preview/flag-gated rather than GA, since that changes the verdict for solo/Pro users.
>
> **Cross-checks (orchestrator, after the swarm):**
> - Independently reproduce the 8–12 most load-bearing findings first-hand (do not trust agent reports for anything that changes a score or an ADOPT/REJECT call); list them in an "Independently verified" section.
> - Note where two or more agents corroborate the same defect (raises confidence) and where any two agents conflict (resolve it first-hand before scoring).
> - Distinguish defects the repo already has in its own backlog (cite the WORK-/ADR- id) from defects it has NOT recorded — the latter are the higher-value findings.
>
> **Scoring & calibration:**
> - Each agent scores 0-10, calibrated and adversarial (10 exceptional, 5 adequate, 0 unacceptable; most real code is 4-7), with concrete `file:line` evidence and a "what would raise the score" recommendation.
> - Distinguish intrinsic-quality scores from competitive-defensibility scores; report both sub-averages and the overall average, name exactly which agents feed each, and explain any gap between the sub-averages as a signal in itself.
> - Every claim must be independently reproducible from the cited evidence; flag and CORRECT any factual error found in the target's own docs, with the corrected value.
>
> **Output:**
> A detailed, comprehensive markdown report at <OUTPUT_DIR> with: a pre-claim baseline section; per-agent findings (summary, strengths, weaknesses with `file:line`, recommendation, score); an overall summary scoring 0-10 (the average of the agents, with both sub-averages); an explicit ADOPT or REJECT decision per identified tool/project/capability in a single table; and — where the target overlaps existing or native tooling — the specific native/focused tool to adopt instead and HOW. Include an "Independently verified" section listing claims reproduced first-hand, a confidence level per dimension, and an explicit "Not checked" list (runtime behavior — scripts were not executed; CI run history; preview/flag-gated native features; unsampled files). Keep full per-agent detail in separate numbered files and digest them in the main report.
>
> **Mandatory:**
> Include this exact prompt in the report as a reference to what was executed.
> Provide an improved prompt to use next time in order to improve the quality of the adversarial review going forwards.
> The improved prompt must include this same mandatory section, with the exact same requirements.
