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

    def test_work_decisions_triggers_existential_challenger(self) -> None:
        # WORK-0005 / ADR-017: existential-challenger is mandatory for ADR writes.
        self.assertIn("existential-challenger", _matches(".work/decisions/ADR-001-example.md"))

    def test_alternatives_triggers_existential_challenger(self) -> None:
        self.assertIn("existential-challenger", _matches("docs/alternatives.md"))

    def test_alternatives_rule_is_anchored(self) -> None:
        self.assertNotIn("existential-challenger", _matches("docs/not-alternatives.md"))
        self.assertNotIn("existential-challenger", _matches("vendor/docs/alternatives.md"))

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


class TestShouldPollCi(unittest.TestCase):
    """The ci check polls the PR's own check-runs (which include this gate's
    matrix jobs), so it must not run in the default gate pass — only on an
    explicit --check ci. Regression guard for the self-referential CI failure
    surfaced by WORK-0030."""

    def test_default_run_does_not_poll_ci(self) -> None:
        self.assertFalse(M._should_poll_ci(None, 16))

    def test_explicit_ci_check_without_pr_does_not_poll(self) -> None:
        self.assertFalse(M._should_poll_ci("ci", None))

    def test_explicit_ci_check_with_pr_polls(self) -> None:
        self.assertTrue(M._should_poll_ci("ci", 16))

    def test_other_explicit_check_does_not_poll_ci(self) -> None:
        self.assertFalse(M._should_poll_ci("git", 16))


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


