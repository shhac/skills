# Mid-Stack Edit

You've changed a branch in the middle of a stack (amended a commit, added new commits, or rebased it). Its descendants are now based on the old version and need restacking.

## Before (B was amended)

```
main:  ●──────●
       └─ A ──●
          └─ B (old) ──●
             └─ C ─────●
```

B has been amended to B'. C is still based on old B.

## What Happens

1. The script detects B's children (C) need restacking because B's tip ≠ the merge-base between B and C.
2. Use `--branch B` to restack only B's descendants:
   ```bash
   python3 <script> restack --branch B
   ```
3. C is an **immediate child** of the edited branch, so the merge-base strategy is used (not the backup ref, which would capture B's post-edit state):
   ```bash
   mb=$(git merge-base B C)
   git rebase --empty=drop --onto B $mb C
   ```
   This replays commits from the merge-base to C onto new B. Any of old-B's commits that get replayed are dropped by `--empty=drop` since they'll produce empty diffs against new B's equivalent changes.

## After

```
main:  ●──────●
       └─ A ──●
          └─ B' ─●
             └─ C'●
```

C' contains only its unique commits, replayed on top of the amended B'.

## Deep Stacks

If the stack is deeper (A→B→C→D), amending B causes a cascade: C rebases onto new B (using merge-base strategy, since C is an immediate child of the edited branch), then D rebases onto new C (using the normal backup-ref strategy, since D is a deeper descendant — the backup of C was created before C was rebased). The topological order ensures each branch is rebased only after its parent.

## Why Not the Backup Ref for Immediate Children?

The backup ref (`restack/pre-rebase/B`) is created when the restack script runs — AFTER the user already amended B. So the backup captures B's post-edit tip, which is the same as B itself. Using it as the `--onto` cut point would be: `git rebase --onto B B C` — a no-op that doesn't actually replay C's commits onto the new B.

The merge-base between B (post-edit) and C (still on old B) correctly identifies where they diverge, giving the right set of commits to replay.
