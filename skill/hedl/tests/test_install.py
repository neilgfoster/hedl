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
from unittest import mock

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

    def test_fresh_install_reproduces_work_state_from_template(self) -> None:
        """AC4 (WORK-0025): a fresh install materialises .work/ as a faithful
        byte-for-byte copy of the skill/hedl/work-state/ template."""
        import os as _os
        M.cmd_install(self._args())
        template_root = M.SKILL_ROOT / "work-state"
        live_root = self.tmp / ".work"
        compared = 0
        for dirpath, _dirs, filenames in _os.walk(template_root):
            for fn in filenames:
                src = pathlib.Path(dirpath) / fn
                rel = src.relative_to(template_root)
                dst = live_root / rel
                self.assertTrue(dst.exists(), f"{rel} not reproduced in .work/")
                self.assertEqual(
                    src.read_bytes(), dst.read_bytes(),
                    f"{rel} differs between template and fresh .work/",
                )
                compared += 1
        self.assertGreater(compared, 0, "no template files compared")


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


class TestTierMarkerContract(unittest.TestCase):
    """WORK-0016: .hedl-tier records only the tier — no absolute skill path.

    The marker is per-installation state (git-ignored, regenerated on each
    install). It must never carry the installing machine's absolute layout,
    and a fresh clone (no marker present) must install + pass the install-side
    health checks across every tier without manual edits.
    """

    TIERS = ("gate", "lightweight", "team")

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_marker_records_only_tier(self) -> None:
        for tier in self.TIERS:
            with self.subTest(tier=tier):
                repo = self.tmp / tier
                repo.mkdir()
                M.cmd_install(_ns(tier=tier, repo=str(repo)))
                data = json.loads((repo / ".hedl-tier").read_text())
                self.assertEqual(data, {"tier": tier},
                                 "marker must contain only the tier key")
                self.assertNotIn("skill", data, "dead absolute skill path must be gone")

    def test_marker_contains_no_absolute_path(self) -> None:
        # Regression guard: the original defect committed a hardcoded developer
        # absolute path. No marker value may be an absolute path on any OS.
        for tier in self.TIERS:
            with self.subTest(tier=tier):
                repo = self.tmp / tier
                repo.mkdir()
                M.cmd_install(_ns(tier=tier, repo=str(repo)))
                data = json.loads((repo / ".hedl-tier").read_text())
                for key, value in data.items():
                    if not isinstance(value, str):
                        continue
                    self.assertFalse(
                        pathlib.PurePosixPath(value).is_absolute(),
                        f"marker[{key!r}]={value!r} is a POSIX absolute path",
                    )
                    self.assertFalse(
                        pathlib.PureWindowsPath(value).is_absolute(),
                        f"marker[{key!r}]={value!r} is a Windows absolute path",
                    )

    def test_fresh_clone_install_status_doctor(self) -> None:
        # Simulate a fresh clone: no .hedl-tier present. Install, then exercise
        # the install-side health flow (status + doctor) end-to-end per tier.
        for tier in self.TIERS:
            with self.subTest(tier=tier):
                repo = self.tmp / tier
                repo.mkdir()
                self.assertFalse((repo / ".hedl-tier").exists(),
                                 "fresh clone must start with no marker")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc_install = M.cmd_install(_ns(tier=tier, repo=str(repo)))
                    rc_status = M.cmd_status(_ns(repo=str(repo)))
                    rc_doctor = M.cmd_doctor(_ns(repo=str(repo)))
                self.assertEqual(rc_install, 0, "install failed from fresh-clone state")
                self.assertTrue((repo / ".hedl-tier").exists(), "marker not generated")
                self.assertEqual(rc_status, 0, "status failed after fresh install")
                self.assertEqual(rc_doctor, 0, "doctor failed after fresh install")


