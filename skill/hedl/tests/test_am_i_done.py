"""Tests for the deterministic completion gate.

Covers: dispatch rule regex anchoring, fresh-clone error handling,
CI check status classification, branch pattern validation, Dependabot
validation, PR thread checks, check_git, check_config, check_commands,
check_template, and tool-absent hardening for lint/types/tests.

Run: pytest skill/hedl/tests/test_am_i_done.py
"""

import importlib.util
import os
import pathlib
import re
import sys
import unittest
from typing import Any
from unittest import mock

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "am_i_done.py"


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("am_i_done", _SCRIPT)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    sys.modules["am_i_done"] = mod
    spec.loader.exec_module(mod)
    return mod


M = _load_module()


def _matches(path: str) -> set[str]:
    """Apply dispatch rules to a single path; return the set of required agents."""
    mandatory_agents, _ = M._load_dispatch_rules()
    out: set[str] = set()
    for pattern, agents in mandatory_agents:
        if re.search(pattern, path):
            out.update(agents)
    return out


class TestDispatchRulesRegex(unittest.TestCase):
    def test_claude_md_at_root_triggers_historian(self) -> None:
        self.assertIn("historian", _matches("CLAUDE.md"))

    def test_claude_md_in_subdir_triggers_historian(self) -> None:
        self.assertIn("historian", _matches("docs/CLAUDE.md"))

    def test_not_claude_md_does_not_trigger_historian(self) -> None:
        self.assertNotIn("historian", _matches("docs/notCLAUDE.md"))
        self.assertNotIn("historian", _matches("vendor/notCLAUDE.md.bak"))

    def test_claudeignore_at_root_triggers_security_auditor(self) -> None:
        self.assertIn("security-auditor", _matches(".claudeignore"))

    def test_dotted_suffix_not_claudeignore_does_not_trigger(self) -> None:
        self.assertNotIn("security-auditor", _matches("foo.claudeignore"))

    def test_nested_claude_agents_does_not_trigger(self) -> None:
        self.assertNotIn("model-optimizer", _matches("vendor/.claude/agents/x.md"))

    def test_claude_agents_at_root_triggers_security_and_historian(self) -> None:
        self.assertIn("security-auditor", _matches(".claude/agents/security-auditor.md"))
        self.assertIn("historian", _matches(".claude/agents/security-auditor.md"))

    def test_py_file_triggers_security_auditor(self) -> None:
        self.assertIn("security-auditor", _matches(".github/scripts/am_i_done.py"))

    def test_work_decisions_triggers_historian(self) -> None:
        self.assertIn("historian", _matches(".work/decisions/ADR-001-example.md"))

    def test_nested_work_decisions_does_not_trigger(self) -> None:
        self.assertNotIn("historian", _matches("backup/.work/decisions/foo.md"))


class TestChangedFilesFreshClone(unittest.TestCase):
    def test_both_refs_missing_returns_error(self) -> None:
        # Simulate `git diff main...HEAD` and `git diff origin/main...HEAD`
        # both failing (fresh clone of a fork with no main upstream).
        with mock.patch.object(M, "run", return_value=(1, "", "fatal: bad revision")):
            files, err = M._get_changed_files()
        self.assertEqual(files, [])
        self.assertIsNotNone(err)
        self.assertIn("main", err)


class TestCheckCiJson(unittest.TestCase):
    def test_cancelled_check_is_failure_not_pass(self) -> None:
        payload = '[{"name":"build","state":"CANCELLED","bucket":"fail"}]'
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, payload, "")):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_ci(1)
        self.assertFalse(res.passed)
        self.assertIn("failing", res.message)

    def test_timed_out_check_is_failure(self) -> None:
        payload = '[{"name":"build","state":"TIMED_OUT","bucket":"fail"}]'
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, payload, "")):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_ci(1)
        self.assertFalse(res.passed)

    def test_all_success_passes(self) -> None:
        payload = (
            '[{"name":"a","state":"SUCCESS","bucket":"pass"},'
            ' {"name":"b","state":"SUCCESS","bucket":"pass"}]'
        )
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, payload, "")):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_ci(1)
        self.assertTrue(res.passed)

    def test_auth_error_distinguished(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run",
                               return_value=(1, "", "error: authentication required, run gh auth login")):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_ci(1)
        self.assertFalse(res.passed)
        self.assertIn("authenticated", res.message)

    def test_rate_limit_distinguished(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run",
                               return_value=(1, "", "API rate limit exceeded for foo")):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_ci(1)
        self.assertFalse(res.passed)
        self.assertIn("rate-limited", res.message)

    def test_no_checks_distinguished_from_failure(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "[]", "")):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_ci(1)
        self.assertFalse(res.passed)
        self.assertIn("no CI checks", res.message)


