# Adversarial Review — WORK-0030 (architecture)

**Log:** adversarial-review-2026-05-28-architecture
**Session:** in-session
**Depth:** Standard
**Commit:** 8811d78

Panel: [scope-auditor](scope-auditor.md),
[edge-case-hunter](edge-case-hunter.md),
[security-auditor](security-auditor.md),
[determinism-auditor](determinism-auditor.md).
Verdict: **CONDITIONAL → resolved (PASS)**.

## Dimension Scores

| Dimension | Verdict |
|---|---|
| Scope containment | PASS — change confined to install.py, its tests, the four .github copies, and a note |
| Correctness / edge cases | PASS after fixes (cmd_status false-green fixed; predicate drift locked) |
| Security | PASS — no new risk vs the prior symlink model |
| Determinism | PASS after fix — single-source-of-truth drift now test-guarded |

## Strengths

- The copy-vs-symlink distinction is data-driven from tiers.json and the
  predicate is small and pure.
- `--doctor` gained real drift detection (symlink, missing, content) with a
  clear remedy.
- New tests cover the predicate, copy/symlink behavior, symlink->copy
  migration, and both drift modes.

## Blocking Findings

None upheld. edge-case-hunter raised two BLOCKING items; both were rejected:
the "data loss on migration" case is the intended projection model (copies
are regenerated from skill/hedl/, and doctor reports drift), and the
"dry-run unlink" case was withdrawn by the finder as actually correct.

## Significant Findings

- **cmd_status false green** (edge-case-hunter) — `--status` reported a
  symlinked GitHub-parsed file as `ok`. FIXED: it now reports DRIFT.
- **Single-source-of-truth drift** (determinism-auditor, edge-case-hunter,
  scope-auditor) — `_GITHUB_PARSED_NAMES` could silently disagree with
  tiers.json. FIXED: a data-driven test asserts every non-script `.github/`
  projection is classified GitHub-parsed.
- Deferred (pre-existing or out of scope): path-traversal containment
  (tracked by WORK-0020), TOCTOU windows, install locking, unguarded
  read_bytes on permission-denied, line-ending platform variance. None are
  introduced by this diff.

## Minor Findings

- `CODEOWNERS` is a forward-declaration (named in AC#1) with no source yet;
  kept and now covered by the drift test.
- Audit-hash logging and Windows backslash handling: deferred as
  over-engineering / non-applicable to POSIX tiers.json targets.

## Next Actions

- None blocking. The two upheld SIGNIFICANT findings are fixed in this PR.
- After the PR opens, confirm AC#4: `gh api .../check-runs` shows real
  `am_i_done (3.11)`-`(3.14)` runs on the PR head.
