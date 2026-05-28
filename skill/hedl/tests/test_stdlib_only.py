"""Invariant: consumer-facing scripts must import only the Python standard library.

Parsing is static (ast) so this catches violations before runtime and without
installing anything. Fails with a clear message naming the script and the
offending module.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

CONSUMER_SCRIPTS = [
    "am_i_done.py",
    "budget_manager.py",
    "check_markdown_schema.py",
    "check_pr_template.py",
    "install.py",
    "release.py",
    "reflect.py",
    "contribute.py",
]


def _collect_top_level_imports(source: str) -> set[str]:
    """Return the set of top-level module names imported by the source."""
    tree = ast.parse(source)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.add(node.module.split(".")[0])
    return modules


def test_consumer_scripts_stdlib_only() -> None:
    stdlib = sys.stdlib_module_names  # available in Python 3.10+
    violations: list[str] = []

    for script_name in CONSUMER_SCRIPTS:
        path = SCRIPTS_DIR / script_name
        assert path.exists(), f"Expected script not found: {path}"
        source = path.read_text()
        imports = _collect_top_level_imports(source)
        third_party = imports - stdlib - {"__future__"}
        for mod in sorted(third_party):
            violations.append(f"  {script_name}: imports '{mod}' (not stdlib)")

    assert not violations, (
        "Consumer-facing scripts must be stdlib-only — found third-party imports:\n"
        + "\n".join(violations)
    )
