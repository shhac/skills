# Landed Branch

A branch in the stack has been merged (or squash-merged) into trunk. Its descendants need re-parenting.

## Before (A was merged into main)

```
main:  ●──────●──── (A's changes are here now)
       └─ A ──●
          └─ B ──●
             └─ C ●
```

A's patches are in trunk (possibly squash-merged with different SHAs). B and C still reference old A.

## Detection

The script detects landed branches via:
1. **Exact merge:** branch tip is an ancestor of trunk
2. **Patch equivalence:** `git log --cherry-pick --right-only trunk...branch` produces no output (all patches have equivalents in trunk, handles squash-merge)

## What Happens

1. The `sync` command reports A as `landed`.
2. After user confirms, delete A (local + remote).
3. B's parent was A. With A gone, B's closest ancestor is now trunk (main).
4. Restack B onto main. B's commits that overlap with A's (now in trunk) are dropped by `--empty=drop`.
5. Then restack C onto new B.

## After

```
main:  ●──────●──────────●
       (includes A's work) │
                       └─ B'●
                          └─ C'●
```

B' contains only commits unique to B (A's commits were dropped as empty). C' is unchanged relative to B'.

## Partial Landing

If A was partially merged (some commits cherry-picked), the `sync` command won't flag it as landed. When B is restacked onto trunk, the overlapping commits become empty and are dropped by `--empty=drop`. The remaining commits survive.
