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
   - **Fully merged into upstream** (`git branch -r --merged <upstream>/<default-branch> | grep <fork>/`) — these can be deleted. Note: upstream may have squash-merged a branch, making commit SHAs differ. If `--merged` misses a branch, check whether `git diff <upstream>/<default-branch>...<fork>/<branch> --stat` is empty — if so, the branch's changes are already in upstream. See `examples/promoted-branch.md`.
   - **Have commits not in upstream** — for each remaining fork branch, check `git log --oneline <upstream>/<default-branch>..<branch-ref>`. These have local-only work to preserve.
5. Present a summary table and proposed plan. Wait for user confirmation before proceeding.

### Phase 2: Reset Shared Branches

For each shared branch (in order: default branch first, then others):

1. Check out the branch locally.
2. `git reset --hard <upstream>/<branch>` to align with upstream.
3. `git push <fork> <branch> --force-with-lease` to update the fork.

### Phase 3: Rebase Fork-Only Branches

Fork-only branches may depend on each other (e.g., stacked PRs). Rebase must respect this dependency graph.

**Before starting this phase**, read the example files in the `examples/` directory adjacent to this skill file. Match the detected dependency graph to the closest topology and follow its rebase strategy. The examples cover: independent branches, linear chains, fan-out, and deep chains.

#### Diagram legend

```
───       flow (left-to-right = time)
├── X     branch X forks here
└── X     branch X forks here (last branch at this point)
──┘       merge point (branch merges into line above)
●         notable state on the line
```

#### 3a. Build the dependency graph

For each fork-only branch, find its **parent** — the closest ancestor among shared branches and other fork-only branches:

```bash
for branch in "${fork_only_branches[@]}"; do
  best_parent=""
  best_distance=999999
  for candidate in "${shared_branches[@]}" "${fork_only_branches[@]}"; do
    [ "$candidate" = "$branch" ] && continue
    if git merge-base --is-ancestor "$candidate" "$branch"; then
      distance=$(git rev-list --count "$candidate".."$branch")
      if [ "$distance" -lt "$best_distance" ]; then
        best_distance=$distance
        best_parent=$candidate
      fi
    fi
  done
  # branch's parent is best_parent
done
```

This produces a forest of trees rooted at shared branches. Topologically sort it (parents before children) to get the rebase order.

#### 3b. Save pre-rebase refs

Before rebasing anything, save every fork-only branch's current tip:

```bash
old_ref[branch]=$(git rev-parse <branch>)
```

These old refs are needed for `--onto` when rebasing chained branches.

#### 3c. Rebase in topological order

For each fork-only branch (parents first, children last):

- **If parent is a shared branch:** `git rebase <shared-branch>`
- **If parent is another fork-only branch:** `git rebase --onto <parent> <old_ref[parent]> <branch>`
  - This replays only the branch's own commits (between old parent tip and branch tip) onto the rebased parent — avoiding duplicate commits from the parent's history.
- If rebase conflicts occur, resolve them. Show the user what you resolved and why.
- `git push <fork> <branch> --force-with-lease` to update the fork.

### Phase 4: Re-merge into Shared Branches

For each shared branch that has fork-only branches targeting it:

1. Check out the shared branch locally.
2. Merge each rebased fork-only branch with `--no-ff` in **topological order** (parents before children) to preserve merge commits.
   - These merges should be clean since the branches were just rebased. If a conflict occurs, resolve it and show the user what you resolved.
3. `git push <fork> <branch> --force-with-lease` to update the fork.

### Phase 5: Clean Up

1. Delete remote branches (`git push <fork> --delete <branch>`) that are fully merged into upstream.
2. List any local tracking branches that can be pruned.
3. Show the user a final summary of what was synced, merged, deleted, and what branches remain.

### Rules

- **Always confirm** the plan with the user before resetting or force-pushing.
- **Use `--force-with-lease`**, never `--force`, when pushing reset branches.
- **Preserve local-only work** — the point is to keep branches that upstream hasn't accepted while aligning with upstream's current state.
- **Don't delete branches that have unmerged work** — only clean up branches whose content is already in upstream (even if commit SHAs differ due to squash-merging).
- **Don't touch branches unrelated to the fork sync** — leave feature branches that aren't targeting a shared branch alone.
