# devil-advocate — WORK-0027 review

**Run:** adversarial-review-2026-05-30-architecture-work-0027
**Model:** claude-sonnet-4-6
**Commit:** 800e481..df2e89f

## Findings

| Severity | Category | Finding | Evidence | Status |
|---|---|---|---|---|
| SIGNIFICANT → recorded | Naming economics | the four WS-* hold the name "workstream" while the recursive concept fits it better | standards.md:107; ADR-019 | Accepted tradeoff — operator-approved; recoverable (recursive model gets a new name if built) |
| SIGNIFICANT → defused | Deferred migration | framed as "no migration" but is a migration deferred, correct only if WORK-0010 never ships | work.json WORK-0010; ADR-019 | Defused — ADR-019 note now states WS-* is never renamed; only the deferred primitive takes a new name |
| SIGNIFICANT → deferred | Unswept collision | recursive sense still ships in ADR-020/021/031 + (claimed) epic-template | ADR-031; epic-template.md | epic-template rebutted (column = classification); rest → WORK-0015 |
| MINOR | Verb choice | "Superseded" implies a successor; this is a postponement | ADR-019 Status | Kept per AC3; rationale distinguishes term-superseded from model-deferred |
| MINOR | Routing overstated | WS-* "routing" is prose LLM instruction, not code | iterate.md:33-36 | Noted — name kept on naming-economy grounds, not behaviour-coupling |

## Recommendations

- The decision withstands challenge on its core ("don't migrate 58 items for an
  unbuilt model"). The naming-economy and verb points are recorded; the cull-vs-
  keep question for the recursive cluster is routed to /phase-complete.