class TestProjectionContainment(unittest.TestCase):
    """WORK-0020: tiers.json projection paths must stay within SKILL_ROOT
    (sources) and the consumer repo (targets). A crafted entry with `..`, an
    absolute path, or a symlink escape must be rejected before any write."""

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.skill = self.tmp / "skill"
        self.skill.mkdir()
        (self.skill / "scripts").mkdir()
        self.repo = self.tmp / "repo"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _tiers(self, source: str, target: str) -> dict[str, Any]:
        return {"tiers": {"evil": {"projections": [
            {"source": source, "target": target}]}}}

    def _validate(self, source: str, target: str) -> None:
        M._validate_tier_paths(
            self.repo, self._tiers(source, target), "evil", skill_root=self.skill)

    def test_relative_escape_target_rejected(self) -> None:
        with self.assertRaises(M.ProjectionContainmentError):
            self._validate("scripts/am_i_done.py", "../../../etc/evil")

    def test_relative_escape_source_rejected(self) -> None:
        with self.assertRaises(M.ProjectionContainmentError):
            self._validate("../../../etc/passwd", "ok.txt")

    def test_absolute_path_injection_rejected(self) -> None:
        with self.assertRaises(M.ProjectionContainmentError):
            self._validate("/etc/passwd", "/tmp/evil-target")

    def test_symlink_escape_target_rejected(self) -> None:
        # A symlink inside the repo pointing outside it; the target rel routes
        # through it. resolve() follows the link and the check catches the escape.
        outside = self.tmp / "outside"
        outside.mkdir()
        (self.repo / "link").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(M.ProjectionContainmentError):
            self._validate("scripts/am_i_done.py", "link/evil")

    def test_valid_paths_pass(self) -> None:
        # No raise for in-bounds source and nested target.
        self._validate("scripts/am_i_done.py", "sub/dir/file.py")

    def test_terminal_symlink_at_target_is_allowed(self) -> None:
        # A projection that REPLACES an existing terminal symlink — even one
        # pointing outside the repo — must NOT be rejected: _project_one unlinks
        # before writing, so it never writes through the link. Parent dir is in
        # repo; only the terminal leaf is a symlink. Regression for the
        # WORK-0030 symlink->copy migration false-positive.
        outside = self.tmp / "outside"
        outside.mkdir()
        leafdir = self.repo / ".github" / "workflows"
        leafdir.mkdir(parents=True)
        (leafdir / "wf.yml").symlink_to(outside / "wf.yml")
        self._validate("scripts/am_i_done.py", ".github/workflows/wf.yml")

    def test_source_terminal_symlink_escape_rejected(self) -> None:
        # A projection SOURCE that is a terminal symlink escaping SKILL_ROOT must
        # be rejected: copy2/read_bytes follow it, so validation follows it too.
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "secret").write_text("x")
        (self.skill / "evil_src").symlink_to(outside / "secret")
        with self.assertRaises(M.ProjectionContainmentError):
            self._validate("evil_src", "ok.txt")

    def test_init_target_terminal_dir_symlink_rejected(self) -> None:
        # An init TARGET that is a terminal directory symlink escaping the repo
        # must be rejected: copytree/archive-move operate through it.
        outside = self.tmp / "outside"
        outside.mkdir()
        (self.repo / "linkwork").symlink_to(outside, target_is_directory=True)
        tiers = {"tiers": {"evil": {"init": [
            {"source": "scripts", "target": "linkwork"}]}}}
        with self.assertRaises(M.ProjectionContainmentError):
            M._validate_tier_paths(self.repo, tiers, "evil", skill_root=self.skill)

    def test_empty_rel_rejected(self) -> None:
        with self.assertRaises(M.ProjectionContainmentError):
            self._validate("", "ok.txt")

    def test_resolve_contained_returns_resolved_path(self) -> None:
        got = M._resolve_contained(self.repo, "a/b", kind="target", follow=False)
        self.assertEqual(got, (self.repo / "a/b").resolve())

    def test_real_tiers_all_tiers_pass(self) -> None:
        # Behaviour on the well-formed shipped tiers.json is unchanged: every
        # tier validates clean against the real SKILL_ROOT.
        tiers = M._load_tiers()
        for tier in ("gate", "lightweight", "team"):
            with self.subTest(tier=tier):
                M._validate_tier_paths(self.repo, tiers, tier)

    def test_cmd_install_rejects_escaping_tiers_without_writing(self) -> None:
        # End-to-end: the guard is wired into cmd_install and bails before writes.
        malicious = {"tiers": {"team": {"projections": [
            {"source": "scripts/am_i_done.py", "target": "../../escape-victim.txt"}]}}}
        with mock.patch.object(M, "_load_tiers", return_value=malicious):
            rc = M.cmd_install(_ns(tier="team", repo=str(self.repo)))
        self.assertEqual(rc, 1)
        self.assertFalse((self.repo / ".github").exists(),
                         "install performed writes despite a containment violation")
        self.assertFalse((self.repo / ".hedl-tier").exists(),
                         "install wrote the tier marker despite bailing")


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


