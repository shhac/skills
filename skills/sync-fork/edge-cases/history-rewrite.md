# Edge Case: Upstream History Rewrite

## Trigger

Phase 1 step 4 shows commits on BOTH sides that the other doesn't have for a shared branch.

This can mean either:
- **Expected patched-upstream divergence:** the fork's shared branch contains fork-only branch commits and previous `sync-fork:` merge commits on top of an older upstream.
- **Actual upstream history rewrite:** upstream force-pushed, rebased, or squash-merged commits on the shared branch itself, and the fork-side commits are not clearly represented by known fork-only branches.

## What's happening

```
fork/main:      ●─A─B─C─●────●
                         ├─ X ┘
upstream/main:  ●─A─D─E─●
```

Commits B and C exist on fork but not upstream. Commits D and E exist on upstream but not fork. A is the last common ancestor. Upstream replaced B,C with D,E (e.g., rebased, squashed, or force-pushed).

## Risk

Phase 2's `reset --hard` will discard B and C from fork/main. In the normal patched-upstream case, Phase 3 rebases those commits from their fork-only branches and Phase 4 creates new merge commits on top of current upstream.

The risk is losing or mishandling fork-side commits that are not represented by active fork-only branches, or rebasing branches that depended on replaced upstream commits and now need manual conflict resolution.

## What to do

1. **Classify the fork-only side before warning.** List commits with:
   ```bash
   git log --oneline <upstream>/<branch>..<fork>/<branch>
   ```
   Separate previous `sync-fork:` merge commits from real patch commits. If the real patch commits are tips or ancestors of active fork-only branches, this is usually expected patched-upstream divergence.

2. **Warn the user clearly:** *"`<branch>` has fork-side commits that will be removed from the shared branch reset and replayed from fork-only branches. These are: [list commits]. Commits not represented by active fork-only branches may need manual attention."*

3. **Check if fork-only branches are affected.** For each fork-only branch, check if any of the discarded commits are ancestors:
   ```bash
   # For each discarded commit
   git merge-base --is-ancestor <discarded-commit> <fork-only-branch>
   ```
   If true, that fork-only branch is directly affected.

4. **If all non-merge discarded commits are represented by active fork-only branches,** proceed normally after confirmation. The reset removes old shared-branch copies; the rebase and re-merge phases reconstruct equivalent commits on top of upstream.

5. **If discarded commits are not represented by active fork-only branches,** present this to the user and ask how to proceed. The rebase in Phase 3 may not preserve those commits automatically.

6. Get explicit confirmation before continuing.

7. **After re-merge, verify the replay.** Before deleting backups, run a range comparison such as:
   ```bash
   base=$(git merge-base sync-fork/pre-reset/<branch> <upstream>/<branch>)
   git range-diff $base..sync-fork/pre-reset/<branch> <upstream>/<branch>..<branch>
   ```
   Expected output maps old patch commits to new rebased commits. Sync merge commits will normally be recreated with new SHAs.
