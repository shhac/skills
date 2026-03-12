# Edge Case: Upstream Reverts

## Trigger

Phase 1 step 5 finds revert commits in upstream's new commits (`git log --grep="^Revert"`).

## What's happening

Upstream intentionally reverted a change. If a fork-only branch contains the original (now-reverted) commits, rebasing that branch onto the new upstream will silently re-apply the reverted change. Git sees no conflict — the revert removed the code, and the rebase puts it back.

## Risk

The fork ends up with changes that upstream explicitly removed. This is a silent semantic conflict — git won't flag it.

## What to do

1. **Identify which reverts matter.** For each revert commit, find what was reverted (the commit message usually says "This reverts commit <sha>").

2. **Check if any fork-only branches contain the original commit:**
   ```bash
   git merge-base --is-ancestor <original-commit> <fork-only-branch>
   ```

3. **If no fork-only branches contain the reverted commit,** proceed normally.

4. **If a fork-only branch DOES contain it,** warn the user:
   *"Upstream reverted commit `<sha>` (`<message>`). Your branch `<branch>` contains the original change. Rebasing will silently re-apply it. Options:*
   - *(a) Proceed — you want the change in your fork despite upstream reverting it.*
   - *(b) Drop the commit from your branch before rebasing: `git rebase -i` and remove it.*
   - *(c) Skip this branch for now."*

5. Wait for the user's decision before rebasing affected branches.
