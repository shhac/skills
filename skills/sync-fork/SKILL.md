---
name: sync-fork
description: Sync a forked repository with its upstream. Fetches both remotes, shows divergence, resets shared branches to upstream, re-merges local-only branches, cleans up branches already merged upstream, and pushes. Use when upstream has accepted PRs or moved ahead and you need to bring your fork in line.
---

# Sync Fork

Sync a forked repository with its upstream remote. Resets shared branches to upstream, re-merges any local-only work, and cleans up branches that upstream has already merged.

## Usage

`/sync-fork [<fork-remote> <upstream-remote>]`

- With **no arguments** — auto-detect if exactly two remotes exist. If more than two, ask the user to specify.
- With **one argument** — the provided name is ambiguous. Look up its URL with `git remote get-url <name>` and ask the user: *"`<name>` points to `<url>` — is this your fork, or the repo you forked from?"* Then ask for the other remote name.
- With **two arguments** — first is the fork remote, second is the upstream remote.

When auto-detecting with exactly two remotes, use heuristics to guess which is the fork and which is upstream (e.g., a remote named `origin` is more likely the fork; a remote whose URL org differs from the other is more likely upstream). Present your guess and ask the user to confirm.

## Instructions for Claude

You are syncing a fork with its upstream.

### Phase 0: Identify Remotes

1. Run `git remote -v` to list all remotes.
2. Resolve which remote is the fork and which is upstream using the rules in the Usage section above.
3. Confirm with the user before proceeding if there was any ambiguity.

### Phase 1: Assess Divergence

1. Fetch both remotes.
2. Identify **shared branches** — branches that exist on both remotes (e.g., both have `main`, or both have `main` and `develop`). These are the branches that will be reset to upstream.
3. For each shared branch, show the user:
   - **Commits on upstream not in fork** (`git log --oneline <fork>/<branch>..<upstream>/<branch>`)
   - **Commits on fork not in upstream** (`git log --oneline <upstream>/<branch>..<fork>/<branch>`)
4. Identify fork-only branches:
   - **Fully merged into upstream** (`git branch -r --merged <upstream>/<default-branch> | grep <fork>/`) — these can be deleted.
   - **Have commits not in upstream** — for each remaining fork branch, check `git log --oneline <upstream>/<default-branch>..<branch-ref>`. These have local-only work to preserve.
5. Present a summary table and proposed plan. Wait for user confirmation before proceeding.

### Phase 2: Reset and Re-merge

For each shared branch (in order: default branch first, then others):

1. Check out the branch locally.
2. `git reset --hard <upstream>/<branch>` to align with upstream.
3. For each fork-only branch that targets this shared branch and has commits **not** in upstream, merge it with `--no-ff` to preserve a merge commit.
   - If a merge conflict occurs, resolve it. Show the user what you resolved and why.
   - Merge branches in dependency order if any branch builds on another.
4. `git push <fork> <branch> --force-with-lease` to update the fork.

### Phase 2.5: Rebase Fork-Only Branches (if merge conflicts occurred)

If any merge conflicts occurred during Phase 2, ask the user if they'd like to rebase the fork-only branches onto the updated shared branch. This prevents the same conflicts from recurring on the next sync.

If the user confirms:

1. For each fork-only branch that caused a merge conflict:
   - Check out the branch locally.
   - `git rebase <shared-branch>` to replay its commits on top of the updated shared branch.
   - If rebase conflicts occur, resolve them. Show the user what you resolved.
   - `git push <fork> <branch> --force-with-lease` to update the fork.
2. Switch back to the default shared branch when done.

### Phase 3: Clean Up

1. Delete remote branches (`git push <fork> --delete <branch>`) that are fully merged into upstream.
2. List any local tracking branches that can be pruned.
3. Show the user a final summary of what was synced, merged, deleted, and what branches remain.

### Rules

- **Always confirm** the plan with the user before resetting or force-pushing.
- **Use `--force-with-lease`**, never `--force`, when pushing reset branches.
- **Preserve local-only work** — the point is to keep branches that upstream hasn't accepted while aligning with upstream's current state.
- **Don't delete branches that have unmerged work** — only clean up branches whose content is already in upstream (even if commit SHAs differ due to squash-merging).
- **Don't touch branches unrelated to the fork sync** — leave feature branches that aren't targeting a shared branch alone.
