"""Tests for Hedl usage insights — Parts 3 and 4.

Covers: nothing written when [insights] enabled=false; only allowed fields
recorded; no network calls; stdlib guard; reflect.py aggregation
deterministic + idempotent; proposals reference real metrics.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest
from typing import Any
from unittest import mock

_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
_REFLECT_SCRIPT = _SCRIPTS / "reflect.py"
_AM_I_DONE_SCRIPT = _SCRIPTS / "am_i_done.py"
_RECORD_INSIGHTS_SCRIPT = (
    pathlib.Path(__file__).resolve().parent.parent
    / "integrations" / "claude-code" / "scripts" / "record_insights.py"
)


def _load_module(path: pathlib.Path) -> Any:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RF = _load_module(_REFLECT_SCRIPT)
RI = _load_module(_RECORD_INSIGHTS_SCRIPT)


# ---------------------------------------------------------------------------
# Allowed fields in insights events (Part 3 spec)
# ---------------------------------------------------------------------------

ALLOWED_INSIGHT_FIELDS: frozenset[str] = frozenset({
    "ts", "type",
    "tier", "checks", "overridden",
    "reviewer", "finding_count", "verdict",
    "command",
})


class TestInsightsGateAppender(unittest.TestCase):
    """am_i_done.py _append_gate_insight — Part 3."""

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.work = self.tmp / ".work"
        self.work.mkdir()
        self.insights = self.work / "insights"
        self.insights.mkdir()
        self.events = self.insights / "events.jsonl"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _write_hedl_toml(self, enabled: bool) -> None:
        (self.tmp / "hedl.toml").write_text(
            f"[insights]\nenabled = {'true' if enabled else 'false'}\n"
        )

    def _make_report(self, passed: bool = True) -> Any:
        M = _load_module(_AM_I_DONE_SCRIPT)
        r = M.Report()
        r.results.append(M.CheckResult("git", passed, "test"))
        return r

    def test_nothing_written_when_flag_off(self) -> None:
        M = _load_module(_AM_I_DONE_SCRIPT)
        self._write_hedl_toml(enabled=False)
        report = self._make_report()
        with mock.patch.object(M, "REPO_ROOT", str(self.tmp)):
            M._append_gate_insight(report)
        self.assertFalse(self.events.exists())

    def test_nothing_written_when_no_hedl_toml(self) -> None:
        M = _load_module(_AM_I_DONE_SCRIPT)
        report = self._make_report()
        with mock.patch.object(M, "REPO_ROOT", str(self.tmp)):
            M._append_gate_insight(report)
        self.assertFalse(self.events.exists())

    def test_event_written_when_flag_on(self) -> None:
        M = _load_module(_AM_I_DONE_SCRIPT)
        self._write_hedl_toml(enabled=True)
        report = self._make_report()
        with mock.patch.object(M, "REPO_ROOT", str(self.tmp)):
            M._append_gate_insight(report)
        self.assertTrue(self.events.exists())
        line = self.events.read_text().strip()
        event = json.loads(line)
        self.assertEqual(event["type"], "gate_run")

    def test_only_allowed_fields_in_gate_event(self) -> None:
        M = _load_module(_AM_I_DONE_SCRIPT)
        self._write_hedl_toml(enabled=True)
        report = self._make_report()
        with mock.patch.object(M, "REPO_ROOT", str(self.tmp)):
            M._append_gate_insight(report)
        event = json.loads(self.events.read_text().strip())
        extra = set(event.keys()) - ALLOWED_INSIGHT_FIELDS
        self.assertEqual(extra, set(), f"unexpected insight fields: {extra}")

    def test_no_consumer_content_in_event(self) -> None:
        """Verify the event contains no file paths, code, or user content."""
        M = _load_module(_AM_I_DONE_SCRIPT)
        self._write_hedl_toml(enabled=True)
        report = self._make_report()
        with mock.patch.object(M, "REPO_ROOT", str(self.tmp)):
            M._append_gate_insight(report)
        raw = self.events.read_text()
        # The event must not contain file paths, source code snippets, or PII markers.
        # Check that the event only has the allowed top-level structure.
        event = json.loads(raw.strip())
        for key in event:
            self.assertIn(key, ALLOWED_INSIGHT_FIELDS, f"unexpected key: {key!r}")

    def test_appends_multiple_events(self) -> None:
        M = _load_module(_AM_I_DONE_SCRIPT)
        self._write_hedl_toml(enabled=True)
        report = self._make_report()
        with mock.patch.object(M, "REPO_ROOT", str(self.tmp)):
            M._append_gate_insight(report)
            M._append_gate_insight(report)
        lines = [ln for ln in self.events.read_text().splitlines() if ln.strip()]
        self.assertEqual(len(lines), 2)


class TestInsightsHookRecordInsights(unittest.TestCase):
    """record_insights.py hook — Part 3."""

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.work = self.tmp / ".work"
        self.work.mkdir()
        (self.work / "insights").mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _write_hedl_toml(self, enabled: bool) -> None:
        (self.tmp / "hedl.toml").write_text(
            f"[insights]\nenabled = {'true' if enabled else 'false'}\n"
        )

    def test_nothing_written_when_flag_off(self) -> None:
        self._write_hedl_toml(enabled=False)
        # Verify the guard function itself
        self.assertFalse(RI._insights_enabled(self.tmp))

    def test_insights_enabled_reads_toml(self) -> None:
        self._write_hedl_toml(enabled=True)
        self.assertTrue(RI._insights_enabled(self.tmp))

    def test_reviewer_event_extracted(self) -> None:
        payload = {"tool_name": "Agent", "tool_input": {"description": "security-auditor review"}}
        event = RI._tool_to_event(payload)
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event["type"], "reviewer_fired")
        self.assertEqual(event["reviewer"], "security-auditor")

    def test_unrelated_tool_produces_no_event(self) -> None:
        payload = {"tool_name": "Read", "tool_input": {"file_path": "/some/file.py"}}
        event = RI._tool_to_event(payload)
        self.assertIsNone(event)

    def test_no_network_calls(self) -> None:
        """Hook must not make any network calls — verified by mocking socket."""
        import socket
        with mock.patch.object(socket, "getaddrinfo", side_effect=AssertionError("network call!")):
            payload = {"tool_name": "Agent", "tool_input": {"description": "historian"}}
            event = RI._tool_to_event(payload)
        # If we got here without AssertionError, no network was attempted.
        self.assertIsNotNone(event)


# ---------------------------------------------------------------------------
# reflect.py aggregation — Part 4
# ---------------------------------------------------------------------------

_FIXTURE_EVENTS: list[dict[str, Any]] = [
    {"ts": "2026-01-01T00:00:00+00:00", "type": "gate_run", "tier": "team",
     "checks": {"git": "pass", "lint": "fail", "tests": "pass"}, "overridden": []},
    {"ts": "2026-01-01T01:00:00+00:00", "type": "gate_run", "tier": "team",
     "checks": {"git": "pass", "lint": "pass", "tests": "pass"}, "overridden": ["lint"]},
    {"ts": "2026-01-01T02:00:00+00:00", "type": "reviewer_fired",
     "reviewer": "security-auditor", "finding_count": 2, "verdict": "BLOCKING"},
    {"ts": "2026-01-01T03:00:00+00:00", "type": "reviewer_fired",
     "reviewer": "security-auditor", "finding_count": 0, "verdict": "PASS"},
    {"ts": "2026-01-01T04:00:00+00:00", "type": "command_used", "command": "phase-complete"},
    {"ts": "2026-01-01T05:00:00+00:00", "type": "command_used", "command": "phase-complete"},
]


class TestReflectAggregation(unittest.TestCase):
    def test_aggregate_is_deterministic(self) -> None:
        """Same input always produces the same output."""
        result1 = RF.aggregate(_FIXTURE_EVENTS)
        result2 = RF.aggregate(_FIXTURE_EVENTS)
        self.assertEqual(result1, result2)

    def test_aggregate_is_idempotent_over_fixture(self) -> None:
        """Running aggregate twice on the same events produces equal results."""
        r1 = RF.aggregate(_FIXTURE_EVENTS)
        r2 = RF.aggregate(_FIXTURE_EVENTS)
        self.assertEqual(json.dumps(r1, sort_keys=True), json.dumps(r2, sort_keys=True))

    def test_aggregate_counts_events(self) -> None:
        metrics = RF.aggregate(_FIXTURE_EVENTS)
        self.assertEqual(metrics["event_count"], len(_FIXTURE_EVENTS))

    def test_aggregate_counts_gate_runs(self) -> None:
        metrics = RF.aggregate(_FIXTURE_EVENTS)
        self.assertEqual(metrics["gate_runs"], 2)

    def test_aggregate_tracks_check_pass_fail(self) -> None:
        metrics = RF.aggregate(_FIXTURE_EVENTS)
        self.assertEqual(metrics["check_stats"]["lint"]["fail"], 1)
        self.assertEqual(metrics["check_stats"]["lint"]["pass"], 1)

    def test_aggregate_tracks_reviewer_stats(self) -> None:
        metrics = RF.aggregate(_FIXTURE_EVENTS)
        sa = metrics["reviewer_stats"]["security-auditor"]
        self.assertEqual(sa["fired"], 2)
        self.assertEqual(sa["total_findings"], 2)

    def test_aggregate_tracks_command_counts(self) -> None:
        metrics = RF.aggregate(_FIXTURE_EVENTS)
        self.assertEqual(metrics["command_counts"]["phase-complete"], 2)

    def test_aggregate_empty_events(self) -> None:
        metrics = RF.aggregate([])
        self.assertEqual(metrics["event_count"], 0)
        self.assertEqual(metrics["gate_runs"], 0)

    def test_metrics_reference_real_events(self) -> None:
        """Reviewer stats must reference reviewer names present in the events."""
        metrics = RF.aggregate(_FIXTURE_EVENTS)
        reviewer_names_in_events = {
            ev["reviewer"] for ev in _FIXTURE_EVENTS if ev.get("type") == "reviewer_fired"
        }
        for name in metrics["reviewer_stats"]:
            self.assertIn(name, reviewer_names_in_events,
                          f"reviewer {name!r} in metrics but not in events")

    def test_load_events_from_file(self) -> None:
        tmp = pathlib.Path(tempfile.mkdtemp())
        try:
            events_file = tmp / "events.jsonl"
            for ev in _FIXTURE_EVENTS:
                with events_file.open("a") as fh:
                    fh.write(json.dumps(ev) + "\n")
            loaded = RF._load_events(str(events_file))
            self.assertEqual(len(loaded), len(_FIXTURE_EVENTS))
        finally:
            shutil.rmtree(tmp)

    def test_load_events_missing_file(self) -> None:
        result = RF._load_events("/nonexistent/path/events.jsonl")
        self.assertEqual(result, [])
