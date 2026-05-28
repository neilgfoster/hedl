# WORK-0029 — How PR #8 and PR #10 merged green despite producing a red main

**Date:** 2026-05-28
**Author:** WORK-0029 implementation
**Work item:** WORK-0029
**Branch:** fix/work-0029-gate-on-main

## Question

Acceptance criterion 4 of WORK-0029 asks for an investigation note explaining
how PR #8 and PR #10 landed on main green even though, on a fresh
`git checkout main` + `python3 .github/scripts/am_i_done.py`, the gate now
fails with the violations they introduced (review-report schema; MD013
heading-line-length).

## Method

- Read `.github/workflows/am-i-done.yml`.
- Pulled GitHub Actions runs for the head SHAs of PR #8 (452a2848) and
  PR #10 (218d3729) via `gh api repos/:owner/:repo/actions/runs`.
- Pulled branch protection on `main` via
  `gh api repos/:owner/:repo/branches/main/protection`.

## Findings

### 1. The gate workflow ran and failed for both PRs

GitHub Actions shows `am-i-done.yml` runs on every commit since (and
including) PR #8. Every run has `conclusion: failure`. The two PRs in
question are no exception:

- run 26586519124 — `am-i-done.yml` on `452a284` (PR #8 head) — failure
- run 26587432286 — `am-i-done.yml` on `218d372` (PR #10 head) — failure
- run 26586686348 — `am-i-done.yml` on `de35a65` (main, post-merge) — failure

So the gate did its job and reported red.

### 2. The gate is not a required status check on main

`gh api repos/:owner/:repo/branches/main/protection` shows:

```json
{
  "required_pull_request_reviews": {"required_approving_review_count": 1, ...},
  "required_signatures": {"enabled": false},
  "enforce_admins": {"enabled": false},
  "required_linear_history": {"enabled": false},
  "allow_force_pushes": {"enabled": false},
  "allow_deletions": {"enabled": false},
  "required_conversation_resolution": {"enabled": true}
}
```

There is no `required_status_checks` block. Branch protection on main
requires one approving review and resolved conversations — nothing else.
A red `am-i-done` does not block merge.

This makes the gate purely advisory at the merge point. Any reviewer who
clicks "Merge" without scrolling to the checks panel ships a red main.

### 3. The pattern is older than WORK-0029

The same query shows every workflow run since PR #8 is failure
(am-i-done.yml AND codeql.yml). Five PRs in a row merged green-looking
into a main whose CI was, in fact, red. This is the validation-theatre
finding (BLOCKING #5 in the 2026-05-28 repo-health report) showing up at
the merge gate itself.

## Why the gate let those merges land

It didn't. The merge button did, because nothing was wired to it.

## Recommended merge-protection adjustment

The Phase-1 fix that makes the gate non-bypassable is two-line:

1. Add `am_i_done` to `required_status_checks.contexts` in branch
   protection on `main`. The matrix uses Python 3.11-3.14, so the
   required context names need to match what GitHub actually publishes
   (`am_i_done (3.11)` through `am_i_done (3.14)`), or a check-suite
   aggregation rule needs to be used.
2. Set `strict: true` so PR branches must be up to date with main before
   merging (catches the "two PRs each green individually, broken
   together" case).

Optionally:

- Enable `enforce_admins: true` so the rule applies to the repo owner.
- Document the protection requirement in CONTRIBUTING.md or
  docs/getting-started.md so first-time contributors (and any team-tier
  adopters) know which CI check is the gate.

This change cannot land inside WORK-0029 (branch protection lives in
GitHub config, not in this repo) and the user — repo admin — is the only
one who can apply it. Filing the action as the recommended next step:
either a dedicated WORK item, or an addendum to WORK-0018 (Phase-1
discipline-restoration tracker) which already calls out
validation-theatre as the underlying defect.

## What WORK-0029 fixes

This branch fixes the two artefacts the gate flagged (report.md schema
shape; alternatives.md:183 heading length). It does NOT close the gap
that let them land in the first place — that requires the branch
protection change above. Without it, the same class of red-on-main
regression can recur on any future PR.
