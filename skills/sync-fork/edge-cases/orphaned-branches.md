# Edge Case: Orphaned Branches

## Trigger

Phase 3a dependency graph algorithm finds no ancestor for a branch — no shared branch or fork-only branch passes `git merge-base --is-ancestor`.

## What's happening

The branch is disconnected from all known branches. Possible causes:
- The branch was based on a commit from a branch that has since been deleted from both remotes.
- The branch was created from a completely unrelated history (e.g., `git checkout --orphan`).
- The branch was rebased onto a commit that is no longer reachable from any current branch.

## What to do

1. **Report to the user:**
   *"Branch `<branch>` appears to be orphaned — it has no detectable ancestor among shared or fork-only branches. This means I can't determine where to rebase it."*

2. **Show context to help the user decide:**
   ```bash
   # What's the closest thing to an ancestor?
   git merge-base <default-shared-branch> <branch>
   # Show the branch's root commits
   git log --oneline --reverse <branch> | head -5
   ```

3. **Offer options:**
   - *(a) Rebase onto the default shared branch (`main`) — treat it as an independent branch.*
   - *(b) Rebase onto a specific branch the user names.*
   - *(c) Skip — leave the branch untouched.*

4. Wait for the user's decision. If they choose (a) or (b), proceed with a standard `git rebase <target> <branch>` in Phase 3d.
