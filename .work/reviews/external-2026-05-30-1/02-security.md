# Security

## Summary

Hedl is an Agent Skill that an adopter wires into their own Claude Code session
and CI. The threat surface that matters is: three auto-running hooks
(SessionStart `startup.sh`, PostToolUse `posttooluse_lint.py`, Stop
`stop_reminder.py`), the installer (`install.py`), the self-improvement scrub
(`contribute.py` / `reflect.py`), the gate (`am_i_done.py`) which shells out to
`git`/`gh`, and the projected GitHub workflows.

The codebase is unusually security-conscious for its size. There is **no
`shell=True`, no `os.system`, no `eval`/`exec`/`pickle`/`yaml.load`, no
`tarfile`, and no network egress anywhere** in the scripts or hooks
(`grep` across `skill/hedl/scripts/` and `skill/hedl/integrations/`). Every
subprocess call uses argv-list form. Untrusted-looking inputs (branch names, PR
titles, work-item IDs, agent names, repo slugs, file paths) are validated
against strict regexes before reaching `gh`/`git`, and the `[verify]` command
surface in `am_i_done.py` is gated by an allow-list + interpreter denylist +
shell-metachar rejection. The hooks fail closed on a missing
`CLAUDE_PROJECT_DIR` and bound every path to the project root. `install.py`
enforces containment on both projection sources (within `SKILL_ROOT`) and
targets (within the repo) before any write.

I found **no BLOCKING issue**. The real residual risks are: (1) the
`_comment_security` note flags a genuine, only partially-mitigated trust
expansion (the committed `settings.json` auto-runs shell and auto-allows
`Write(.claude/agents/*)`); (2) the `contribute.py` "privacy scrub" is a
**path-prefix check only** and does not — and cannot — guarantee the
*contents* of `skill/hedl/` files are free of copied adopter source/secrets,
which is a weaker guarantee than the docs imply; (3) the projected workflows
have drifted from their canonical source on the `actions/checkout` pin.

## Strengths (file:line)

- **No shell, no dynamic eval, no network.** Verified by grep across
  `skill/hedl/scripts/` and `skill/hedl/integrations/`: zero `shell=True`,
  `os.system`, `eval(`, `exec(`, `pickle`, `yaml.load`, `tarfile`, or
  `urllib/requests/socket`. All `subprocess.run`/`check_output` calls pass an
  argv list (e.g. `am_i_done.py:142`, `stop_reminder.py:47,73`,
  `posttooluse_lint.py:89`, `budget_manager.py:46`, `gen_skill_metadata.py:53`).

- **PostToolUse hook is path-bounded and flag-injection-safe.**
  `posttooluse_lint.py:63-76` resolves the edited file to an absolute path and
  requires `target.relative_to(project_root)`; line 90 runs ruff with `--` so a
  path beginning with `-` cannot inject a ruff flag; only `.py` files that exist
  are linted; always exits 0.

- **Stop hook validates the branch name before passing it to `gh`.**
  `stop_reminder.py:35` `_BRANCH_RE` plus `--head=<branch>` (line 75) means a
  branch starting with `-` cannot become a `gh` flag; missing/unauth/rate-limited
  `gh` is surfaced as a distinct warning, not silently swallowed
  (`stop_reminder.py:91-97`). Read-only `gh pr list` only; 5s timeout.

- **Hooks fail closed on missing project dir.** Both
  `posttooluse_lint.py:59-62` and `stop_reminder.py:110-115` refuse to fall back
  to cwd when `CLAUDE_PROJECT_DIR` is unset.

- **`install.py` containment is real and pre-write.**
  `_resolve_contained` (`install.py:275-308`) is a parents-membership prefix
  check on the resolved path (not a string `startswith`), with a deliberate,
  documented `follow` distinction for sources vs. symlink targets.
  `_validate_tier_paths` (`install.py:311-340`) runs before any write/delete,
  for both the target tier and (on downgrade) the current tier
  (`cmd_install:551-558`). No remote fetch; `SKILL_ROOT` is derived from the
  script's own location, never from input.

- **`.hedl-tier` marker records only the tier**, deliberately not an absolute
  skill path, to avoid leaking the installing machine's layout
  (`install.py:609-614`).

- **TOML-injection defense on state-backend migration.**
  `_validate_backend_name` (`install.py:110-119`) rejects anything but a bounded
  lowercase identifier before the value is written verbatim into `hedl.toml`,
  closing a crafted-`context.json` → injected `[verify]` table vector.

