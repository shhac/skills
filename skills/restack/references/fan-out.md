# Fan-Out

Multiple branches (B, C, D) are based on the same parent branch (A). They are siblings — independent of each other but all depend on A.

## Before (main has advanced)

```
main:  ●──────●
       └─ A ──●
          ├─ B ──●
          ├─ C ──●
          └─ D ──●
```

## Detection

The graph builder finds that B, C, and D all have A as their closest ancestor. None is an ancestor of the others — they are siblings, not stacked on each other.

## Rebase Strategy

1. A onto main: `git rebase --empty=drop main A`
2. B, C, D onto new A (in any order — they're independent):
   ```bash
   git rebase --empty=drop --onto A restack/pre-rebase/A B
   git rebase --empty=drop --onto A restack/pre-rebase/A C
   git rebase --empty=drop --onto A restack/pre-rebase/A D
   ```

All three use the same backup ref (`restack/pre-rebase/A`) because they all forked from the same point on old A.

## After

```
main:  ●──────────●
                   └─ A' ──●
                      ├─ B' ──●
                      ├─ C' ──●
                      └─ D' ──●
```

## Fan-Out vs Ambiguous

Fan-out is NOT the same as ambiguous branches. In a fan-out, all siblings have a clear parent (A). Ambiguity occurs when branches fork from the same point on trunk with no intermediary — the script can't tell if they should be stacked or independent.

## Mid-Stack Edit

If A is amended, all three children (B, C, D) need restacking. They're all immediate children of the edited branch, so all use the merge-base strategy.
