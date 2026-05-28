# Repo-health review — 2026-05-28

**Log:** per-agent JSON outputs in this directory (one file per reviewer)
**Session:** fresh
**Depth:** Full (6 core + 6 composable reviewers)
**Commit:** de35a65ae67e4631f67e7242b9b8bd8a2ce04b1b
**Target:** read-only clone at `/tmp/hedl-repohealth.LD6Nk7/hedl`
**Reviewers run:** security-auditor, determinism-auditor, edge-case-hunter,
historian, scope-auditor, simplicity-enforcer, new-engineer,
contradiction-finder, existential-challenger, evidence-checker,
drift-detector, quality-synthesizer

---

## Verdict

The gate, supply-chain hygiene, and test discipline are reference-quality.
Around that core, the framework has accreted a layer of process and design
artefacts that runs ahead of empirical validation, and the project has not
kept its own state files in step with the ADRs it has been writing about
itself. The strongest single signal is that **Phase 0 is unauthored**
(`.work/phases/phase-0.json` is still the EDIT-ME template) while six ADRs
designing Phase 2 features have been accepted. Most BLOCKING findings are
housekeeping that the framework itself was supposed to prevent.

---

## Dimension Scores

Quality-synthesizer scores (out of 10):

| Dimension              | Score |
|------------------------|-------|
| Code                   | 7     |
| Design                 | 6     |
| Security               | 8     |
| Supply chain           | 9     |
| Claude-Code utility    | 7     |
| Accuracy               | 6     |
| Maintenance            | 7     |
| Utility-vs-complexity  | 5     |

---

## Strengths

- Hash-pinned pip fallback auto-generated from uv.lock; Dependabot for
  uv/pip/actions; full-SHA-pinned Actions; CodeQL covers python and actions.
- Concurrency- and crash-safe state writes via fcntl flock + atomic
  tempfile/os.replace + corrupt-file quarantine (budget_manager.py:116-157).
- Fail-closed defaults with explicit error propagation
  (am_i_done.py:282-297).
- Input validation regexes applied before subprocess use
  (budget_manager.py:275-295).
- 291 deterministic tests; mypy --strict and ruff clean; CI matrix
  Py 3.11-3.14.

---

## Blocking Findings

Eight items, ordered by severity.

1. **.hedl-tier ships with a hardcoded developer absolute path**
   (`/home/nfoster/github/scratch/hedl/skill/hedl`). Any fresh clone is born
   broken. Source: `.hedl-tier`. *new-engineer*

2. **Phase 0 is unauthored**: `.work/phases/phase-0.json` is byte-identical
   to the EDIT-ME template; `.work/context.json:13` still says
   `phase_0_complete: false` despite seven merged Phase-1 PRs. CLAUDE.md
   asserts a configured Setup phase that does not exist.
   *new-engineer, existential-challenger, contradiction-finder,
   quality-synthesizer*

3. **Phase discipline broken**: 8 of 15 backlog items target Phase 2; ADRs
   018-023 design Phase 2 features (multi-operator, recursive workstreams,
   templates, PM-pluggability, invisible mode) while Phase 0 has no defined
   DoD. CLAUDE.md Principle 5 forbids this.
   *existential-challenger, scope-auditor*

4. **Goal displacement**: ~4650 lines of process artefacts (ADRs, SKILL,
   agents, commands, templates, references) vs ~4145 lines of Python +
   tests; one shipped capability (the gate). The product is the process.
   *existential-challenger*

5. **Validation theatre**: 26 reviewer personas exist; `.work/reviews/` and
   `.work/insights/` had only README/.gitkeep before this run. The 'every
   agent output is validated' loop had never closed with a saved finding.
   *existential-challenger*

6. **install.py command-injection / RCE vectors** (3 findings):
   - `startup.sh:6-8` interpolates project name into a printf format string
     without sanitisation.
   - `install.py:258-273` applies `tiers.json` source/target paths without
     verifying containment in SKILL_ROOT / repo.
   - `am_i_done.py:169-203` runs arbitrary `[verify] cmd` strings from
     `hedl.toml` with no allow-list; any PR adding a `[verify.x] cmd`
     becomes RCE on the next gate run.
   *security-auditor*

