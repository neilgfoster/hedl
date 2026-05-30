# Versioning

Hedl tracks two independent version axes. They must never be conflated.

---

## Axis A — Hedl's own version

**Source of truth**: `pyproject.toml` `[project] version`.

**Exposed via**:

```bash
python3 skill/hedl/scripts/install.py --version
python3 .github/scripts/am_i_done.py --version
```

### Compatibility contract

| Change | Bump |
|---|---|
| Breaking change to `hedl.toml` schema (section removed, field type changed) | MAJOR |
| Breaking change to `.work/` state schema (field removed or type changed) | MAJOR |
| Change to gate exit-code semantics | MAJOR |
| Change to `tiers.json` / `install.py` projection layout | MAJOR |
| Removing a slash command from `commands/` | MAJOR |
| Removing an agent from `agents/` | MAJOR |
| New tier, new gate check, new reviewer agent, new optional config field | MINOR |
| Bug fix, no interface change | PATCH |

MAJOR bumps always require a migration entry (see schema versioning below).

---

## Axis B — Consumer project version

**Source of truth**: `.work/context.json` `project_version` field.

This is the version of the **product being built with Hedl**, not Hedl itself.
It is proposed and recorded by `/phase-complete` when a phase closes.

The bump is computed deterministically from the `change_class` of completed work
items in the closing phase:

| Completed items contain | Bump |
|---|---|
| Any `breaking` item | major |
| Any `feat` item (and no `breaking`) | minor |
| Only `fix`, `chore`, `docs`, or empty | patch |

`change_class` values: `feat`, `fix`, `breaking`, `chore`, `docs`. Default: `chore`.

**Phase-to-release mapping**: persisted in `.work/context.json` `releases` object:

```json
{
  "project_version": "1.2.0",
  "releases": {
    "phase-1": {"version": "0.1.0", "bump": "minor", "date": "2026-05-27"},
    "phase-2": {"version": "1.0.0", "bump": "major", "date": "2026-06-15"}
  }
}
```

---

## Schema versioning

Hedl embeds a schema version in `.work/context.json` (`schema_version` field). It
tracks the format version of Hedl's state files, independent of the product or Hedl
semver. `hedl.toml` does not carry a schema version — `install.py` reads
`schema_version` only from `.work/context.json`, and no gate or installer code
reads a `[hedl] schema_version`.

Current state schema: **2**

### Checking and migrating

```bash
# Report Hedl version + schema compatibility
python3 skill/hedl/scripts/install.py --doctor

# Apply pending migrations
python3 skill/hedl/scripts/install.py --migrate

# Dry-run migration
python3 skill/hedl/scripts/install.py --migrate --dry-run
```

Doctor output states:

| Status | Meaning |
|---|---|
| `ok` | Schema matches this Hedl build |
| `needs-migrate` | State is older — run `--migrate` |
| `too-new` | State is newer — upgrade Hedl |
| `not-installed` | Gate-only tier; no state files |

### Migration registry

Migrations are ordered, idempotent, and always archive state before mutating it.
Archives land in `.work/archive/YYYYMMDD_HHMMSS/`. No user data is ever destroyed.

Current migration sequence:

| From | To | Effect |
|---|---|---|
| unversioned | 1 | Adds `schema_version: "1"` to `context.json` |
| 1 | 2 | Relocates `state_backend` from `context.json` to `hedl.toml` `[state] backend` (ADR-022) |
