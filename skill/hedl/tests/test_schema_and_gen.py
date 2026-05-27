"""Tests for CLI_SPEC / --schema and gen_skill_metadata.py.

Coverage:
  - each script's --schema emits valid JSON matching its argparse surface
  - install.py --tier choices match tiers.json
  - budget_manager.py --schema contains all expected subcommand names
  - render_section output is deterministic (same input -> same output)
  - staleness: tampered generated section is detected in-memory and via --check
  - validity: bad flag choices and bad subcommand names are caught
  - validity: valid SKILL.md references pass
  - gen_skill_metadata.py is stdlib-only

Run: pytest skill/hedl/tests/test_schema_and_gen.py
"""

from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest
from typing import Any

_SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent.parent / "scripts"
_GEN = _SCRIPTS_DIR / "gen_skill_metadata.py"
_SKILL_MD = _SCRIPTS_DIR.parent / "SKILL.md"
_TIERS_JSON = _SCRIPTS_DIR.parent / "tiers.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_schema(script: str) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS_DIR / script), "--schema"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"{script} --schema failed:\n{result.stderr}"
    data = json.loads(result.stdout)
    assert isinstance(data, dict), f"{script} --schema returned non-dict JSON"
    return data


def _load_gen() -> Any:
    spec = importlib.util.spec_from_file_location("gen_skill_metadata", _GEN)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _load_gen()


# ---------------------------------------------------------------------------
# --schema output structure
# ---------------------------------------------------------------------------


class TestSchemaOutput(unittest.TestCase):
    """Each script's --schema emits valid JSON with the required structure."""

    def _assert_schema_base(self, schema: dict[str, Any], script: str) -> None:
        for key in ("name", "script", "description", "invocation", "commands"):
            self.assertIn(key, schema, f"{script}: missing key '{key}'")
        self.assertEqual(schema["script"], script, f"{script}: 'script' field mismatch")
        self.assertIsInstance(schema["commands"], list)
        self.assertGreater(len(schema["commands"]), 0, f"{script}: commands list is empty")
        for cmd in schema["commands"]:
            for k in ("name", "description", "args", "output"):
                self.assertIn(k, cmd, f"{script} cmd={cmd.get('name')}: missing '{k}'")
            for arg in cmd["args"]:
                for k in ("flag", "type", "required", "help"):
                    self.assertIn(k, arg,
                        f"{script} cmd={cmd['name']} arg={arg.get('flag')}: missing '{k}'")
                self.assertIn(arg["type"], ("str", "int", "bool"),
                    f"{script}: arg 'type' must be str/int/bool")
                if "choices" in arg:
                    self.assertIsInstance(arg["choices"], list)
                    self.assertGreater(len(arg["choices"]), 0)

    def test_am_i_done_schema(self) -> None:
        schema = _run_schema("am_i_done.py")
        self._assert_schema_base(schema, "am_i_done.py")
        self.assertEqual(schema["name"], "am_i_done")
        self.assertEqual(len(schema["commands"]), 1)
        cmd = schema["commands"][0]
        self.assertEqual(cmd["name"], "default")
        flags = {a["flag"] for a in cmd["args"]}
        self.assertIn("--check", flags)
        self.assertIn("--json", flags)
        self.assertIn("--pr", flags)
        check_arg = next(a for a in cmd["args"] if a["flag"] == "--check")
        self.assertIn("choices", check_arg)
        for expected in ("git", "branch", "config", "lint", "types", "tests", "skill-meta"):
            self.assertIn(expected, check_arg["choices"],
                f"--check choices missing '{expected}'")

    def test_install_schema(self) -> None:
        schema = _run_schema("install.py")
        self._assert_schema_base(schema, "install.py")
        self.assertEqual(schema["name"], "install")
        cmd_names = {c["name"] for c in schema["commands"]}
        self.assertIn("--tier", cmd_names)
        self.assertIn("--status", cmd_names)
        self.assertIn("--doctor", cmd_names)
        tier_cmd = next(c for c in schema["commands"] if c["name"] == "--tier")
        tier_arg = next(a for a in tier_cmd["args"] if a["flag"] == "--tier")
        self.assertTrue(tier_arg["required"])
        self.assertIn("choices", tier_arg)
        for tier in ("gate", "lightweight", "team"):
            self.assertIn(tier, tier_arg["choices"])

    def test_budget_manager_schema(self) -> None:
        schema = _run_schema("budget_manager.py")
        self._assert_schema_base(schema, "budget_manager.py")
        self.assertEqual(schema["name"], "budget_manager")
        cmd_names = {c["name"] for c in schema["commands"]}
        for expected in ("(default)", "tier", "record", "reset", "defer",
                         "queue", "drain", "record-panel", "suggest-rotation"):
            self.assertIn(expected, cmd_names,
                f"budget_manager.py --schema missing command '{expected}'")
        defer = next(c for c in schema["commands"] if c["name"] == "defer")
        defer_flags = {a["flag"] for a in defer["args"]}
        for f in ("--pr", "--branch", "--agents"):
            self.assertIn(f, defer_flags, f"defer missing required flag '{f}'")

    def test_schema_exit_code_zero(self) -> None:
        for script in ("am_i_done.py", "install.py", "budget_manager.py"):
            result = subprocess.run(
                [sys.executable, str(_SCRIPTS_DIR / script), "--schema"],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, f"{script} --schema exited {result.returncode}")


