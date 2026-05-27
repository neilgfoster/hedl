"""Tests for .github/scripts/check_pr_template.py.

Covers: empty/unfilled/valid PR bodies, code-fence bypass, substring
bypass, lowercase prefix, indented checkbox, and bare-dash bullet.

Run: pytest skill/hedl/tests/test_check_pr_template.py
"""

import importlib.util
import os
import pathlib
import sys
import unittest

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "check_pr_template.py"


def _run(body: str) -> tuple[int, list[str]]:
    """Reload the module with PR_BODY set; return (exit_code, errors)."""
    os.environ["PR_BODY"] = body
    # Reload from source so module-level PR_BODY refreshes.
    spec = importlib.util.spec_from_file_location("check_pr_template", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_pr_template"] = mod
    spec.loader.exec_module(mod)
    mod.ERRORS.clear()
    code = mod.main()
    return code, list(mod.ERRORS)


VALID_BODY = """## Summary

Adds a feature.

## Work item

Closes WORK-42

## Type

- [x] feature

## Changes

- Did one thing
- Did another thing

## Validation

Tests pass; manually verified.
"""

VALID_NONE_BODY = """## Summary

Foundational rename.

## Work item

none — bootstrap refactor, no tracked work item yet

## Type

- [x] refactor

## Changes

- Renamed everything

## Validation

Symmetric diff verified.
"""


class TestCheckPrTemplate(unittest.TestCase):
    def test_empty_body_fails(self) -> None:
        code, _ = _run("")
        self.assertEqual(code, 1)

    def test_null_string_body_fails(self) -> None:
        # GitHub Actions can render `null` body as the literal string "null".
        code, _ = _run("null")
        self.assertEqual(code, 1)

    def test_unfilled_template_fails_with_per_section_errors(self) -> None:
        unfilled = """## Summary

<!-- Required: 1-3 sentences -->

## Work item

<!-- Required: WORK-XXXX or "none" with justification -->

## Type

- [ ] feature
- [ ] fix

## Changes

<!-- Required: bullet list -->

## Validation

<!-- Required: how was this verified? -->
"""
        code, errs = _run(unfilled)
        self.assertEqual(code, 1)
        # At least Summary, Work item, Type, Changes, Validation each fail.
        self.assertGreaterEqual(len(errs), 5)

    def test_valid_body_passes(self) -> None:
        code, errs = _run(VALID_BODY)
        self.assertEqual(code, 0, msg=str(errs))

    def test_valid_none_with_justification_passes(self) -> None:
        code, errs = _run(VALID_NONE_BODY)
        self.assertEqual(code, 0, msg=str(errs))

    def test_sec8_fenced_heading_in_summary_does_not_satisfy_validation(self) -> None:
        # A fenced `## Changes` inside Summary must NOT terminate Summary
        # nor satisfy the Changes section.
        body = """## Summary

```
## Changes
- decoy bullet inside code fence
```

## Work item

Closes WORK-1

## Type

- [x] feature

## Validation

ok
"""
        # Changes section is missing once fenced blocks are stripped.
        code, errs = _run(body)
        self.assertEqual(code, 1)
        self.assertTrue(any("Changes" in e for e in errs))

    def test_sec9_substring_none_in_paragraph_does_not_satisfy_work_item(self) -> None:
        body = VALID_BODY.replace(
            "Closes WORK-42",
            "This affects none of the legacy paths but no WORK ref",
        )
        code, errs = _run(body)
        self.assertEqual(code, 1)
        self.assertTrue(any("Work item" in e for e in errs))

    def test_sec10_lowercase_prefix_does_not_satisfy_work_item(self) -> None:
        body = VALID_BODY.replace("Closes WORK-42", "Closes work-42")
        code, errs = _run(body)
        self.assertEqual(code, 1)
        self.assertTrue(any("Work item" in e for e in errs))

    def test_ec4_unchecked_box_fails(self) -> None:
        body = VALID_BODY.replace("- [x] feature", "- [ ] feature")
        code, errs = _run(body)
        self.assertEqual(code, 1)
        self.assertTrue(any("Type" in e for e in errs))

    def test_ec5_bare_dash_does_not_count_as_bullet(self) -> None:
        body = VALID_BODY.replace("- Did one thing\n- Did another thing", "-\n-")
        code, errs = _run(body)
        self.assertEqual(code, 1)
        self.assertTrue(any("Changes" in e for e in errs))

    def test_none_without_justification_fails(self) -> None:
        body = VALID_BODY.replace("Closes WORK-42", "none")
        code, errs = _run(body)
        self.assertEqual(code, 1)
        self.assertTrue(any("Work item" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
