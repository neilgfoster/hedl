"""Regression guard for WORK-0019 — startup.sh printf format-string safety.

The repo-health 2026-05-28 review flagged a printf format-string injection
(RCE) in .claude/startup.sh. Audit found it non-reproducible: the project
name is passed as a `%s` data argument, never as the format string, so
conversion specifiers in the name are not interpreted. These tests lock that
in across the whole script's dynamic surface, and a negative test proves the
guard would catch a refactor that moved a dynamic value into the format-string
position.

Run: pytest skill/hedl/tests/test_startup_sh.py
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

_STARTUP = (
    pathlib.Path(__file__).resolve().parent.parent
    / "integrations" / "claude-code" / "startup.sh"
)

# Conversion specifiers that would misbehave if the carrying value reached a
# format position: %n (write) and %s (read) are the classic vectors.
_SPEC = "%n%n%s%s"


class TestStartupPrintfSafety(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        (self.tmp / ".work").mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _write_state(self, project: str, *, full: bool = False) -> None:
        """Write the three state files startup.sh reads. When full=True, every
        interpolated field carries the format specifiers so the python-driven
        sections are exercised too — not just the printf line."""
        (self.tmp / ".work" / "context.json").write_text(
            json.dumps({"meta": {"project": project, "phase": 1}}) + "\n"
        )
        if full:
            (self.tmp / ".work" / "work.json").write_text(json.dumps({
                "meta": {"active_item": "WORK-9999"},
                "active": [{
                    "id": "WORK-9999",
                    "title": f"{_SPEC} title",
                    "status": f"{_SPEC} status",
                    "acceptance_criteria": [f"{_SPEC} criterion"],
                }],
                "backlog": [{"id": "WORK-8888", "title": f"{_SPEC} backlog",
                             "dependencies": []}],
            }) + "\n")
            (self.tmp / ".work" / "session.json").write_text(json.dumps({
                "date": f"{_SPEC} date",
                "completed": [f"{_SPEC} done"],
                "blockers": [],
                "next_item": f"{_SPEC} next",
            }) + "\n")

    def _run(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(_STARTUP)],
            cwd=self.tmp, capture_output=True, text=True, timeout=30,
        )

    def test_startup_script_exists(self) -> None:
        self.assertTrue(_STARTUP.exists(), f"missing startup.sh at {_STARTUP}")

    def test_project_name_specifiers_are_literal(self) -> None:
        self._write_state(f"{_SPEC} INJECT")
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stderr)
        # Specifiers appear verbatim -> printf treated the name as data, not format.
        self.assertIn(_SPEC, result.stdout,
                      "project name was not rendered literally — printf may be "
                      "interpreting it as a format string")

    def test_all_dynamic_fields_render_literally(self) -> None:
        # Exercise the python-driven sections too: work-item title/status/
        # criteria and session fields must all surface verbatim.
        self._write_state(f"{_SPEC} INJECT", full=True)
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"{_SPEC} title", result.stdout)
        self.assertIn(f"{_SPEC} done", result.stdout)
        self.assertIn(f"{_SPEC} next", result.stdout)

    def test_guard_catches_vulnerable_printf_form(self) -> None:
        # Negative test: prove the guard has teeth. Rebuild the script with the
        # name moved INTO the format string (the vulnerable form) and confirm
        # the specifiers are NO LONGER rendered literally — i.e. the positive
        # test above would fail on a regression like this.
        lines = _STARTUP.read_text().splitlines()
        mutated, replaced = [], 0
        for ln in lines:
            if "printf" in ln and "%-36s" in ln and "PROJECT_NAME" in ln:
                mutated.append('printf "|  $PROJECT_NAME - SESSION START |\\n"')
                replaced += 1
            else:
                mutated.append(ln)
        self.assertEqual(replaced, 1,
                         "could not locate the printf line to mutate — update "
                         "this guard if startup.sh's banner line changed")
        vuln = self.tmp / "startup_vuln.sh"
        vuln.write_text("\n".join(mutated) + "\n")
        self._write_state(f"{_SPEC} INJECT")
        result = subprocess.run(
            ["bash", str(vuln)],
            cwd=self.tmp, capture_output=True, text=True, timeout=30,
        )
        self.assertNotIn(
            _SPEC, result.stdout,
            "vulnerable name-in-format form still rendered the specifiers "
            "literally — the positive guard cannot distinguish the two forms")

    def test_normal_project_name_renders(self) -> None:
        self._write_state("hedl")
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("hedl", result.stdout)
        self.assertIn("SESSION START", result.stdout)


if __name__ == "__main__":
    unittest.main()
