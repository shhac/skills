---
name: sync-fork
description: Sync a forked repository with its upstream. Fetches both remotes, shows divergence, resets shared branches to upstream, re-merges local-only branches, cleans up branches already merged upstream, and pushes. Use when upstream has accepted PRs or moved ahead and you need to bring your fork in line.
---

# Sync Fork

Sync a forked repository with its upstream remote. The fork's shared branches (e.g., `main`) are maintained as the equivalent of upstream plus local patches re-merged on top — a "patched upstream" model. Each sync resets to upstream, rebases fork-only branches, and re-merges them.

If upstream hasn't advanced (i.e., `upstream/main` is already an ancestor of `fork/main`), the sync is a no-op.

## Usage

`/sync-fork [<fork-remote> <upstream-remote>]`

- With **no arguments** — auto-detect if exactly two remotes exist. If more than two, ask the user to specify.
- With **one argument** — the provided name is ambiguous. Look up its URL with `git remote get-url <name>` and ask the user: *"`<name>` points to `<url>` — is this your fork, or the repo you forked from?"* Then ask for the other remote name.
- With **two arguments** — first is the fork remote, second is the upstream remote.

When auto-detecting with exactly two remotes, use heuristics to guess which is the fork and which is upstream (e.g., a remote named `origin` is more likely the fork; a remote whose URL org differs from the other is more likely upstream). Present your guess and ask the user to confirm.

## Diagram legend

Used in reference files adjacent to this skill:

```
───       flow (left-to-right = time)
├── X     branch X forks here
└── X     branch X forks here (last branch at this point)
──┘       merge point (branch merges into line above)
●         notable state on the line
```

## Instructions for Claude

You are syncing a fork with its upstream. Follow the phases below in order.

This skill uses **incremental discovery** — the main flow below covers the common case. When you encounter a specific situation (a topology, an edge case), you will be directed to read the relevant reference file at that point. **Do not read all reference files upfront.** Read them only when triggered.

Reference files live in two directories adjacent to this skill:
- `examples/` — branch topology diagrams and rebase strategies
- `edge-cases/` — handling for unusual situations

### Phase 0: Pre-flight

1. **Check for interrupted previous run.** Look for branches matching `sync-fork/*`. If found, a previous sync was interrupted. Show the user what backup branches exist and ask: restore from backups, or clean up (`git branch --list 'sync-fork/*' | xargs git branch -D`) and start fresh?

2. **Save current branch.** Record `git symbolic-ref --short HEAD` (or the detached commit) so we can restore it at the end.

3. **Guard dirty working tree.** Run `git status --porcelain`. If there are uncommitted changes, stash them:
   ```bash
   git stash push -m "sync-fork: uncommitted changes"
   ```
   This will be popped at the end. Stash is branch-independent, so it survives the checkout/reset operations that follow.

4. **Identify remotes.** Run `git remote -v` and resolve which remote is the fork and which is upstream using the rules in the Usage section above. Confirm with the user if there was any ambiguity.

### Phase 1: Assess Divergence

1. Fetch both remotes.

2. **No-op check.** For each shared branch, check `git merge-base --is-ancestor <upstream>/<branch> <fork>/<branch>`. If upstream is already an ancestor of fork for ALL shared branches, the sync is a no-op — upstream hasn't advanced. Tell the user and stop.

3. Identify **shared branches** — branches that exist on both remotes. These will be reset to upstream.

4. For each shared branch, show the user:
   - **Commits on upstream not in fork** (`git log --oneline <fork>/<branch>..<upstream>/<branch>`)
   - **Commits on fork not in upstream** (`git log --oneline <upstream>/<branch>..<fork>/<branch>`)
   - ⚠️ If BOTH sides have commits the other doesn't → **STOP and read `edge-cases/history-rewrite.md`** before proceeding.

5. Check upstream's new commits for reverts: `git log --oneline --grep="^Revert" <fork>/<branch>..<upstream>/<branch>`
   - ⚠️ If revert commits found → **STOP and read `edge-cases/upstream-reverts.md`** before proceeding.

6. Identify fork-only branches:
   - **Fully merged into upstream:** `git branch -r --merged <upstream>/<default-branch> | grep <fork>/` — these can be deleted.
   - For remaining branches, check patch equivalence: `git log --oneline --cherry-pick --right-only <upstream>/<default-branch>...<fork>/<branch>`. If empty, all patches have equivalents in upstream.
     - ⚠️ If a branch appears partially promoted (some but not all commits matched) → **read `edge-cases/partial-promotion.md`**.
     - For fully promoted branches → **read `examples/promoted-branch.md`** for the full handling strategy.
   - **Have commits not in upstream** — branches where the above check returns commits. These have local-only work to preserve.

7. Present a summary table and proposed plan. Wait for user confirmation before proceeding.

### Phase 2: Reset Shared Branches

For each shared branch (in order: default branch first, then others):