class TestCheckStateTemplateSync(unittest.TestCase):
    """check_state_template_sync (WORK-0025): guarded framework-config files must
    stay byte-identical between live .work/ and the skill/hedl/work-state/ seed,
    but only in the framework source repo, and only for the guarded subset."""

    GUARDED = (
        "config/dispatch-rules.json",
        "config/markdown-schemas.json",
        "decisions/README.md",
        "reviews/README.md",
    )

    def _build(self, tmpdir: str, *, with_template: bool = True,
               overrides: "dict[str, tuple[str, str]] | None" = None,
               omit: "set[str] | None" = None) -> None:
        """Create a .work/ tree and (optionally) a skill/hedl/work-state/ seed.

        overrides maps a guarded rel-path to (live_bytes, template_bytes) so a
        single file can be made to drift. omit drops a rel-path from the seed.
        """
        import os as _os
        overrides = overrides or {}
        omit = omit or set()
        live_root = _os.path.join(tmpdir, ".work")
        template_root = _os.path.join(tmpdir, "skill", "hedl", "work-state")
        # A non-guarded file that legitimately diverges (scout-populated).
        live_files = dict.fromkeys(self.GUARDED, "shared-content\n")
        live_files["config/project-registry.json"] = '{"competing_projects": ["x"]}\n'
        template_files = dict.fromkeys(self.GUARDED, "shared-content\n")
        template_files["config/project-registry.json"] = '{"competing_projects": []}\n'
        for rel, (live_b, tmpl_b) in overrides.items():
            live_files[rel] = live_b
            template_files[rel] = tmpl_b
        for rel, content in live_files.items():
            p = _os.path.join(live_root, rel)
            _os.makedirs(_os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(content)
        if with_template:
            for rel, content in template_files.items():
                if rel in omit:
                    continue
                p = _os.path.join(template_root, rel)
                _os.makedirs(_os.path.dirname(p), exist_ok=True)
                with open(p, "w") as f:
                    f.write(content)

    def _run(self, tmpdir: str) -> Any:
        original_root = M.REPO_ROOT
        M.REPO_ROOT = tmpdir
        try:
            return M.check_state_template_sync()
        finally:
            M.REPO_ROOT = original_root

    def test_in_sync_passes(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir)
            res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertTrue(res.passed)

    def test_drift_fails_and_names_file(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir, overrides={
                "config/dispatch-rules.json": ("live-edited\n", "seed-stale\n"),
            })
            res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("config/dispatch-rules.json", res.detail)

    def test_missing_guarded_file_fails(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir, omit={"reviews/README.md"})
            res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("reviews/README.md", res.detail)

    def test_consumer_layout_skips(self) -> None:
        """Only .work/ at root (no skill/hedl/work-state/) — adopter repo, skip."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir, with_template=False)
            res = self._run(tmpdir)
        self.assertIsNone(res)

    def test_project_registry_divergence_allowed(self) -> None:
        """project-registry.json is scout-populated per project and NOT guarded;
        its divergence must not fail the gate."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir)  # builds with project-registry already diverging
            res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertTrue(res.passed)

    def test_live_side_missing_fails(self) -> None:
        """A guarded file removed from the live .work/ tree (not the template)
        must FAIL — exercises the live-side branch of the missing check."""
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir)
            _os.remove(_os.path.join(tmpdir, ".work", "reviews", "README.md"))
            res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("reviews/README.md", res.detail)

    def test_directory_at_guarded_path_fails_without_crash(self) -> None:
        """A directory where a guarded file is expected must FAIL cleanly
        (not a regular file), never crash the gate with IsADirectoryError."""
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir)
            p = _os.path.join(tmpdir, ".work", "config", "dispatch-rules.json")
            _os.remove(p)
            _os.makedirs(p)
            res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("not a regular file", res.detail)
        self.assertIn("config/dispatch-rules.json", res.detail)

    def test_unreadable_file_fails_without_crash(self) -> None:
        """An OSError on read (e.g. permission denied) must FAIL cleanly, not
        propagate a traceback out of the gate."""
        import tempfile
        from unittest import mock
        real_open = open

        def selective_open(path: Any, *a: Any, **k: Any) -> Any:
            # Raise only for the file under test; delegate everything else so the
            # patch can't mask unrelated I/O (avoids a brittle global open patch).
            if "dispatch-rules.json" in str(path):
                raise PermissionError("denied")
            return real_open(path, *a, **k)

        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir)
            with mock.patch("builtins.open", side_effect=selective_open):
                res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("unreadable", res.detail)

    def test_symlink_escaping_tree_fails(self) -> None:
        """A guarded path that resolves outside its tree via a symlink must FAIL
        (escapes tree), never be read."""
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir)
            outside = _os.path.join(tmpdir, "outside.txt")
            with open(outside, "w") as f:
                f.write("secret\n")
            guarded = _os.path.join(tmpdir, ".work", "config", "dispatch-rules.json")
            _os.remove(guarded)
            _os.symlink(outside, guarded)
            res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("escapes tree", res.detail)

    def test_empty_guarded_set_fails(self) -> None:
        """An empty _STATE_SYNC_GUARDED must FAIL, not vacuously pass."""
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmpdir:
            self._build(tmpdir)
            with mock.patch.object(M, "_STATE_SYNC_GUARDED", ()):
                res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("no guarded files", res.message)

    def test_framework_repo_missing_template_tree_fails(self) -> None:
        """In the framework repo (skill/hedl/ present) a missing work-state/
        tree must FAIL — not silently skip and stop guarding."""
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Framework marker + live tree, but NO skill/hedl/work-state/.
            _os.makedirs(_os.path.join(tmpdir, "skill", "hedl"))
            _os.makedirs(_os.path.join(tmpdir, ".work"))
            res = self._run(tmpdir)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertFalse(res.passed)
        self.assertIn("state tree missing", res.message)


