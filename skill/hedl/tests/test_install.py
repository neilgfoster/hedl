"""Tests for skill/hedl/scripts/install.py.

Covers: tiers.json validity, tier inheritance, gate/lightweight/team install,
idempotency, dry-run, --copy flag, .work/ copy-once protection, --status,
--doctor, tier upgrades, tier downgrades, delta dry-run, archive.

Run: pytest skill/hedl/tests/test_install.py
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

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "install.py"


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("install", _SCRIPT)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _load_module()


def _ns(**kwargs: Any) -> argparse.Namespace:
    defaults: dict[str, Any] = {"tier": None, "status": False, "doctor": False,
                                  "dry_run": False, "copy": True, "repo": "."}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestTiersJson(unittest.TestCase):
    """Verify tiers.json is internally consistent."""

    def setUp(self) -> None:
        self.tiers: Any = M._load_tiers()

    def test_schema_version_present(self) -> None:
        self.assertIn("schema_version", self.tiers)

    def test_three_tiers_exist(self) -> None:
        self.assertEqual(set(self.tiers["tiers"].keys()), {"gate", "lightweight", "team"})

    def test_each_tier_has_description(self) -> None:
        for name, tier in self.tiers["tiers"].items():
            self.assertIn("description", tier, f"tier {name!r} missing description")

    def test_gate_includes_am_i_done(self) -> None:
        targets = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        self.assertIn(".github/scripts/am_i_done.py", targets)

    def test_lightweight_is_superset_of_gate(self) -> None:
        gate = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        lightweight = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        self.assertTrue(gate.issubset(lightweight), f"gate items missing from lightweight: {gate - lightweight}")

    def test_team_is_superset_of_lightweight(self) -> None:
        lw = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        team = {p["target"] for p in M._flatten_projections(self.tiers, "team")}
        self.assertTrue(lw.issubset(team), f"lightweight items missing from team: {lw - team}")

    def test_all_projection_sources_exist_on_disk(self) -> None:
        seen: set[str] = set()
        for tier_name in self.tiers["tiers"]:
            for proj in M._flatten_projections(self.tiers, tier_name):
                src = proj["source"]
                if src in seen:
                    continue
                seen.add(src)
                source_path = M.SKILL_ROOT / src
                self.assertTrue(source_path.exists(), f"source missing: {src!r}")

    def test_no_duplicate_targets_within_tier(self) -> None:
        for tier_name in ("gate", "lightweight", "team"):
            targets = [p["target"] for p in M._flatten_projections(self.tiers, tier_name)]
            self.assertEqual(len(targets), len(set(targets)),
                             f"duplicate targets in tier {tier_name!r}")

    def test_lightweight_has_work_state_init(self) -> None:
        inits = M._flatten_inits(self.tiers, "lightweight")
        self.assertTrue(any(e["target"] == ".work" for e in inits))


class TestGateTierInstall(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _args(self, **kwargs: Any) -> argparse.Namespace:
        return _ns(tier="gate", repo=str(self.tmp), **kwargs)

    def test_creates_am_i_done(self) -> None:
        rc = M.cmd_install(self._args())
        self.assertEqual(rc, 0)
        self.assertTrue((self.tmp / ".github/scripts/am_i_done.py").exists())

    def test_creates_tier_marker(self) -> None:
        M.cmd_install(self._args())
        marker = self.tmp / ".hedl-tier"
        self.assertTrue(marker.exists())
        data = json.loads(marker.read_text())
        self.assertEqual(data["tier"], "gate")

    def test_dry_run_writes_nothing(self) -> None:
        M.cmd_install(self._args(dry_run=True))
        self.assertFalse((self.tmp / ".github/scripts/am_i_done.py").exists())
        self.assertFalse((self.tmp / ".hedl-tier").exists())

    def test_idempotent(self) -> None:
        M.cmd_install(self._args())
        rc = M.cmd_install(self._args())
        self.assertEqual(rc, 0)
        self.assertTrue((self.tmp / ".github/scripts/am_i_done.py").exists())

    def test_copy_flag_produces_regular_file(self) -> None:
        M.cmd_install(self._args(copy=True))
        target = self.tmp / ".github/scripts/am_i_done.py"
        self.assertTrue(target.exists())
        self.assertFalse(target.is_symlink())

    def test_default_produces_symlink(self) -> None:
        M.cmd_install(self._args(copy=False))
        target = self.tmp / ".github/scripts/am_i_done.py"
        self.assertTrue(target.is_symlink())

    def test_symlink_resolves_to_correct_source(self) -> None:
        M.cmd_install(self._args(copy=False))
        target = self.tmp / ".github/scripts/am_i_done.py"
        expected = (M.SKILL_ROOT / "scripts/am_i_done.py").resolve()
        self.assertEqual(target.resolve(), expected)

    def test_all_gate_projections_created(self) -> None:
        M.cmd_install(self._args())
        tiers = M._load_tiers()
        for proj in M._flatten_projections(tiers, "gate"):
            self.assertTrue((self.tmp / proj["target"]).exists(),
                            f"missing: {proj['target']}")


class TestLightweightTierInstall(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _args(self, **kwargs: Any) -> argparse.Namespace:
        return _ns(tier="lightweight", repo=str(self.tmp), **kwargs)

    def test_includes_gate_files(self) -> None:
        M.cmd_install(self._args())
        self.assertTrue((self.tmp / ".github/scripts/am_i_done.py").exists())

    def test_creates_work_state(self) -> None:
        M.cmd_install(self._args())
        self.assertTrue((self.tmp / ".work").is_dir())

    def test_work_state_contains_work_json(self) -> None:
        M.cmd_install(self._args())
        self.assertTrue((self.tmp / ".work/work.json").exists())

    def test_work_dir_not_overwritten_on_rerun(self) -> None:
        M.cmd_install(self._args())
        sentinel = self.tmp / ".work/DO_NOT_DELETE"
        sentinel.write_text("user data")
        M.cmd_install(self._args())
        self.assertTrue(sentinel.exists(), ".work/ was destructively overwritten")

    def test_creates_slash_commands(self) -> None:
        M.cmd_install(self._args())
        self.assertTrue((self.tmp / ".claude/commands/start-session.md").exists())

    def test_creates_agents(self) -> None:
        M.cmd_install(self._args())
        self.assertTrue((self.tmp / ".claude/agents/scope-auditor.md").exists())

    def test_creates_spec_templates(self) -> None:
        M.cmd_install(self._args())
        self.assertTrue((self.tmp / "docs/spec/prd-template.md").exists())


class TestStatusAndDoctor(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _repo_args(self) -> argparse.Namespace:
        return _ns(repo=str(self.tmp))

    def test_status_no_installation(self) -> None:
        rc = M.cmd_status(self._repo_args())
        self.assertEqual(rc, 0)

    def test_status_after_gate_install(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        rc = M.cmd_status(self._repo_args())
        self.assertEqual(rc, 0)

    def test_doctor_no_marker(self) -> None:
        rc = M.cmd_doctor(self._repo_args())
        self.assertEqual(rc, 0)

    def test_doctor_passes_after_gate_install(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        rc = M.cmd_doctor(self._repo_args())
        self.assertEqual(rc, 0)

    def test_doctor_fails_on_broken_projection(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp), copy=False))
        # Snap the symlink by removing the target's parent directory
        broken = self.tmp / ".github/scripts/am_i_done.py"
        broken.unlink()
        broken.symlink_to("/nonexistent/am_i_done.py")
        rc = M.cmd_doctor(self._repo_args())
        self.assertEqual(rc, 1)


class TestTierUpgrades(unittest.TestCase):
    """Upgrade paths: gate->lightweight->team, idempotent re-run."""

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.tiers: Any = M._load_tiers()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _gate_only(self) -> set[str]:
        gate = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        lw = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        return gate - lw

    def test_upgrade_gate_to_lightweight_adds_exactly_missing_projections(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        gate_targets = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        lw_targets = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        lw_only = lw_targets - gate_targets

        for t in lw_only:
            self.assertFalse((self.tmp / t).exists(), f"lw projection present before upgrade: {t}")

        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))

        for t in lw_targets:
            self.assertTrue((self.tmp / t).exists(), f"missing after upgrade: {t}")

    def test_upgrade_lightweight_to_team_adds_exactly_missing_projections(self) -> None:
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        lw_targets = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        team_targets = {p["target"] for p in M._flatten_projections(self.tiers, "team")}
        team_only = team_targets - lw_targets

        for t in team_only:
            self.assertFalse((self.tmp / t).exists(), f"team projection present before upgrade: {t}")

        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))

        for t in team_targets:
            self.assertTrue((self.tmp / t).exists(), f"missing after upgrade: {t}")

    def test_upgrade_gate_to_team_in_one_step(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))
        team_targets = {p["target"] for p in M._flatten_projections(self.tiers, "team")}
        for t in team_targets:
            self.assertTrue((self.tmp / t).exists(), f"missing after upgrade: {t}")

    def test_idempotent_rerun_same_tier(self) -> None:
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        sentinel = self.tmp / ".work" / "DO_NOT_DELETE"
        sentinel.write_text("user data")
        rc = M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        self.assertEqual(rc, 0)
        self.assertTrue(sentinel.exists(), ".work/ user data was touched by idempotent re-run")

    def test_tier_marker_updated_on_upgrade(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        data = json.loads((self.tmp / ".hedl-tier").read_text())
        self.assertEqual(data["tier"], "gate")
        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))
        data = json.loads((self.tmp / ".hedl-tier").read_text())
        self.assertEqual(data["tier"], "team")


class TestTierDowngrades(unittest.TestCase):
    """Downgrade paths: team->lightweight->gate, archive of .work/."""

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.tiers: Any = M._load_tiers()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_downgrade_team_to_lightweight_removes_team_projections(self) -> None:
        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))
        lw_targets = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        team_targets = {p["target"] for p in M._flatten_projections(self.tiers, "team")}
        team_only = team_targets - lw_targets

        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))

        for t in team_only:
            self.assertFalse((self.tmp / t).exists(), f"team projection still present: {t}")
        for t in lw_targets:
            self.assertTrue((self.tmp / t).exists(), f"lw projection removed by mistake: {t}")

    def test_downgrade_team_to_lightweight_preserves_work_dir(self) -> None:
        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))
        sentinel = self.tmp / ".work" / "user.txt"
        sentinel.write_text("important")
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        # .work/ is still part of lightweight — must not be archived
        self.assertTrue(sentinel.exists(), ".work/ was touched on team->lightweight downgrade")
        self.assertFalse((self.tmp / ".work" / "archive").exists())

    def test_downgrade_lightweight_to_gate_removes_lw_projections(self) -> None:
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        gate_targets = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        lw_targets = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        lw_only = lw_targets - gate_targets

        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))

        for t in lw_only:
            self.assertFalse((self.tmp / t).exists(), f"lw projection still present: {t}")
        for t in gate_targets:
            self.assertTrue((self.tmp / t).exists(), f"gate projection removed by mistake: {t}")

    def test_downgrade_lightweight_to_gate_archives_work_dir(self) -> None:
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        sentinel = self.tmp / ".work" / "important.txt"
        sentinel.write_text("user data")
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))

        archive_base = self.tmp / ".work" / "archive"
        self.assertTrue(archive_base.exists(), ".work/archive/ not created on downgrade")
        timestamp_dirs = list(archive_base.iterdir())
        self.assertEqual(len(timestamp_dirs), 1, "expected exactly one archive timestamp dir")
        archived_sentinel = timestamp_dirs[0] / "important.txt"
        self.assertTrue(archived_sentinel.exists(), "user data not found in archive")
        self.assertEqual(archived_sentinel.read_text(), "user data")

    def test_downgrade_to_gate_archives_work_json(self) -> None:
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        archive_base = self.tmp / ".work" / "archive"
        timestamp_dirs = list(archive_base.iterdir())
        archived_work = timestamp_dirs[0] / "work.json"
        self.assertTrue(archived_work.exists(), "work.json not found in archive")

    def test_downgrade_team_to_gate_removes_all_non_gate_projections(self) -> None:
        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))
        gate_targets = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        team_targets = {p["target"] for p in M._flatten_projections(self.tiers, "team")}
        non_gate = team_targets - gate_targets

        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))

        for t in non_gate:
            self.assertFalse((self.tmp / t).exists(), f"non-gate projection still present: {t}")
        for t in gate_targets:
            self.assertTrue((self.tmp / t).exists(), f"gate projection removed by mistake: {t}")

    def test_tier_marker_updated_on_downgrade(self) -> None:
        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        data = json.loads((self.tmp / ".hedl-tier").read_text())
        self.assertEqual(data["tier"], "gate")

    def test_downgrade_never_deletes_state(self) -> None:
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        work_json_content = (self.tmp / ".work" / "work.json").read_bytes()
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        # work.json must be reachable somewhere under .work/archive/
        found = list((self.tmp / ".work" / "archive").rglob("work.json"))
        self.assertTrue(found, "work.json vanished — state was deleted, not archived")
        self.assertEqual(found[0].read_bytes(), work_json_content)


class TestDryRunDelta(unittest.TestCase):
    """--dry-run prints accurate delta and writes nothing."""

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.tiers: Any = M._load_tiers()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _run(self, **kwargs: Any) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.cmd_install(_ns(repo=str(self.tmp), **kwargs))
        return rc, buf.getvalue()

    def test_dry_run_downgrade_writes_nothing(self) -> None:
        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))
        team_targets = {p["target"] for p in M._flatten_projections(self.tiers, "team")}

        self._run(tier="gate", dry_run=True)

        for t in team_targets:
            self.assertTrue((self.tmp / t).exists(), f"dry-run removed projection: {t}")
        self.assertFalse((self.tmp / ".work" / "archive").exists(),
                         "dry-run created archive")
        data = json.loads((self.tmp / ".hedl-tier").read_text())
        self.assertEqual(data["tier"], "team", "dry-run updated .hedl-tier")

    def test_dry_run_downgrade_output_is_accurate(self) -> None:
        M.cmd_install(_ns(tier="team", repo=str(self.tmp)))
        _, output = self._run(tier="gate", dry_run=True)
        self.assertIn("would remove", output)
        self.assertIn("would archive", output)

    def test_dry_run_upgrade_writes_nothing(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp)))
        gate_targets = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        lw_targets = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        lw_only = lw_targets - gate_targets

        self._run(tier="lightweight", dry_run=True)

        for t in lw_only:
            self.assertFalse((self.tmp / t).exists(), f"dry-run created projection: {t}")
        data = json.loads((self.tmp / ".hedl-tier").read_text())
        self.assertEqual(data["tier"], "gate", "dry-run updated .hedl-tier")

    def test_dry_run_idempotent_writes_nothing(self) -> None:
        M.cmd_install(_ns(tier="lightweight", repo=str(self.tmp)))
        sentinel = self.tmp / ".work" / "sentinel.txt"
        sentinel.write_text("preserved")
        self._run(tier="lightweight", dry_run=True)
        self.assertTrue(sentinel.exists())


class TestComputeDowngradeDelta(unittest.TestCase):
    """Unit tests for _compute_downgrade_delta."""

    def setUp(self) -> None:
        self.tiers: Any = M._load_tiers()

    def test_team_to_lightweight_delta(self) -> None:
        to_remove, to_archive = M._compute_downgrade_delta(self.tiers, "team", "lightweight")
        team_targets = {p["target"] for p in M._flatten_projections(self.tiers, "team")}
        lw_targets = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        self.assertEqual(set(to_remove), team_targets - lw_targets)
        self.assertEqual(to_archive, [])

    def test_lightweight_to_gate_delta(self) -> None:
        to_remove, to_archive = M._compute_downgrade_delta(self.tiers, "lightweight", "gate")
        lw_targets = {p["target"] for p in M._flatten_projections(self.tiers, "lightweight")}
        gate_targets = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        self.assertEqual(set(to_remove), lw_targets - gate_targets)
        self.assertEqual(to_archive, [".work"])

    def test_team_to_gate_delta(self) -> None:
        to_remove, to_archive = M._compute_downgrade_delta(self.tiers, "team", "gate")
        team_targets = {p["target"] for p in M._flatten_projections(self.tiers, "team")}
        gate_targets = {p["target"] for p in M._flatten_projections(self.tiers, "gate")}
        self.assertEqual(set(to_remove), team_targets - gate_targets)
        self.assertEqual(to_archive, [".work"])
