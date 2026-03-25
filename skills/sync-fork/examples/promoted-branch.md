# Promoted Branch

A fork-only branch (A) has been accepted upstream (merged or squash-merged).
Another branch (B) was based on A and still has unmerged work.

## Before (upstream accepted A, has advanced)

```
fork/main:  ●────●────●
            ├─ A ┘    │
            │  └─ B ──┘

upstream/main:  ●──────●
                (includes A's changes, possibly squash-merged)
```

A's content is in upstream but commit SHAs may differ (squash-merge, cherry-pick).
B still has commits not in upstream.

## Detection: how to identify promoted branches

Use three methods in order:

1. **Exact merge:** `git branch -r --merged <upstream/main>` catches branches whose
   tip is an ancestor of upstream/main (direct merge or fast-forward).

2. **Patch equivalence:** For remaining branches, check:
   ```bash
   git log --oneline --cherry-pick --right-only <upstream/main>...<fork>/A
   ```
   If this produces no output, every commit on A has a patch-equivalent commit in
   upstream (handles squash-merges and cherry-picks where SHAs differ).

3. **Content absorption (reverse-apply):** For remaining branches, generate the
   branch's patch and check if it can be reverse-applied against upstream's tree:
   ```bash
   mb=$(git merge-base <upstream/main> <fork>/A)
   # Set up a temp index with upstream's tree
   GIT_INDEX_FILE=/tmp/test.idx git read-tree <upstream/main>
   # Check if the branch's changes can be "undone" from upstream
   git diff $mb..<fork>/A | GIT_INDEX_FILE=/tmp/test.idx \
     git apply --cached --reverse --check -C0
   # Exit 0 = all changes present in upstream, branch is absorbed
   ```
   Uses `-C0` (zero context) so matching succeeds even when upstream added
   surrounding content beyond the branch's changes. This catches the case where
   upstream took the branch, added extra commits on top, then squash-merged
   everything. The individual patches don't match (method 2 fails) and the SHAs
   differ (method 1 fails), but the branch's content is fully present in upstream.

## What happens

1. **Phase 1** detects A as fully merged into upstream — it drops out of the
   fork-only set and is flagged for deletion.
2. **Phase 3** builds the dependency graph from remaining fork-only branches
   only. Since A is gone, B's closest ancestor is now `main` (the shared
   branch), not A.
3. B rebases directly onto the reset `main` with `git rebase main B --empty=drop`.
   If any of B's commits overlap with changes upstream already took from A, those
   commits become empty and are dropped automatically.
4. **Phase 5** deletes A from the fork remote.

## After

```
fork/main:  ●─────────●────●
            (= upstream)   │
                       └─ B┘

(A deleted — its content is in upstream)
```

## Edge case: upstream modified the branch before squash-merging

If upstream took A, added extra commits, then squash-merged everything into a
single commit, methods 1 and 2 won't detect it (SHAs differ, and the combined
patch doesn't match A's individual patches). Method 3 (content absorption) catches
this: merging A into the updated upstream produces no new changes, so A is
classified as promoted.

If the reverse-apply check fails (e.g., upstream substantially refactored the
changes), A will appear as active. When rebased in Phase 3, its commits may
become empty (dropped by `--empty=drop`). Phase 3 will then flag it: *"Branch A
appears to be fully absorbed by upstream."* The user can confirm deletion.
