# Self-Improvement

Hedl can propose improvements to its own framework through a structured three-layer
loop. The loop is **local-first, opt-in, and human-gated** — it never acts
autonomously and never phones home.

---

## Three layers

### Layer A — Usage instrumentation (/insights)

Behind an opt-in flag (`[insights] enabled = false` in `hedl.toml`), Hedl records
its own operation metadata locally:

- Gate check pass/fail/override counts
- Which reviewers fired and whether they produced findings
- Gate-block frequency and friction points
- Tier and command usage

**What is recorded**: timestamps, tool/reviewer/command names, pass/fail results,
finding counts.

**What is never recorded**: consumer source code, file contents, commit messages,
user names, PII, or any natural-language content from the project.

**Network**: none — ever. Events are append-only JSONL in `.work/insights/events.jsonl`.

Enable:

```toml
# hedl.toml
[insights]
enabled = true
```

### Layer B — Reflection (/reflect)

The `/reflect` command (see `references/commands.md`) aggregates `.work/insights/`
into a deterministic metrics summary, then passes the metrics to the existing
review agents (existential-challenger, drift-detector, agent-evaluator) to
synthesise structured improvement proposals.

```bash
python3 .github/scripts/reflect.py --work-dir .work
```

Proposals are written to `.work/insights/proposals/` as structured JSON. The
aggregation step is pure arithmetic (deterministic). The agents only interpret.

### Layer C — Contribution (/contribute)

The `/contribute` command turns a Layer-B proposal into an upstream PR using
Hedl's own workflow (spec → implement → gate → PR).

The flow **prepares and opens a PR**. It **cannot merge**. That is structural.

---

## Privacy fail-closed scrub

Before any PR is opened, the contribution diff is scrubbed by `contribute.py scrub`:

```bash
git diff main...HEAD --name-only | xargs python3 .github/scripts/contribute.py scrub \
  --diff-files
```

Any file outside `skill/hedl/` is a hard rejection. Consumer source code, `.work/`
state, CI configuration, and root files are all violations. The scrub is fail-closed:
when in doubt, it refuses.

---

## Semver classification

The implied Hedl version bump for a contribution is computed deterministically by
`contribute.py classify`:

```bash
python3 .github/scripts/contribute.py classify --change-type new-reviewer
# {"change_type": "new-reviewer", "bump": "minor"}
```

See `docs/versioning.md` for the full classification table.

---

## Human-in-the-loop: branch protection

The structural enforcement of "never autonomous" is **branch protection on `main`**.
The `/contribute` flow opens a PR; a human must review and approve before the merge
can happen. No code can bypass this.

### Configure branch protection (run once, Hedl repo maintainer)

```bash
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api "repos/$REPO/branches/main/protection" \
  --method PUT \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["am-i-done"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": false
  },
  "restrictions": null
}
EOF
```

This enforces:
- At least one approving review before merge
- The `am-i-done` CI check must pass
- Direct pushes to `main` are blocked

**This is what makes self-improvement non-autonomous.** The `/contribute` flow
can open a PR. It cannot merge. Merging requires a human reviewer.

---

## /contribute flow (operator steps)

1. Run `/reflect` to generate `.work/insights/proposals/`.
2. Review proposals; select one to act on.
3. Say "contribute" or run `/contribute` — Hedl begins the normal
   spec → implement → gate → PR loop applied to the selected proposal.
4. Before any push, the diff is scrubbed (privacy fail-closed) and classified.
5. **Confirm remote push when prompted** — the operator is always asked before
   any `gh pr create` runs.
6. A PR is opened against the upstream Hedl repo's `main` branch.
7. A human reviews and approves the PR. Hedl never merges.

Note: `/contribute` targets the self-hosting Hedl repo (derived from
`git remote get-url origin`). It is fully operational only once Hedl has been
adopted into its own repo.

---

## What the loop is NOT

- It is not autonomous. Every merge requires human approval.
- It does not phone home. No data leaves the machine.
- It does not enable by default. `[insights] enabled = false`.
- It does not run unsupervised. Each step requires an explicit operator action.
