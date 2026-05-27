"""
Tests for check_markdown_schema.py.

Covers: frontmatter presence/required fields, enum/pattern/length validation,
required title and title_pattern, required headings, required patterns,
and exclude_globs skipping.
"""

import os
import sys
import tempfile
import textwrap
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import check_markdown_schema as cms

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

AGENT_SCHEMA = {
    "id": "agent",
    "glob": ".claude/agents/*.md",
    "frontmatter": {
        "required": ["name", "description", "tools", "model"],
        "fields": {
            "name": {"pattern": "^[a-z][a-z0-9-]+$"},
            "description": {"min_length": 10, "max_length": 200},
            "model": {"enum": ["haiku", "sonnet", "opus"]},
        },
    },
}

ADR_SCHEMA = {
    "id": "adr",
    "glob": ".work/decisions/ADR-*.md",
    "title_pattern": r"^# ADR-\d{3}-.+",
    "required_headings": ["Status", "Context", "Decision", "Consequences"],
}

REVIEW_REPORT_SCHEMA = {
    "id": "review-report",
    "glob": ".work/reviews/**/report.md",
    "required_headings": [
        "Dimension Scores",
        "Strengths",
        "Blocking Findings",
        "Significant Findings",
        "Minor Findings",
        "Next Actions",
    ],
    "required_patterns": [
        {"pattern": r"\*\*Log:\*\*", "description": "log line"},
        {"pattern": r"\*\*Session:\*\*", "description": "session type"},
        {"pattern": r"\*\*Depth:\*\*", "description": "review depth"},
        {"pattern": r"\*\*Commit:\*\*", "description": "commit SHA"},
    ],
}

REVIEW_AGENT_SCHEMA = {
    "id": "review-agent",
    "glob": ".work/reviews/**/*.md",
    "exclude_globs": [
        ".work/reviews/**/report.md",
        ".work/reviews/README.md",
    ],
    "required_headings": ["Findings"],
    "required_patterns": [
        {"pattern": r"\*\*Run:\*\*"},
        {"pattern": r"\*\*Model:\*\*"},
        {"pattern": r"\*\*Commit:\*\*"},
    ],
}

COMMAND_SCHEMA = {
    "id": "command",
    "glob": ".claude/commands/*.md",
    "required_title": True,
    "title_max_length": 120,
}


VALID_AGENT_CONTENT = textwrap.dedent("""\
    ---
    name: my-agent
    description: Does something useful for review purposes.
    tools: Read, Grep
    model: haiku
    ---

    # my-agent

    Agent body.
""")

VALID_ADR_CONTENT = textwrap.dedent("""\
    # ADR-001-use-python

    ## Status

    Accepted

    ## Context

    We need a scripting language.

    ## Decision

    Use Python 3.

    ## Consequences

    All scripts must be Python 3 compatible.
""")

