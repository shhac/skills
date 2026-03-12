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

Use two methods in order:

1. **Exact merge:** `git branch -r --merged <upstream/main>` catches branches whose
   tip is an ancestor of upstream/main (direct merge or fast-forward).

2. **Patch equivalence:** For remaining branches, check:
   ```bash
   git log --oneline --cherry-pick --right-only <upstream/main>...<fork>/A
   ```
   If this produces no output, every commit on A has a patch-equivalent commit in
   upstream (handles squash-merges and cherry-picks where SHAs differ).

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

## Edge case: partial promotion

If upstream squash-merged A alongside other work into a single commit, neither
`--merged` nor `--cherry-pick` will detect it (the combined commit's patch doesn't
match A's individual patches). In this case A will appear as "has commits not in
upstream" during Phase 1. When A is rebased in Phase 3, its commits may become
empty (dropped by `--empty=drop`). Phase 3 will then flag it: *"Branch A appears
to be fully absorbed by upstream."* The user can confirm deletion.