class TestCheckTemplate(unittest.TestCase):
    @staticmethod
    def _pr_json(body: str, *, login: str = "alice", is_bot: bool = False) -> str:
        import json as _json
        return _json.dumps({"author": {"login": login, "is_bot": is_bot}, "body": body})

    def test_valid_template_passes(self) -> None:
        good_body = (
            "## Summary\nFixed a bug.\n\n"
            "## Work item\nWORK-0001 — fix the thing\n\n"
            "## Type\n- [x] fix\n\n"
            "## Changes\n- fixed it\n\n"
            "## Validation\nRan tests\n"
        )
        with mock.patch.object(M, "run", return_value=(0, self._pr_json(good_body), "")), \
             mock.patch("subprocess.run") as sp_run:
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

    def test_dependabot_pr_is_exempt(self) -> None:
        # WORK-0041: a Dependabot-authored PR with a non-template body passes
        # without invoking the template validator. (Fails before the fix.)
        payload = self._pr_json("Bumps foo from 1.0 to 1.1.", login="app/dependabot", is_bot=True)
        with mock.patch.object(M, "run", return_value=(0, payload, "")), \
             mock.patch("subprocess.run") as sp_run:
            res = M.check_template(1)
            sp_run.assert_not_called()  # exemption short-circuits before the validator
        self.assertTrue(res.passed)
        self.assertIn("Dependabot", res.message)

    def test_human_incomplete_body_still_fails(self) -> None:
        # Human author + empty body must still FAIL — run the real validator.
        with mock.patch.object(M, "run", return_value=(0, self._pr_json(""), "")):
            res = M.check_template(1)
        self.assertFalse(res.passed)

    def test_dependabot_login_without_is_bot_not_exempt(self) -> None:
        # Security: the login alone is not enough; is_bot (GitHub-verified) is
        # required, so a non-bot account using that login is NOT exempt and an
        # empty body still fails through the real validator.
        payload = self._pr_json("", login="app/dependabot", is_bot=False)
        with mock.patch.object(M, "run", return_value=(0, payload, "")):
            res = M.check_template(1)
        self.assertFalse(res.passed)

    def test_dependabot_bot_bracket_login_exempt(self) -> None:
        # The second login variant in _DEPENDABOT_LOGINS is also exempt.
        payload = self._pr_json("Bumps foo.", login="dependabot[bot]", is_bot=True)
        with mock.patch.object(M, "run", return_value=(0, payload, "")), \
             mock.patch("subprocess.run") as sp_run:
            res = M.check_template(1)
            sp_run.assert_not_called()
        self.assertTrue(res.passed)

    def test_is_bot_non_bool_truthy_not_exempt(self) -> None:
        # Security: `is True` rejects a non-bool truthy is_bot (e.g. integer 1);
        # the exemption must not fire, so an empty body still fails.
        import json as _json
        payload = _json.dumps({"author": {"login": "app/dependabot", "is_bot": 1}, "body": ""})
        with mock.patch.object(M, "run", return_value=(0, payload, "")):
            res = M.check_template(1)
        self.assertFalse(res.passed)

    def test_null_author_not_exempt(self) -> None:
        # Fail-closed: a null/absent author must not be exempt.
        import json as _json
        payload = _json.dumps({"author": None, "body": ""})
        with mock.patch.object(M, "run", return_value=(0, payload, "")):
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

    def test_reads_state_backend_from_hedl_toml(self) -> None:
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(_os.path.join(tmpdir, "hedl.toml"), "w") as f:
                f.write('[state]\nbackend = "github-issues"\n')
            original = M.REPO_ROOT
            M.REPO_ROOT = tmpdir
            try:
                backend = M._state_backend()
            finally:
                M.REPO_ROOT = original
        self.assertEqual(backend, "github-issues")

    def test_state_backend_ignores_context_json(self) -> None:
        """ADR-022: state_backend now lives in hedl.toml; a legacy context.json
        value must NOT be read by the gate (migration relocates it)."""
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
        self.assertEqual(backend, "local-file")

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

    def test_github_issues_null_title_does_not_crash(self) -> None:
        """A present-but-null issue title must be ignored, not crash the gate."""
        payload = (
            '[{"number":1,"title":"WORK-0001: real"},'
            ' {"number":2,"title":null}]'
        )
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, payload, "")):
            sh.which.return_value = "/usr/bin/gh"
            ids, err = M._load_work_items_github()
        self.assertIsNone(err)
        self.assertEqual(ids, {"WORK-0001"})

    def test_github_issues_truncated_read_fails_loudly(self) -> None:
        """A read that hits the issue cap must FAIL, not silently drop IDs —
        a partial set would let a stale WORK-ID slip past the gate (WORK-0007)."""
        import json as _json
        capped = M._GITHUB_ISSUE_READ_LIMIT
        payload = _json.dumps(
            [{"number": n, "title": f"WORK-{n:04d}: item"} for n in range(1, capped + 1)]
        )
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, payload, "")):
            sh.which.return_value = "/usr/bin/gh"
            ids, err = M._load_work_items_github()
        self.assertEqual(ids, set())
        self.assertIsNotNone(err)
        assert err is not None
        self.assertIn("read cap", err)


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
                               return_value={"verify": {"lint": "golangci-lint run"},
                                             "gate": {"allowed_commands": ["golangci-lint"]}}), \
             mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")):
            sh.which.return_value = "/usr/bin/golangci-lint"
            res = M.check_lint()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertTrue(res.passed)

    def test_declared_lint_fails_on_nonzero_exit(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"lint": "golangci-lint run"},
                                             "gate": {"allowed_commands": ["golangci-lint"]}}), \
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
                               return_value={"verify": {"types": "tsc --noEmit"},
                                             "gate": {"allowed_commands": ["tsc"]}}), \
             mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")):
            sh.which.return_value = "/usr/bin/tsc"
            res = M.check_types()
        self.assertIsNotNone(res)
        assert res is not None
        self.assertTrue(res.passed)

    def test_declared_test_runs_command(self) -> None:
        with mock.patch.object(M, "_load_hedl_config",
                               return_value={"verify": {"test": "go test ./..."},
                                             "gate": {"allowed_commands": ["go"]}}), \
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
                               return_value={"verify": {"lint": "golangci-lint run"},
                                             "gate": {"allowed_commands": ["golangci-lint"]}}), \
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
            M._run_declared_check("e2e", spec, 120, frozenset({"playwright"}))
        _, kwargs = mock_run.call_args
        self.assertEqual(kwargs.get("timeout"), 600)

    def test_long_form_cwd_honored(self) -> None:
        spec = {"cmd": "playwright test", "cwd": "e2e"}
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            sh.which.return_value = "/usr/bin/playwright"
            M._run_declared_check("e2e", spec, 120, frozenset({"playwright"}))
        _, kwargs = mock_run.call_args
        self.assertTrue(kwargs.get("cwd", "").endswith("e2e"))

    def test_gate_timeout_used_when_no_per_command_timeout(self) -> None:
        spec = {"cmd": "some-tool check"}
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            sh.which.return_value = "/usr/bin/some-tool"
            M._run_declared_check("check", spec, 300, frozenset({"some-tool"}))
        _, kwargs = mock_run.call_args
        self.assertEqual(kwargs.get("timeout"), 300)

    # -- WORK-0021: shell metacharacters rejected outright (fail closed) --

    def test_shell_metacharacters_rejected(self) -> None:
        # The pre-WORK-0021 behaviour split ";" into a literal argv element under
        # shell=False. The contract now rejects shell metacharacters up front so
        # the operator gets a clear error instead of a silently-mangled command;
        # run() must never be reached.
        malicious = "ruff check; rm -rf /"
        with mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            res = M._run_declared_check("test", malicious, 120, frozenset({"ruff"}))
        self.assertFalse(res.passed)
        self.assertIn("metacharacter", res.message)
        mock_run.assert_not_called()

    def test_shlex_parse_error_fails_check(self) -> None:
        broken = "cmd 'unclosed"
        with mock.patch.object(M, "shutil"):
            res = M._run_declared_check("test", broken, 120, frozenset({"cmd"}))
        self.assertFalse(res.passed)
        self.assertIn("parse error", res.message)


