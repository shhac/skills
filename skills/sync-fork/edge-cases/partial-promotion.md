# Edge Case: Partial Promotion

## Trigger

Phase 1 step 3 (`classify`) shows `fork-only-partial` entries — SOME but not all of a branch's commits have patch equivalents in upstream.

## What's happening

Upstream took part of a branch's work — maybe cherry-picked specific commits, or squash-merged the branch alongside other changes into a combined commit where only some patches match.

```
fork/main:  ●────●────●
            └─ A ┘
               (commits: a1, a2, a3)

upstream/main:  ●────●────●
                (a1 and a2 are in here, a3 is not)
```

## What to do

1. **Show the user which commits are matched and which aren't:**
   ```bash
   # Commits WITHOUT equivalents in upstream (still unique to fork)
   git log --oneline --cherry-pick --right-only <upstream>/<default-branch>...<fork>/<branch>

   # Commits WITH equivalents (already in upstream)
   git log --oneline --cherry-mark --right-only <upstream>/<default-branch>...<fork>/<branch>
   # Lines prefixed with "=" have equivalents, "+" do not
   ```

2. **The branch is NOT fully promoted** — it still has unique work. Treat it as "has commits not in upstream" for the rest of the sync.

3. **During Phase 3 rebase,** the matched commits will become empty and be dropped by `--empty=drop`. Only the unmatched commits survive. This is the correct behavior — no special handling needed beyond informing the user.

4. **If ALL remaining commits become empty after rebase** (the partial detection was incomplete), Phase 3 step 3 will catch this and suggest deleting the branch.
