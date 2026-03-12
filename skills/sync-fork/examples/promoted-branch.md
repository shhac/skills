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

A's content is in upstream but commit SHAs differ (squash-merge). B still has
commits not in upstream.

## What happens

1. **Phase 1** detects A as "fully merged into upstream" — it drops out of the
   fork-only set and is flagged for deletion.
2. **Phase 3** builds the dependency graph from remaining fork-only branches
   only. Since A is gone, B's closest ancestor is now `main` (the shared
   branch), not A.
3. B rebases directly onto the reset `main` with a plain `git rebase main`.
4. **Phase 5** deletes A from the fork remote.

## After

```
fork/main:  ●─────────●────●
            (= upstream)   │
                       └─ B┘

(A deleted — its content is in upstream)
```

## Edge case: squash-merge detection

Upstream may have squash-merged A, so `git merge-base --is-ancestor` won't
detect it as merged. Use `git branch -r --merged <upstream/main>` first, and
if that misses it, compare patches:

```bash
# Check if A's diff is already contained in upstream
git diff <upstream/main>...<fork>/A --stat
```

If the diff is empty (or near-empty), A's changes are in upstream even though
the commits differ.
