# WORK-0030 — The real root cause: GitHub never parsed our symlinked workflows

**Date:** 2026-05-28
**Author:** WORK-0030 implementation
**Work item:** WORK-0030
**Branch:** fix/work-0030-github-copies
**Supersedes:** the root-cause hypothesis in
[WORK-0029-gate-bypass-investigation.md](WORK-0029-gate-bypass-investigation.md)

## Why this note exists

WORK-0029's investigation note concluded that PRs #8 and #10 merged red
because `am_i_done` was not a `required_status_checks` context on `main` —
the merge button was wired to nothing. That observation is correct as far
as it goes, but it is downstream of a deeper defect this note records as the
actual root cause. WORK-0029's note should be read with this correction.

## The actual root cause

GitHub does not follow symlinks for the files it parses itself:
`.github/workflows/*`, `.github/dependabot.yml`,
`.github/PULL_REQUEST_TEMPLATE.md`, and `.github/CODEOWNERS`. install.py
projected all of these as symlinks into `skill/hedl/workflows/`. So GitHub
never saw a valid workflow file — it saw a tiny text blob containing a
relative path.

Consequence: the CI gate has never actually run in CI. Every "run" since
PR #2 is an `event: push` fallback failure with zero check_runs created.
The GitHub UI label "This run likely failed because of a workflow file
issue" is GitHub rejecting the symlink text as an invalid workflow file.

Verified via:

```text
gh api repos/neilgfoster/hedl/commits/<sha>/check-runs
```

on multiple PR head SHAs (218d3729, 452a2848, 5c6df42, 97b24a3) — all
returned zero check_runs.

## Why this supersedes the WORK-0029 hypothesis

Adding `required_status_checks` would not have helped on its own. A required
status check matches a *context name* that the workflow publishes. Because
the workflow never parsed, GitHub never had a context to attach — there was
nothing for branch protection to require. Fixing the symlinks is the
precondition that makes the WORK-0029 branch-protection fix meaningful.

## The distinction install.py now makes

- **GitHub-parsed paths** (`workflows/*`, `dependabot.yml`,
  `PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS`): copied as real files. GitHub
  reads them directly, so a symlink is invisible to it.
- **Workflow-invoked paths** (`.github/scripts/*.py`): left as symlinks.
  These are opened by the job at runtime on the runner filesystem, which
  resolves symlinks normally, so a link is fine and keeps a single source
  of truth.

`_github_parses_directly()` encodes this rule. `install.py --doctor` now
reports DRIFT when a GitHub-parsed target is still a symlink or when its
copy differs from the canonical source in `skill/hedl/`, with the remedy
"re-run install".

## Remaining follow-up (now unblocked)

Once a PR head shows real check_runs for `am_i_done (3.11)` through
`am_i_done (3.14)`, apply branch protection on `main`:
`required_status_checks` with those four contexts and `strict: true`. This
is the WORK-0029 follow-up; it could not work before this fix and can now.
Branch protection lives in GitHub config, not in this repo, so the repo
admin must apply it.
