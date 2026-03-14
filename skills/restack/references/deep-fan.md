# Deep Fan

A combination of depth and fan-out: a branch has multiple children, and some of those children have their own children. This is the most complex common topology.

## Before (main has advanced)

```
main:  ●──────●
       └─ A ──●
          ├─ B ──●
          │  └─ D ──●
          │     └─ E ──●
          └─ C ──●
             └─ F ──●
```

A has two children (B, C). B has a child chain (D→E). C has a child (F).

## Rebase Strategy

Topological order — every branch is rebased after its parent, but siblings can go in any order:

1. A onto main: `git rebase --empty=drop main A`
2. B onto new A: `git rebase --empty=drop --onto A restack/pre-rebase/A B`
3. C onto new A: `git rebase --empty=drop --onto A restack/pre-rebase/A C`
4. D onto new B: `git rebase --empty=drop --onto B restack/pre-rebase/B D`
5. E onto new D: `git rebase --empty=drop --onto D restack/pre-rebase/D E`
6. F onto new C: `git rebase --empty=drop --onto C restack/pre-rebase/C F`

Steps 2/3 can swap order. Steps 4-6 can run in any order as long as D is before E.

## After

```
main:  ●──────────●
                   └─ A' ──●
                      ├─ B' ──●
                      │  └─ D' ──●
                      │     └─ E' ──●
                      └─ C' ──●
                         └─ F' ──●
```

## Conflict in One Sub-tree

If a conflict occurs during D's rebase, E (D's child) is blocked — but C and F (in a separate sub-tree) can still be restacked. The topological sort guarantees D comes before E, but the C→F sub-tree is independent.

## Mid-Stack Edit at the Fan Point

If A is amended, all descendants need restacking. B and C are immediate children of the edited branch, so both use the merge-base strategy. D, E, and F are deeper descendants, so they use normal backup refs.

If B is amended (but not A), only B's sub-tree (D, E) needs restacking. C and F are unaffected. Use `--branch B` to scope the restack.