class TestVerifyAllowlist(unittest.TestCase):
    """WORK-0021: [verify] executable allow-list + operator extension."""

    def test_default_allowlist_blocks_interpreters(self) -> None:
        allowed = M._verify_allowlist(None)
        for interp in ("python", "python3", "bash", "sh", "node", "perl", "ruby"):
            self.assertNotIn(interp, allowed, f"{interp} must not be default-allowed")
        for tool in ("pytest", "mypy", "ruff", "npm", "pnpm", "make"):
            self.assertIn(tool, allowed)

    def test_disallowed_executable_rejected(self) -> None:
        # cargo is neither default-allowed nor denylisted → allow-list rejection
        # (distinct from the interpreter-denylist path tested separately).
        res = M._run_declared_check("x", "cargo build", 120, M._verify_allowlist(None))
        self.assertFalse(res.passed)
        self.assertIn("allow-list", res.message)

    def test_allowlist_extension_adds_command(self) -> None:
        allowed = M._verify_allowlist({"gate": {"allowed_commands": ["cargo", "go"]}})
        self.assertIn("cargo", allowed)
        self.assertIn("go", allowed)
        self.assertIn("ruff", allowed)  # additive: default still present

    def test_extension_cannot_smuggle_path_or_metachars(self) -> None:
        allowed = M._verify_allowlist(
            {"gate": {"allowed_commands": ["/usr/bin/python", "sh;rm", "ok"]}}
        )
        self.assertNotIn("python", allowed)          # path separator → ignored
        self.assertNotIn("/usr/bin/python", allowed)
        self.assertNotIn("sh;rm", allowed)           # metacharacter → ignored
        self.assertIn("ok", allowed)                 # clean bare name → added

    def test_path_in_executable_rejected(self) -> None:
        # cmd[0] must be a bare name. A path is rejected even when its basename
        # is allow-listed — closes the planted-binary bypass (/attacker/ruff,
        # ./ruff). run() must never be reached.
        with mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            res = M._run_declared_check(
                "lint", "/usr/bin/ruff check", 120, M._verify_allowlist(None)
            )
        self.assertFalse(res.passed)
        self.assertIn("bare name", res.message)
        mock_run.assert_not_called()

    def test_extension_rejects_interpreters_and_forwarders(self) -> None:
        allowed = M._verify_allowlist({"gate": {"allowed_commands": [
            "sh", "bash", "env", "python3", "node", "xargs", "find", "go"]}})
        for bad in ("sh", "bash", "env", "python3", "node", "xargs", "find"):
            self.assertNotIn(bad, allowed, f"{bad} must be denied even as a bare name")
        self.assertIn("go", allowed)  # a non-denylisted tool still adds

    def test_cwd_escaping_repo_rejected(self) -> None:
        spec = {"cmd": "ruff check", "cwd": "../../../tmp"}
        with mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            res = M._run_declared_check("lint", spec, 120, M._verify_allowlist(None))
        self.assertFalse(res.passed)
        self.assertIn("escapes the repo", res.message)
        mock_run.assert_not_called()

    def test_tab_separator_rejected(self) -> None:
        # A tab is whitespace to shlex but reads as one token to a human, so it
        # is rejected as a metacharacter rather than silently splitting args.
        with mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            res = M._run_declared_check(
                "lint", "ruff\tcheck", 120, M._verify_allowlist(None)
            )
        self.assertFalse(res.passed)
        self.assertIn("metacharacter", res.message)
        mock_run.assert_not_called()

    def test_denylist_enforced_even_in_handbuilt_allowset(self) -> None:
        # Two-layer defense: a denied interpreter rejected at run time even if a
        # caller hands in an allow-list that wrongly contains it.
        with mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            res = M._run_declared_check("x", "bash run.sh", 120, frozenset({"bash"}))
        self.assertFalse(res.passed)
        self.assertIn("denied", res.message)
        mock_run.assert_not_called()

    def test_happy_path_allowlisted_command_runs(self) -> None:
        with mock.patch.object(M, "shutil") as sh, \
             mock.patch.object(M, "run", return_value=(0, "", "")) as mock_run:
            sh.which.return_value = "/usr/bin/ruff"
            res = M._run_declared_check(
                "lint", "ruff check .", 120, M._verify_allowlist(None)
            )
        self.assertTrue(res.passed)
        mock_run.assert_called_once()


