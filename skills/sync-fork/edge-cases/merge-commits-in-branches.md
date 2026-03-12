# Edge Case: Merge Commits in Fork-Only Branches

## Trigger

Phase 3d step 1 detects merge commits in a fork-only branch via `git log --merges <parent>..<branch>`.

## What's happening

The branch contains merge commits — e.g., the user merged another branch into it locally, or merged main into the feature branch at some point. Standard `git rebase` drops merge commits and linearizes the history.

## Risk

Dropping merge commits can:
- Lose the semantic grouping of merged work
- Cause unexpected conflicts if the merge resolved conflicts that the linearized rebase encounters again
- Change the effective diff if the merge brought in changes from another branch

## What to do

Present the user with options:

1. **`--rebase-merges`** — preserves merge topology during rebase. The merge commits are recreated on top of the new base. Use when the merge structure is meaningful (e.g., the branch intentionally merged another feature).
   ```bash
   git rebase --rebase-merges --empty=drop <target> <branch>
   # or with --onto:
   git rebase --rebase-merges --empty=drop --onto <parent> sync-fork/pre-rebase/<parent> <branch>
   ```

2. **Choose a different rebase base** — the user may know a cleaner point to rebase from that avoids the merge commits. Ask: *"Is there a commit or branch that represents a clean base for this branch, before the merges were introduced?"*

3. **Skip** — leave the branch untouched for this sync. The user can handle it manually.

Wait for the user's decision before rebasing this branch.
