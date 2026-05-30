"""Tests for budget_manager.py concurrency and atomicity.

Covers: concurrent record calls must not lose increments (flock),
partial write on SIGKILL must not reset to defaults (atomic rename),
JSONDecodeError on load must not silently destroy history.

Run: pytest skill/hedl/tests/test_budget_manager.py
"""

import importlib.util
import multiprocessing as mp
import pathlib
import sys
import tempfile
import unittest
from typing import Any
from unittest import mock

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "budget_manager.py"


def _load_module(tmp_root: pathlib.Path) -> Any:
    """Load budget_manager with REPO_ROOT pointed at a tmp dir for isolation."""
    spec = importlib.util.spec_from_file_location("budget_manager", _SCRIPT)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    sys.modules["budget_manager"] = mod
    spec.loader.exec_module(mod)
    mod.REPO_ROOT = tmp_root
    mod.BUDGET_FILE = tmp_root / ".work" / "budget.json"
    mod.QUEUE_FILE = tmp_root / ".work" / "reviews" / "queue.json"
    return mod


def _record_one(tmp_root: str) -> int:
    """Worker target: load budget_manager fresh and record(1)."""
    mod = _load_module(pathlib.Path(tmp_root))
    mod.cmd_record(1)
    return 0


class TestConcurrency(unittest.TestCase):
    def test_parallel_record_does_not_lose_increments(self) -> None:
        # B7: 10 concurrent processes each record(1) → final must be 10.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = pathlib.Path(tmp)
            N = 10
            # Use spawn so each child re-loads the module (most pessimistic case).
            ctx = mp.get_context("spawn")
            with ctx.Pool(N) as pool:
                pool.map(_record_one, [str(tmp_root)] * N)

            mod = _load_module(tmp_root)
            budget = mod._load_budget()
            self.assertEqual(budget["session"]["invocations_used"], N,
                msg=f"Lost increments: got {budget['session']['invocations_used']} of {N}")


class TestAtomicity(unittest.TestCase):
    def test_corrupt_budget_file_is_quarantined_not_silently_reset(self) -> None:
        # B7 / CE2: a half-written budget.json must not silently destroy history.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = pathlib.Path(tmp)
            mod = _load_module(tmp_root)
            # Seed with valid budget that has interesting state
            mod.cmd_record(5)
            self.assertEqual(mod._load_budget()["session"]["invocations_used"], 5)

            # Corrupt the file
            mod.BUDGET_FILE.write_text("not json {{{")

            # Load should quarantine and return defaults
            budget = mod._load_budget()
            self.assertEqual(budget["session"]["invocations_used"], 0)

            # The corrupt file is preserved as .corrupt-<ts>
            corrupted = list(mod.BUDGET_FILE.parent.glob("budget.json.corrupt-*"))
            self.assertEqual(len(corrupted), 1,
                msg=f"Expected one quarantine file, got: {corrupted}")

    def test_atomic_write_does_not_leave_tmp_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = pathlib.Path(tmp)
            mod = _load_module(tmp_root)
            mod.cmd_record(1)
            tmps = list(mod.BUDGET_FILE.parent.glob("*.tmp"))
            self.assertEqual(tmps, [],
                msg=f"Stray tmp files left after atomic write: {tmps}")


class TestQueueOps(unittest.TestCase):
    def test_defer_then_drain_under_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = pathlib.Path(tmp)
            mod = _load_module(tmp_root)
            mod.cmd_defer(pr=42, branch="feat/x", agents=["scope-auditor"],
                          reason="test")
            self.assertEqual(len(mod._load_queue()["queue"]), 1)

            mod.cmd_drain(1, mod._load_queue())
            self.assertEqual(len(mod._load_queue()["queue"]), 0)


class TestTierLogic(unittest.TestCase):
    def test_tier_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = pathlib.Path(tmp)
            mod = _load_module(tmp_root)

            # default thresholds: reduced_at=12, minimal_at=22, deferred_at=28, budget=30
            for n, expected in [
                (0, "FULL"), (11, "FULL"),
                (12, "REDUCED"), (21, "REDUCED"),
                (22, "MINIMAL"), (27, "MINIMAL"),
                (28, "DEFERRED"), (30, "DEFERRED"),
            ]:
                # Reset and bump to n
                budget = mod._default_budget()
                budget["session"]["invocations_used"] = n
                mod._save_budget(budget)
                self.assertEqual(mod.get_tier(), expected,
                    msg=f"At {n} invocations expected {expected}")


class TestGateOnlyTier(unittest.TestCase):
    """WORK-0002: a state-mutating budget op must not create .work/ in a
    gate-only repo (no .work/ by design). Read commands are unaffected."""

    def _run_main(self, mod: Any, argv: list[str]) -> int:
        with mock.patch.object(sys, "argv", ["budget_manager.py", *argv]):
            return int(mod.main())

    # Every state-mutating command, with representative args.
    _MUTATING_INVOCATIONS = {
        "record": ["record", "5"],
        "reset": ["reset"],
        "defer": ["defer", "--pr", "1", "--branch", "b", "--agents", "x"],
        "drain": ["drain", "1"],
        "record-panel": ["record-panel", "--pr", "1", "--agents", "x"],
    }

    def test_no_mutating_command_creates_work_dir_when_absent(self) -> None:
        # Covers the whole _MUTATING set so a new writer not added to the guard
        # (or a member removed from it) is caught here.
        mod_probe = _load_module(pathlib.Path("/nonexistent-probe"))
        self.assertEqual(
            set(self._MUTATING_INVOCATIONS), mod_probe._MUTATING_COMMANDS,
            "test invocation table is out of sync with budget_manager._MUTATING_COMMANDS")
        for cmd, argv in self._MUTATING_INVOCATIONS.items():
            with self.subTest(cmd=cmd), tempfile.TemporaryDirectory() as tmp:
                tmp_root = pathlib.Path(tmp)
                mod = _load_module(tmp_root)
                rc = self._run_main(mod, argv)
                self.assertEqual(rc, 0, f"{cmd} should no-op (exit 0)")
                self.assertFalse(
                    (tmp_root / ".work").exists(),
                    f"{cmd} created .work/ in a gate-only repo")

    def test_record_writes_when_work_dir_exists(self) -> None:
        # Team/lightweight behaviour unchanged: .work/ present -> record writes.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = pathlib.Path(tmp)
            (tmp_root / ".work").mkdir()
            mod = _load_module(tmp_root)
            rc = self._run_main(mod, ["record", "5"])
            self.assertEqual(rc, 0)
            self.assertTrue((tmp_root / ".work" / "budget.json").exists(),
                            "budget.json should be written when .work/ exists")


if __name__ == "__main__":
    unittest.main()
