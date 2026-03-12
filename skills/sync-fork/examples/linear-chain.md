# Linear Chain

B is based on A (e.g., stacked PRs). B contains A's commits plus its own.

## Before (upstream has advanced)

```
fork/main:  ●────●────●
            ├─ A ┘    │
            │  └─ B ──┘
```

## Rebase Strategy

- **Order:** A first, then B (parent before child)
- **Targets:**
  - A: `git rebase main`
  - B: `git rebase --onto A <old-A> B`
- **Merge order:** A first, then B

## After

```
fork/main:  ●─────────●────●────●
            (= upstream)   │    │
                       ├─ A┘    │
                       │  └─ B ┘
```

## Why `--onto` is required

After rebasing A, its commits have new SHAs. B still references A's old commits.
Plain `git rebase main` on B would replay all of B's commits (including A's old
ones), causing duplicates and conflicts.

`--onto` tells git: "take only the commits between old-A and B, replay them on
top of new-A."

```bash
old_A=$(git rev-parse A)    # save before rebasing A
git checkout A
git rebase main             # A is now rebased

git rebase --onto A $old_A B  # replay only B's unique commits onto rebased A
```