VALID_REVIEW_REPORT_CONTENT = textwrap.dedent("""\
    # Repo Health — 2026-01-01

    **Log:** written at 2026-01-01
    **Session:** fresh
    **Depth:** Full
    **Commit:** abc1234

    ## Dimension Scores

    | Dimension | Score |
    |---|---|

    ## Strengths

    - Good.

    ## Blocking Findings

    None.

    ## Significant Findings

    None.

    ## Minor Findings

    None.

    ## Next Actions

    Proceed.
""")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate(content: str, schema: dict[str, Any], filename: str = "test.md") -> list[dict[str, Any]]:
    """Write content to a temp file and validate it, returning violations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(content)
        return cms.validate_file(filepath, schema, tmpdir)


def _fields(violations: list[dict[str, Any]]) -> list[str]:
    return [v["field"] for v in violations]


def _messages(violations: list[dict[str, Any]]) -> list[str]:
    return [v["message"] for v in violations]


# ---------------------------------------------------------------------------
# Frontmatter — presence
# ---------------------------------------------------------------------------

def test_valid_agent_passes() -> None:
    violations = _validate(VALID_AGENT_CONTENT, AGENT_SCHEMA)
    assert violations == [], f"Expected no violations, got: {violations}"


def test_no_frontmatter_fails() -> None:
    content = "# my-agent\n\nNo frontmatter here.\n"
    violations = _validate(content, AGENT_SCHEMA)
    assert "frontmatter" in _fields(violations)


def test_missing_required_field_fails() -> None:
    content = textwrap.dedent("""\
        ---
        name: my-agent
        tools: Read
        model: haiku
        ---
        # my-agent
    """)
    violations = _validate(content, AGENT_SCHEMA)
    fields = _fields(violations)
    assert "description" in fields


def test_all_required_fields_present_passes() -> None:
    violations = _validate(VALID_AGENT_CONTENT, AGENT_SCHEMA)
    assert not any(v["field"] in ("name", "description", "tools", "model") for v in violations)


# ---------------------------------------------------------------------------
# Frontmatter — enum validation
# ---------------------------------------------------------------------------

def test_invalid_model_enum_fails() -> None:
    content = VALID_AGENT_CONTENT.replace("model: haiku", "model: gpt-4")
    violations = _validate(content, AGENT_SCHEMA)
    assert "model" in _fields(violations)
    assert any("not in allowed values" in m for m in _messages(violations))


def test_valid_model_enum_passes() -> None:
    for model in ("haiku", "sonnet", "opus"):
        content = VALID_AGENT_CONTENT.replace("model: haiku", f"model: {model}")
        violations = _validate(content, AGENT_SCHEMA)
        assert not any(v["field"] == "model" for v in violations), f"model={model} should pass"


# ---------------------------------------------------------------------------
# Frontmatter — pattern validation
# ---------------------------------------------------------------------------

def test_invalid_name_pattern_fails() -> None:
    content = VALID_AGENT_CONTENT.replace("name: my-agent", "name: My_Agent")
    violations = _validate(content, AGENT_SCHEMA)
    assert "name" in _fields(violations)


def test_valid_name_pattern_passes() -> None:
    content = VALID_AGENT_CONTENT.replace("name: my-agent", "name: security-auditor")
    violations = _validate(content, AGENT_SCHEMA)
    assert not any(v["field"] == "name" for v in violations)


# ---------------------------------------------------------------------------
# Frontmatter — length validation
# ---------------------------------------------------------------------------

def test_description_too_short_fails() -> None:
    content = VALID_AGENT_CONTENT.replace(
        "description: Does something useful for review purposes.",
        "description: Short.",
    )
    violations = _validate(content, AGENT_SCHEMA)
    assert "description" in _fields(violations)
    assert any("too short" in m for m in _messages(violations))


def test_description_too_long_fails() -> None:
    long_desc = "A" * 201
    content = VALID_AGENT_CONTENT.replace(
        "description: Does something useful for review purposes.",
        f"description: {long_desc}",
    )
    violations = _validate(content, AGENT_SCHEMA)
    assert "description" in _fields(violations)
    assert any("too long" in m for m in _messages(violations))


def test_description_boundary_passes() -> None:
    # exactly 10 chars
    content = VALID_AGENT_CONTENT.replace(
        "description: Does something useful for review purposes.",
        "description: 1234567890",
    )
    violations = _validate(content, AGENT_SCHEMA)
    assert not any(v["field"] == "description" for v in violations)


# ---------------------------------------------------------------------------
# Title checks
# ---------------------------------------------------------------------------

def test_required_title_missing_fails() -> None:
    content = "No heading here.\n"
    violations = _validate(content, COMMAND_SCHEMA)
    assert "title" in _fields(violations)


def test_required_title_present_passes() -> None:
    content = "# /my-command\n\nBody.\n"
    violations = _validate(content, COMMAND_SCHEMA)
    assert not any(v["field"] == "title" for v in violations)


def test_title_too_long_fails() -> None:
    long_title = "A" * 121
    content = f"# {long_title}\n\nBody.\n"
    violations = _validate(content, COMMAND_SCHEMA)
    assert "title" in _fields(violations)
    assert any("too long" in m for m in _messages(violations))


def test_title_pattern_valid_passes() -> None:
    violations = _validate(VALID_ADR_CONTENT, ADR_SCHEMA)
    assert not any(v["field"] == "title" for v in violations)


def test_title_pattern_invalid_fails() -> None:
    content = VALID_ADR_CONTENT.replace("# ADR-001-use-python", "# Use Python")
    violations = _validate(content, ADR_SCHEMA)
    assert "title" in _fields(violations)


def test_title_pattern_no_heading_fails() -> None:
    content = "No heading.\n\n## Status\n\nAccepted.\n"
    violations = _validate(content, ADR_SCHEMA)
    assert "title" in _fields(violations)


# ---------------------------------------------------------------------------
# Required headings
# ---------------------------------------------------------------------------

def test_missing_required_heading_fails() -> None:
    content = VALID_ADR_CONTENT.replace("## Context\n\nWe need a scripting language.\n\n", "")
    violations = _validate(content, ADR_SCHEMA)
    assert "heading" in _fields(violations)
    assert any("Context" in m for m in _messages(violations))


def test_all_required_headings_present_passes() -> None:
    violations = _validate(VALID_ADR_CONTENT, ADR_SCHEMA)
    assert not any(v["field"] == "heading" for v in violations)


def test_review_report_missing_heading_fails() -> None:
    content = VALID_REVIEW_REPORT_CONTENT.replace("## Strengths\n\n- Good.\n\n", "")
    violations = _validate(content, REVIEW_REPORT_SCHEMA)
    assert any(v["field"] == "heading" and "Strengths" in v["message"] for v in violations)


def test_review_report_all_headings_pass() -> None:
    violations = _validate(VALID_REVIEW_REPORT_CONTENT, REVIEW_REPORT_SCHEMA)
    heading_viols = [v for v in violations if v["field"] == "heading"]
    assert heading_viols == [], f"Unexpected heading violations: {heading_viols}"


# ---------------------------------------------------------------------------
# Required patterns
# ---------------------------------------------------------------------------

def test_missing_required_pattern_fails() -> None:
    content = VALID_REVIEW_REPORT_CONTENT.replace("**Log:** written at 2026-01-01\n", "")
    violations = _validate(content, REVIEW_REPORT_SCHEMA)
    assert any(v["field"] == "pattern" and "log" in v["message"].lower() for v in violations)


def test_all_required_patterns_present_passes() -> None:
    violations = _validate(VALID_REVIEW_REPORT_CONTENT, REVIEW_REPORT_SCHEMA)
    pattern_viols = [v for v in violations if v["field"] == "pattern"]
    assert pattern_viols == [], f"Unexpected pattern violations: {pattern_viols}"


# ---------------------------------------------------------------------------
# exclude_globs — file skipped when it matches an exclusion
# ---------------------------------------------------------------------------

def test_exclude_globs_skip_report_md() -> None:
    """report.md is excluded from review-agent schema; it should match no schema in that set."""
    schemas = [REVIEW_REPORT_SCHEMA, REVIEW_AGENT_SCHEMA]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = os.path.join(tmpdir, ".work", "reviews", "repo-health-2026-01-01")
        os.makedirs(run_dir)

        report_path = os.path.join(run_dir, "report.md")
        with open(report_path, "w") as fh:
            fh.write(VALID_REVIEW_REPORT_CONTENT)

        # find_schema_for_file should return review-report schema (not review-agent)
        schema = cms.find_schema_for_file(report_path, schemas, tmpdir)
        assert schema is not None
        assert schema["id"] == "review-report", f"Expected review-report, got {schema['id']}"


def test_exclude_globs_readme_gets_no_schema() -> None:
    """README.md in reviews dir is excluded from review-agent and not in review-report glob."""
    schemas = [REVIEW_REPORT_SCHEMA, REVIEW_AGENT_SCHEMA]

    with tempfile.TemporaryDirectory() as tmpdir:
        reviews_dir = os.path.join(tmpdir, ".work", "reviews")
        os.makedirs(reviews_dir)

        readme_path = os.path.join(reviews_dir, "README.md")
        with open(readme_path, "w") as fh:
            fh.write("# Reviews\n")

        schema = cms.find_schema_for_file(readme_path, schemas, tmpdir)
        assert schema is None, f"README.md should have no schema, got: {schema}"


def test_agent_file_in_run_dir_matches_review_agent_schema() -> None:
    """Individual agent output files in run dirs should match review-agent schema."""
    schemas = [REVIEW_REPORT_SCHEMA, REVIEW_AGENT_SCHEMA]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = os.path.join(tmpdir, ".work", "reviews", "repo-health-2026-01-01")
        os.makedirs(run_dir)

        agent_path = os.path.join(run_dir, "security-auditor.md")
        with open(agent_path, "w") as fh:
            fh.write("# security-auditor\n")

        schema = cms.find_schema_for_file(agent_path, schemas, tmpdir)
        assert schema is not None
        assert schema["id"] == "review-agent", f"Expected review-agent, got {schema}"


# ---------------------------------------------------------------------------
# validate_all — integration
# ---------------------------------------------------------------------------

def test_validate_all_specific_files_skips_nonexistent() -> None:
    """Passing a nonexistent file does not raise; it is silently skipped."""
    violations = cms.validate_all([AGENT_SCHEMA], "/tmp", specific_files=["/tmp/nonexistent.md"])
    assert violations == []


def test_validate_all_no_files_returns_empty_for_empty_dir() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        violations = cms.validate_all([AGENT_SCHEMA], tmpdir)
        assert violations == []


# ---------------------------------------------------------------------------
# _parse_frontmatter
# ---------------------------------------------------------------------------

def test_parse_frontmatter_basic() -> None:
    content = "---\nname: foo\nmodel: haiku\n---\n\n# Body\n"
    fm, body = cms._parse_frontmatter(content)
    assert fm == {"name": "foo", "model": "haiku"}
    assert "# Body" in body


def test_parse_frontmatter_missing_returns_none() -> None:
    content = "# No frontmatter\n\nBody text.\n"
    fm, body = cms._parse_frontmatter(content)
    assert fm is None
    assert body == content


def test_parse_frontmatter_unclosed_returns_none() -> None:
    content = "---\nname: foo\n\n# No closing delimiter\n"
    fm, body = cms._parse_frontmatter(content)
    assert fm is None
