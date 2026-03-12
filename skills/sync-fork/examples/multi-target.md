# Multi-target Branches

Fork-only branches targeting different shared branches. A targets `main`, C targets `develop`.

## Before (both upstream/main and upstream/develop have advanced)

```
fork/main:     ●────●────●
               ├─ A ┘    │
               │  └─ B ──┘

fork/develop:  ●────●
               └─ C ┘
```

## Rebase Strategy

Each tree is independent — branches targeting `main` and branches targeting `develop`
are processed separately.

- **main tree:** A rebases onto `main`, B onto `A'` (via `--onto`)
- **develop tree:** C rebases onto `develop`
- **Merge order:** A then B into `main`. C into `develop`. The two trees don't interact.

## After

```
fork/main:     ●─────────●────●────●
               (= upstream)   │    │
                          ├─ A┘    │
                          │  └─ B ┘

fork/develop:  ●─────────●────●
               (= upstream)   │
                          └─ C┘
```

## Detection

The dependency graph algorithm naturally handles this — each branch's closest
ancestor determines which shared branch tree it belongs to. A's closest ancestor
is `main`, C's closest ancestor is `develop`. They form separate trees in the
forest.
