"""Tests for check_docs_index -- orphan-doc detection gate check.

Verifies: an unlinked doc fails; a fully-linked state passes; the check is
deterministic (same inputs always produce the same result).
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import sys
import tempfile
from typing import Any
from unittest import mock

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "am_i_done.py"


def _load_module() -> Any:
    if "am_i_done" in sys.modules:
        return sys.modules["am_i_done"]
    spec = importlib.util.spec_from_file_location("am_i_done", _SCRIPT)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    sys.modules["am_i_done"] = mod
    spec.loader.exec_module(mod)
    return mod


M = _load_module()


def _make_repo(readme_content: str, docs: list[str]) -> str:
    """Write README.md and docs into a temp directory; return the directory path.

    Includes a skill/hedl/ marker so check_docs_index treats the fixture as the
    framework source repo (WORK-0061 added an adopter-repo skip keyed on that
    directory's absence)."""
    tmpdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmpdir, "skill", "hedl"), exist_ok=True)
    with open(os.path.join(tmpdir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(readme_content)
    for doc in docs:
        full = os.path.join(tmpdir, doc)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(f"# {doc}\n")
    return tmpdir


class TestCheckDocsIndex:
    def test_unlinked_doc_fails(self) -> None:
        tmpdir = _make_repo("# README\n\nNo links here.\n", ["docs/orphan.md"])
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        assert result is not None
        assert not result.passed
        assert "orphan.md" in result.detail
        assert "1 doc" in result.message

    def test_linked_doc_passes(self) -> None:
        tmpdir = _make_repo(
            "# README\n\n[Linked](docs/linked.md)\n",
            ["docs/linked.md"],
        )
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        assert result is not None
        assert result.passed

    def test_multiple_unlinked_all_reported(self) -> None:
        tmpdir = _make_repo("# README\n", ["docs/a.md", "docs/b.md", "docs/c.md"])
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        assert result is not None
        assert not result.passed
        assert "3 doc" in result.message

    def test_partial_links_reports_only_orphans(self) -> None:
        tmpdir = _make_repo(
            "# README\n\n[A](docs/a.md)\n",
            ["docs/a.md", "docs/b.md"],
        )
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        assert result is not None
        assert not result.passed
        assert "docs/b.md" in result.detail
        assert "docs/a.md" not in result.detail

    def test_missing_readme_fails(self) -> None:
        tmpdir = tempfile.mkdtemp()
        # Framework-repo marker so the adopter-skip guard (WORK-0061) does not fire.
        os.makedirs(os.path.join(tmpdir, "skill", "hedl"), exist_ok=True)
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        assert result is not None
        assert not result.passed
        assert "README" in result.message

    def test_anchor_fragment_stripped_from_link(self) -> None:
        tmpdir = _make_repo(
            "# README\n\n[Section](docs/guide.md#section)\n",
            ["docs/guide.md"],
        )
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        assert result is not None
        assert result.passed

    def test_external_links_ignored(self) -> None:
        tmpdir = _make_repo(
            "# README\n\n[External](https://example.com)\n",
            ["docs/local.md"],
        )
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        assert result is not None
        assert not result.passed
        assert "local.md" in result.detail

    def test_deterministic_on_repeated_calls(self) -> None:
        tmpdir = _make_repo(
            "# README\n\n[A](docs/a.md)\n",
            ["docs/a.md", "docs/b.md"],
        )
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            r1 = M.check_docs_index()
            r2 = M.check_docs_index()
        assert r1.passed == r2.passed
        assert r1.message == r2.message
        assert r1.detail == r2.detail

    def test_no_docs_dir_passes(self) -> None:
        tmpdir = _make_repo("# README\n\nNo docs.\n", [])
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        assert result is not None
        assert result.passed

    def test_symlink_deduplication(self) -> None:
        tmpdir = _make_repo(
            "# README\n\n[Canonical](docs/real.md)\n",
            ["docs/real.md"],
        )
        # Create a symlink docs/alias.md -> docs/real.md
        os.symlink(
            os.path.join(tmpdir, "docs", "real.md"),
            os.path.join(tmpdir, "docs", "alias.md"),
        )
        with mock.patch.object(M, "REPO_ROOT", tmpdir):
            result = M.check_docs_index()
        # alias.md points to the same inode as real.md; linking real.md covers both
        assert result is not None
        assert result.passed