class TestGithubParsedCopies(unittest.TestCase):
    """GitHub-parsed .github/ files must be real copies, not symlinks, because
    GitHub never follows a symlink for files it parses itself (WORK-0030)."""

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_predicate_true_for_github_parsed_paths(self) -> None:
        for t in (
            ".github/workflows/am-i-done.yml",
            ".github/workflows/codeql.yml",
            ".github/dependabot.yml",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/CODEOWNERS",
        ):
            self.assertTrue(M._github_parses_directly(t), f"should be parsed: {t}")

    def test_predicate_false_for_workflow_invoked_and_other_paths(self) -> None:
        for t in (
            ".github/scripts/am_i_done.py",
            ".github/scripts/release.py",
            ".claude/commands/iterate.md",
            "requirements-ci.txt",
        ):
            self.assertFalse(M._github_parses_directly(t), f"should not be parsed: {t}")

    def test_every_github_projection_except_scripts_is_classified_parsed(self) -> None:
        # Regression lock against _GITHUB_PARSED_NAMES silently drifting from
        # tiers.json: every .github/ projection that is not a workflow-invoked
        # script must be classified GitHub-parsed (and so copied, not
        # symlinked). Adding a new GitHub-parsed projection (e.g. FUNDING.yml)
        # without teaching the predicate about it fails here.
        tiers = M._load_tiers()
        for tier_name in tiers["tiers"]:
            for proj in M._flatten_projections(tiers, tier_name):
                t = proj["target"]
                if not t.startswith(".github/"):
                    continue
                if t.startswith(".github/scripts/"):
                    self.assertFalse(
                        M._github_parses_directly(t),
                        f"workflow-invoked script should stay a symlink: {t}",
                    )
                else:
                    self.assertTrue(
                        M._github_parses_directly(t),
                        f".github projection not classified GitHub-parsed: {t}",
                    )

    def test_workflow_is_copy_even_in_symlink_mode(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp), copy=False))
        wf = self.tmp / ".github/workflows/am-i-done.yml"
        self.assertTrue(wf.exists())
        self.assertFalse(wf.is_symlink(), "workflow must be a real file, not a symlink")

    def test_script_stays_symlink_in_symlink_mode(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp), copy=False))
        script = self.tmp / ".github/scripts/am_i_done.py"
        self.assertTrue(script.is_symlink(), "workflow-invoked script should stay a symlink")

    def test_workflow_copy_content_matches_source(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp), copy=False))
        wf = self.tmp / ".github/workflows/am-i-done.yml"
        src = (M.SKILL_ROOT / "workflows/am-i-done.yml").resolve()
        self.assertEqual(wf.read_bytes(), src.read_bytes())

    def test_rerun_migrates_existing_symlink_to_copy(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp), copy=False))
        wf = self.tmp / ".github/workflows/am-i-done.yml"
        # Simulate the legacy on-disk state: a symlink into the source tree.
        wf.unlink()
        src = (M.SKILL_ROOT / "workflows/am-i-done.yml").resolve()
        wf.symlink_to(src)
        self.assertTrue(wf.is_symlink())
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp), copy=False))
        self.assertFalse(wf.is_symlink(), "re-run did not migrate symlink to copy")
        self.assertEqual(wf.read_bytes(), src.read_bytes())

    def test_doctor_detects_workflow_symlink_drift(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp), copy=False))
        wf = self.tmp / ".github/workflows/am-i-done.yml"
        wf.unlink()
        wf.symlink_to((M.SKILL_ROOT / "workflows/am-i-done.yml").resolve())
        rc = M.cmd_doctor(_ns(repo=str(self.tmp)))
        self.assertEqual(rc, 1, "doctor must flag a github-parsed file left as a symlink")

    def test_doctor_detects_workflow_content_drift(self) -> None:
        M.cmd_install(_ns(tier="gate", repo=str(self.tmp), copy=False))
        wf = self.tmp / ".github/workflows/am-i-done.yml"
        wf.write_text(wf.read_text() + "\n# local drift\n")
        rc = M.cmd_doctor(_ns(repo=str(self.tmp)))
        self.assertEqual(rc, 1, "doctor must flag a github-parsed copy that drifts from source")


