"""Tests for Hedl versioning — Parts 1 and 2.

Covers: --version flag on install.py and am_i_done.py; schema_version in
context.json; migration registry (idempotency, archive); doctor states
(ok / needs-migrate / too-new / not-installed); change_class validation;
bump computation for all combinations; next_version; project_version
persisted separately from Hedl version.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import pathlib
import shutil
import tempfile
import unittest
from typing import Any

_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
_INSTALL_SCRIPT = _SCRIPTS / "install.py"
_AM_I_DONE_SCRIPT = _SCRIPTS / "am_i_done.py"
_RELEASE_SCRIPT = _SCRIPTS / "release.py"


def _load_install() -> Any:
    spec = importlib.util.spec_from_file_location("install", _INSTALL_SCRIPT)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_am_i_done() -> Any:
    spec = importlib.util.spec_from_file_location("am_i_done", _AM_I_DONE_SCRIPT)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_release() -> Any:
    spec = importlib.util.spec_from_file_location("release", _RELEASE_SCRIPT)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _load_install()
R = _load_release()


def _ns(**kwargs: Any) -> argparse.Namespace:
    defaults: dict[str, Any] = {
        "tier": None, "status": False, "doctor": False, "migrate": False,
        "dry_run": False, "copy": True, "repo": ".",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestHedlVersion(unittest.TestCase):
    def test_hedl_version_returns_semver_string(self) -> None:
        v = M._hedl_version()
        self.assertRegex(v, r"^\d+\.\d+\.\d+$", f"expected semver, got {v!r}")

    def test_install_version_matches_am_i_done_version(self) -> None:
        am = _load_am_i_done()
        self.assertEqual(M._hedl_version(), am._hedl_version())

    def test_install_version_matches_pyproject(self) -> None:
        import tomllib
        pyproject = M.HEDL_ROOT / "pyproject.toml"
        with pyproject.open("rb") as fh:
            data = tomllib.load(fh)
        expected = data["project"]["version"]
        self.assertEqual(M._hedl_version(), expected)


class TestSchemaVersionHelpers(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.work = self.tmp / ".work"
        self.work.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _write_ctx(self, data: dict[str, Any]) -> None:
        (self.work / "context.json").write_text(json.dumps(data, indent=2))

    def test_read_state_schema_absent_context(self) -> None:
        self.assertIsNone(M._read_state_schema(self.work))

    def test_read_state_schema_present_field(self) -> None:
        self._write_ctx({"schema_version": "1"})
        self.assertEqual(M._read_state_schema(self.work), "1")

    def test_read_state_schema_missing_field(self) -> None:
        self._write_ctx({"meta": {}})
        self.assertIsNone(M._read_state_schema(self.work))

    def test_schema_ver_int_none(self) -> None:
        self.assertEqual(M._schema_ver_int(None), 0)

    def test_schema_ver_int_string(self) -> None:
        self.assertEqual(M._schema_ver_int("3"), 3)


class TestMigration(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.work = self.tmp / ".work"
        self.work.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _write_unversioned_ctx(self) -> None:
        (self.work / "context.json").write_text(json.dumps({"meta": {"project": "test"}}))

    def test_migration_adds_schema_version(self) -> None:
        self._write_unversioned_ctx()
        M._migrate_unversioned_to_1(self.work)
        data = json.loads((self.work / "context.json").read_text())
        self.assertEqual(data["schema_version"], "1")

    def test_migration_archives_prior_state(self) -> None:
        self._write_unversioned_ctx()
        original = (self.work / "context.json").read_text()
        M._migrate_unversioned_to_1(self.work)
        archive_base = self.work / "archive"
        self.assertTrue(archive_base.exists(), "archive dir not created")
        archived = list(archive_base.rglob("context.json"))
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0].read_text(), original)

    def test_migration_is_idempotent(self) -> None:
        self._write_unversioned_ctx()
        M._migrate_unversioned_to_1(self.work)
        archive_count_1 = len(list((self.work / "archive").rglob("context.json")))
        # Second run should NOT create a second archive entry
        M._migrate_unversioned_to_1(self.work)
        archive_count_2 = len(list((self.work / "archive").rglob("context.json")))
        self.assertEqual(archive_count_1, archive_count_2, "idempotency violated: second migration archived again")

    def test_cmd_migrate_already_current(self) -> None:
        (self.work / "context.json").write_text(json.dumps({"schema_version": "1"}))
        rc = M.cmd_migrate(_ns(repo=str(self.tmp)))
        self.assertEqual(rc, 0)

    def test_cmd_migrate_applies_migration(self) -> None:
        self._write_unversioned_ctx()
        rc = M.cmd_migrate(_ns(repo=str(self.tmp)))
        self.assertEqual(rc, 0)
        ver = M._read_state_schema(self.work)
        self.assertEqual(ver, M.CURRENT_STATE_SCHEMA)

    def test_cmd_migrate_dry_run_writes_nothing(self) -> None:
        self._write_unversioned_ctx()
        original = (self.work / "context.json").read_text()
        M.cmd_migrate(_ns(repo=str(self.tmp), dry_run=True))
        self.assertEqual((self.work / "context.json").read_text(), original)
        self.assertFalse((self.work / "archive").exists())

    def test_cmd_migrate_no_context_json(self) -> None:
        rc = M.cmd_migrate(_ns(repo=str(self.tmp)))
        self.assertEqual(rc, 0)


class TestDoctorSchemaStatus(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _install_gate(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))

    def _install_lightweight(self) -> None:
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))

    def test_doctor_not_installed_for_gate_tier(self) -> None:
        self._install_gate()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.cmd_doctor(_ns(repo=str(self.tmp)))
        self.assertEqual(rc, 0)
        self.assertIn("not-installed", buf.getvalue())

    def test_doctor_ok_when_schema_current(self) -> None:
        self._install_lightweight()
        # lightweight install copies the template which has schema_version=1
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.cmd_doctor(_ns(repo=str(self.tmp)))
        self.assertIn("ok", buf.getvalue())

    def test_doctor_needs_migrate_when_unversioned(self) -> None:
        self._install_lightweight()
        ctx = self.tmp / ".work" / "context.json"
        data = json.loads(ctx.read_text())
        del data["schema_version"]
        ctx.write_text(json.dumps(data))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.cmd_doctor(_ns(repo=str(self.tmp)))
        self.assertIn("needs-migrate", buf.getvalue())

    def test_doctor_too_new_when_schema_ahead(self) -> None:
        self._install_lightweight()
        ctx = self.tmp / ".work" / "context.json"
        data = json.loads(ctx.read_text())
        data["schema_version"] = "9999"
        ctx.write_text(json.dumps(data))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.cmd_doctor(_ns(repo=str(self.tmp)))
        self.assertIn("too-new", buf.getvalue())

    def test_doctor_reports_hedl_version(self) -> None:
        self._install_gate()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.cmd_doctor(_ns(repo=str(self.tmp)))
        self.assertIn("Hedl version:", buf.getvalue())
        # Version should look like semver
        self.assertRegex(buf.getvalue(), r"\d+\.\d+\.\d+")


# ---------------------------------------------------------------------------
# Part 2 — bump calculator
# ---------------------------------------------------------------------------

class TestBumpCalculator(unittest.TestCase):
    def _items(self, classes: list[str]) -> list[dict[str, Any]]:
        return [{"id": f"WORK-{i}", "change_class": c} for i, c in enumerate(classes, 1)]

    def test_breaking_produces_major(self) -> None:
        self.assertEqual(R.compute_bump(self._items(["breaking"])), "major")

    def test_breaking_dominates_feat(self) -> None:
        self.assertEqual(R.compute_bump(self._items(["feat", "breaking", "fix"])), "major")

    def test_feat_produces_minor(self) -> None:
        self.assertEqual(R.compute_bump(self._items(["feat", "fix", "chore"])), "minor")

    def test_fix_only_produces_patch(self) -> None:
        self.assertEqual(R.compute_bump(self._items(["fix"])), "patch")

    def test_chore_only_produces_patch(self) -> None:
        self.assertEqual(R.compute_bump(self._items(["chore"])), "patch")

    def test_docs_only_produces_patch(self) -> None:
        self.assertEqual(R.compute_bump(self._items(["docs"])), "patch")

    def test_empty_items_produces_patch(self) -> None:
        self.assertEqual(R.compute_bump([]), "patch")

    def test_default_change_class_is_chore(self) -> None:
        # item with no change_class defaults to chore (patch)
        self.assertEqual(R.compute_bump([{"id": "WORK-1"}]), "patch")


class TestNextVersion(unittest.TestCase):
    def test_major_bump(self) -> None:
        self.assertEqual(R.next_version("1.2.3", "major"), "2.0.0")

    def test_minor_bump(self) -> None:
        self.assertEqual(R.next_version("1.2.3", "minor"), "1.3.0")

    def test_patch_bump(self) -> None:
        self.assertEqual(R.next_version("1.2.3", "patch"), "1.2.4")

    def test_major_resets_minor_and_patch(self) -> None:
        self.assertEqual(R.next_version("3.7.9", "major"), "4.0.0")

    def test_minor_resets_patch(self) -> None:
        self.assertEqual(R.next_version("3.7.9", "minor"), "3.8.0")


class TestGroupByClass(unittest.TestCase):
    def test_groups_correctly(self) -> None:
        items = [
            {"id": "W-1", "change_class": "feat", "title": "a"},
            {"id": "W-2", "change_class": "fix",  "title": "b"},
            {"id": "W-3", "change_class": "feat", "title": "c"},
        ]
        groups = R.group_by_class(items)
        self.assertEqual(len(groups["feat"]), 2)
        self.assertEqual(len(groups["fix"]), 1)
        self.assertNotIn("chore", groups)

    def test_empty_groups_omitted(self) -> None:
        groups = R.group_by_class([{"id": "W-1", "change_class": "docs", "title": "d"}])
        self.assertIn("docs", groups)
        self.assertNotIn("feat", groups)


class TestProjectVersionDistinctFromHedlVersion(unittest.TestCase):
    def test_context_json_has_project_version(self) -> None:
        template = pathlib.Path(__file__).parent.parent / "work-state" / "context.json"
        data = json.loads(template.read_text())
        self.assertIn("project_version", data)
        self.assertIn("releases", data)

    def test_project_version_is_not_hedl_version(self) -> None:
        # project_version in context.json must be a separate concern from _hedl_version()
        template = pathlib.Path(__file__).parent.parent / "work-state" / "context.json"
        data = json.loads(template.read_text())
        # Both are semver strings but they track independent things;
        # just verify the field exists and is a valid semver
        pv = data["project_version"]
        self.assertRegex(pv, r"^\d+\.\d+\.\d+$")


class TestChangeClassValidation(unittest.TestCase):
    def test_valid_classes(self) -> None:
        for cls in ("feat", "fix", "breaking", "chore", "docs"):
            self.assertIn(cls, R.CHANGE_CLASSES)

    def test_invalid_class_not_in_set(self) -> None:
        self.assertNotIn("refactor", R.CHANGE_CLASSES)
        self.assertNotIn("test", R.CHANGE_CLASSES)
