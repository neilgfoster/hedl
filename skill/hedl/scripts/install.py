#!/usr/bin/env python3
"""Hedl installer — project skill/hedl/ files into a target repository.

Usage:
    install.py --tier {gate|lightweight|team}   install or change tier
    install.py --status                          show installed tier + projection state
    install.py --doctor                          verify all projections are healthy

Options:
    --dry-run   show what would happen without writing anything
    --copy      copy files instead of symlinking (auto on Windows)
    --repo DIR  target repo root (default: current directory)
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import platform
import shutil
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any, Callable

SKILL_ROOT: Path = Path(__file__).resolve().parent.parent
HEDL_ROOT: Path = SKILL_ROOT.parent.parent
TIERS_FILE: Path = SKILL_ROOT / "tiers.json"
TIER_MARKER: str = ".hedl-tier"
TIER_ORDER: list[str] = ["gate", "lightweight", "team"]

CURRENT_STATE_SCHEMA: str = "1"


def _hedl_version() -> str:
    try:
        with (HEDL_ROOT / "pyproject.toml").open("rb") as fh:
            data = tomllib.load(fh)
        return str(data.get("project", {}).get("version", "unknown"))
    except Exception:
        return "unknown"


def _read_state_schema(work_dir: Path) -> str | None:
    """Return schema_version from .work/context.json, or None if absent/missing."""
    ctx = work_dir / "context.json"
    if not ctx.exists():
        return None
    try:
        data: dict[str, Any] = json.loads(ctx.read_text())
        v = data.get("schema_version")
        return str(v) if v is not None else None
    except Exception:
        return None


def _schema_ver_int(v: str | None) -> int:
    if v is None:
        return 0
    try:
        return int(v)
    except ValueError:
        return 0


def _archive_state_file(path: Path) -> None:
    """Copy path into .work/archive/YYYYMMDD_HHMMSS/ before mutation."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = path.parent / "archive" / ts
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst / path.name)


def _migrate_unversioned_to_1(work_dir: Path) -> None:
    """Migration None->1: add schema_version field to context.json."""
    ctx = work_dir / "context.json"
    if not ctx.exists():
        return
    data = json.loads(ctx.read_text())
    if "schema_version" in data:
        return  # idempotent
    _archive_state_file(ctx)
    data["schema_version"] = "1"
    ctx.write_text(json.dumps(data, indent=2) + "\n")


MIGRATIONS: list[tuple[str | None, str, Callable[[Path], None]]] = [
    (None, "1", _migrate_unversioned_to_1),
]


def _load_tiers() -> Any:
    with TIERS_FILE.open() as f:
        return json.load(f)


def _flatten_projections(tiers: Any, tier_name: str) -> list[dict[str, str]]:
    """Return all projections for a tier with inheritance expanded, in order."""
    tier = tiers["tiers"][tier_name]
    out: list[dict[str, str]] = []
    for included in tier.get("includes", []):
        out.extend(_flatten_projections(tiers, included))
    out.extend(tier.get("projections", []))
    return out


def _flatten_inits(tiers: Any, tier_name: str) -> list[dict[str, str]]:
    """Return all init (copy-once) entries for a tier with inheritance expanded."""
    tier = tiers["tiers"][tier_name]
    out: list[dict[str, str]] = []
    for included in tier.get("includes", []):
        out.extend(_flatten_inits(tiers, included))
    out.extend(tier.get("init", []))
    return out


def _use_copy(flag: bool) -> bool:
    return flag or platform.system() == "Windows"


# Files GitHub parses itself — the Actions runner never gets a chance to follow
# a symlink, so these must be real copies in .github/, not links into
# skill/hedl/. Paths under .github/scripts/ are opened by the workflow at
# runtime, where the filesystem resolves links normally, so those stay symlinks.
_GITHUB_PARSED_NAMES: set[str] = {
    "dependabot.yml",
    "PULL_REQUEST_TEMPLATE.md",
    "CODEOWNERS",
}