class TestStateBackendMigration(unittest.TestCase):
    """WORK-0024 / ADR-022: state_backend relocates from context.json to hedl.toml."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._td.name)
        self.work = self.repo / ".work"
        self.work.mkdir()

    def tearDown(self) -> None:
        self._td.cleanup()

    def _write_ctx(self, data: dict[str, Any]) -> None:
        (self.work / "context.json").write_text(json.dumps(data, indent=2) + "\n")

    def test_migrates_non_default_backend_to_hedl_toml(self) -> None:
        self._write_ctx({"schema_version": "1", "state_backend": "github-issues"})
        rc = M.cmd_migrate(_ns(repo=str(self.repo), dry_run=False))
        self.assertEqual(rc, 0)
        ctx = json.loads((self.work / "context.json").read_text())
        self.assertEqual(ctx["schema_version"], "2")
        self.assertNotIn("state_backend", ctx)
        toml_text = (self.repo / "hedl.toml").read_text()
        self.assertIn("[state]", toml_text)
        self.assertIn('backend = "github-issues"', toml_text)

    def test_default_backend_needs_no_hedl_toml_entry(self) -> None:
        self._write_ctx({"schema_version": "1"})
        rc = M.cmd_migrate(_ns(repo=str(self.repo), dry_run=False))
        self.assertEqual(rc, 0)
        ctx = json.loads((self.work / "context.json").read_text())
        self.assertEqual(ctx["schema_version"], "2")
        self.assertFalse((self.repo / "hedl.toml").exists())

    def test_migration_is_idempotent(self) -> None:
        self._write_ctx({"schema_version": "1", "state_backend": "github-issues"})
        M.cmd_migrate(_ns(repo=str(self.repo), dry_run=False))
        first = (self.repo / "hedl.toml").read_text()
        rc = M.cmd_migrate(_ns(repo=str(self.repo), dry_run=False))
        self.assertEqual(rc, 0)
        self.assertEqual((self.repo / "hedl.toml").read_text(), first)

    def test_preserves_existing_hedl_toml_sections(self) -> None:
        (self.repo / "hedl.toml").write_text("[insights]\nenabled = true\n")
        self._write_ctx({"schema_version": "1", "state_backend": "github-issues"})
        M.cmd_migrate(_ns(repo=str(self.repo), dry_run=False))
        toml_text = (self.repo / "hedl.toml").read_text()
        self.assertIn("[insights]", toml_text)
        self.assertIn('backend = "github-issues"', toml_text)

    def test_rejects_unsafe_backend_value(self) -> None:
        """A crafted state_backend must not inject TOML into hedl.toml (the
        gate's [verify]/[gate] command surface). The migration refuses it."""
        with self.assertRaises(ValueError):
            M._set_hedl_state_backend(self.repo, 'x"\n[verify.evil]\ncmd = "id')
        self.assertFalse((self.repo / "hedl.toml").exists())

    def test_cmd_migrate_fails_cleanly_on_unsafe_value(self) -> None:
        """A crafted value yields a clean exit 1, not a traceback, and leaves
        context.json untouched (schema 1, value intact) so no archive churn."""
        self._write_ctx({"schema_version": "1", "state_backend": 'evil"\n[verify.x]\ncmd="id'})
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.cmd_migrate(_ns(repo=str(self.repo), dry_run=False))
        self.assertEqual(rc, 1)
        ctx = json.loads((self.work / "context.json").read_text())
        self.assertEqual(ctx["schema_version"], "1")
        self.assertIn("state_backend", ctx)
        self.assertFalse((self.repo / "hedl.toml").exists())

    def test_chained_unversioned_to_2(self) -> None:
        """An unversioned context.json migrates None->1->2 in one run."""
        self._write_ctx({"meta": {"project": "x"}})
        rc = M.cmd_migrate(_ns(repo=str(self.repo), dry_run=False))
        self.assertEqual(rc, 0)
        ctx = json.loads((self.work / "context.json").read_text())
        self.assertEqual(ctx["schema_version"], "2")

    def test_refuses_state_table_without_backend(self) -> None:
        """A [state] table lacking 'backend' must not get a second [state]
        header appended (which would be a duplicate-table parse error)."""
        (self.repo / "hedl.toml").write_text("[state]\nother = 1\n")
        with self.assertRaises(ValueError):
            M._set_hedl_state_backend(self.repo, "github-issues")

    def test_explicit_local_file_dropped_without_hedl_toml(self) -> None:
        self._write_ctx({"schema_version": "1", "state_backend": "local-file"})
        M.cmd_migrate(_ns(repo=str(self.repo), dry_run=False))
        ctx = json.loads((self.work / "context.json").read_text())
        self.assertEqual(ctx["schema_version"], "2")
        self.assertNotIn("state_backend", ctx)
        self.assertFalse((self.repo / "hedl.toml").exists())


class TestTierDescriptionMatchesProjections(unittest.TestCase):
    """WORK-0026 (AC3): a tiers.json description must not diverge from the tier's
    actual projection counts/paths, across all three tiers. Each assertion derives
    its expectation from M._flatten_projections (real install.py behaviour), so the
    test cannot pass by editing a hardcoded copy — changing a projection without
    reconciling the description fails the relevant check."""

    def setUp(self) -> None:
        self.tiers: Any = M._load_tiers()

    def _targets(self, tier: str) -> list[str]:
        return [p["target"] for p in M._flatten_projections(self.tiers, tier)]

    def test_gate_description_matches_projections(self) -> None:
        desc = self.tiers["tiers"]["gate"]["description"].lower()
        targets = self._targets("gate")
        # The description names CI workflow + PR template + scripts, and no Claude Code.
        self.assertTrue(any(t.startswith(".github/workflows/") for t in targets))
        self.assertIn(".github/PULL_REQUEST_TEMPLATE.md", targets)
        self.assertTrue(any(t.startswith(".github/scripts/") for t in targets))
        self.assertFalse(any(t.startswith(".claude/") for t in targets),
                         "gate must project no Claude Code files (its description says so)")
        self.assertIn("no claude code", desc)

    def test_lightweight_description_counts_match_projections(self) -> None:
        targets = self._targets("lightweight")
        n_cmds = sum(1 for t in targets if t.startswith(".claude/commands/"))
        n_agents = sum(1 for t in targets if t.startswith(".claude/agents/"))
        desc = self.tiers["tiers"]["lightweight"]["description"].lower()
        # The stated counts must equal the actual projected counts.
        self.assertIn(f"{n_cmds} slash command", desc,
                      f"lightweight projects {n_cmds} commands; reconcile its description (WORK-0026)")
        self.assertIn(f"{n_agents} adversarial agent", desc,
                      f"lightweight projects {n_agents} agents; reconcile its description (WORK-0026)")

    def test_team_projects_only_claude_code_integration(self) -> None:
        # Intentionally checks the team-OWN delta (not the flattened/inherited set):
        # the description claims "Lightweight + Claude Code integration", so the delta
        # is what must be Claude Code files. Inheritance consistency (team superset of
        # lightweight) is covered separately in TestTiersJson.
        own = {p["target"] for p in self.tiers["tiers"]["team"]["projections"]}
        self.assertTrue(
            all(t.startswith(".claude/") or t == ".claudeignore" for t in own),
            f"team projects a non-Claude-Code file; reconcile its description (WORK-0026): {own}",
        )
        desc = self.tiers["tiers"]["team"]["description"].lower()
        self.assertIn("claude code", desc)
        # github-issues / worktrees are config/workflow capabilities, not projected
        # files; if named, they must be qualified so the tier is not implied to install
        # them. Guards against re-introducing the WORK-0026 drift.
        if "github issues" in desc:
            self.assertTrue(
                any(w in desc for w in ("config", "planned", "read")),
                "team description names GitHub Issues without marking it config/read/planned (WORK-0026)",
            )


class TestInstallGuards(unittest.TestCase):
    """WORK-0022: malformed .hedl-tier produces an actionable message (no
    traceback); a tiers.json `includes` cycle is named and exits non-zero."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._td.name)
        self.marker = self.repo / M.TIER_MARKER

    def tearDown(self) -> None:
        self._td.cleanup()

    # --- .hedl-tier reader ---

    def test_read_tier_marker_valid(self) -> None:
        self.marker.write_text('{"tier": "lightweight"}\n', encoding="utf-8")
        tier, err = M._read_tier_marker(self.marker)
        self.assertEqual(tier, "lightweight")
        self.assertIsNone(err)

    def test_read_tier_marker_malformed_json(self) -> None:
        self.marker.write_text('{"tier": "light', encoding="utf-8")  # truncated
        tier, err = M._read_tier_marker(self.marker)
        self.assertIsNone(tier)
        self.assertIsNotNone(err)
        self.assertIn("not valid JSON", err)

    def test_read_tier_marker_missing_tier_field(self) -> None:
        self.marker.write_text('{"other": 1}', encoding="utf-8")
        tier, err = M._read_tier_marker(self.marker)
        self.assertIsNone(tier)
        self.assertIn("'tier' field", err)

    def test_read_tier_marker_wrong_type(self) -> None:
        self.marker.write_text('{"tier": 5}', encoding="utf-8")
        tier, err = M._read_tier_marker(self.marker)
        self.assertIsNone(tier)
        self.assertIsNotNone(err)

    def test_read_tier_marker_empty_tier(self) -> None:
        self.marker.write_text('{"tier": "  "}', encoding="utf-8")
        tier, err = M._read_tier_marker(self.marker)
        self.assertIsNone(tier)
        self.assertIsNotNone(err)

    def test_read_tier_marker_non_dict_toplevel(self) -> None:
        self.marker.write_text('["lightweight"]', encoding="utf-8")
        tier, err = M._read_tier_marker(self.marker)
        self.assertIsNone(tier)
        self.assertIsNotNone(err)

    def test_cmd_status_malformed_marker_no_traceback(self) -> None:
        self.marker.write_text("not json at all", encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.cmd_status(_ns(repo=str(self.repo)))
        self.assertEqual(rc, 1)
        self.assertIn(".hedl-tier", buf.getvalue())

    def test_cmd_doctor_malformed_marker_no_traceback(self) -> None:
        self.marker.write_text("not json at all", encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.cmd_doctor(_ns(repo=str(self.repo)))
        self.assertEqual(rc, 1)
        self.assertIn(".hedl-tier", buf.getvalue())

    # --- includes cycle ---

    _CYCLE = {"tiers": {"a": {"includes": ["b"]}, "b": {"includes": ["a"]}}}

    def test_flatten_projections_detects_cycle(self) -> None:
        with self.assertRaises(M.TiersIncludeCycleError) as ctx:
            M._flatten_projections(self._CYCLE, "a")
        self.assertIn("a -> b -> a", str(ctx.exception))

    def test_flatten_inits_detects_cycle(self) -> None:
        with self.assertRaises(M.TiersIncludeCycleError):
            M._flatten_inits(self._CYCLE, "a")

    def test_self_include_cycle(self) -> None:
        tiers = {"tiers": {"x": {"includes": ["x"]}}}
        with self.assertRaises(M.TiersIncludeCycleError) as ctx:
            M._flatten_projections(tiers, "x")
        self.assertIn("x -> x", str(ctx.exception))

    def test_unknown_tier_reference_raises(self) -> None:
        tiers = {"tiers": {"a": {"includes": ["nope"]}}}
        with self.assertRaises(M.TiersConfigError) as ctx:
            M._flatten_projections(tiers, "a")
        self.assertIn("unknown tier", str(ctx.exception))
        self.assertIn("nope", str(ctx.exception))

    def test_diamond_includes_not_a_cycle(self) -> None:
        # a -> b, a -> c, b -> d, c -> d : not a cycle; must not raise.
        tiers = {"tiers": {
            "a": {"includes": ["b", "c"]},
            "b": {"includes": ["d"]},
            "c": {"includes": ["d"]},
            "d": {"projections": [{"source": "s", "target": "t"}]},
        }}
        result = M._flatten_projections(tiers, "a")
        self.assertEqual(len(result), 2)  # d's projection appears once per branch

    def test_excessive_include_depth_raises(self) -> None:
        # A linear chain deeper than the cap raises TiersConfigError, not RecursionError.
        n = M._MAX_INCLUDE_DEPTH + 5
        tiers = {"tiers": {f"t{i}": {"includes": [f"t{i+1}"]} for i in range(n)}}
        tiers["tiers"][f"t{n}"] = {}
        with self.assertRaises(M.TiersConfigError):
            M._flatten_projections(tiers, "t0")

    def test_cmd_install_warns_on_malformed_marker(self) -> None:
        self.marker.write_text("garbage{", encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.cmd_install(_ns(tier="gate", repo=str(self.repo), copy=True))
        self.assertIn("WARN", buf.getvalue())

    def test_main_exits_1_on_includes_cycle(self) -> None:
        import sys as _sys
        self.marker.write_text('{"tier": "a"}\n', encoding="utf-8")
        argv = ["install.py", "--status", "--repo", str(self.repo)]
        with mock.patch.object(M, "_load_tiers", return_value=self._CYCLE), \
                mock.patch.object(_sys, "argv", argv):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = M.main()
        self.assertEqual(rc, 1)  # clean exit, not a RecursionError traceback
        self.assertIn("cycle", buf.getvalue().lower())


class TestGitignoreProjection(unittest.TestCase):
    """WORK-0042 / ADR-005: install ships a .gitignore block protecting
    local-only artefacts; idempotent; preserves existing content."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._td.name)
        self.gi = self.repo / ".gitignore"

    def tearDown(self) -> None:
        self._td.cleanup()

    def _install(self, **kw: Any) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.cmd_install(_ns(tier="team", repo=str(self.repo), copy=True, **kw))

    def test_fresh_install_creates_gitignore(self) -> None:
        self._install()
        self.assertTrue(self.gi.exists())
        txt = self.gi.read_text()
        for needle in (".work/insights/*.jsonl", ".work/insights/metrics.json",
                       ".work/insights/proposals/", ".pytest_cache/", "__pycache__/",
                       "*.pyc", "ADR-005"):
            self.assertIn(needle, txt)
        # The over-broad unanchored 'events.jsonl' line must NOT be present
        # (it is covered by the anchored .work/insights/*.jsonl glob).
        self.assertNotIn("\nevents.jsonl\n", txt)

    def test_empty_gitignore_gets_clean_block(self) -> None:
        self.gi.write_text("")  # zero-byte existing file
        self._install()
        txt = self.gi.read_text()
        self.assertTrue(txt.startswith(M._GITIGNORE_BEGIN), "no leading blank line")
        self.assertEqual(txt.count(M._GITIGNORE_BEGIN), 1)

    def test_unreadable_gitignore_skips_without_crash(self) -> None:
        # .gitignore as a directory -> read_text raises; install must not crash.
        (self.repo / ".gitignore").mkdir()
        status = M._ensure_gitignore_block(self.repo, dry_run=False)
        self.assertIn("skip", status)
        self.assertTrue((self.repo / ".gitignore").is_dir())  # untouched

    def test_existing_gitignore_appended_preserving_content(self) -> None:
        self.gi.write_text("# my stuff\nnode_modules/\n")
        self._install()
        txt = self.gi.read_text()
        self.assertIn("node_modules/", txt)            # preserved
        self.assertIn(".work/insights/*.jsonl", txt)   # appended

    def test_idempotent_no_duplicate_block(self) -> None:
        self._install()
        self._install()
        self.assertEqual(self.gi.read_text().count(M._GITIGNORE_BEGIN), 1)

    def test_dry_run_writes_nothing(self) -> None:
        self._install(dry_run=True)
        self.assertFalse(self.gi.exists())

    def test_git_actually_ignores_insights(self) -> None:
        import subprocess
        if not shutil.which("git"):
            self.skipTest("git not available")
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self._install()
        (self.repo / ".work" / "insights").mkdir(parents=True, exist_ok=True)
        (self.repo / ".work" / "insights" / "events.jsonl").write_text("{}\n")
        (self.repo / ".work" / "insights" / "metrics.json").write_text("{}\n")
        (self.repo / ".work" / "insights" / "proposals").mkdir(exist_ok=True)
        (self.repo / ".work" / "insights" / "proposals" / "p1.json").write_text("{}\n")
        for rel in (".work/insights/events.jsonl", ".work/insights/metrics.json",
                    ".work/insights/proposals/p1.json"):
            r = subprocess.run(
                ["git", "-C", str(self.repo), "check-ignore", rel],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, f"git should ignore {rel}")
        # README under .work/insights/ must remain trackable (NOT ignored).
        (self.repo / ".work" / "insights" / "README.md").write_text("# notes\n")
        r = subprocess.run(
            ["git", "-C", str(self.repo), "check-ignore", ".work/insights/README.md"],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 1, ".work/insights/README.md must stay trackable")


class TestTiersManifestErrors(unittest.TestCase):
    """WORK-0048: a missing or corrupt tiers.json must surface as a clean
    TiersConfigError (non-zero exit via main()), never a raw traceback."""

    def test_missing_tiers_raises_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = pathlib.Path(tmp) / "nonexistent-tiers.json"
            with mock.patch.object(M, "TIERS_FILE", missing):
                with self.assertRaises(M.TiersConfigError) as ctx:
                    M._load_tiers()
            self.assertIn("not found", str(ctx.exception))

    def test_corrupt_tiers_raises_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            corrupt = pathlib.Path(tmp) / "tiers.json"
            corrupt.write_text("{ not valid json")
            with mock.patch.object(M, "TIERS_FILE", corrupt):
                with self.assertRaises(M.TiersConfigError) as ctx:
                    M._load_tiers()
            self.assertIn("not valid JSON", str(ctx.exception))

    def test_valid_tiers_still_loads(self) -> None:
        # Regression: the real manifest still parses unchanged.
        tiers = M._load_tiers()
        self.assertIn("tiers", tiers)


if __name__ == "__main__":
    unittest.main()
