# Utility

## Summary

Hedl's realistic user is a solo developer or very small team running Claude Code who
wants AI-generated work held to a hard, scriptable "done" boundary rather than the
model's self-assessment. For that user the core artifact — `am_i_done.py` — is
genuinely useful: it is a real, non-trivial, well-defended deterministic gate that
checks things teams forget (clean tree, branch naming, PR-template completeness, stale
work-item IDs, unresolved review threads, Dependabot alerts, plus the project's own
lint/types/tests) and returns one exit code with no LLM inference. That is the
defensible value, and it is mostly real today.

The friction, however, is high and the "two-minute drop-in" pitch is contradicted by
the repo's own tracker. The gate tier ships a CI workflow that cannot run in a fresh
adopter repo (it needs a uv/`pyproject.toml` setup the tier does not project), the
docs-index gate check FAILs on a vanilla lightweight install (the project's own
WORK-0061), the install path SKILL.md routes to does not exist in consumer repos
(WORK-0001), and getting-started tells adopters to run a test suite that no tier
projects. Adoption is one self-referential row in ADOPTERS.md against a 2.5-day,
single-author repo, and a meaningful slice of the team-tier pitch (write-back, invisible
mode, multi-operator, pluggable backends) is explicitly backlog. The honest "Don't use
Hedl if" list is a real strength and largely accurate, but the headline onboarding
promise does not survive first contact with an adopter repo.

## Strengths (file:line)

- The gate is substantive, not ceremony. The check list is real and each check catches
  a class of error: working tree / branch (`am_i_done.py:306-360`), stale work-item IDs
  cross-checked against the live backend (`am_i_done.py:774-817`), unresolved PR review
  threads via GraphQL that fail *closed* on error (`am_i_done.py:1049-1100`), Dependabot
  alerts (`am_i_done.py:982-1038`), and the consumer's own lint/types/tests
  (`am_i_done.py:902-979`). None of this requires model inference; the script decides.
- The stack-agnostic `hedl.toml [verify]` path is a genuine, careful design: declarative
  checks, `shell=False`, allow-listed bare executables, denylisted interpreters, and
  cwd-containment (`am_i_done.py:226-303`, `_verify_allowlist` 199-223). It honestly
  documents that the allow-list is defense-in-depth, not an RCE control
  (`am_i_done.py:169-179`). This makes the "not a Python-only gate" claim mostly true.
- The installer is the most polished piece: dry-run, status, doctor, migrate,
  reversible archive-on-downgrade, path-containment validation before any write
  (`install.py:311-340`, `523-619`), and a correct insight that GitHub-parsed files
  (`workflows/`, `PULL_REQUEST_TEMPLATE.md`, `dependabot.yml`) must be real copies not
  symlinks (`install.py:347-368`). The "tiered + reversible" claim holds.
- The "Don't use Hedl if" list is unusually honest for a project pitch
  (`README.md:9-19`): it tells solo/throwaway/zero-Python users not to adopt, and the
  alternatives doc concedes the gate itself is prior art from mcp-cli
  (`README.md:33-52`, `docs/alternatives.md:47-82`). This is a real credibility asset.

## Weaknesses (file:line)

- **The shipped CI gate cannot run in a fresh adopter repo, breaking the central
  CI-symmetry promise.** The gate tier projects `workflows/am-i-done.yml`
  (`tiers.json:12`), whose dependency step is `uv sync --frozen --only-group dev`
  (`workflows/am-i-done.yml:41`) — requiring a committed `uv.lock` and a
  `pyproject.toml` `dev` dependency group. The gate tier projects neither; it ships only
  `requirements-ci.txt` (`tiers.json:16`). An adopter who does the "two-minute drop-in"
  gets a CI workflow that fails at install-deps. The README's headline — "a local pass
  means a green PR" (`README.md:39-41`) — does not hold out of the box.
- **The gate FAILs on a vanilla lightweight install — admitted by the project itself.**
  `check_docs_index` has no adopter/framework guard and always runs
  (`am_i_done.py:1360-1422`, dispatched unconditionally at `am_i_done.py:1623-1624`),
  unlike `check_state_template_sync` which returns None in adopter layout
  (`am_i_done.py:676-678`). The lightweight tier projects `docs/spec/*-template.md`
  (`tiers.json:36-38`) with no README to link them, so the first `am_i_done.py` run in a
  fresh adopter repo fails. This is WORK-0061, still in backlog (`.work/work.json`).
- **The install command SKILL.md routes to does not exist in a consumer repo.** No tier
  projects `install.py` (absent from all `tiers.json` projection lists), yet SKILL.md
  routes install operations to `python3 skill/hedl/scripts/install.py`. WORK-0001
  (backlog) documents that an agent following SKILL.md verbatim in an installed repo
  hits file-not-found for every install operation.
