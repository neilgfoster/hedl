# Adversarial Review Panels

> Use `/adversarial-review [type]` to convene a panel.
> Full agent index and reference library: `skill/hedl/references/review-library.md`
> Dispatch rules (mandatory agent floor): `.work/config/dispatch-rules.json`

Panels are convened by the `review-dispatcher` agent, which reads the actual diff
and selects the minimal sufficient reviewer set. Budget auto-scaling applies;
check current tier with `/budget-status`.

For verdicts, finding format, when reviews run, the budget-tier table, and the
full review flow diagram, see `skill/hedl/references/commands.md`.

---

## Panel by task type

Core agents (`[core]` = named file in `.claude/agents/`) run via sub-agent calls.
Reference library agents are instantiated from `skill/hedl/references/review-library.md`.

| Task | Panel |
|------|-------|
| Coding | security-auditor, edge-case-hunter, scope-auditor + one of: performance-skeptic, new-engineer |
| Infra | chaos-engineer, security-auditor, operator + one of: cost-analyst, scope-auditor |
| Architecture / ADR | historian, devil-advocate, simplicity-enforcer, oss-scout + future-engineer or new-engineer |
| Requirements | ambiguity-hunter, contradiction-finder, scope-auditor, oss-scout |
| Phase review | evidence-checker, assumption-challenger, scope-auditor, historian |
| Self review | existential-challenger, drift-detector, determinism-auditor, historian |

Use 3–4 personas. Add a 5th only for high-stakes outputs.
`oss-scout` (WebSearch) — include for architecture and requirements involving new components.
`claude-code-scout` (WebSearch) — include when building agent tooling, slash commands, or hooks.
`model-optimizer` — include when agent definitions or model routing config is part of the change.