- **Gate `[verify]` command surface is layered.** `am_i_done.py:180-303`:
  built-in allow-list (`pytest/mypy/ruff/npm/pnpm/make`), an interpreter/
  forwarder denylist (`sh,bash,python,node,env,xargs,find,eval,exec,…`,
  lines 188-195) enforced even if a future caller bypasses
  `_verify_allowlist`, shell-metachar rejection (`_SHELL_METACHARS`, line 196),
  bare-name-only executables, and a `cwd` containment check (lines 244-249).
  The module comment (lines 169-179) is honest that this is defense-in-depth,
  not a complete RCE control for untrusted PRs — that control is GitHub fork
  approval. Correct framing.

- **PR-template / Dependabot exemption keys off GitHub-verified identity**, not
  spoofable PR body/branch: `is_bot is True` AND the Dependabot app login
  (`am_i_done.py:1112,1138`). The repo slug from `gh` is regex-validated before
  interpolation into a `gh api` path (`am_i_done.py:994`).

- **`check_template` passes the untrusted PR body via an env var, not argv**,
  and strips NULs (`am_i_done.py:1145-1152`); `check_pr_template.py:25` reads
  `PR_BODY` from the environment. No interpolation of body text into a shell.

- **Workflows: least privilege, pinned by SHA, no `pull_request_target`.**
  `am-i-done.yml` uses `permissions: contents/pull-requests/security-events:
  read` only; CodeQL uses `security-events: write` (required to upload).
  Actions are pinned to full commit SHAs. `PR_NUMBER` is assigned to an `env`
  var with an explicit comment that this avoids `${{ }}` expression injection in
  `run:` steps (`am-i-done.yml:29-32,44`). `GH_TOKEN` is the default
  `github.token`; no long-lived secret is referenced.

- **`budget_manager.py` validates every external token** before it lands in
  state: `_BRANCH_RE`, `_AGENT_RE`, `_PRINTABLE_RE` (lines 280-300), atomic
  writes via tempfile+`os.replace`, `flock`-guarded read-modify-write.

- **CodeQL actually covers the code.** `languages: [python, actions]` — Python
  is the entire script surface and `actions` covers the workflows. Appropriate.

## Weaknesses / risks

- **MEDIUM — Committed `settings.json` is an auto-trust expansion that is only
  partly mitigated.** `skill/hedl/integrations/claude-code/settings.json:9-37`
  wires SessionStart→`bash startup.sh`, PostToolUse→`posttooluse_lint.py`, and
  Stop→`stop_reminder.py` to run automatically every session, and line 4
  auto-allows `Write(.claude/agents/*)`. The `_comment_security` note (line 2)
  flags this honestly and asks reviewers to consciously approve changes — that
  is the right *process*, but it is a convention, not an enforced control. An
  adopter who installs Hedl is trusting whatever those three scripts contain at
  HEAD; a future malicious or compromised commit to any of them executes in the
  operator's session with no further prompt. The flagged risk is **real and
  correctly described**; mitigation is partial (the scripts are currently
  benign and well-bounded, and `Write(.claude/agents/*)` is a narrow glob, but
  nothing structurally prevents a later expansion). Net: the note is accurate,
  not overstated — verified, not refuted.

