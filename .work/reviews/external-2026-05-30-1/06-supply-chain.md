# Supply-chain

Reviewer: independent adversarial external reviewer (adopter perspective).
Target: Hedl @ `796639c6c926ba2535bac3a5474f5d2feb62cb28`, read-only clone at
`/tmp/hedl-review-UKKLTd/hedl`. Dimension: SUPPLY-CHAIN only.

## Summary

Hedl's supply-chain posture is strong on the fundamentals an adopter cares
about most: the installer and every shipped runtime script are stdlib-only and
make **zero network calls** at install or runtime — the only subprocesses are
`git` and `gh` against the adopter's own remote. There is no postinstall fetch,
no `pip install`/`uv add`/`git clone` anywhere in the install path. GitHub
Actions are pinned to full 40-char commit SHAs (no floating tags). Dependabot
covers uv, pip, and github-actions. Dev deps are exact-pinned and the pip
fallback is fully hash-pinned (24/24 packages, all with `--hash`).

Two concrete defects drag the score down:
1. **Lockfile/requirements drift.** `requirements-ci.txt` pins `ruff==0.15.14`
   while `uv.lock` and `pyproject.toml` both pin `ruff==0.15.15`. The
   "generated, in sync with uv.lock" claim in the file header is false. CI
   itself uses `uv sync --frozen` (uv.lock), so this only bites an adopter who
   uses the documented pip fallback — but it directly refutes a stated
   invariant.
2. **Workflow SHA drift between canonical source and shipped `.github/`.** The
   `actions/checkout` pin differs between Hedl's own committed
   `.github/workflows/*.yml` (v6.0.2, `de0fac2…`) and the canonical projected
   source `skill/hedl/workflows/*.yml` (v5.0.1, `93cb6ef…`). Both are valid
   full SHAs, neither is unpinned, but the two disagree — an adopter installs
   v5.0.1 while Hedl's own repo runs v6.0.2.

The largest residual concern is trust-surface, not network: the
lightweight/team tiers project a committed `settings.json` that auto-runs shell
+ Python on SessionStart / every Edit-Write / Stop. This is honestly
self-documented and reversible, but it is real auto-execution an adopter
inherits.

## What an adopter executes (trace, file:line)

Entry point: `skill/hedl/scripts/install.py`, invoked as
`python3 skill/hedl/scripts/install.py --tier {gate|lightweight|team}`
(`install.py:840`).

End-to-end trace of `cmd_install` (`install.py:523-619`):
- `_load_tiers()` reads bundled `skill/hedl/tiers.json` only (`install.py:189-214`).
- `_validate_tier_paths()` enforces containment: every projection *source* must
  stay inside `SKILL_ROOT` and every *target* inside the adopter repo, BEFORE
  any write/delete (`install.py:311-340`, `_resolve_contained` 275-308). This is
  a genuine path-traversal guard (WORK-0020), checked for both the target tier
  and, on downgrade, the current tier (`install.py:551-558`).
- Writes/symlinks files per `tiers.json` via `_project_one`
  (`install.py:371-405`): symlink by default, real copy on Windows or for
  GitHub-parsed files. GitHub-parsed targets (`.github/workflows/*`,
  `dependabot.yml`, `PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS`) are forced to real
  copies so the Actions runner can read them (`install.py:347-368, 581`).
- `init` entries are copy-once directory trees via `shutil.copytree`
  (`install.py:587-596`).
- `_ensure_gitignore_block` appends a delimited hedl-managed `.gitignore` block
  (`install.py:494-520`).
- team tier: only *prints* guidance and probes `shutil.which("gh")` — no install,
  no network (`install.py:601-607`).
- Writes `.hedl-tier` marker JSON (`install.py:614`).

Files an adopter gets (from `tiers.json`): under `.github/` (workflows,
dependabot.yml, PR template), `.claude/` (agents, commands, scripts,
settings.json, startup.sh), `docs/` symlinks, and `.work/` init dirs. Source of
all of it is the bundled `skill/hedl/` tree — nothing downloaded.

Runtime scripts the adopter then executes (via CI or hooks): `am_i_done.py`,
`budget_manager.py`, `check_pr_template.py`, `check_markdown_schema.py`,
`reflect.py`, `release.py`, `contribute.py`, plus the claude-code hook scripts.
Subprocess audit shows every external call is `git …` or `gh …` only
(`am_i_done.py:71,307,316,524,988,997,1066,1117,1186,1250`;
`budget_manager.py:46`; `check_markdown_schema.py:34`; `stop_reminder.py:48,75`).
No urllib/requests/httpx/socket/http.client in any shipped script.

Install is auditable and reversible: `--dry-run` (`install.py:534,987`),
`--status` (`cmd_status` 622-670), `--doctor` (`cmd_doctor` 728-833), downgrade
delta archives rather than deletes init dirs (`_apply_downgrade_delta`
423-462).

