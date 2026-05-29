# Team Tier

GitHub Issues backend + parallel worktree execution, layered on top of lightweight.

**Full reference**: `skill/hedl/references/tiers.md`

---

## Install

```bash
python3 skill/hedl/scripts/install.py --tier team
```

## Quick config (GitHub Issues backend)

Add to `hedl.toml` (ADR-022):

```toml
[state]
backend = "github-issues"

[state_backend.github-issues]
repo = "owner/repo"
label_prefix = "work"
phase_label = "phase-{N}"
```

When `backend` is `local-file` (the default), `.work/work.json` is used and no
GitHub access is required. `install.py --migrate` relocates any legacy
`state_backend` value from `.work/context.json` into `hedl.toml`.

See `skill/hedl/references/tiers.md` for the parallel worktree gate pattern,
migration steps from lightweight, and the full backend interface reference.
