# simplicity-enforcer — ADR-037 (doing-it-wrong rules)

**Run:** adversarial-review-2026-05-31-architecture-adr-037
**Model:** claude-opus-4-8 (1M) — Agent subagent
**Commit:** docs/doing-it-wrong-rules-adr @ pre-commit working tree

## Findings

| Severity | Finding | Evidence | Disposition |
|---|---|---|---|
| SIGNIFICANT | `[verify]` already enables deterministic project rules in the gate (a declared command running a project script), WORK-0021-hardened. A third mechanism (rule-dir + discovery + contract + runner) is unjustified. | am_i_done.py `_run_declared_check` / `_verify_allowlist`. | ACCEPTED — decision is now "adopt via a single `[verify]`-declared rules script"; no new mechanism. |
| SIGNIFICANT | The "minimal MVP" (discovery + contract + runner + workflow + seed) is already a plugin system; premature for ~1 rule. | ADR-037 Shape. | ACCEPTED — reduced to a single `project_rules`-style script; no discovery/contract until a real threshold. |
| MINOR | New gate surface (new check name, CLI_SPEC entry, protocol docs) to maintain. | ADR-037 Shape item 3. | ACCEPTED — eliminated by reusing `[verify]`. |
| MINOR | Building the framework before the rules exist inverts "rules accrue by use". | ADR-037 anti-accretion note. | ACCEPTED — flip the order: script first, prove the loop, design discovery only if 10+ rules accrue. |

## Recommendation

Don't build a new mechanism. Document the `[verify]`-a-rules-script convention,
put seed rules in one script, revisit directory discovery at 10-20 rules. Applied.