## SHA-pinning audit

| workflow:line | action | pinned? | SHA / tag |
|---|---|---|---|
| `.github/workflows/am-i-done.yml:34` | actions/checkout | yes (full SHA) | `de0fac2e4500dabe0009e67214ff5f5447ce83dd` # v6.0.2 |
| `.github/workflows/am-i-done.yml:36` | astral-sh/setup-uv | yes (full SHA) | `08807647e7069bb48b6ef5acd8ec9567f424441b` # v8.1.0 |
| `.github/workflows/codeql.yml:32` | actions/checkout | yes (full SHA) | `de0fac2e4500dabe0009e67214ff5f5447ce83dd` # v6.0.2 |
| `.github/workflows/codeql.yml:35` | github/codeql-action/init | yes (full SHA) | `7211b7c8077ea37d8641b6271f6a365a22a5fbfa` # v4.36.0 |
| `.github/workflows/codeql.yml:40` | github/codeql-action/analyze | yes (full SHA) | `7211b7c8077ea37d8641b6271f6a365a22a5fbfa` # v4.36.0 |
| `skill/hedl/workflows/am-i-done.yml:34` | actions/checkout | yes (full SHA) | `93cb6efe18208431cddfb8368fd83d5badbf9bfd` # v5.0.1 |
| `skill/hedl/workflows/am-i-done.yml:36` | astral-sh/setup-uv | yes (full SHA) | `08807647e7069bb48b6ef5acd8ec9567f424441b` # v8.1.0 |
| `skill/hedl/workflows/codeql.yml:32` | actions/checkout | yes (full SHA) | `93cb6efe18208431cddfb8368fd83d5badbf9bfd` # v5.0.1 |
| `skill/hedl/workflows/codeql.yml:35` | github/codeql-action/init | yes (full SHA) | `7211b7c8077ea37d8641b6271f6a365a22a5fbfa` # v4.36.0 |
| `skill/hedl/workflows/codeql.yml:40` | github/codeql-action/analyze | yes (full SHA) | `7211b7c8077ea37d8641b6271f6a365a22a5fbfa` # v4.36.0 |

**No unpinned actions.** Every `uses:` is a 40-char commit SHA with a version
comment. BUT: `actions/checkout` is pinned to **two different SHAs** between
Hedl's live `.github/` copy (v6.0.2) and the canonical source an adopter
installs (v5.0.1) — see `diff .github/workflows/am-i-done.yml
skill/hedl/workflows/am-i-done.yml` → line 34 only. The shipped source is a
minor version behind Hedl's own repo. setup-uv and codeql pins match across both.

## Lockfile / manifest / requirements consistency (findings, file:line)

- `pyproject.toml:6-12` `[dependency-groups].dev`: `mypy==2.1.0`,
  `pymarkdownlnt==0.9.37`, `pytest==9.0.3`, `ruff==0.15.15`. All exact-pinned. No
  `[project.dependencies]` table → **stdlib-only runtime confirmed** (no
  third-party runtime deps).
- `uv.lock` present (`version = 1`), 24 packages (excluding the `hedl` root).
  Direct dev deps resolve to: mypy 2.1.0, pymarkdownlnt 0.9.37, pytest 9.0.3,
  **ruff 0.15.15** (`uv.lock` parsed package set).
- `requirements-ci.txt` (real path `skill/hedl/requirements-ci.txt`, also
  symlinked at repo root): header claims "GENERATED — Source of truth: uv.lock"
  and "kept in sync with uv.lock". Package set is the same 24, versions match
  uv.lock for 23 of 24 — **except `ruff==0.15.14`** at
  `requirements-ci.txt:322`, vs `ruff==0.15.15` in both uv.lock and
  pyproject.toml. **DRIFT** — the file is stale / was not regenerated after the
  ruff bump. Refutes the "in sync with uv.lock" header claim.
- Hash completeness: all 24 packages in `requirements-ci.txt` carry `--hash`
  lines (verified programmatically: 0 missing). Fully hash-pinned pip fallback.
- Impact scoping: CI consumes uv.lock, not the requirements file —
  `am-i-done.yml:41` runs `uv sync --frozen --only-group dev`. So the drift does
  NOT affect Hedl's own CI; it bites an adopter who follows the documented pip
  fallback `pip install -r requirements-ci.txt` (`requirements-ci.txt:2`), who
  would get the older ruff and potentially a different lint result than the gate
  expects.

## Network-fetch surface at install/runtime (file:line or "none found")

- Install time: **none found.** `install.py` imports only stdlib
  (argparse, datetime, json, os, platform, re, shutil, sys, tomllib, pathlib,
  typing — `install.py:17-27`). No urllib/socket/http/requests. The only
  environment probe is `shutil.which("gh")` (`install.py:602`); the only
  "network-adjacent" output is a printed URL string for the team tier
  (`install.py:607`), never fetched.