def _github_parses_directly(rel_target: str) -> bool:
    """True if GitHub reads this projection target directly (so it must be a
    real copy, not a symlink): anything under .github/workflows/, plus the
    fixed set of top-level .github/ files GitHub parses."""
    parts = PurePosixPath(rel_target).parts
    if not parts or parts[0] != ".github":
        return False
    rest = parts[1:]
    if rest and rest[0] == "workflows":
        return True
    return len(rest) == 1 and rest[0] in _GITHUB_PARSED_NAMES


def _project_one(
    source: Path,
    target: Path,
    *,
    copy: bool,
    dry_run: bool,
) -> str:
    """Ensure target is a projection of source. Returns a one-word status string."""
    if target.is_symlink():
        if not copy and target.resolve() == source.resolve():
            return "ok"
        if not dry_run:
            target.unlink()
        status = "updated"
    elif target.exists():
        if copy:
            if target.read_bytes() == source.read_bytes():
                return "ok"
            if not dry_run:
                shutil.copy2(source, target)
            return "updated"
        return "skip (user file exists)"
    else:
        status = "created"

    if dry_run:
        return f"would {status}"

    target.parent.mkdir(parents=True, exist_ok=True)
    if copy:
        shutil.copy2(source, target)
    else:
        rel = os.path.relpath(source, target.parent)
        target.symlink_to(rel)
    return status


def _compute_downgrade_delta(
    tiers: Any, current_tier: str, target_tier: str
) -> tuple[list[str], list[str]]:
    """Return (projections_to_remove, init_dirs_to_archive) for a tier downgrade."""
    current_projs = {p["target"] for p in _flatten_projections(tiers, current_tier)}
    target_projs = {p["target"] for p in _flatten_projections(tiers, target_tier)}
    to_remove = sorted(current_projs - target_projs)

    current_init_targets = {e["target"] for e in _flatten_inits(tiers, current_tier)}
    target_init_targets = {e["target"] for e in _flatten_inits(tiers, target_tier)}
    to_archive = sorted(current_init_targets - target_init_targets)

    return to_remove, to_archive


def _apply_downgrade_delta(
    repo: Path,
    tiers: Any,
    current_tier: str,
    target_tier: str,
    *,
    dry_run: bool,
) -> None:
    """Remove projections and archive init dirs when downgrading tiers."""
    to_remove, to_archive = _compute_downgrade_delta(tiers, current_tier, target_tier)

    for target_rel in to_remove:
        target = repo / target_rel
        if not target.exists() and not target.is_symlink():
            print(f"  [skip (not found)] {target_rel}")
        elif dry_run:
            print(f"  [would remove] {target_rel}")
        else:
            if target.is_symlink() or target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            print(f"  [removed] {target_rel}")

    for init_target in to_archive:
        src_dir = repo / init_target
        if not src_dir.exists():
            print(f"  [skip (not found)] {init_target}/")
            continue
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = src_dir / "archive" / timestamp
        if dry_run:
            print(f"  [would archive] {init_target}/ -> {init_target}/archive/{timestamp}/")
        else:
            archive_path.mkdir(parents=True, exist_ok=True)
            for item in src_dir.iterdir():
                if item.name == "archive":
                    continue
                shutil.move(str(item), str(archive_path / item.name))
            print(f"  [archived] {init_target}/ -> {init_target}/archive/{timestamp}/")


