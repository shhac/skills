# Deep Chain

Three or more branches stacked linearly: A → B → C → D. Each branch depends on the one below it.

## Before (main has advanced)

```
main:  ●──────●
       └─ A ──●
          └─ B ──●
             └─ C ──●
                └─ D ──●
```

## Rebase Strategy

Strict topological order — each branch is rebased only after its parent:

1. A onto main: `git rebase --empty=drop main A`
2. B onto new A: `git rebase --empty=drop --onto A restack/pre-rebase/A B`
3. C onto new B: `git rebase --empty=drop --onto B restack/pre-rebase/B C`
4. D onto new C: `git rebase --empty=drop --onto C restack/pre-rebase/C D`

Each `--onto` uses the previous branch's backup ref as the cut point.

## After

```
main:  ●──────────●
                   └─ A' ──●
                      └─ B' ──●
                         └─ C' ──●
                            └─ D' ──●
```

## Conflict Cascade

If a conflict occurs during B's rebase, resolve it before continuing to C. C's rebase depends on B's new position. If you abort B's rebase, you must also abort C and D (everything above the conflict point).

## Mid-Stack Edit in a Deep Chain

If the user amends B (not triggered by trunk advance), only C and D need restacking — not A or B. Use `--branch B` to restack B's descendants. C uses merge-base strategy (immediate child of edited branch), D uses normal backup-ref strategy (deeper descendant).
