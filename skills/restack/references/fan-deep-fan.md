# Fan-Deep-Fan

A fan-out reconnects into a single branch, which then fans out again. The "diamond" or "hourglass" pattern.

## Before (main has advanced)

```
main:  ●──────●
       └─ A ──●
          ├─ B ──●
          └─ C ──●
             └─ D ──●  (D is based on C, not on both B and C)
                ├─ E ──●
                └─ F ──●
```

A fans into B and C. C continues into D (the "deep" segment). D fans into E and F.

## Rebase Strategy

Topological order respects both fan levels:

1. A onto main
2. B onto new A (--onto backup A)
3. C onto new A (--onto backup A)
4. D onto new C (--onto backup C)
5. E onto new D (--onto backup D)
6. F onto new D (--onto backup D)

Steps 2/3 can swap. Steps 5/6 can swap.

## After

```
main:  ●──────────●
                   └─ A' ──●
                      ├─ B' ──●
                      └─ C' ──●
                         └─ D' ──●
                            ├─ E' ──●
                            └─ F' ──●
```

## The Diamond Trap

This topology looks like B and C might converge into D (a merge). But in a stacking workflow, D is based on ONE parent (C), not both. The graph builder confirms this — D's closest ancestor is C, not B. B is an independent sibling that happens to share a grandparent.

If D actually DOES merge B and C (a real merge commit), that's an edge case — the rebase will need `--rebase-merges` to preserve the merge topology, or the user should restructure.

## Mid-Stack Edit

| Edited branch | What needs restacking |
|---|---|
| A | Everything (B, C, D, E, F) |
| B | Nothing (B is a leaf) |
| C | D, E, F |
| D | E, F |

B is isolated — editing it affects nothing else. C is the bottleneck between the two fan levels — editing it cascades through the entire lower fan.