7. **install.py unguarded crashes / recursion**:
   - `cmd_status` / `cmd_doctor` call `json.loads(.hedl-tier)` with no
     try/except (install.py:303, ~397).
   - `_flatten_projections` / `_flatten_inits` recurse via `includes` with
     no cycle detection (install.py:99-105). *edge-case-hunter*

8. **release.py version parse**: `next_version()` raises
   IndexError/ValueError on non-canonical `--current-version`, producing
   malformed JSON callers cannot parse (release.py:94-95, 136).
   *edge-case-hunter*

---

## Significant Findings

### ADR-vs-implementation drift

| ADR | Status | Reality | Tracked? |
|-----|--------|---------|----------|
| ADR-011 (disqualifiers + alternatives.md) | Accepted | README has no disqualifier section; `docs/alternatives.md` did not exist | No (now PR #10) |
| ADR-017 (existential-challenger mandatory for ADR writes) | Accepted | Not promoted to named agent; dispatch-rules.json maps `^\.work/decisions/` to historian only | WORK-0005 |
| ADR-018 (Principle 4 = one per operator) | Accepted | CLAUDE.md:35 unchanged | WORK-0009 |
| ADR-019 (recursive workstream schema) | Accepted | `.work/work.json` still flat | WORK-0010 |
| ADR-022 (state_backend lives in hedl.toml) | Accepted | Code, tests, installer, docs all use `.work/context.json` | WORK-0024 |

*historian, evidence-checker, contradiction-finder*

### Duplicated / divergent state

- `.work/config/` and `skill/hedl/work-state/config/` are byte-identical
  committed twins; no doc explains the relationship. Editing one silently
  drifts. *simplicity-enforcer, new-engineer*
- The same shape exists for `phases/`, `session.json`, `work.json`.
  *simplicity-enforcer*

### Tier-description mismatch

`tiers.json:46` describes team tier as 'Lightweight + Claude Code hooks';
README/tiers.md/team-tier.md describe it as 'Lightweight + GitHub Issues
backend + parallel worktrees with gate-enforced merge'. `install.py
--tier team` only projects six Claude Code files. *contradiction-finder*

### Workstream double-definition

`standards.md` and `iterate.md` define workstream as one of four fixed
categories (WS-PLAN/WS-REQ/WS-TECH/WS-ARCH); ADR-019 redefines workstream
as a recursive container subsuming phase and work-item. Both meanings are
live in shipped files. *contradiction-finder*

### Count drift

- review-library.md says 'Six core agents' (misses determinism-auditor);
  /repo-health spec says 'all 6 core agents' (so this Full run silently
  under-panels). *drift-detector*
- `tiers.md:78` says 'all 15 command behaviors'; commands.md has 18.
  *evidence-checker, contradiction-finder*
- ADR-016 references 'full panel of 8'; only 7 named agents exist.
  *evidence-checker*

### Security (lower severity)

- GitHub Actions: matrix.python-version inlined into `run:`
  (am-i-done.yml:41,44) — pattern flagged by GitHub guidance; safe today,
  unsafe under any future change. *security-auditor*
- No hook execution audit log — contradicts CLAUDE.md's identity→
  permission→blast→validation→execution principle. *security-auditor*
- `record_insights.py` derives reviewer from model-controlled tool
  description (prompt-injection surface). *security-auditor*
- `am_i_done.py:950-952` interpolates branch names into `git diff` without
  validating against the existing BRANCH_PATTERN regex; an arg-injection
  vector via stream branches. *security-auditor, edge-case-hunter*

---

## Minor Findings

### Edge cases (other notable)

- `budget_manager.py record` accepts `n<=0`. *edge-case-hunter*
- `install.py` tier downgrade is non-atomic; mid-loop failure leaves marker
  pointing to old tier with files already gone. *edge-case-hunter*
- `_schema_ver_int` silently maps non-integer schema_version to 0,
  replaying migrations. *edge-case-hunter*
- `tgt_dir.exists()` accepts a regular file at the target path as
  'directory exists, skip'. *edge-case-hunter*
- Bare `except: pass` in `_append_gate_insight` (am_i_done.py:1261) hides
  disk-full / read-only / corrupt log. *edge-case-hunter*
- Unsynced JSONL appends to `events.jsonl` from two writers — no flock.
  *edge-case-hunter*
- Fork-PR token scope makes `dependabot` check skip path return PASS,
  hiding that it never ran. *edge-case-hunter*

### Determinism

The first principle is 'Deterministic over inference' but several flows
use LLM inference where a function would suffice:

- `review-dispatcher` (Sonnet, hot path) for choices dispatch-rules.json
  patterns could already cover.
- `phase-status` health (ON TRACK / AT RISK / BLOCKED) — explicit
  thresholds.
- `agent-evaluator`'s own determinism screen.
- prd-template fill (string substitution).
- ADR slug generation.
- evidence-checker (file existence / grep).

*determinism-auditor*

### Onboarding (new-engineer)

- Scripts live in two paths (`.github/scripts/` symlinks →
  `skill/hedl/scripts/`) with no single onboarding sentence explaining
  which to invoke.
- `hedl.toml [verify]` schema is undocumented (recognised keys, defaults,
  unknown-key behaviour).
- `budget_manager.py` uses 'invocations' without defining the unit, who
  records, or how it relates to actual Claude usage limits.
- `--agents` / `--optional` value format (comma/repeated/JSON) is not
  documented.
- First gate run from `main` fails by design; no doc warns.
- README/getting-started omit `release.py`, `reflect.py`, `contribute.py`.
- CLAUDE.md calls commands.md the 'Full behavior catalog' but it omits
  start-session / iterate / adversarial-review / phase-complete.

### Simplicity / overlap

- `review-dispatcher.md` lists determinism-auditor under 'reference
  library agents' but no prompt for it exists in `review-library.md`.
  *contradiction-finder*
- `review-library.md:182` instructs detectors to inspect a
  `MANDATORY_AGENTS` constant that no longer exists. `am_i_done.py:19`
  --help still mentions it. *drift-detector*
- `review-library.md` ambiguity-hunter / contradiction-finder /
  assumption-challenger overlap with core scope-auditor / historian.
  *simplicity-enforcer*
- `budget_manager.py` exposes derived thresholds
  (reduced_at/minimal_at/deferred_at) as if independent.
  *simplicity-enforcer*
- `.gitignore` opens with Obsidian + committed `.obsidian/` directory;
  not mentioned in docs. *new-engineer*

---

## Next Actions

The /repo-health flow does not prescribe action — these are suggestions
for backlog grooming.

1. **Fix the dogfood**: author phase-0.json with real DoD; regenerate or
   rewrite `.hedl-tier` so a fresh clone is not pre-broken; resolve
   `.work/` vs `skill/hedl/work-state/` duplication. Without this the
   framework cannot make any claim about discipline.
2. **Close the ADR-implementation gap before adding more ADRs**: ADR-011
   (disqualifiers + alternatives.md), ADR-017 dispatch rule, ADR-018
   wording, ADR-022 state_backend file. WORK-0005, WORK-0009 are already
   in the backlog; ADR-011 / ADR-022 are not.
3. **Promote the security findings to fixes**: the three RCE-class
   findings (startup.sh printf, install.py path containment, hedl.toml
   `cmd` allow-list) are small fixes and high-leverage.
4. **Inventory drift**: bump 'Six core agents' to seven everywhere; update
   the /repo-health spec from 6 to 7 so Full runs do not under-panel;
   reconcile the 15/18 command count.
5. **Defer Phase 2 design work** until Phase 0 has a real DoD and Phase 1
   has a credible plan.
6. **Pick the deterministic wins**: phase health, ADR slug generation,
   prd-template substitution — small scripts that match the first
   principle.

Counts: 8 BLOCKING, ~30 SIGNIFICANT, ~25 MINOR across all reviewers. There
is overlap between agents; the report above merges the strongest evidence
rather than listing every finding twice.