- **MEDIUM — `contribute.py` "privacy scrub" guarantees paths, not contents.**
  `contribute.py:87-90` `scrub_diff` rejects any changed file whose path does
  not start with `skill/hedl/`. That is the *entire* check. Docs describe this
  as a "privacy fail-closed scrub" that blocks "consumer source code … PII"
  (`docs/self-improvement.md:60-72`, `references/commands.md:294-298`). The gap:
  a contribution that *creates or edits a file under* `skill/hedl/` whose
  **body** contains copied adopter source, secrets, or PII passes the scrub
  cleanly — the scrub never inspects diff content. For self-improvement PRs the
  upstream diff content legitimately ships, so this is an inherent limitation,
  but the docs overstate the guarantee: the scrub prevents *out-of-tree* leakage
  (the common accident), not *in-tree* content leakage. The separate insights
  privacy claim (`references/commands.md:284`: "only Hedl metadata … no source,
  no paths, no PII") **does** hold — `_append_gate_insight`
  (`am_i_done.py:1665-1699`) writes only `tier`, check names, and pass/fail, and
  `reflect.py:56-64` aggregates only an allow-listed field set. So: refine the
  contribute-scrub wording, the insights claim is accurate.

- **LOW — Projected workflows have drifted from their canonical source.**
  `diff skill/hedl/workflows/am-i-done.yml .github/workflows/am-i-done.yml`
  shows the `actions/checkout` pin differs: source is
  `…@93cb6efe…  # v5.0.1`, the live `.github/` copy is
  `…@de0fac2e…  # v6.0.2` (same for `codeql.yml`). Since `install.py` copies
  source→target for `.github/workflows/*` (`_github_parses_directly`,
  `install.py:358-368`), `install.py --doctor` would report these as
  `DRIFT (copy differs from source)` (`install.py:780-782`). Not an injection
  vector (both are SHA-pinned to legitimate `actions/checkout` releases), but it
  means an adopter who re-installs would silently *downgrade* checkout to v5.0.1,
  and the source-of-truth invariant the project relies on is currently violated
  in its own repo.

- **LOW — Documented scrub recipe is whitespace-fragile and dash-fragile.**
  `references/commands.md:296` and `docs/self-improvement.md:65` pipe
  `git diff --name-only | xargs … scrub --diff-files`. `xargs` splits on
  whitespace, so a tracked path containing a space is split into two bogus
  "files"; and a path beginning with `-` would be consumed by argparse as an
  option to `scrub` rather than a value. Both only affect the *operator's own*
  contribution flow (not adopter execution) and the failure mode is a spurious
  scrub result, not code execution — hence LOW. A `-z` / `--null` +
  `xargs -0` recipe would harden it.

- **LOW — `am_i_done.py` trusts `.work/config/dispatch-rules.json` regexes via
  `re.search`** (`am_i_done.py:415,1518`). The patterns come from a
  repo-committed config, and `re.search` on attacker-controlled *patterns* (not
  just input) permits catastrophic-backtracking ReDoS. In practice the file is
  trusted repo content under branch protection, and the gate has per-check
  timeouts, so impact is bounded — noting it only as defense-in-depth.

## What would raise the score

- Add a content-aware layer to the contribute scrub (e.g. entropy / secret
  pattern scan over the diff body, even if best-effort) **or** soften the docs
  to state precisely what the scrub does and does not guarantee (path-only).
- Re-sync `skill/hedl/workflows/*.yml` with the live `.github/workflows/*.yml`
  checkout pin so the project's own source-of-truth invariant holds; add a gate
  check that the two are byte-identical (mirrors the existing `state-sync`
  check).
- Convert the `_comment_security` convention into an enforced control: e.g. a
  CI check that fails any PR touching `integrations/claude-code/settings.json`
  or the hook scripts unless a `trust-expansion-reviewed` label/section is
  present.
- Harden the documented scrub recipe to `git diff -z … | xargs -0`.

## Scores

- **Security (intrinsic) score: 8/10** — This is genuinely strong, defensive
  engineering: no shell, no eval, no network, consistent input validation,
  pre-write path containment, least-privilege SHA-pinned workflows, no
  `pull_request_target`, and an honest, accurate self-assessment of the residual
  hook-trust risk. It falls short of 9-10 because (a) the headline
  "privacy scrub" guarantee is weaker than the docs claim (path-only, no content
  inspection), and (b) the project's own source-of-truth invariant is currently
  violated by the workflow-pin drift, which is exactly the class of silent
  regression the gate is meant to catch. No BLOCKING or HIGH issue found.
- **Competitive-defensibility: N/A** — security-only review dimension.

## Confidence and why

High confidence on the code-level claims: I read every script and hook in full
(`install.py`, `am_i_done.py`, `contribute.py`, `reflect.py`, `release.py`,
`budget_manager.py`, `check_pr_template.py`, `check_markdown_schema.py`,
`gen_skill_metadata.py`, all three hooks, both workflows, `settings.json`) and
grepped the whole script/integration tree for the dangerous-primitive set, so
the "no shell / no eval / no network" assertion is first-hand and exhaustive for
the static surface. Medium confidence on the scrub-content claim's operational
impact (it depends on how the operator drives `/contribute`, which I did not
execute). The workflow-drift finding was reproduced directly with `diff`.

## Not checked (runtime behavior not executed; anything skipped)

- Per the read-only rule, **nothing was executed** — no install, no gate run, no
  hook invocation. Runtime behavior (actual ruff/gh/git execution, race
  conditions under concurrent `budget_manager` writers, real symlink resolution
  on the installing host) is inferred from code, not observed.
- I did not audit the full `.work/reviews/**` historical artifacts, the agent
  prompt markdown (`skill/hedl/agents/*.md`) for prompt-injection framing, or
  `tiers.json` projection entries individually beyond confirming the containment
  guard wraps them.
- I did not verify the upstream `actions/checkout` SHAs against GitHub's release
  tags (network disallowed); I took the in-repo `# vX.Y.Z` comments at face
  value and only compared source-vs-projection internally.
- Dependency supply chain (`uv.lock`, `requirements-ci.txt`) was not analyzed
  for known-vulnerable pins.
