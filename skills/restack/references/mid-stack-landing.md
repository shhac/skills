# Mid-Stack Landing

A branch in the MIDDLE of a stack has been merged into trunk, while branches above and below it still have unmerged work.

## Before (B landed, A and C remain)

```
main:  ●──────●──── (B's changes are here now)
       └─ A ──●
          └─ B ──● (landed)
             └─ C ──●
```

B was merged (or squash-merged) into main. A is still pending review. C depends on B.

## What Happens

This is trickier than bottom-of-stack landing because A is still active.

1. **Sync detects B as landed** — all of B's patches have equivalents in trunk.

2. **C needs re-parenting.** B is going away. C's new parent should be A (not trunk), because C was built on B which was built on A. C's unique commits should land on top of A's work.

3. **But the graph builder handles this automatically.** After B is deleted from the branch list, the graph builder finds C's closest ancestor among remaining branches. A is an ancestor of C (A→B→C), so A becomes C's parent.

4. **Restack C onto A:**
   ```bash
   git rebase --empty=drop A C
   ```
   B's commits that exist in C's history are also in trunk. With `--empty=drop`, they're discarded. C's unique commits land on A.

## After

```
main:  ●──────●──── (B's changes are here)
       └─ A ──●
          └─ C' ──●  (B's commits dropped, only C's unique work remains)
```

## Important: Delete B Before Rebuilding the Graph

The sync flow should:
1. Detect B as landed
2. Confirm with user and delete B
3. Re-run status/graph with B removed
4. C now naturally parents on A
5. Restack C onto A

If you rebuild the graph with B still present, B appears as C's parent and the script doesn't know B has landed (it still exists as a branch).

## What About A?

A is unaffected. It doesn't need restacking just because B landed. A's relationship to trunk hasn't changed.

If trunk also advanced (beyond just B's merge), A would need restacking too — but that's the normal trunk-advance case.
