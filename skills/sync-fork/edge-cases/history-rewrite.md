# Edge Case: Upstream History Rewrite

## Trigger

Phase 1 step 4 shows commits on BOTH sides that the other doesn't have for a shared branch. This means upstream has rewritten history (force-pushed, rebased, or squash-merged commits on the shared branch itself).

## What's happening

```
fork/main:      ●─A─B─C─●────●
                         ├─ X ┘
upstream/main:  ●─A─D─E─●
```

Commits B and C exist on fork but not upstream. Commits D and E exist on upstream but not fork. A is the last common ancestor. Upstream replaced B,C with D,E (e.g., rebased, squashed, or force-pushed).

## Risk

Phase 2's `reset --hard` will discard B and C from fork/main. If any fork-only branches were based on B or C (not just on the merge commits layered on top), their rebase in Phase 3 may encounter unexpected conflicts.

## What to do

1. **Warn the user clearly:** *"Upstream appears to have rewritten history on `<branch>`. Your fork has X commits that will be discarded by the reset. These are: [list commits]. Any fork-only branches based on these specific commits may need manual attention."*

2. **Check if fork-only branches are affected.** For each fork-only branch, check if any of the discarded commits are ancestors:
   ```bash
   # For each discarded commit
   git merge-base --is-ancestor <discarded-commit> <fork-only-branch>
   ```
   If true, that fork-only branch is directly affected.

3. **If no fork-only branches are affected,** proceed normally — the reset is safe, the discarded commits were only in the merge history on main.

4. **If fork-only branches ARE affected,** present this to the user and ask how to proceed. The rebase in Phase 3 will likely need manual conflict resolution.

5. Get explicit confirmation before continuing.