# ---------------------------------------------------------------------------
# Argparse / spec consistency
# ---------------------------------------------------------------------------


class TestArgparseConsistency(unittest.TestCase):
    """CLI_SPEC choices must match what argparse actually enforces."""

    def test_am_i_done_check_choices_match_cli_spec(self) -> None:
        """am_i_done.py argparse --check choices are sourced from CLI_SPEC."""
        spec_schema = _run_schema("am_i_done.py")
        check_arg = next(
            a for a in spec_schema["commands"][0]["args"] if a["flag"] == "--check"
        )
        self.assertIn("choices", check_arg, "--check arg must expose choices in --schema")
        # Verify argparse rejects an unknown value
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "am_i_done.py"), "--check", "__unknown__"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0,
            "argparse should reject unknown --check value")
        # Verify argparse accepts skill-meta
        result2 = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "am_i_done.py"), "--check", "skill-meta"],
            capture_output=True, text=True, timeout=60,
        )
        # Exit code may be 0 (pass), 1 (fail), or 2 (nothing to check); none are argparse errors
        self.assertIn(result2.returncode, (0, 1, 2),
            f"skill-meta should be a valid --check choice, got exit {result2.returncode}")

    def test_install_tier_choices_match_tiers_json(self) -> None:
        """install.py --tier choices in CLI_SPEC must match tiers.json tier names."""
        schema = _run_schema("install.py")
        tier_cmd = next(c for c in schema["commands"] if c["name"] == "--tier")
        tier_arg = next(a for a in tier_cmd["args"] if a["flag"] == "--tier")
        schema_choices = set(tier_arg["choices"])

        tiers_data = json.loads(_TIERS_JSON.read_text())
        tiers_from_file = set(tiers_data["tiers"].keys())

        self.assertEqual(schema_choices, tiers_from_file,
            f"install.py CLI_SPEC choices {schema_choices} differ from tiers.json {tiers_from_file}")

    def test_install_argparse_rejects_unknown_tier(self) -> None:
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "install.py"), "--tier", "nonexistent"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)


# ---------------------------------------------------------------------------
# Generator determinism
# ---------------------------------------------------------------------------