def cmd_install(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    tiers = _load_tiers()
    tier_names: list[str] = list(tiers["tiers"].keys())

    if args.tier not in tier_names:
        print(f"Unknown tier '{args.tier}'. Available: {', '.join(tier_names)}", file=sys.stderr)
        return 1

    copy = _use_copy(args.copy)
    target_tier: str = args.tier
    prefix = "[dry-run] " if args.dry_run else ""

    # Detect existing installation and classify the operation.
    marker = repo / TIER_MARKER
    current_tier: str | None = None
    if marker.exists():
        try:
            current_tier = json.loads(marker.read_text()).get("tier")
        except (json.JSONDecodeError, AttributeError):
            pass

    if current_tier == target_tier:
        print(f"{prefix}Tier '{target_tier}' already installed — verifying projections.")
    elif (
        current_tier in TIER_ORDER
        and target_tier in TIER_ORDER
        and TIER_ORDER.index(target_tier) < TIER_ORDER.index(current_tier)
    ):
        print(f"{prefix}Downgrading tier '{current_tier}' -> '{target_tier}'")
        _apply_downgrade_delta(repo, tiers, current_tier, target_tier, dry_run=args.dry_run)
    elif current_tier and current_tier in TIER_ORDER:
        print(f"{prefix}Upgrading tier '{current_tier}' -> '{target_tier}'")
    else:
        print(f"{prefix}Installing tier: {target_tier}")

    projections = _flatten_projections(tiers, target_tier)
    inits = _flatten_inits(tiers, target_tier)

    any_skip = False
    for proj in projections:
        source = (SKILL_ROOT / proj["source"]).resolve()
        target = repo / proj["target"]
        proj_copy = copy or _github_parses_directly(proj["target"])
        status = _project_one(source, target, copy=proj_copy, dry_run=args.dry_run)
        print(f"  [{status}] {proj['target']}")
        if "skip" in status:
            any_skip = True

    for entry in inits:
        tgt_dir = repo / entry["target"]
        if tgt_dir.exists():
            print(f"  [skip (exists)] {entry['target']}/")
        elif args.dry_run:
            print(f"  [would create] {entry['target']}/")
        else:
            src_dir = SKILL_ROOT / entry["source"]
            shutil.copytree(src_dir, tgt_dir)
            print(f"  [created] {entry['target']}/")

    if target_tier == "team":
        if shutil.which("gh"):
            print("\n[team] gh CLI detected. To enable the GitHub Issues backend:")
            print('       Add to .work/context.json: "state_backend": "github-issues"')
        else:
            print("\n[team] gh CLI not found — install for the GitHub Issues backend:")
            print("       https://cli.github.com/  then: gh auth login")

    if not args.dry_run:
        marker.write_text(
            json.dumps({"tier": target_tier, "skill": str(SKILL_ROOT)}) + "\n"
        )

    if any_skip:
        print("\nWARN: some projections were skipped — review 'skip' lines above.")
    print(f"\n{prefix}Done. Tier '{target_tier}' installed.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    marker = repo / TIER_MARKER

    if not marker.exists():
        print("No Hedl installation found (no .hedl-tier file).")
        return 0

    data: Any = json.loads(marker.read_text())
    tier: str = data.get("tier", "unknown")
    print(f"Installed tier: {tier}")

    tiers = _load_tiers()
    projections = _flatten_projections(tiers, tier)

    print("\nProjections:")
    for proj in projections:
        target = repo / proj["target"]
        if _github_parses_directly(proj["target"]):
            # GitHub-parsed targets must be real copies; a symlink here is the
            # WORK-0030 defect, so flag it rather than reporting a false "ok".
            if target.is_symlink():
                status = "DRIFT (symlink; re-run install)"
            elif target.exists():
                status = "ok (copy)"
            else:
                status = "MISSING"
        elif target.is_symlink():
            status = "ok" if target.resolve().exists() else "BROKEN"
        elif target.exists():
            status = "ok (copy)"
        else:
            status = "MISSING"
        print(f"  [{status}] {proj['target']}")

    return 0


def cmd_migrate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    work_dir = repo / ".work"

    if not (work_dir / "context.json").exists():
        print("No .work/context.json — nothing to migrate (gate-only tier).")
        return 0

    current = _read_state_schema(work_dir)
    current_int = _schema_ver_int(current)
    target_int = _schema_ver_int(CURRENT_STATE_SCHEMA)

    if current_int == target_int:
        print(f"State schema {CURRENT_STATE_SCHEMA!r} — already up to date.")
        return 0

    if current_int > target_int:
        print(
            f"Context.json schema {current!r} is newer than this Hedl build "
            f"({CURRENT_STATE_SCHEMA!r}). Upgrade Hedl to apply migrations."
        )
        return 1

    prefix = "[dry-run] " if args.dry_run else ""
    applied = 0
    # Walk migrations in order; re-read current after each application.
    changed = True
    while changed:
        changed = False
        for from_ver, to_ver, fn in MIGRATIONS:
            if current != from_ver:
                continue
            print(f"  {prefix}Applying migration {from_ver!r} -> {to_ver!r}")
            if not args.dry_run:
                fn(work_dir)
                current = _read_state_schema(work_dir)
            else:
                current = to_ver
            applied += 1
            changed = True
            break  # restart from top with new current

    if applied == 0:
        print("No applicable migration steps found.")
        return 1

    print(f"\n{prefix}Migration complete. State schema: {current!r}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    marker = repo / TIER_MARKER
    all_ok = True

    print("Skill scripts:")
    for script in [
        "am_i_done.py",
        "budget_manager.py",
        "check_pr_template.py",
        "check_markdown_schema.py",
        "install.py",
    ]:
        p = SKILL_ROOT / "scripts" / script
        ok = p.exists()
        if not ok:
            all_ok = False
        print(f"  [{'ok' if ok else 'MISSING'}] skill/hedl/scripts/{script}")

    if not marker.exists():
        print("\nNo .hedl-tier file — run: install.py --tier <name>")
        return 0

    data: Any = json.loads(marker.read_text())
    tier: str = data.get("tier", "unknown")
    tiers = _load_tiers()
    projections = _flatten_projections(tiers, tier)

    print(f"\nTier '{tier}' projections:")
    for proj in projections:
        target = repo / proj["target"]
        if _github_parses_directly(proj["target"]):
            source = (SKILL_ROOT / proj["source"]).resolve()
            if target.is_symlink():
                status = "DRIFT (symlink; GitHub needs a real copy — re-run install)"
                all_ok = False
            elif not target.exists():
                status = "MISSING"
                all_ok = False
            elif target.read_bytes() != source.read_bytes():
                status = "DRIFT (copy differs from source — re-run install)"
                all_ok = False
            else:
                status = "ok (copy)"
        elif target.is_symlink():
            ok = target.resolve().exists()
            status = "ok" if ok else "BROKEN (dangling symlink)"
            if not ok:
                all_ok = False
        elif target.exists():
            status = "ok (copy)"
        else:
            status = "MISSING"
            all_ok = False
        print(f"  [{status}] {proj['target']}")

    # Schema version check
    work_dir = repo / ".work"
    ctx_exists = (work_dir / "context.json").exists()
    ctx_ver = _read_state_schema(work_dir)

    print(f"\nHedl version: {_hedl_version()}")
    if not ctx_exists:
        print("State schema: not-installed (gate-only tier)")
    else:
        ver_display = ctx_ver if ctx_ver is not None else "unversioned"
        ctx_int = _schema_ver_int(ctx_ver)
        cur_int = _schema_ver_int(CURRENT_STATE_SCHEMA)
        if ctx_int == cur_int:
            schema_status = "ok"
        elif ctx_int < cur_int:
            schema_status = "needs-migrate"
        else:
            schema_status = "too-new"
        print(
            f"State schema: current={CURRENT_STATE_SCHEMA}  "
            f"context.json={ver_display}  [{schema_status}]"
        )
        if schema_status == "needs-migrate":
            print("  Run: python3 skill/hedl/scripts/install.py --migrate")
            all_ok = False
        elif schema_status == "too-new":
            print("  Context.json schema is newer than this Hedl build — upgrade Hedl.")
            all_ok = False

    print()
    if all_ok:
        print("All projections healthy.")
    else:
        print("WARN: some projections are broken or missing.")
        return 1

    return 0


CLI_SPEC: dict[str, Any] = {
    "name": "install",
    "script": "install.py",
    "description": "Install, upgrade, downgrade, or diagnose a Hedl installation.",
    "invocation": "python3 skill/hedl/scripts/install.py",
    "commands": [
        {
            "name": "--tier",
            "description": "Install or change the Hedl tier",
            "args": [
                {
                    "flag": "--tier",
                    "type": "str",
                    "required": True,
                    "choices": ["gate", "lightweight", "team"],
                    "help": "Target tier to install or transition to",
                },
                {
                    "flag": "--dry-run",
                    "type": "bool",
                    "required": False,
                    "help": "Show what would happen without writing",
                },
                {
                    "flag": "--copy",
                    "type": "bool",
                    "required": False,
                    "help": "Copy files instead of symlinking (auto on Windows)",
                },
                {
                    "flag": "--repo",
                    "type": "str",
                    "required": False,
                    "help": "Target repo root directory (default: current directory)",
                },
            ],
            "output": "Exits 0 on success, 1 on error.",
        },
        {
            "name": "--status",
            "description": "Show installed tier and projection state",
            "args": [
                {
                    "flag": "--status",
                    "type": "bool",
                    "required": True,
                    "help": "Show installed tier and projection state",
                },
                {
                    "flag": "--repo",
                    "type": "str",
                    "required": False,
                    "help": "Target repo root directory (default: current directory)",
                },
            ],
            "output": "Exits 0. Prints installed tier and status of each projection.",
        },
        {
            "name": "--doctor",
            "description": "Verify all projections are healthy and report schema compatibility",
            "args": [
                {
                    "flag": "--doctor",
                    "type": "bool",
                    "required": True,
                    "help": "Verify all projections are healthy",
                },
                {
                    "flag": "--repo",
                    "type": "str",
                    "required": False,
                    "help": "Target repo root directory (default: current directory)",
                },
            ],
            "output": (
                "Exits 0 if all healthy. Reports Hedl version and state schema status: "
                "ok / needs-migrate / too-new / not-installed."
            ),
        },
        {
            "name": "--migrate",
            "description": "Apply pending schema migrations to .work/context.json",
            "args": [
                {
                    "flag": "--migrate",
                    "type": "bool",
                    "required": True,
                    "help": "Apply pending schema migrations",
                },
                {
                    "flag": "--dry-run",
                    "type": "bool",
                    "required": False,
                    "help": "Show what would happen without writing",
                },
                {
                    "flag": "--repo",
                    "type": "str",
                    "required": False,
                    "help": "Target repo root directory (default: current directory)",
                },
            ],
            "output": "Exits 0 on success, 1 if migration fails or schema is too new.",
        },
        {
            "name": "--version",
            "description": "Print Hedl version",
            "args": [
                {
                    "flag": "--version",
                    "type": "bool",
                    "required": True,
                    "help": "Print Hedl version and exit",
                },
            ],
            "output": "Prints X.Y.Z version string and exits 0.",
        },
    ],
}


def main() -> int:
    if "--schema" in sys.argv:
        print(json.dumps(CLI_SPEC, indent=2))
        return 0

    if "--version" in sys.argv:
        print(_hedl_version())
        return 0

    parser = argparse.ArgumentParser(
        description="Install, upgrade, or diagnose a Hedl installation.",
        epilog="""
commands:
  --tier {gate|lightweight|team}   install or change tier
  --status                         show installed tier and projection state
  --doctor                         verify all projections are healthy
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _tier_cmd = next(c for c in CLI_SPEC["commands"] if c["name"] == "--tier")
    _tier_choices = next(a["choices"] for a in _tier_cmd["args"] if a["flag"] == "--tier")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tier", choices=_tier_choices,
                       metavar="{" + "|".join(_tier_choices) + "}")
    group.add_argument("--status", action="store_true",
                       help="show installed tier and projection state")
    group.add_argument("--doctor", action="store_true",
                       help="verify all projections are healthy and report schema")
    group.add_argument("--migrate", action="store_true",
                       help="apply pending schema migrations to .work/context.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would happen without writing")
    parser.add_argument("--copy", action="store_true",
                        help="copy files instead of symlinking (auto on Windows)")
    parser.add_argument("--repo", default=".", metavar="DIR",
                        help="target repo root (default: current directory)")

    args = parser.parse_args()

    if args.tier:
        return cmd_install(args)
    if args.status:
        return cmd_status(args)
    if args.doctor:
        return cmd_doctor(args)
    if args.migrate:
        return cmd_migrate(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