class TestBranchPattern(unittest.TestCase):
    def test_valid_feat_branch(self) -> None:
        self.assertTrue(M.BRANCH_PATTERN.match("feat/add-widget"))

    def test_main_rejected(self) -> None:
        self.assertFalse(M.BRANCH_PATTERN.match("main"))

    def test_uppercase_rejected(self) -> None:
        self.assertFalse(M.BRANCH_PATTERN.match("feat/FooBar"))

    def test_underscore_rejected(self) -> None:
        self.assertFalse(M.BRANCH_PATTERN.match("feat/foo_bar"))


class TestCheckDependabot(unittest.TestCase):
    def _repo_ok(self) -> tuple[int, str, str]:
        return (0, "octocat/example\n", "")

    def test_no_gh_cli_skips(self) -> None:
        with mock.patch.object(M, "shutil") as sh:
            sh.which.return_value = None
            res = M.check_dependabot()
        self.assertTrue(res.passed)
        self.assertIn("skipping", res.message)

    def test_repo_lookup_failure_skips(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(1, "", "error")):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_dependabot()
        self.assertTrue(res.passed)
        self.assertIn("repo", res.message)

    def test_404_skips(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (1, "", "Not Found (HTTP 404)"),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_dependabot()
        self.assertTrue(res.passed)
        self.assertIn("not configured", res.message.lower())

    def test_any_403_skips(self) -> None:
        # Any 403 on the Dependabot API (integration limit or org restriction) skips.
        for err_msg in [
            "Resource not accessible by integration (HTTP 403)",
            "HTTP 403 Forbidden",
        ]:
            with self.subTest(err=err_msg):
                with mock.patch.object(M, "shutil") as sh, \
                     mock.patch.object(M, "run", side_effect=[
                         self._repo_ok(),
                         (1, "", err_msg),
                     ]):
                    sh.which.return_value = "/usr/bin/gh"
                    res = M.check_dependabot()
                self.assertTrue(res.passed)
                self.assertIn("token lacks access", res.message)

    def test_auth_error_fails(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (1, "", "authentication required (HTTP 401)"),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_dependabot()
        self.assertFalse(res.passed)
        self.assertIn("authenticated", res.message)

    def test_other_api_error_fails_closed(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (1, "", "internal server error"),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_dependabot()
        self.assertFalse(res.passed)

    def test_zero_alerts_passes(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (0, "", ""),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_dependabot()
        self.assertTrue(res.passed)
        self.assertIn("no open", res.message)

    def test_open_alerts_fails(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (0, "1\n2\n", ""),
                 (0, "lodash (high)\npkg-b (medium)", ""),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_dependabot()
        self.assertFalse(res.passed)
        self.assertIn("2", res.message)


class TestCheckPrThreads(unittest.TestCase):
    def _repo_ok(self) -> tuple[int, str, str]:
        return (0, "octocat/example\n", "")

    def test_no_gh_cli_skips(self) -> None:
        with mock.patch.object(M, "shutil") as sh:
            sh.which.return_value = None
            res = M.check_pr_threads(1)
        self.assertTrue(res.passed)

    def test_repo_lookup_failure_skips(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(1, "", "error")):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_pr_threads(1)
        self.assertTrue(res.passed)

    def test_malformed_repo_output_skips(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 (0, "example\n", ""),  # no slash — can't partition owner/name
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_pr_threads(1)
        self.assertTrue(res.passed)
        self.assertIn("skipping", res.message)

    def test_403_skips(self) -> None:
        for err_msg in [
            "Resource not accessible by integration (HTTP 403)",
            "HTTP 403 Forbidden",
        ]:
            with self.subTest(err=err_msg):
                with mock.patch.object(M, "shutil") as sh, \
                     mock.patch.object(M, "run", side_effect=[
                         self._repo_ok(),
                         (1, "", err_msg),
                     ]):
                    sh.which.return_value = "/usr/bin/gh"
                    res = M.check_pr_threads(1)
                self.assertTrue(res.passed)
                self.assertIn("token lacks access", res.message)

    def test_auth_error_fails(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (1, "", "authentication required (HTTP 401)"),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_pr_threads(1)
        self.assertFalse(res.passed)
        self.assertIn("authenticated", res.message)

    def test_graphql_error_fails_closed(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (1, "", "something unexpected"),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_pr_threads(1)
        self.assertFalse(res.passed)
        self.assertIn("failing closed", res.message)

    def test_zero_unresolved_passes(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (0, "0\n", ""),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_pr_threads(1)
        self.assertTrue(res.passed)

    def test_unresolved_threads_fails(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", side_effect=[
                 self._repo_ok(),
                 (0, "3\n", ""),
             ]):
            sh.which.return_value = "/usr/bin/gh"
            res = M.check_pr_threads(1)
        self.assertFalse(res.passed)
        self.assertIn("3", res.message)


class TestCheckGit(unittest.TestCase):
    def test_clean_branch_passes(self) -> None:
        with mock.patch.object(M, "run", side_effect=[
            (0, "", ""),         # git status --porcelain — clean
            (0, "feat/foo\n", ""),  # git rev-parse --abbrev-ref HEAD
        ]):
            res = M.check_git()
        self.assertTrue(res.passed)
        self.assertIn("feat/foo", res.message)

    def test_uncommitted_changes_fails(self) -> None:
        with mock.patch.object(M, "run", side_effect=[
            (0, "M README.md\n", ""),  # git status --porcelain — dirty
        ]):
            res = M.check_git()
        self.assertFalse(res.passed)
        self.assertIn("uncommitted", res.message)

    def test_on_main_fails(self) -> None:
        with mock.patch.object(M, "run", side_effect=[
            (0, "", ""),        # git status --porcelain — clean
            (0, "main\n", ""),  # git rev-parse --abbrev-ref HEAD
        ]):
            res = M.check_git()
        self.assertFalse(res.passed)
        self.assertIn("main", res.message)


class TestCheckConfig(unittest.TestCase):
    def test_skips_when_no_work_dir(self) -> None:
        """Gate-only installs have no .work/ — check must be skipped, not failed."""
        with mock.patch("os.path.isdir", return_value=False):
            res = M.check_config()
        self.assertIsNone(res)

    def test_fails_when_work_dir_exists_but_rules_missing(self) -> None:
        """Partial config (.work/ exists, dispatch-rules.json absent) is a hard failure."""
        def fake_isdir(p: str) -> bool:
            return ".work" in p and "config" not in p and "dispatch" not in p

        with mock.patch("os.path.isdir", side_effect=fake_isdir), \
             mock.patch("os.path.exists", return_value=False):
            res = M.check_config()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("not found", res.message)

    def test_all_referenced_agents_present_passes(self) -> None:
        rules: dict[str, Any] = {
            "mandatory_agents": [{"pattern": ".*\\.py$", "agents": ["security-auditor"]}],
            "always_required": ["scope-auditor"],
        }
        on_disk = ["security-auditor.md", "scope-auditor.md"]
        with mock.patch.object(M, "_load_dispatch_rules", return_value=(
            [(r["pattern"], r["agents"]) for r in rules["mandatory_agents"]],
            rules["always_required"],
        )), mock.patch("os.path.exists", return_value=True), \
             mock.patch("os.path.isdir", return_value=True), \
             mock.patch("os.listdir", return_value=on_disk):
            res = M.check_config()
        self.assertTrue(res.passed)

    def test_stale_reference_fails(self) -> None:
        rules = {
            "mandatory_agents": [{"pattern": ".*\\.py$", "agents": ["deleted-agent"]}],
            "always_required": [],
        }
        on_disk = ["scope-auditor.md"]
        with mock.patch.object(M, "_load_dispatch_rules", return_value=(
            [(r["pattern"], r["agents"]) for r in rules["mandatory_agents"]],
            rules["always_required"],
        )), mock.patch("os.path.exists", return_value=True), \
             mock.patch("os.path.isdir", return_value=True), \
             mock.patch("os.listdir", return_value=on_disk):
            res = M.check_config()
        self.assertFalse(res.passed)
        self.assertIn("deleted-agent", res.detail)


class TestCheckCommands(unittest.TestCase):
    def test_no_stale_ids_passes(self) -> None:
        import json as _json
        import os as _os
        import tempfile
        work = {"meta": {"active_item": "WORK-0001"}, "active": [{"id": "WORK-0001"}], "backlog": []}
        cmd_content = "# /start-session\nLoad context.\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_dir = _os.path.join(tmpdir, ".claude", "commands")
            _os.makedirs(cmd_dir)
            with open(_os.path.join(cmd_dir, "start-session.md"), "w") as f:
                f.write(cmd_content)
            work_dir = _os.path.join(tmpdir, ".work")
            _os.makedirs(work_dir)
            with open(_os.path.join(work_dir, "work.json"), "w") as f:
                _json.dump(work, f)
            original_root = M.REPO_ROOT
            M.REPO_ROOT = tmpdir
            try:
                res = M.check_commands()
            finally:
                M.REPO_ROOT = original_root
        self.assertIsNone(res) if res is None else self.assertTrue(res.passed)

    def test_stale_id_fails(self) -> None:
        work: dict[str, Any] = {"meta": {}, "active": [], "backlog": []}
        cmd_content = "# /iterate\nSee WORK-9999 for context.\n"

        original_isdir = os.path.isdir
        original_exists = os.path.exists

        def fake_isdir(p: str) -> bool:
            if ".claude/commands" in p or p.endswith("commands"):
                return True
            return original_isdir(p)

        def fake_exists(p: str) -> bool:
            if "work.json" in p:
                return True
            return original_exists(p)

        import json as _json
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_dir = _os.path.join(tmpdir, ".claude", "commands")
            _os.makedirs(cmd_dir)
            with open(_os.path.join(cmd_dir, "iterate.md"), "w") as f:
                f.write(cmd_content)
            work_dir = _os.path.join(tmpdir, ".work")
            _os.makedirs(work_dir)
            work_path = _os.path.join(work_dir, "work.json")
            with open(work_path, "w") as f:
                _json.dump(work, f)

            original_root = M.REPO_ROOT
            M.REPO_ROOT = tmpdir
            try:
                res = M.check_commands()
            finally:
                M.REPO_ROOT = original_root

        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("WORK-9999", res.detail)


    def test_skips_when_no_work_json(self) -> None:
        """Commands dir present but no work.json — cannot validate stale IDs; skip."""
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_dir = _os.path.join(tmpdir, ".claude", "commands")
            _os.makedirs(cmd_dir)
            with open(_os.path.join(cmd_dir, "iterate.md"), "w") as f:
                f.write("# /iterate\nSee WORK-9999 for context.\n")
            # Deliberately do NOT create .work/work.json

            original_root = M.REPO_ROOT
            M.REPO_ROOT = tmpdir
            try:
                res = M.check_commands()
            finally:
                M.REPO_ROOT = original_root

        self.assertIsNone(res)


class TestCheckTemplate(unittest.TestCase):
    def test_valid_template_passes(self) -> None:
        good_body = (
            "## Summary\nFixed a bug.\n\n"
            "## Work item\nWORK-0001 — fix the thing\n\n"
            "## Type\n- [x] fix\n\n"
            "## Changes\n- fixed it\n\n"
            "## Validation\nRan tests\n"
        )
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, good_body, "")), \
             mock.patch("subprocess.run") as sp_run:
            sh.which.return_value = "/usr/bin/gh"
            sp_result = mock.MagicMock()
            sp_result.returncode = 0
            sp_result.stdout = ""
            sp_run.return_value = sp_result
            res = M.check_template(1)
        self.assertTrue(res.passed)

    def test_gh_unavailable_fails(self) -> None:
        with mock.patch.object(M, "run", return_value=(1, "", "not found")):
            res = M.check_template(1)
        self.assertFalse(res.passed)


class TestToolAbsentHardening(unittest.TestCase):
    """check_lint, check_types, check_tests fail loudly when config present but tool absent."""

    def test_lint_fails_when_ruff_missing_but_config_present(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch("os.path.exists") as exists:
            sh.which.return_value = None  # ruff not found
            exists.side_effect = lambda p: "pyproject.toml" in p
            res = M.check_lint()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("ruff not found", res.message)

    def test_lint_skips_when_no_config(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch("os.path.exists", return_value=False):
            sh.which.return_value = None
            res = M.check_lint()
        self.assertIsNone(res)

    def test_types_fails_when_mypy_missing_but_sources_present(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch("os.path.isdir") as isdir, \
             mock.patch("os.listdir", return_value=["am_i_done.py"]):
            sh.which.return_value = None  # mypy not found
            isdir.side_effect = lambda p: p.endswith("skill/hedl/scripts")
            res = M.check_types()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("mypy not found", res.message)

    def test_types_skips_when_no_source_dirs(self) -> None:
        with mock.patch("os.path.isdir", return_value=False):
            res = M.check_types()
        self.assertIsNone(res)

    def test_tests_fails_when_pytest_missing_but_tests_dir_present(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch("os.path.isdir", return_value=True), \
             mock.patch("os.listdir", return_value=["test_something.py"]):
            sh.which.return_value = None  # pytest not found
            res = M.check_tests()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("pytest not found", res.message)

    def test_tests_skips_when_no_tests_dir(self) -> None:
        with mock.patch("os.path.isdir", return_value=False):
            res = M.check_tests()
        self.assertIsNone(res)


class TestStateBackend(unittest.TestCase):
    """Tests for _load_work_items / _load_work_items_local / _load_work_items_github."""

    def test_local_file_reads_work_json(self) -> None:
        work = {
            "active": [{"id": "WORK-0001"}],
            "backlog": [{"id": "WORK-0002"}],
        }
        import json as _json
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = _os.path.join(tmpdir, ".work")
            _os.makedirs(work_dir)
            with open(_os.path.join(work_dir, "work.json"), "w") as f:
                _json.dump(work, f)
            original = M.REPO_ROOT
            M.REPO_ROOT = tmpdir
            try:
                ids, err = M._load_work_items_local()
            finally:
                M.REPO_ROOT = original
        self.assertIsNone(err)
        self.assertIn("WORK-0001", ids)
        self.assertIn("WORK-0002", ids)

    def test_local_file_returns_empty_when_no_work_json(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            original = M.REPO_ROOT
            M.REPO_ROOT = tmpdir
            try:
                ids, err = M._load_work_items_local()
            finally:
                M.REPO_ROOT = original
        self.assertIsNone(err)
        self.assertEqual(ids, set())

    def test_defaults_to_local_when_no_context_json(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            original = M.REPO_ROOT
            M.REPO_ROOT = tmpdir
            try:
                backend = M._state_backend()
            finally:
                M.REPO_ROOT = original
        self.assertEqual(backend, "local-file")

    def test_reads_state_backend_from_context_json(self) -> None:
        import json as _json
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = _os.path.join(tmpdir, ".work")
            _os.makedirs(work_dir)
            with open(_os.path.join(work_dir, "context.json"), "w") as f:
                _json.dump({"state_backend": "github-issues"}, f)
            original = M.REPO_ROOT
            M.REPO_ROOT = tmpdir
            try:
                backend = M._state_backend()
            finally:
                M.REPO_ROOT = original
        self.assertEqual(backend, "github-issues")

    def test_github_issues_parses_open_issues(self) -> None:
        payload = (
            '[{"number":1,"title":"WORK-0001: add feature"},'
            ' {"number":2,"title":"WORK-0002: fix bug"},'
            ' {"number":3,"title":"Not a work item"}]'
        )
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, payload, "")):
            sh.which.return_value = "/usr/bin/gh"
            ids, err = M._load_work_items_github()
        self.assertIsNone(err)
        self.assertIn("WORK-0001", ids)
        self.assertIn("WORK-0002", ids)
        self.assertNotIn("Not a work item", ids)
        self.assertEqual(len(ids), 2)

    def test_github_issues_no_gh_cli_returns_error(self) -> None:
        with mock.patch.object(M, "shutil") as sh:
            sh.which.return_value = None
            ids, err = M._load_work_items_github()
        self.assertEqual(ids, set())
        self.assertIsNotNone(err)
        self.assertIn("gh CLI", err)

    def test_github_issues_gh_failure_returns_error(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(1, "", "authentication required")):
            sh.which.return_value = "/usr/bin/gh"
            ids, err = M._load_work_items_github()
        self.assertEqual(ids, set())
        self.assertIsNotNone(err)


class TestCheckStreams(unittest.TestCase):
    def _run(self, side_effects: list[tuple[int, str, str]], streams: list[str]) -> Any:
        with mock.patch.object(M, "run", side_effect=side_effects):
            return M.check_streams(streams)

    def test_empty_streams_passes(self) -> None:
        result = M.check_streams([])
        self.assertTrue(result.passed)
        self.assertIn("no parallel streams", result.message)

    def test_single_stream_passes(self) -> None:
        result = self._run(
            [(0, "src/foo.py\n", "")],
            ["feat/only-stream"],
        )
        self.assertTrue(result.passed)
        self.assertIn("1 stream(s) clean", result.message)

    def test_no_overlap_passes(self) -> None:
        result = self._run(
            [(0, "src/a.py\n", ""), (0, "src/b.py\n", "")],
            ["feat/stream-a", "feat/stream-b"],
        )
        self.assertTrue(result.passed)
        self.assertIn("2 stream(s) clean", result.message)
        self.assertIn("2 total file(s)", result.message)

    def test_overlap_fails(self) -> None:
        result = self._run(
            [(0, "src/shared.py\nsrc/a.py\n", ""), (0, "src/shared.py\nsrc/b.py\n", "")],
            ["feat/stream-a", "feat/stream-b"],
        )
        self.assertFalse(result.passed)
        self.assertIn("1 file(s) touched by multiple streams", result.message)
        self.assertIn("src/shared.py", result.detail or "")

    def test_git_diff_failure_falls_back_to_origin(self) -> None:
        result = self._run(
            [(1, "", "fatal: bad revision"), (0, "src/foo.py\n", "")],
            ["feat/only-stream"],
        )
        self.assertTrue(result.passed)

    def test_git_diff_both_fail_returns_failure(self) -> None:
        result = self._run(
            [(1, "", "fatal: bad revision"), (1, "", "fatal: bad revision")],
            ["feat/missing-branch"],
        )
        self.assertFalse(result.passed)
        self.assertIn("could not diff stream", result.message)


class TestDeclaredVerify(unittest.TestCase):
    """Tests for the hedl.toml [verify] declarative check mechanism."""

    # -- resolution: no hedl.toml + Python markers → default profile --

    def test_no_hedl_toml_python_repo_lint_uses_default(self) -> None:
        with mock.patch.object(M, "_load_hedl_config", return_value=None), \
             mock.patch.object(M, "shutil") as sh, \
             mock.patch("os.path.exists") as exists:
            sh.which.return_value = "/usr/bin/ruff"
            exists.side_effect = lambda p: "pyproject.toml" in p
            res = M.check_lint()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertTrue(res.passed)
        self.assertEqual(res.message, "ruff clean")

    # -- resolution: no hedl.toml + no Python markers → skip --

    def test_no_hedl_toml_non_python_lint_skips(self) -> None:
        with mock.patch.object(M, "_load_hedl_config", return_value=None), \
             mock.patch("os.path.exists", return_value=False):
            res = M.check_lint()
        self.assertIsNone(res)

    def test_no_hedl_toml_non_python_types_skips(self) -> None:
        with mock.patch.object(M, "_load_hedl_config", return_value=None), \
             mock.patch("os.path.isdir", return_value=False):
            res = M.check_types()
        self.assertIsNone(res)

    def test_no_hedl_toml_non_python_tests_skips(self) -> None:
        with mock.patch.object(M, "_load_hedl_config", return_value=None), \
             mock.patch("os.path.isdir", return_value=False):
            res = M.check_tests()
        self.assertIsNone(res)

    # -- resolution: [verify] present → declared commands run, gate on exit code --

    def test_declared_lint_passes_on_exit_zero(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"lint": "golangci-lint run"}}), \
             mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")):
            sh.which.return_value = "/usr/bin/golangci-lint"
            res = M.check_lint()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertTrue(res.passed)

    def test_declared_lint_fails_on_nonzero_exit(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"lint": "golangci-lint run"}}), \
             mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(1, "", "lint errors")):
            sh.which.return_value = "/usr/bin/golangci-lint"
            res = M.check_lint()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("golangci-lint", res.message)

    def test_declared_types_runs_command(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"types": "tsc --noEmit"}}), \
             mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")):
            sh.which.return_value = "/usr/bin/tsc"
            res = M.check_types()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertTrue(res.passed)

    def test_declared_test_runs_command(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"test": "go test ./..."}}), \
             mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")):
            sh.which.return_value = "/usr/bin/go"
            res = M.check_tests()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertTrue(res.passed)
        self.assertEqual(res.name, "tests")  # display name stays "tests"

    # -- declared-but-missing-binary → fail loudly --

    def test_declared_missing_binary_fails_with_name(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"lint": "golangci-lint run"}}), \
             mock.patch.object(M, "shutil") as sh:
            sh.which.return_value = None
            res = M.check_lint()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("golangci-lint", res.message)
        self.assertIn("not found", res.message)
        self.assertNotIn("pip", res.message)  # no Python hint

    # -- undeclared standard check with [verify] present → skipped --

    def test_undeclared_lint_skipped_when_verify_present(self) -> None:
        # [verify] present, but no "lint" key — must NOT fall back to ruff
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"test": "go test ./..."}}), \
             mock.patch("os.path.exists", return_value=True):  # pyproject.toml "exists"
            res = M.check_lint()
        self.assertIsNone(res)

    def test_undeclared_types_skipped_when_verify_present(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"lint": "golangci-lint run"}}), \
             mock.patch("os.path.isdir", return_value=True), \
             mock.patch("os.listdir", return_value=["main.go"]):
            res = M.check_types()
        self.assertIsNone(res)

    def test_undeclared_test_skipped_when_verify_present(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"lint": "golangci-lint run"}}), \
             mock.patch("os.path.isdir", return_value=True), \
             mock.patch("os.listdir", return_value=["something_test.go"]):
            res = M.check_tests()
        self.assertIsNone(res)

    # -- long-form [verify.<name>] timeout and cwd honored --

    def test_long_form_timeout_honored(self) -> None:
        spec = {"cmd": "playwright test", "timeout": 600}
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            sh.which.return_value = "/usr/bin/playwright"
            M._run_declared_check("e2e", spec, 120)
        _, kwargs = mock_run.call_args
        self.assertEqual(kwargs.get("timeout"), 600)

    def test_long_form_cwd_honored(self) -> None:
        spec = {"cmd": "playwright test", "cwd": "e2e"}
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            sh.which.return_value = "/usr/bin/playwright"
            M._run_declared_check("e2e", spec, 120)
        _, kwargs = mock_run.call_args
        self.assertTrue(kwargs.get("cwd", "").endswith("e2e"))

    def test_gate_timeout_used_when_no_per_command_timeout(self) -> None:
        spec = {"cmd": "some-tool check"}
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            sh.which.return_value = "/usr/bin/some-tool"
            M._run_declared_check("check", spec, 300)
        _, kwargs = mock_run.call_args
        self.assertEqual(kwargs.get("timeout"), 300)

    # -- shlex parsing: no shell injection --

    def test_shlex_no_shell_injection(self) -> None:
        # Shell metacharacters must NOT be interpreted — they are literal argv elements
        malicious = "echo hello; rm -rf /"
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            sh.which.return_value = "/bin/echo"
            M._run_declared_check("test", malicious, 120)
        cmd_arg = mock_run.call_args[0][0]
        self.assertIsInstance(cmd_arg, list)  # list form, not a shell string
        self.assertEqual(cmd_arg[0], "echo")
        self.assertIn("hello;", cmd_arg)  # ";" is a literal argument, not shell operator

    def test_shlex_parse_error_fails_check(self) -> None:
        broken = "cmd 'unclosed"
        with mock.patch.object(M, "shutil"):
            res = M._run_declared_check("test", broken, 120)
        self.assertFalse(res.passed)
        self.assertIn("parse error", res.message)


if __name__ == "__main__":
    unittest.main()