- **getting-started's verification step is not reproducible by an adopter.**
  `docs/getting-started.md:88` instructs `pytest skill/hedl/tests/ -q` to "verify the
  installation", but no tier projects `skill/hedl/tests/` into an adopter repo (absent
  from `tiers.json`). The verification a new adopter is told to run only works inside the
  framework repo itself.
- **Onboarding cost is materially understated.** Beyond `python3`, lightweight requires
  hand-editing three JSON files (`getting-started.md:53-61`), buy-in to a `.work/` filing
  discipline, and `gh` + auth for the PR-aware checks. The "~2 min / ~5 min" table
  (`getting-started.md:30-36`) does not account for the broken-first-run remediation
  above.
- **Adoption is aspirational.** ADOPTERS.md has exactly one row — Hedl itself, "First
  adopter; self-hosted" (`ADOPTERS.md:8`). Against a repo whose first commit is
  2026-05-28 and HEAD is 2026-05-30 (2.5 days), 73 commits, a single human author
  (verified via `git log`). "The dogfood is the proof" (`ADOPTERS.md:10-12`) is the only
  evidence of use, and even the dogfood repo carries the broken-adopter bugs above
  because they only manifest in *consumer* layout.
- **A real slice of the pitch is vaporware, and the README leans on it.** Invisible mode
  is in "Use Hedl if" (`README.md:29-31`) and "What Hedl doesn't do" (`README.md:69-77`)
  but is unbuilt (WORK-0013, backlog). GitHub Issues write-back is named in the team-tier
  pitch (`README.md:59`, `tiers.json:48`) but is WORK-0012 (backlog); today the backend
  is read-only. Multi-operator coordination and pluggable backends are likewise backlog
  (WORK-0006/0012/0059). The alternatives doc's own Phase-1 verdicts demote the
  self-improvement loop and multi-operator coordination to culling-candidates with zero
  supporting evidence (`docs/alternatives.md:451-462`).
- **164 markdown files for a 2.5-day tool is bloat-leaning.** 31 ADRs in
  `.work/decisions/` and a large `docs/` tree document a process whose only practitioner
  is the author. A new adopter does not need 31 ADRs to drop in a gate; the volume is
  process-archaeology, not adopter onboarding material. The doc-facts and docs-index
  gate checks (`am_i_done.py:1467-1555`, `1360-1422`) are effort spent policing this
  volume — useful for the framework repo, pure overhead (and a failure source) for
  adopters.

## What would raise the score

- Fix the first-run experience so a fresh `--tier gate` and `--tier lightweight` install
  passes `am_i_done.py` and a green CI run with no manual remediation (close WORK-0061,
  WORK-0001; ship a CI workflow whose deps the tier actually projects, or a
  pip/`requirements-ci.txt` path in the workflow).
- Project `install.py` (or ship a `hedl` CLI per WORK-0045) so SKILL.md's install routing
  resolves in consumer repos.
- Make getting-started's verification reproducible in an adopter repo (don't point at
  `skill/hedl/tests/`).
- Move invisible mode / write-back out of the "Use Hedl if" framing until built, or label
  them inline as not-yet-available everywhere they appear, not only in one caveat.
- Earn a second, independent ADOPTERS.md row. One non-author adopter surviving the
  install would do more for utility than any further doc.

## Scores

- Utility (intrinsic) score: 5/10 — The core gate is real, well-engineered, and solves a
  problem AI-assisted teams genuinely have; the installer and `hedl.toml` design are
  strong. But utility is measured at the adopter, and the adopter's first run is broken in
  three independently-verified ways (CI deps, docs-index FAIL, missing install path), the
  promised onboarding cost is understated, adoption is a single self-referential row, and
  a visible fraction of the value proposition is backlog. For the author it is a 7-8; for
  a real external adopter today it is closer to a 4. 5/10 is the honest blend.
- Competitive-defensibility: N/A — utility-only review.

## Confidence and why

High on the broken-first-run findings: each is reproduced first-hand from the shipped
`tiers.json`, `workflows/am-i-done.yml`, `am_i_done.py` dispatch, and corroborated by the
project's own backlog items (WORK-0001, WORK-0061). High on the gate's intrinsic value —
the check code was read end-to-end. Medium on the exact friction of the daily loop and on
the documentation-volume judgment, since I did not execute the install (read-only rules)
and did not read all 164 markdown files.

## Not checked

- Did not run `install.py`, `am_i_done.py`, or the CI workflow (read-only constraint), so
  the failures are inferred from source + manifest, not observed at runtime.
- Did not read all 164 markdown files; sampled README, getting-started, alternatives,
  ADOPTERS, tiers.json, and the two core scripts.
- Did not assess the adversarial-review agents' actual finding quality (covered by other
  dimensions); utility of the review panel is taken from `docs/alternatives.md:436-441`
  self-report, not independently verified.
- Did not evaluate Windows `--copy` mode behavior or the GitHub Issues backend against a
  live repo.