- Runtime (shipped scripts): **no direct network.** All subprocesses are `git`
  and `gh` invocations against the adopter's own repo/remote
  (`am_i_done.py:524,988,997,1025,1066,1117,1186`, etc.). `gh` reaches GitHub,
  but that is the adopter's own remote via their own auth, not a Hedl-controlled
  endpoint. `gen_skill_metadata.py:53` runs the local scripts with
  `sys.executable` (dev tooling, not adopter-facing). No urllib/requests/httpx
  in any `.py` under `skill/hedl/`.

## Strengths / Weaknesses

Strengths:
- Zero network fetch at install or runtime; stdlib-only installer and runtime
  confirmed by direct read, not just claimed.
- All GitHub Actions pinned to full commit SHAs with version comments.
- Dependabot present and covers all three relevant ecosystems: uv
  (`dependabot.yml:4`), pip (`:13`), github-actions (`:21`).
- pip fallback fully hash-pinned (24/24).
- Strong install-time containment guard against tiers.json path traversal
  (`install.py:275-340`), validated before any FS mutation.
- Auditable + reversible: `--dry-run`, `--status`, `--doctor`; downgrades
  archive rather than delete.
- `settings.json` carries an explicit security comment demanding PR-review of
  any change to it (`settings.json:2`).

Weaknesses:
- `requirements-ci.txt` ruff version drifts from uv.lock/pyproject
  (0.15.14 vs 0.15.15) and contradicts its own "in sync" header.
- `actions/checkout` SHA differs between live `.github/` (v6.0.2) and the
  shipped canonical source (v5.0.1) — the artifact adopters get is a version
  behind, indicating the projection-vs-source sync is manual and lossy.
- Trust surface: lightweight/team tiers auto-execute shell + Python via
  SessionStart/PostToolUse/Stop hooks (`settings.json:8-39`, `startup.sh`). An
  adopter inherits standing auto-execution on session events. Documented and
  reversible, but real.
- No published checksum/signature for the skill bundle itself; integrity rests
  on the adopter trusting the git source.
- `_hedl_version()` reads `0.1.0` (`pyproject.toml:3`) — pre-1.0, so SHA/version
  guarantees are early-stage.

## What would raise the score

- Regenerate `requirements-ci.txt` from uv.lock (fix ruff to 0.15.15) and add a
  CI check that fails if `uv export` output differs from the committed file
  (close the drift class, not just this instance).
- Add a CI/`gen_skill_metadata`-style check that the projected
  `skill/hedl/workflows/*` are byte-identical to the live `.github/workflows/*`
  (or generate one from the other), so action SHAs cannot diverge.
- Reduce standing auto-execution or make the hook tier opt-in with a clear
  consent prompt at install; document exactly what each hook runs.
- Publish a bundle checksum/signature and have `install.py --doctor` verify it.

## Scores

- Supply-chain (intrinsic) score: **7/10** — Excellent on the load-bearing
  invariants (no network fetch, full SHA-pinning, hash-pinned fallback,
  Dependabot all-ecosystems, traversal-guarded installer). Held back by two
  verified, concrete defects that each refute a stated guarantee: a stale
  `requirements-ci.txt` ruff pin (drift vs uv.lock, contradicting its own "in
  sync" header) and a checkout-action SHA mismatch between the shipped source
  and Hedl's live workflows. Both are sync-discipline failures, not design
  flaws, but they are exactly the things an adopter relying on the "pinned and
  generated" claims would be burned by. Not lower because neither introduces an
  untrusted network path and CI itself uses the correct (uv.lock) versions.
- Competitive-defensibility: **N/A** — supply-chain-only agent.

## Confidence and why

High. Every claim is reproduced first-hand from the pinned commit by reading
source and diffing files (install.py traced line-by-line; uv.lock parsed and
diffed against requirements-ci.txt; both workflow trees grepped for `uses:` and
diffed; all `.py` scripts grepped for network primitives). The only residual
uncertainty is behavioral (I did not execute code per the read-only rule), but
the absence of network imports and the subprocess argv lists are unambiguous in
source.

## Not checked

- Transitive integrity of the *pinned action SHAs themselves* (whether
  `de0fac2…`/`93cb6ef…` actually correspond to the commented tags upstream) — I
  verified pinning form, not that each SHA matches its label on GitHub.
- Runtime behavior of `gh`/`git` calls (read-only; not executed).
- Whether `uv.lock` hashes themselves are correct/complete per-package (checked
  requirements-ci.txt hash presence; did not enumerate every uv.lock hash).
- The full content of every projected file an adopter receives (focused on the
  supply-chain-relevant set: workflows, dependabot, settings/hooks, lock/req).
- Non-supply-chain dimensions (correctness, security of gate logic, etc.).
