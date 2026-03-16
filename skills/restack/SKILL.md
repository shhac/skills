---
name: restack
description: Manage stacked branches — rebase cascades, detect landed PRs, show stack status. Use when branches are stacked (B on A on main), trunk has advanced, a mid-stack branch changed, or a PR has landed and descendants need rebasing. Lightweight alternative to Graphite that infers the stack from git history.
---

# Restack

Manage stacked branches without external tooling. Infers the dependency graph from git history (merge-base ancestry + commit distance) — no metadata files, no init step, no account.

Handles the common stacking pain points:
- **Trunk advances** → cascade rebases through the stack
- **Mid-stack edit** → rebase descendants onto the changed branch
- **PR lands** → detect merged branches, clean up, re-parent descendants
- **What's my stack?** → show tree structure with per-branch state

## Usage

`/restack [status | sync | <description of what to do>]`

- With **no arguments** — run status and ask the user what they'd like to do.
- With **status** — show the current stack state.
- With **sync** — fetch trunk, detect landed branches, restack.
- With **a description** — interpret intent and act.

## Helper script

This skill includes `scripts/restack.py` — a deterministic Python helper for graph inference and status detection. Requires Python 3.9+ (stdlib only).

Locate the script relative to this skill file. Invoke as:
```bash
python3 <skill-dir>/scripts/restack.py <subcommand> [options]
```

Subcommands: `status`, `graph`, `restack`, `sync`, `cleanup`. Run with `--help` for full usage. Default output is compact key-value (LLM-friendly). Add `--json` for structured output.

### Branch selection

The script supports three modes for selecting which branches to analyze:
- `--branches a,b,c` — explicit list
- `--prefix paul/` — all branches matching a prefix
- Neither — all local branches with commits ahead of trunk

If the user has a naming convention (e.g., `paul/*` branches), use `--prefix`. Otherwise, let it auto-discover.

## Instructions

You are managing stacked branches. Follow the steps below. This skill uses **incremental discovery** — read reference files only when triggered by specific conditions.

Reference files live in `references/` adjacent to this skill.

### Step 1: Determine Context

1. **Check for interrupted operation.** Look for branches matching `restack/pre-rebase/*`. If found, a previous restack was interrupted. Show the user what backups exist and offer to restore or clean up (`python3 <script> cleanup`).

2. **Identify trunk.** The script auto-detects `main` or `master`. If neither exists, ask the user.

3. **Identify branches.** If the user specified branches, use those. Otherwise, detect from context:
   - If the user has a branch prefix in their git config or CLAUDE.md, use `--prefix`
   - Otherwise, let the script auto-discover all local branches ahead of trunk

4. **Guard working tree.** If there are uncommitted changes:
   ```bash
   git stash push -m "restack: uncommitted changes"
   ```

### Step 2: Assess State

Run the status command:
```bash
python3 <script> status [--trunk <trunk>] [--prefix <prefix> | --branches <list>]
```

This outputs a tree showing each stack with per-branch state:
- `ok` — branch is based on the current tip of its parent
- `needs-restack` — parent has moved, branch needs rebasing
- `landed` — all patches are in trunk (PR was merged)
- `orphaned` — no detectable parent

**Incremental discovery triggers from status output:**
- ⚠️ If `ambiguous` entries appear → **read `references/ambiguous-graph.md`**
- ⚠️ If `landed` branches appear → **read `references/landed-branch.md`**
- ⚠️ If `orphaned` branches appear → ask the user what to do (rebase onto trunk, skip, or specify parent)

If the user ran `/restack` with no arguments, present this status and ask what they'd like to do.

### Step 3: Execute

Based on user intent and status, pick the appropriate flow:

#### Restack (trunk advanced)

→ **Read `references/trunk-advance.md`** for the basic cascade pattern.

Then **read the matching topology reference** based on the graph structure:

| Topology detected | Read this file |
|---|---|
| Linear stack (A→B, no branching) | `trunk-advance.md` is sufficient |
| Three or more branches in a chain (A→B→C→D) | `references/deep-chain.md` |
| Multiple branches off the same parent (B,C on A) | `references/fan-out.md` |
| Fan-out with depth (A→B,C and C→D→E) | `references/deep-fan.md` |
| Fan-out, reconverge, fan-out again (hourglass) | `references/fan-deep-fan.md` |
| Multiple independent stacks side by side | `references/independent-stacks.md` |
| Mixed (combination of above) | Read ALL applicable files |

