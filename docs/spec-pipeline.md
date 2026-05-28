# Spec Pipeline — PRD → Epic → Task

The spec pipeline is optional. Use it when you need to capture requirements before
building — a new product, a significant feature, or any work where the "what" is not
yet clear. Skip it for bug fixes, refactors, and tasks where the work is already
well-defined.

---

## When to use it

| Work type | Pipeline needed? |
|-----------|-----------------|
| New product / greenfield | Yes — start with PRD |
| Significant new feature (>1 week) | Yes — PRD or epic |
| Small feature (1-3 days) | Optional — epic only |
| Bug fix, refactor, chore | No — go straight to work.json |

The guiding principle: process scales with work size. A one-line fix triggers no
PRD/epic/phase ceremony.

---

## The three levels

```
PRD (product requirements doc)
  └── Epics (major deliverable chunks)
        └── Tasks (work items in work.json)
```

### PRD

What problem are we solving and for whom? Captures:
- Problem statement and user need
- Goals and non-goals
- Success criteria (measurable)
- Constraints and risks
- Open questions

Lives at `docs/spec/prd.md`. Generated via the requirements flow ("requirements for X")
or written directly. One PRD per product or major initiative.

### Epic

A major deliverable that maps to one or more phases. Captures:
- Scope and boundaries
- Definition of done (maps to phase-{N}.json `definition_of_done`)
- Task breakdown (maps to work.json items)

Lives at `docs/spec/epics/epic-NNN.md`. One file per epic.

### Task

A work item that fits in a single session or day. Captured in `.work/work.json` as
a work item with `acceptance_criteria`. Tasks do not get their own spec files —
`work.json` is the source of truth.

---

## Directory layout

```
docs/spec/
  prd.md                    # product requirements doc (one per initiative)
  epics/
    epic-001.md             # one file per epic
    epic-002.md
```

Templates:
- PRD: `docs/spec/prd-template.md`
- Epic: `docs/spec/epic-template.md`

---

## Workflow

### Starting a new initiative

1. Write (or generate) `docs/spec/prd.md` using the requirements flow
2. Decompose into epics — one `docs/spec/epics/epic-NNN.md` per major chunk
3. Map each epic to a phase in `.work/phases/`
4. Decompose each epic into tasks in `.work/work.json`
5. Run `/iterate` to execute

### Starting a new feature (no full PRD)

1. Create `docs/spec/epics/epic-NNN.md` describing the feature
2. Add tasks to `.work/work.json`
3. Run `/iterate`

### Inline (no spec files)

For small, well-defined work: add items directly to `.work/work.json` and run
`/iterate`. No spec files required.

---

## Traceability

Each work item in `work.json` can reference its parent epic:

```json
{
  "id": "WORK-0042",
  "title": "Add user authentication",
  "epic": "epic-003",
  "workstream": "WS-ARCH"
}
```

The `epic` field is optional and informational — the gate does not enforce it.
