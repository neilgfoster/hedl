#!/usr/bin/env python3
"""Generate the deterministic-operations section of SKILL.md from script --schema output.

Usage:
  python3 skill/hedl/scripts/gen_skill_metadata.py            # regenerate SKILL.md in place
  python3 skill/hedl/scripts/gen_skill_metadata.py --dry-run  # print generated section to stdout
  python3 skill/hedl/scripts/gen_skill_metadata.py --check    # exit 0 if up to date, 1 if stale/invalid

The generated section is delimited by marker comments in SKILL.md:
  <!-- GENERATED: deterministic-ops START -->
  <!-- GENERATED: deterministic-ops END -->

Do not edit the content between those markers by hand. Change the script's CLI_SPEC instead
and re-run this generator. The am_i_done.py --check skill-meta gate check calls this script
with --check to enforce that the section is never stale.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).parent
SKILL_MD = SCRIPTS_DIR.parent / "SKILL.md"
COMMANDS_MD = SCRIPTS_DIR.parent / "references" / "commands.md"

_SCRIPTS = [
    SCRIPTS_DIR / "am_i_done.py",
    SCRIPTS_DIR / "install.py",
    SCRIPTS_DIR / "budget_manager.py",
    SCRIPTS_DIR / "release.py",
    SCRIPTS_DIR / "reflect.py",
    SCRIPTS_DIR / "contribute.py",
]

_START = "<!-- GENERATED: deterministic-ops START -->"
_END = "<!-- GENERATED: deterministic-ops END -->"


# ---------------------------------------------------------------------------
# Schema fetching
# ---------------------------------------------------------------------------


def get_schemas() -> list[dict[str, Any]]:
    """Run --schema on each script and return the parsed JSON list."""
    schemas: list[dict[str, Any]] = []
    for script in _SCRIPTS:
        result = subprocess.run(
            [sys.executable, str(script), "--schema"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"{script.name} --schema failed (exit {result.returncode}):\n"
                f"{result.stderr.strip()}"
            )
        try:
            schemas.append(json.loads(result.stdout))
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{script.name} --schema produced invalid JSON: {exc}"
            ) from exc
    return schemas


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _render_invocation(base: str, cmd: dict[str, Any]) -> str:
    """Build the canonical invocation string for one command entry."""
    name: str = cmd["name"]
    args: list[dict[str, Any]] = cmd.get("args", [])
    parts = [base]

    if name not in ("default", "(default)"):
        if name.startswith("--"):
            # Flag-as-command (install.py style): the flag activates the mode
            for arg in args:
                if arg["flag"] == name:
                    if arg.get("choices"):
                        choices_str = "{" + "|".join(arg["choices"]) + "}"
                        parts.append(f"{name} {choices_str}")
                    else:
                        parts.append(name)
                    break
        else:
            # Subcommand (budget_manager.py style)
            parts.append(name)

    # Append required args that are not the activating flag/subcommand
    for arg in args:
        flag: str = arg["flag"]
        if flag == name:
            continue  # already handled above as the activating element
        if not arg.get("required", False):
            # Only exception: drain's optional positional n -> show as [N]
            if flag == "n" and not flag.startswith("-"):
                parts.append("[N]")
            continue
        if arg.get("choices"):
            parts.append(f"{flag} {{{' | '.join(arg['choices'])}}}")
        elif arg["type"] == "int":
            parts.append(f"{flag} N" if flag.startswith("-") else "N")
        else:  # str
            uname = flag.lstrip("-").upper().replace("-", "_")
            parts.append(f"{flag} {uname}" if flag.startswith("-") else uname)

    return " ".join(parts)


def render_section(schemas: list[dict[str, Any]]) -> str:
    """Render the full generated block (START marker through END marker, no trailing newline)."""
    lines: list[str] = [
        _START,
        "> _Do not edit this section — generated from script `--schema` output._",
        "> _To update: change the script's `CLI_SPEC` and run `python3 skill/hedl/scripts/gen_skill_metadata.py`._",
        "",
        "**DETERMINISTIC — always invoke the script, never reason through it:**",
        "",
        "| Operation | Invocation |",
        "|-----------|------------|",
    ]

    for schema in schemas:
        base: str = schema["invocation"]
        for cmd in schema["commands"]:
            inv = _render_invocation(base, cmd)
            # Escape | inside a markdown table cell
            inv_escaped = inv.replace("|", "\\|")
            lines.append(f"| {cmd['description']} | `{inv_escaped}` |")

    lines.append(_END)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# File manipulation
# ---------------------------------------------------------------------------


def _replace_section(text: str, new_section: str) -> str:
    """Replace the content between markers (inclusive) with new_section."""
    start_idx = text.find(_START)
    end_idx = text.find(_END)
    if start_idx == -1 or end_idx == -1:
        raise ValueError(
            f"Markers not found in SKILL.md.\n"
            f"Expected:\n  {_START}\n  {_END}"
        )
    after_end = end_idx + len(_END)
    return text[:start_idx] + new_section + text[after_end:]


def _extract_outside_generated(text: str) -> str:
    """Return SKILL.md text with the generated section removed."""
    start_idx = text.find(_START)
    end_idx = text.find(_END)
    if start_idx == -1 or end_idx == -1:
        return text
    after_end = end_idx + len(_END)
    return text[:start_idx] + text[after_end:]


# ---------------------------------------------------------------------------
# Validity checking
# ---------------------------------------------------------------------------


def _extract_code_content(text: str) -> list[str]:
    """Extract all inline code spans and fenced code block bodies."""
    fenced = re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    fenced += re.findall(r"~~~[^\n]*\n(.*?)~~~", text, re.DOTALL)
    inline = re.findall(r"`([^`\n]+)`", text)
    return fenced + inline


def check_validity(skill_md_text: str, commands_md_text: str, schemas: list[dict[str, Any]]) -> list[str]:
    """Scan SKILL.md (outside generated section) and commands.md for invalid script references.

    Returns a list of human-readable error strings (empty = all valid).

    Checks:
    - Flag choice references: 'script.py --flag VALUE' where VALUE is not in choices.
    - Subcommand references: 'script.py WORD' where WORD is not a valid subcommand name.
    """
    errors: list[str] = []

    # Build maps from schemas
    # choice_map[script_basename][flag] = [valid choices]
    choice_map: dict[str, dict[str, list[str]]] = {}
    # subcommand_map[script_basename] = set of valid subcommand names
    subcommand_map: dict[str, set[str]] = {}

    for schema in schemas:
        sfile: str = schema["script"]
        choice_map[sfile] = {}
        subcommand_map[sfile] = set()
        for cmd in schema["commands"]:
            cname: str = cmd["name"]
            # Subcommand names: bare words (not flags, not default/placeholder)
            if not cname.startswith("--") and cname not in ("default", "(default)"):
                subcommand_map[sfile].add(cname)
            for arg in cmd.get("args", []):
                if arg.get("choices"):
                    choice_map[sfile][arg["flag"]] = list(arg["choices"])

    outside = _extract_outside_generated(skill_md_text)
    scan_sources = [("SKILL.md", outside), ("commands.md", commands_md_text)]

    for doc_name, text in scan_sources:
        snippets = _extract_code_content(text)
        for snippet in snippets:
            for sfile, flags in choice_map.items():
                for flag, choices in flags.items():
                    pat = re.escape(sfile) + r"\s+" + re.escape(flag) + r"\s+([\w-]+)"
                    for m in re.finditer(pat, snippet):
                        value = m.group(1)
                        if value not in choices:
                            errors.append(
                                f"{doc_name}: `{sfile} {flag} {value}` — "
                                f"'{value}' not in valid choices {choices}"
                            )

            for sfile, subcmds in subcommand_map.items():
                if not subcmds:
                    continue
                pat = re.escape(sfile) + r"\s+([\w-]+)"
                for m in re.finditer(pat, snippet):
                    value = m.group(1)
                    if value.startswith("-"):
                        continue  # it's a flag, not a subcommand
                    if value not in subcmds:
                        errors.append(
                            f"{doc_name}: `{sfile} {value}` — "
                            f"'{value}' is not a valid subcommand; "
                            f"valid: {sorted(subcmds)}"
                        )

    return errors


# ---------------------------------------------------------------------------
# Regenerate / check entry points
# ---------------------------------------------------------------------------


def regenerate(dry_run: bool = False) -> int:
    """Regenerate SKILL.md's generated section in place. Returns 0 on success."""
    try:
        schemas = get_schemas()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    new_section = render_section(schemas)
    try:
        text = SKILL_MD.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error reading {SKILL_MD}: {exc}", file=sys.stderr)
        return 1

    try:
        new_text = _replace_section(text, new_section)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if dry_run:
        print(new_section)
        return 0

    SKILL_MD.write_text(new_text, encoding="utf-8")
    print(f"Updated {SKILL_MD}")
    return 0