1. Create a backup branch: `git branch sync-fork/pre-reset/<branch> <fork>/<branch>`
2. Check out the branch locally. (If no local tracking branch exists, `git checkout` will auto-create one.)
3. `git reset --hard <upstream>/<branch>` to align with upstream.
4. `git push <fork> <branch> --force-with-lease` to update the fork.

### Phase 3: Rebase Fork-Only Branches

#### 3a. Build the dependency graph

For each fork-only branch, find its **parent** — the closest ancestor among shared branches and other fork-only branches. This runs AFTER Phase 2 (shared branches are at upstream state) but BEFORE any rebases (fork-only branches are still at their pre-sync state):

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

Topologically sort the result (parents before children) to get the rebase and merge order.

- ⚠️ If no ancestor found for a branch → **read `edge-cases/orphaned-branches.md`**.

#### 3b. MANDATORY: Read the matching topology reference

**You MUST read the applicable example file before continuing.** Match the dependency graph you just built to the correct topology and read that file now:

| Topology detected | Read this file |
|---|---|
| All branches root directly on a shared branch, no dependencies between them | `examples/independent-branches.md` |
| One branch depends on another (B based on A) | `examples/linear-chain.md` |
| Multiple branches depend on the same parent (B and C both based on A) | `examples/fan-out.md` |
| Three or more branches in a chain (A → B → C) | `examples/deep-chain.md` |
| Branches root on different shared branches | `examples/multi-target.md` |
| Mixed (combination of above) | Read ALL applicable files |

If the graph has any dependencies between fork-only branches, you **must** understand the `--onto` rebase strategy from the relevant file before proceeding. Getting this wrong causes duplicate commits and false conflicts.

#### 3c. Save pre-rebase refs as backup branches

Before rebasing anything, create a backup branch for every fork-only branch:

```bash
git branch sync-fork/pre-rebase/<branch> <branch>
```

These serve double duty: backup for rollback, and old-ref storage for `--onto` when rebasing chained branches (the backup branch tip IS the old ref).

#### 3d. Rebase in topological order

For each fork-only branch (parents first, children last):

1. **Check for merge commits:** `git log --merges sync-fork/pre-rebase/<parent>..<branch>`
   - ⚠️ If merge commits found → **read `edge-cases/merge-commits-in-branches.md`** before rebasing this branch.

2. **Rebase:**
   - **If parent is a shared branch:** `git rebase --empty=drop <shared-branch> <branch>`
   - **If parent is another fork-only branch:** `git rebase --empty=drop --onto <parent> sync-fork/pre-rebase/<parent> <branch>`
   - `--empty=drop` automatically discards commits already in upstream. If Git < 2.26, omit the flag and use `git rebase --skip` when prompted.
   - If rebase conflicts occur, resolve them. Show the user what you resolved and why.

3. **Check for empty result.** If ALL commits were dropped (branch now points to same commit as its parent), warn the user: *"Branch `<branch>` appears fully absorbed by upstream. Consider deleting it."*

4. `git push <fork> <branch> --force-with-lease` to update the fork.

### Phase 4: Re-merge into Shared Branches

The fork's shared branches are maintained as "upstream + local patches." This phase replays merge commits on top, so fork/main = upstream/main + fork-only work.

For each shared branch that has fork-only branches targeting it:

1. Check out the shared branch locally.
2. Merge each rebased fork-only branch with `--no-ff` in **topological order** (parents before children).
   - These merges should be clean since branches were just rebased. If a conflict occurs, resolve it and show the user what you resolved.
   - After merging a parent (e.g., A), merging its child (e.g., B) only brings in B's unique commits.
3. `git push <fork> <branch> --force-with-lease` to update the fork.

### Phase 5: Clean Up

1. Delete remote branches (`git push <fork> --delete <branch>`) that are fully merged into upstream.
2. Delete all backup branches: `git branch --list 'sync-fork/*' | xargs git branch -D`
3. Restore the original branch saved in Phase 0: `git checkout <saved-branch>`.
4. If changes were stashed in Phase 0, restore them: `git stash pop`.
5. List any local tracking branches that can be pruned.
6. Show the user a final summary of what was synced, rebased, merged, deleted, and what branches remain.

### Rules

- **Always confirm** the plan with the user before resetting or force-pushing.
- **Use `--force-with-lease`**, never `--force`, when pushing reset branches.
- **Preserve local-only work** — the point is to keep branches that upstream hasn't accepted while aligning with upstream's current state.
- **Don't delete branches that have unmerged work** — only clean up branches whose content is already in upstream (even if commit SHAs differ due to squash-merging).
- **Don't touch branches unrelated to the fork sync** — leave feature branches that aren't targeting a shared branch alone.
- **Backup branches use the `sync-fork/` prefix** — these are temporary and cleaned up at the end. If a sync is interrupted, they survive for recovery. Clean up manually with `git branch --list 'sync-fork/*' | xargs git branch -D`.
