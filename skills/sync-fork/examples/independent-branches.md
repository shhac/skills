# Independent Branches

Branches A and B both fork from the shared branch with no relationship to each other.

## Before (upstream has advanced)

```
fork/main:  ●────●────●
            ├─ A ┘    │
            └─── B ───┘
```

## Rebase Strategy

- **Order:** any (A and B are independent)
- **Targets:** both `git rebase main`
- **Merge order:** any

## After

```
fork/main:  ●─────────●────●────●
            (= upstream)   │    │
                       ├─ A┘    │
                       └─── B ──┘
```
