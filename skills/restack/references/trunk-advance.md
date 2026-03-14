# Trunk Advance

The most common restack scenario. Trunk (main) has new commits from other people's merged PRs. Your stacked branches need rebasing to incorporate the new trunk state.

## Before (main has advanced)

```
main:  ●── M1 ── M2 ── M3 ── M4 ── M5
                  │
                  └─ A (a1, a2)
                     └─ B (b1, b2)
```

A was created from M2. main has since advanced to M5. A and B need restacking.

## What Happens

1. Rebase A onto current main:
   ```bash
   git rebase --empty=drop main A
   ```

2. Rebase B onto new A using `--onto` with the backup ref:
   ```bash
   git rebase --empty=drop --onto A restack/pre-rebase/A B
   ```
   `restack/pre-rebase/A` is A's tip before it was rebased (the old a2). This tells git: "take commits between old-A and B (just b1, b2), replay onto new-A."

## After

```
main:  ●── M1 ── M2 ── M3 ── M4 ── M5
                                      │
                                      └─ A' (a1', a2')
                                         └─ B' (b1', b2')
```

All branches are now based on the latest trunk.

## Why `--onto` is Required for B

Without `--onto`, `git rebase main B` would replay ALL commits from the merge-base (M2) to B — including A's old commits (a1, a2) which now have new SHAs (a1', a2'). This causes duplicates and conflicts.

`--onto` with the backup ref isolates just B's unique commits (b1, b2) and replays only those.
