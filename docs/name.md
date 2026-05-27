# The name

## Origin

"Hedl" is a stylized respelling of "heddle" -- a component of a loom. The
heddle is the mechanism that raises and separates individual warp threads so
the weft can pass cleanly between them, keeping many parallel threads from
tangling with each other.

## Why it fits

That is precisely Hedl's hardest problem: coordinating parallel agent
workstreams so they do not collide.

Three concepts from the loom map directly onto the design:

- **Warp** -- the fixed structure every change must trace back to. In Hedl
  that is the spec, the phase definition, and the definition of done. The warp
  threads are set before the weaving starts and do not move.

- **Weft** -- the work woven across that fixed structure. In Hedl that is the
  parallel branches running in separate git worktrees, each changing a
  disjoint set of files.

- **Heddle** -- the mechanism keeping the parallel threads separated so they
  pass cleanly through each other. In Hedl that is the deterministic gate:
  `am_i_done.py` enforces file-scope isolation (`--streams`), spec-driven
  phase discipline, and a no-inference pass/fail verdict before any stream is
  allowed to merge. Without the heddle the threads tangle; without the gate
  parallel branches collide.

## Spelling and pronunciation

Pronounced like "heddle." "Hedl" is the deliberate brand form -- one syllable,
no trailing vowel.
