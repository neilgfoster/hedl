# Development Standards (minimal)

Standards for branches, commits, and pull requests. Scoped to what the
PR-template CI check enforces today. Code-style, testing, and language
rules will land in a separate governance PR.

---

## Branches

### Naming

```text
feat/<short-description>       new capability
fix/<short-description>        bug fix
refactor/<short-description>   restructure without behaviour change
docs/<short-description>       documentation only
chore/<short-description>      tooling, config, deps, CI
spike/<work-id>-<topic>        throwaway tech evaluation
```

- Lowercase, hyphens. No underscores, no uppercase, no slashes beyond the prefix.
- Short descriptions (2-4 words). `feat/user-auth`, not
  `feat/add-the-full-user-authentication-implementation`.
- One concern per branch. The branch name should let a reader predict the
  diff. If the diff outgrows the name, rename the branch and the PR title
  before requesting review.

### Lifecycle

- Branch from `main`. Delete after merge. Linear history enforced.

---

## Commits

### Format

```text
<type>: <short imperative summary>

<optional body — what and why, not how>

Co-Authored-By: Claude <noreply@anthropic.com>   ← if Claude contributed
```

Types match branch prefixes: `feat`, `fix`, `refactor`, `docs`, `chore`, `spike`.

### Rules

- Summary line: ≤72 chars. Imperative mood. No trailing period.
- Describe *why*, not what the diff shows.
- One logical change per commit. If you need "and", split.
- Use a model-agnostic `Co-Authored-By` trailer. The exact model is in the PR description if relevant.

---

## Pull Requests

### When to raise

Every change that touches `main` goes through a PR. Direct push is blocked.

### Title format

```text
<type>: <short imperative description>
```

If there is a tracked work item: `WORK-XXXX: <description>`.

### Template

All PRs must use `.github/PULL_REQUEST_TEMPLATE.md`. The CI workflow
`PR Template Check` enforces it. Required sections:

| Section     | What's required                                                                |
|-------------|--------------------------------------------------------------------------------|
| Summary     | 1-3 sentences on what and why                                                  |
| Work item   | `WORK-XXXX` (uppercase) or `none` followed by ≥12 chars of justification        |
| Type        | At least one checkbox at start of line marked `- [x]`                          |
| Changes     | At least one bullet `- <text>`                                                 |
| Validation  | How was this verified — tests, manual, spike verdict, etc.                     |

The Checklist section is not CI-enforced but should still be considered.

**Documentation impact:** if a change alters a count, name, or behaviour that
docs assert (e.g. agent/command counts, tier descriptions), update the affected
docs in the same PR. This is a convention, not a gate — a gate-enforced form was
weighed and declined as disproportionate; the narrow, mechanical case of
source-derived counts is instead caught by WORK-0028's drift-detector.

### Merging

- Squash or merge commit — keep `main` history readable.
- Branch is deleted after merge.
- Fold the `.work/` item-state update (`active` → `completed`) into the
  delivering PR; do not raise a separate closeout PR. (Convention adopted from
  the 2026-05-28 dogfood learning #6; revisited at `/phase-complete`. A
  github-issues backend would auto-close items via `Closes #N`, retiring the
  question — see ADR-022.)

---

## Work item workstreams

A **workstream** is one of four fixed work classifications, and each work item
belongs to exactly one. This is the canonical meaning of "workstream" across
Hedl's docs, state, and routing: it appears in `work.json` as the `workstream`
field and is used by `/iterate` to select appropriate tools and context.

| ID | Name | When to use |
|---|---|---|
| `WS-PLAN` | Planning | Scope, phase definitions, backlog grooming, project setup |
| `WS-REQ` | Requirements | Gathering or refining requirements, user stories, acceptance criteria |
| `WS-TECH` | Technical evaluation | Spikes, technology choices, proof-of-concept work |
| `WS-ARCH` | Architecture | Design decisions, ADRs, structural changes, interface definitions |

If the work does not clearly fit one category, prefer `WS-PLAN` for process
work and `WS-ARCH` for any decision that affects the codebase structure.

> **One meaning of "workstream."** A separate recursive-container model — a
> single primitive subsuming phase and work item — was proposed in ADR-019 but
> is **deferred and unbuilt**, gated on demand (WORK-0010); the 2026-05-29
> dogfood found prose templates outperform it below ~5-7 concurrent workstreams.
> Until WORK-0010 lands, "workstream" means the work classification defined
> above — not a recursive container. ADR-019 is superseded by this definition
> (see its Status note). This resolves the prior double-definition (WORK-0027).

---

*This minimal standard covers only what the current CI enforces. Code style,
testing rules, dependency policy, and Claude-specific guidance belong with
the governance/CLAUDE.md rewrite PR.*
