# Deep Chain

Three or more branches stacked linearly: C is based on B, which is based on A.

## Before (upstream has advanced)

```
fork/main:  ●────●────●────●
            ├─ A ┘    │    │
            │  └─ B ──┘    │
            │     └─── C ──┘
```

## Rebase Strategy

- **Order:** A, then B, then C (strict topological order)
- **Targets:**
  - A: `git rebase main`
  - B: `git rebase --onto A <old-A> B`
  - C: `git rebase --onto B <old-B> C`
- **Merge order:** A, then B, then C

## After

```
fork/main:  ●─────────●────●────●────●
            (= upstream)   │    │    │
                       ├─ A┘    │    │
                       │  └─ B ┘    │
                       │     └─── C ┘
```

## Chained `--onto`

Each rebase uses the previous branch's saved old ref as the cut point:

```bash
old_A=$(git rev-parse A)
old_B=$(git rev-parse B)

git checkout A && git rebase main
git rebase --onto A $old_A B          # B's unique commits onto rebased A
git rebase --onto B $old_B C          # C's unique commits onto rebased B
```
