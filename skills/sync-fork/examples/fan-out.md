# Fan-out

Multiple branches (B, C) are based on a common fork-only branch (A).

## Before (upstream has advanced)

```
fork/main:  ●────●────●────●
            ├─ A ┘    │    │
            │  ├─ B ──┘    │
            │  └─── C ─────┘
```

## Rebase Strategy

- **Order:** A first, then B and C (in any order — they're siblings)
- **Targets:**
  - A: `git rebase main`
  - B: `git rebase --onto A <old-A> B`
  - C: `git rebase --onto A <old-A> C`
- **Merge order:** A first, then B and C in any order

## After

```
fork/main:  ●─────────●────●────●────●
            (= upstream)   │    │    │
                       ├─ A┘    │    │
                       │  ├─ B ┘    │
                       │  └─── C ───┘
```

## Detection

Both B and C have A as their closest ancestor (shorter `rev-list --count`
distance than main). They are siblings — neither is an ancestor of the other.