class TestDocGeneratedFacts(unittest.TestCase):
    """WORK-0028: check_doc_generated_facts catches doc count/name drift from
    the filesystem source, and skips outside the Hedl source tree."""

    def _build(self, tmp: str, *, agents: list[str], review_lib: str, commands_md: str,
               tiers_md: str, tiers_json_n: int = 3) -> None:
        import json as _json
        import os as _os

        def _write(path: str, content: str) -> None:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        sh = _os.path.join(tmp, "skill", "hedl")
        _os.makedirs(_os.path.join(sh, "agents"))
        _os.makedirs(_os.path.join(sh, "references"))
        for a in agents:
            _write(_os.path.join(sh, "agents", a + ".md"), "# " + a + "\n")
        _write(_os.path.join(sh, "tiers.json"),
               _json.dumps({"tiers": {f"t{i}": {} for i in range(tiers_json_n)}}))
        _write(_os.path.join(sh, "references", "review-library.md"), review_lib)
        _write(_os.path.join(sh, "references", "commands.md"), commands_md)
        _write(_os.path.join(sh, "references", "tiers.md"), tiers_md)

    def _run(self, tmp: str) -> Any:
        original = M.REPO_ROOT
        M.REPO_ROOT = tmp
        try:
            return M.check_doc_generated_facts()
        finally:
            M.REPO_ROOT = original

    def _consistent_kwargs(self) -> dict[str, Any]:
        agents = ["alpha", "beta"]  # 2 agents
        review_lib = ("Two core agents live as named `.claude/agents/` files: "
                      "`alpha`, `beta`.\n")
        commands_md = "## one\n## two\n## three\n"  # 3 behaviours, no ADR template
        tiers_md = ("# Tiers\n\nThree tiers — drop in just the gate, lightweight, team.\n\n"
                    "All 3 command behaviors here.\n")
        return dict(agents=agents, review_lib=review_lib, commands_md=commands_md, tiers_md=tiers_md)

    def test_passes_when_docs_match_source(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self._build(tmp, **self._consistent_kwargs())
            result = self._run(tmp)
            self.assertIsNotNone(result)
            self.assertTrue(result.passed, result.detail)

    def test_fails_on_wrong_agent_count(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            kw = self._consistent_kwargs()
            kw["review_lib"] = ("Five core agents live as named `.claude/agents/` files: "
                                "`alpha`, `beta`.\n")
            self._build(tmp, **kw)
            result = self._run(tmp)
            self.assertFalse(result.passed)
            self.assertIn("core-agent count", result.detail)

    def test_fails_on_missing_agent_name(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            kw = self._consistent_kwargs()
            kw["review_lib"] = "Two core agents live as named `.claude/agents/` files: `alpha`.\n"
            self._build(tmp, **kw)
            result = self._run(tmp)
            self.assertFalse(result.passed)
            self.assertIn("beta", result.detail)

    def test_fails_on_wrong_command_behaviour_count(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            kw = self._consistent_kwargs()
            kw["tiers_md"] = "# Tiers\n\nThree tiers — x.\n\nAll 9 command behaviors here.\n"
            self._build(tmp, **kw)
            result = self._run(tmp)
            self.assertFalse(result.passed)
            self.assertIn("command-behaviour count", result.detail)

    def test_fenced_headings_excluded_from_behaviour_count(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            kw = self._consistent_kwargs()
            # 3 real behaviours + 4 headings inside a code fence (the ADR template
            # example) = 7 `##` lines, but the count must stay 3.
            kw["commands_md"] = ("## one\n## two\n## three\n"
                                 "```markdown\n## Decision\n## Context\n"
                                 "## Options considered\n## Consequences\n```\n")
            self._build(tmp, **kw)
            result = self._run(tmp)
            self.assertTrue(result.passed, result.detail)

    def test_fails_on_wrong_tier_count(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            kw = self._consistent_kwargs()  # tiers_json_n=3, but doc will say "Five"
            kw["tiers_md"] = "# Tiers\n\nFive tiers — drop in just the gate.\n\nAll 3 command behaviors.\n"
            self._build(tmp, **kw)
            result = self._run(tmp)
            self.assertFalse(result.passed)
            self.assertIn("tier count", result.detail)

    def test_fails_on_corrupt_tiers_json(self) -> None:
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self._build(tmp, **self._consistent_kwargs())
            with open(_os.path.join(tmp, "skill", "hedl", "tiers.json"), "w", encoding="utf-8") as f:
                f.write("{ not valid json")
            result = self._run(tmp)
            self.assertFalse(result.passed)
            self.assertIn("tiers.json", result.detail)

    def test_fails_on_missing_commands_md(self) -> None:
        import os as _os
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self._build(tmp, **self._consistent_kwargs())
            _os.remove(_os.path.join(tmp, "skill", "hedl", "references", "commands.md"))
            result = self._run(tmp)
            self.assertFalse(result.passed)
            self.assertIn("commands.md", result.detail)

    def test_skips_outside_source_tree(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(self._run(tmp))


if __name__ == "__main__":
    unittest.main()