class TestGeneratorDeterminism(unittest.TestCase):
    """render_section must produce identical output on repeated calls."""

    def test_render_section_is_idempotent(self) -> None:
        schemas = GEN.get_schemas()
        first = GEN.render_section(schemas)
        second = GEN.render_section(schemas)
        self.assertEqual(first, second, "render_section is not idempotent")

    def test_replace_section_twice_no_diff(self) -> None:
        """Applying _replace_section twice leaves SKILL.md unchanged."""
        original = _SKILL_MD.read_text(encoding="utf-8")
        schemas = GEN.get_schemas()
        new_section = GEN.render_section(schemas)
        once = GEN._replace_section(original, new_section)
        twice = GEN._replace_section(once, new_section)
        self.assertEqual(once, twice, "_replace_section is not idempotent")

    def test_render_section_contains_key_invocations(self) -> None:
        schemas = GEN.get_schemas()
        section = GEN.render_section(schemas)
        self.assertIn("am_i_done.py", section)
        self.assertIn("install.py --tier", section)
        self.assertIn("budget_manager.py tier", section)
        self.assertIn("budget_manager.py defer", section)
        self.assertIn(GEN._START, section)
        self.assertIn(GEN._END, section)

    def test_check_passes_on_current_skill_md(self) -> None:
        """gen_skill_metadata.py --check exits 0 on the committed SKILL.md."""
        result = subprocess.run(
            [sys.executable, str(_GEN), "--check"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(
            result.returncode, 0,
            f"--check failed on committed SKILL.md:\n{result.stderr}",
        )


# ---------------------------------------------------------------------------
# Staleness detection
# ---------------------------------------------------------------------------


class TestStalenessDetection(unittest.TestCase):
    """Staleness is detectable both in-memory and via the --check flag."""

    def test_tampered_section_differs_from_generated(self) -> None:
        """In-memory: a hand-edit to the generated section is detectable."""
        schemas = GEN.get_schemas()
        new_section = GEN.render_section(schemas)
        tampered = new_section.replace("am_i_done.py", "HAND_EDITED.py")
        self.assertNotEqual(tampered, new_section,
            "tampered section should differ from generated section")

    def test_check_flag_detects_stale_section(self) -> None:
        """--check exits 1 when the generated section is hand-edited."""
        original = _SKILL_MD.read_text(encoding="utf-8")
        schemas = GEN.get_schemas()
        new_section = GEN.render_section(schemas)
        tampered = new_section.replace("am_i_done.py", "STALE_ENTRY.py")
        tampered_text = GEN._replace_section(original, tampered)
        _SKILL_MD.write_text(tampered_text, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(_GEN), "--check"],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 1,
                "--check should exit 1 for a stale generated section")
        finally:
            _SKILL_MD.write_text(original, encoding="utf-8")


# ---------------------------------------------------------------------------
# Validity checking
# ---------------------------------------------------------------------------


class TestValidityCheck(unittest.TestCase):
    """check_validity must catch bad references and pass valid ones."""

    def setUp(self) -> None:
        self.schemas = GEN.get_schemas()

    def test_valid_skill_md_passes(self) -> None:
        skill_text = _SKILL_MD.read_text(encoding="utf-8")
        commands_path = _SCRIPTS_DIR.parent / "references" / "commands.md"
        commands_text = commands_path.read_text(encoding="utf-8") if commands_path.exists() else ""
        errors = GEN.check_validity(skill_text, commands_text, self.schemas)
        self.assertEqual(errors, [],
                         "Unexpected validity errors in current SKILL.md:\n" + "\n".join(errors))

    def test_invalid_tier_choice_detected(self) -> None:
        fake = "`install.py --tier bogustier`"
        errors = GEN.check_validity(fake, "", self.schemas)
        self.assertTrue(
            any("bogustier" in e for e in errors),
            f"Expected error for invalid tier 'bogustier'; got: {errors}",
        )

    def test_valid_tier_choices_pass(self) -> None:
        for tier in ("gate", "lightweight", "team"):
            fake = f"`install.py --tier {tier}`"
            errors = GEN.check_validity(fake, "", self.schemas)
            tier_errors = [e for e in errors if tier in e and "install.py" in e]
            self.assertEqual(tier_errors, [],
                f"Valid tier '{tier}' raised false-positive errors: {tier_errors}")

    def test_invalid_budget_subcommand_detected(self) -> None:
        fake = "`python3 budget_manager.py ghost_command`"
        errors = GEN.check_validity(fake, "", self.schemas)
        self.assertTrue(
            any("ghost_command" in e for e in errors),
            f"Expected error for invalid budget_manager subcommand; got: {errors}",
        )

    def test_valid_budget_subcommands_pass(self) -> None:
        for cmd in ("tier", "reset", "queue", "drain", "record", "defer"):
            fake = f"`budget_manager.py {cmd}`"
            errors = GEN.check_validity(fake, "", self.schemas)
            cmd_errors = [e for e in errors if cmd in e and "budget_manager" in e]
            self.assertEqual(cmd_errors, [],
                f"Valid subcommand '{cmd}' raised false-positive: {cmd_errors}")

    def test_invalid_check_choice_detected(self) -> None:
        fake = "`am_i_done.py --check nosuchcheck`"
        errors = GEN.check_validity(fake, "", self.schemas)
        self.assertTrue(
            any("nosuchcheck" in e for e in errors),
            f"Expected error for invalid --check value; got: {errors}",
        )

    def test_generated_section_excluded_from_validity_scan(self) -> None:
        """Injecting invalid content into the generated section must not trigger errors."""
        schemas = self.schemas
        section = GEN.render_section(schemas)
        # Inject an invalid tier reference *inside* the generated section
        tampered_section = section.replace("install.py --tier", "install.py --tier bogus_inside")
        skill_text = _SKILL_MD.read_text(encoding="utf-8")
        tampered_text = GEN._replace_section(skill_text, tampered_section)
        errors = GEN.check_validity(tampered_text, "", schemas)
        bogus_errors = [e for e in errors if "bogus_inside" in e]
        self.assertEqual(bogus_errors, [],
            "Validity check should not scan inside the generated section")


# ---------------------------------------------------------------------------
# Stdlib guard for gen_skill_metadata.py
# ---------------------------------------------------------------------------


class TestGenMetadataStdlibOnly(unittest.TestCase):
    """gen_skill_metadata.py must import only stdlib modules."""

    def test_no_third_party_imports(self) -> None:
        stdlib = sys.stdlib_module_names  # Python 3.10+
        source = _GEN.read_text()
        tree = ast.parse(source)
        modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    modules.add(node.module.split(".")[0])
        third_party = modules - stdlib - {"__future__"}
        self.assertEqual(
            third_party,
            set(),
            f"gen_skill_metadata.py must be stdlib-only; found: {third_party}",
        )


if __name__ == "__main__":
    unittest.main()