def check() -> int:
    """Check staleness and validity. Returns 0 if up to date and valid, 1 otherwise."""
    try:
        schemas = get_schemas()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    new_section = render_section(schemas)

    try:
        skill_text = SKILL_MD.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error reading {SKILL_MD}: {exc}", file=sys.stderr)
        return 1

    start_idx = skill_text.find(_START)
    end_idx = skill_text.find(_END)
    if start_idx == -1 or end_idx == -1:
        print(f"error: markers not found in {SKILL_MD}", file=sys.stderr)
        print(f"  Expected: {_START}", file=sys.stderr)
        print(f"  Expected: {_END}", file=sys.stderr)
        return 1

    current_section = skill_text[start_idx : end_idx + len(_END)]
    if current_section != new_section:
        print("FAIL: SKILL.md deterministic-ops section is stale.", file=sys.stderr)
        print("Run: python3 skill/hedl/scripts/gen_skill_metadata.py", file=sys.stderr)
        current_lines = current_section.splitlines()
        new_lines = new_section.splitlines()
        for i, (cur, new) in enumerate(zip(current_lines, new_lines)):
            if cur != new:
                print(f"  first diff at line {i + 1}:", file=sys.stderr)
                print(f"  - {cur}", file=sys.stderr)
                print(f"  + {new}", file=sys.stderr)
                break
        else:
            print(
                f"  line count: current={len(current_lines)} expected={len(new_lines)}",
                file=sys.stderr,
            )
        return 1

    commands_text = ""
    if COMMANDS_MD.exists():
        commands_text = COMMANDS_MD.read_text(encoding="utf-8")

    errors = check_validity(skill_text, commands_text, schemas)
    if errors:
        print("FAIL: SKILL.md has invalid script references:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    return 0


def main() -> int:
    if "--check" in sys.argv:
        return check()
    if "--dry-run" in sys.argv:
        return regenerate(dry_run=True)
    return regenerate(dry_run=False)


if __name__ == "__main__":
    sys.exit(main())
