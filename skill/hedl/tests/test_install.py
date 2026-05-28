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
