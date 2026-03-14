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
3. C gets rebased onto new B via `--onto`:
   ```bash
   git rebase --empty=drop --onto B restack/pre-rebase/B C
   ```

## After

```
main:  ●──────●
       └─ A ──●
          └─ B' ─●
             └─ C'●
```

C' contains only its unique commits, replayed on top of the amended B'.

## Deep Stacks

If the stack is deeper (A→B→C→D), amending B causes a cascade: C rebases onto new B, then D rebases onto new C. The topological order ensures each branch is rebased only after its parent.