1. Run the restack command to see the plan:
   ```bash
   python3 <script> restack [--trunk <trunk>] [--branches <list>]
   ```
   This creates backup refs and outputs the rebase plan.

2. Present the plan to the user. Wait for confirmation.

3. Execute the rebases in topological order (the `order` from the output):
   - **If parent is trunk:** `git rebase --empty=drop <trunk> <branch>`
   - **If parent is another stacked branch (strategy: `onto-backup`):** `git rebase --empty=drop --onto <parent> restack/pre-rebase/<parent> <branch>`
   - The backup ref `restack/pre-rebase/<parent>` captures the parent's pre-rebase tip — this is the correct `--onto` cut point.

4. If a rebase conflicts, resolve the conflict, then `git rebase --continue`. Continue with the next branch in the cascade.

5. After each successful rebase, push with `--force-with-lease`.

6. After all rebases complete, clean up: `python3 <script> cleanup`

#### Mid-stack edit (user amended a branch)

→ **Read `references/mid-stack-edit.md`** for the cascade pattern.

The `--branch` flag restacks only the descendants of the edited branch (not the branch itself, since the user already changed it).

1. Run:
   ```bash
   python3 <script> restack --branch <edited-branch> [--trunk <trunk>]
   ```

2. The plan output shows the rebase strategy for each branch:
   - **Immediate children of the edited branch (strategy: `onto-merge-base`):** Use the merge-base as the cut point, NOT the backup ref. This is because the backup captures the post-edit state:
     ```bash
     git rebase --empty=drop --onto <parent> <merge-base> <child>
     ```
     Any of the parent's old commits that get replayed are dropped by `--empty=drop`.
   - **Deeper descendants (strategy: `onto-backup`):** Use the normal backup ref approach.

3. Execute in topological order, resolve conflicts, push, clean up.

#### Sync (fetch trunk + detect landed + restack)

→ **Read `references/landed-branch.md`** for landed branch handling.

1. Fetch the remote and update local trunk:
   ```bash
   git fetch origin
   git checkout <trunk> && git merge --ff-only origin/<trunk>
   ```

2. Run the sync command to analyze:
   ```bash
   python3 <script> sync [--trunk <trunk>] [--branches <list>]
   ```

3. If landed branches are detected, confirm with the user before deleting them:
   - Delete local: `git branch -D <branch>`
   - Delete remote: `git push origin --delete <branch>`
   - ⚠️ If a mid-stack branch landed (not the bottom of the stack) → **read `references/mid-stack-landing.md`**

4. After landed branches are cleaned up, re-run status. If remaining branches need restacking, proceed with the restack flow above.

### Rebase Strategy Reference

Two `--onto` strategies depending on context:

**Strategy: `onto-backup`** (normal restack — parent was rebased by this operation):
```bash
git rebase --empty=drop --onto <parent> restack/pre-rebase/<parent> <child>
```
The backup ref is the parent's pre-rebase tip. Takes only the child's unique commits.

**Strategy: `onto-merge-base`** (mid-stack edit — parent was changed outside this operation):
```bash
mb=$(git merge-base <parent> <child>)
git rebase --empty=drop --onto <parent> $mb <child>
```
Uses the merge-base because the backup ref would capture the post-edit state. Any parent commits that get replayed are dropped as empty.

Without `--onto`, a plain `git rebase <parent>` would replay ALL commits from the merge-base, including the parent's old commits that now have new SHAs — causing duplicates and conflicts.

### Rules

- **Always show the plan** before executing rebases. Wait for confirmation unless the user explicitly asked to just do it.
- **Use `--force-with-lease`** when pushing rebased branches, never `--force`.
- **Create backups** before any rebases. The script handles this via `restack/pre-rebase/*` refs.
- **Clean up after success.** Run `python3 <script> cleanup` to remove backup refs.
- **Don't delete landed branches** without user confirmation.
- **Handle conflicts inline.** When a rebase conflicts, resolve it yourself (`git rebase --continue`), then continue the cascade. Only involve the user if the conflict is genuinely ambiguous.
- **Preserve the user's working state.** Stash before starting, restore the original branch and pop stash after.
