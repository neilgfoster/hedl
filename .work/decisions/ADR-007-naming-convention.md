# ADR-007-naming-convention — Naming convention

## Status

Accepted — 2026-05-28 — Phase 0

## Decision

- **snake_case** — Python modules, config keys imported by machines.
- **kebab-case** — docs filenames, slash-command names, branch names, ADR
  slugs, any human-facing slug.

## Context

A naive "all hyphens" rule trips on Python: module names cannot contain
hyphens. A naive "all underscores" rule produces ugly URLs and branch names.
Pick by who reads it.

## Options considered

- All hyphens (consistent for humans) — rejected: breaks Python imports.
- All underscores (consistent for code) — rejected: ugly slugs, fights
  conventions used elsewhere (slash commands are kebab in every Claude tool
  I've seen).
- Two conventions, split by audience (chosen).

## Consequences

- New Python module: snake_case. New doc / slash command / branch:
  kebab-case.
- Config files (`.toml`, `.json`) use snake_case keys, because they are
  loaded by Python.
- Reviewers must apply the right rule to the right surface; "consistency" is
  not the right complaint.
