# Independent Stacks

Multiple stacks exist side by side, rooted on trunk with no relationship between them.

## Before (main has advanced)

```
main:  ●── M1 ── M2 ── M3
              │         │
              └─ A ──●  └─ X ──●
                 └─ B ● 	└─ Y ──●
```

Stack 1 (A→B) was created from M1. Stack 2 (X→Y) was created from M3. Both need restacking.

## Rebase Strategy

The stacks don't interact. Rebase each stack independently, in topological order:

1. A onto main
2. B onto new A (--onto)
3. X onto main
4. Y onto new X (--onto)

The order between stacks doesn't matter — A before X or X before A both work.

## Status Output

The script's tree output shows them as separate branches off trunk:

```
trunk: main
├─ A (2 commits, needs-restack)
│  └─ B (1 commit, needs-restack)
└─ X (3 commits, needs-restack)
   └─ Y (2 commits, needs-restack)
```

## Partial Restack

If only one stack needs restacking (e.g., trunk advanced after stack 1 was created, but stack 2 was created more recently), the script only includes the stale branches. Use `--branch A` to restack only stack 1 and its descendants.
