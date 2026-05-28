"""Tests for the /contribute flow — Part 5.

Covers: scrub rejects diffs containing non-framework files; scrub accepts
diffs with only skill/hedl/ files; semver classification matches the
compatibility contract; remote actions are not executed in tests; the
flow does not proceed to merge.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest
from typing import Any

_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
_CONTRIBUTE_SCRIPT = _SCRIPTS / "contribute.py"


def _load_contribute() -> Any:
    spec = importlib.util.spec_from_file_location("contribute", _CONTRIBUTE_SCRIPT)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = _load_contribute()


class TestScrubDiff(unittest.TestCase):
    def test_clean_when_all_framework_files(self) -> None:
        files = [
            "skill/hedl/scripts/am_i_done.py",
            "skill/hedl/agents/security-auditor.md",
            "skill/hedl/references/commands.md",
        ]
        clean, violations = C.scrub_diff(files)
        self.assertTrue(clean)
        self.assertEqual(violations, [])

    def test_violation_on_non_framework_file(self) -> None:
        files = [
            "skill/hedl/scripts/am_i_done.py",
            "README.md",
        ]
        clean, violations = C.scrub_diff(files)
        self.assertFalse(clean)
        self.assertIn("README.md", violations)

    def test_violation_on_consumer_source_file(self) -> None:
        files = [
            "skill/hedl/scripts/release.py",
            "src/consumer_code.py",
        ]
        clean, violations = C.scrub_diff(files)
        self.assertFalse(clean)
        self.assertIn("src/consumer_code.py", violations)

    def test_violation_on_work_state_file(self) -> None:
        files = [
            "skill/hedl/scripts/am_i_done.py",
            ".work/context.json",
        ]
        clean, violations = C.scrub_diff(files)
        self.assertFalse(clean)
        self.assertIn(".work/context.json", violations)

    def test_clean_on_empty_diff(self) -> None:
        clean, violations = C.scrub_diff([])
        self.assertTrue(clean)
        self.assertEqual(violations, [])

    def test_multiple_violations_all_reported(self) -> None:
        files = [
            "skill/hedl/scripts/am_i_done.py",
            "README.md",
            ".github/workflows/ci.yml",
            "docs/external.md",
        ]
        clean, violations = C.scrub_diff(files)
        self.assertFalse(clean)
        self.assertEqual(len(violations), 3)
        self.assertNotIn("skill/hedl/scripts/am_i_done.py", violations)

    def test_framework_prefix_required_exactly(self) -> None:
        # "skill/hedl-fork/" must NOT pass
        files = ["skill/hedl-fork/scripts/some.py"]
        clean, violations = C.scrub_diff(files)
        self.assertFalse(clean)

    def test_nested_framework_path_clean(self) -> None:
        files = ["skill/hedl/integrations/claude-code/scripts/record_insights.py"]
        clean, violations = C.scrub_diff(files)
        self.assertTrue(clean)


class TestClassifyChange(unittest.TestCase):
    def test_major_signals(self) -> None:
        for signal in C.MAJOR_SIGNALS:
            bump = C.classify_change(signal)
            self.assertEqual(bump, "major", f"Expected major for {signal!r}, got {bump!r}")

    def test_minor_signals(self) -> None:
        for signal in C.MINOR_SIGNALS:
            bump = C.classify_change(signal)
            self.assertEqual(bump, "minor", f"Expected minor for {signal!r}, got {bump!r}")

    def test_patch_for_unlisted_signal(self) -> None:
        self.assertEqual(C.classify_change("fix-typo"), "patch")
        self.assertEqual(C.classify_change("update-doc"), "patch")

    def test_major_signals_include_contract_items(self) -> None:
        """Verify the contract from docs/versioning.md is covered."""
        required_major = {
            "hedl-toml-schema-break",
            "work-state-schema-break",
            "gate-exit-code-change",
            "tier-layout-break",
            "command-removed",
            "agent-removed",
        }
        self.assertTrue(required_major.issubset(C.MAJOR_SIGNALS))

    def test_minor_signals_include_contract_items(self) -> None:
        required_minor = {
            "new-reviewer",
            "new-tier",
            "new-check",
            "new-optional-config",
            "new-command",
        }
        self.assertTrue(required_minor.issubset(C.MINOR_SIGNALS))


class TestNoRemoteActionsInTests(unittest.TestCase):
    """The contribute.py module must not import or invoke any remote-action tools."""

    def test_no_subprocess_in_scrub_or_classify(self) -> None:
        """scrub_diff and classify_change are pure functions — no subprocess."""
        import subprocess
        from unittest import mock
        with mock.patch.object(subprocess, "run", side_effect=AssertionError("subprocess called!")):
            # These must complete without calling subprocess
            clean, _ = C.scrub_diff(["skill/hedl/scripts/am_i_done.py"])
            bump = C.classify_change("new-reviewer")
        self.assertTrue(clean)
        self.assertEqual(bump, "minor")

    def test_no_merge_step_in_module(self) -> None:
        """Verify the module contains no 'merge' CLI invocation logic."""
        source = _CONTRIBUTE_SCRIPT.read_text()
        # Must not contain gh pr merge or git merge calls
        self.assertNotIn("gh pr merge", source)
        self.assertNotIn("git merge", source)

    def test_no_push_without_confirmation_in_module(self) -> None:
        """The module must not hardcode a remote push — operator confirms first."""
        source = _CONTRIBUTE_SCRIPT.read_text()
        # Must not contain unconditional push commands
        self.assertNotIn("git push", source)

    def test_contribute_cli_spec_has_no_push_command(self) -> None:
        """CLI_SPEC must not expose a push/merge command."""
        spec_json = json.dumps(C.CLI_SPEC)
        self.assertNotIn("push", spec_json.lower().replace("gh pr create", ""))
        self.assertNotIn("merge", spec_json.lower())
