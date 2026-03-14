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

## Instructions for Claude

### Step 1: Determine Context

1. **Check for interrupted operation.** Look for branches matching `restack/pre-rebase/*`. If found, a previous restack was interrupted. Show the user what backups exist and offer to restore or clean up (`python3 <script> cleanup`).

2. **Identify trunk.** The script auto-detects `main` or `master`. If neither exists, ask the user.

3. **Identify branches.** If the user specified branches, use those. Otherwise, detect from context:
   - If the user has a branch prefix in their git config or CLAUDE.md, use `--prefix`
   - Otherwise, let the script auto-discover all local branches ahead of trunk

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

If the user ran `/restack` with no arguments, present this status and ask what they'd like to do.

### Step 3: Handle Ambiguities

If the status output shows `ambiguous` entries, the script couldn't determine the stacking order for some branches (they fork from the same commit).

Draw an ASCII diagram showing both possible orderings and ask the user which is correct. Then re-run with the explicit `--branches` list in the intended order.

### Step 4: Execute

Based on user intent and status:

#### Restack (trunk advanced or mid-stack edit)

1. Run the restack command to see the plan:
   ```bash
   python3 <script> restack [--trunk <trunk>] [--branches <list>] [--branch <specific>]
   ```
   This creates backup refs and outputs the rebase plan.

2. Present the plan to the user. Wait for confirmation.

3. Execute the rebases in topological order (the `order` from the output):
   - **If parent is trunk:** `git rebase --empty=drop <trunk> <branch>`
   - **If parent is another stacked branch:** `git rebase --empty=drop --onto <parent> restack/pre-rebase/<parent> <branch>`

4. If a rebase conflicts, resolve the conflict, then `git rebase --continue`. Continue with the next branch in the cascade.

5. After each successful rebase, push with `--force-with-lease`.

6. After all rebases complete, clean up: `python3 <script> cleanup`

#### Sync (fetch trunk + detect landed + restack)

1. Fetch the remote:
   ```bash
   git fetch origin
   ```

2. Update local trunk:
   ```bash
   git checkout <trunk> && git merge --ff-only origin/<trunk>
   ```

3. Run the sync command to analyze:
   ```bash
   python3 <script> sync [--trunk <trunk>] [--branches <list>]
   ```

4. If landed branches are detected, confirm with the user before deleting them:
   - Delete local: `git branch -D <branch>`
   - Delete remote: `git push origin --delete <branch>`

5. If remaining branches need restacking, proceed with the restack flow above.

#### Mid-stack edit

When the user has changed a branch in the middle of a stack (amended, added commits, etc.), use `--branch <changed-branch>` to restack only that branch's descendants:

```bash
python3 <script> restack --branch <changed-branch> [--trunk <trunk>]
```

Then execute the rebases for the descendants only.

### Rebase Strategy Reference

The `--onto` rebase for stacked branches:

```bash
# After rebasing parent-branch, rebase child onto it:
git rebase --empty=drop --onto <parent-branch> restack/pre-rebase/<parent-branch> <child-branch>
```

This says: "take the commits unique to child (between old parent tip and child tip), replay them onto the new parent tip." The backup ref `restack/pre-rebase/<parent-branch>` is the old parent tip before it was rebased.

Without `--onto`, a plain `git rebase <parent>` would replay ALL commits from the merge-base, including the parent's old commits that now have new SHAs — causing duplicates and conflicts.

### Rules

- **Always show the plan** before executing rebases. Wait for confirmation unless the user explicitly asked to just do it.
- **Use `--force-with-lease`** when pushing rebased branches, never `--force`.
- **Create backups** before any rebases. The script handles this via `restack/pre-rebase/*` refs.
- **Clean up after success.** Run `python3 <script> cleanup` to remove backup refs.
- **Don't delete landed branches** without user confirmation.
- **Handle conflicts inline.** When a rebase conflicts, resolve it yourself (`git rebase --continue`), then continue the cascade. Only involve the user if the conflict is genuinely ambiguous.
- **Preserve the user's working state.** If they have uncommitted changes, stash before starting (`git stash push -m "restack: uncommitted changes"`) and pop after.
