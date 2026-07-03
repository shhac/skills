# Diff Equivalence

Use this reference to avoid repeating a review after a rebase, merge from base, or force-push that changes the PR head SHA without changing the effective PR diff.

## Hidden Review Metadata

Every review body from this skill must end with one hidden metadata comment:

```html
<!-- pr-issue-review:v1 profile=<profile> head=<headRefOid> diff=<diff-fingerprint> context=<context-fingerprint> -->
```

Rules:

- Keep it as the final line of the top-level review body.
- Use the selected profile name, not the emoji marker, in `profile`.
- Use the exact `headRefOid` that the review was pinned to in `head`.
- Use `diff=unknown` only if all fingerprint methods fail; do not skip same-diff reviews on `unknown`.
- Use `context=unknown` only if startup context cannot be fetched; do not skip same-diff reviews on `unknown`.
- Do not put findings, severity, or private context inside the hidden comment.

## Startup Same-Diff Check

After exact head-SHA deduplication says this head has not been reviewed with the selected profile:

1. Add the in-progress reaction optimistically.
2. Compute the current diff fingerprint and startup context fingerprint.
3. Compare them with previous hidden metadata from reviews by this skill on the same PR and selected profile.
4. If a previous review has the same `diff` and the same `context`, remove the reaction and stop without posting a review.
5. Otherwise continue with full context gathering and review as normal.

The diff fingerprint below uses `gh pr diff` and needs no checkout, so this check can run before any shallow fetch. Do not do remote context discovery, lens loading, surrounding-source exploration, or full review reasoning before this check. The point is to avoid the slow work when the PR is only a rebase or merge refresh.

## Diff Fingerprint

Fingerprint the PR's own delta, not a tree-to-tree diff of the two fetched tips. The shallow checkout fetches base and head as independent `--depth=1` tips with no shared history, so `git diff origin/base-<number> origin/pr-<number>` is a full tree diff: when the base branch advances past the PR's fork point it absorbs unrelated base changes, and the fingerprint then changes on every base movement even when the PR's effective diff is identical. That defeats the rebase/merge-refresh dedup this file exists for.

`gh pr diff` returns GitHub's merge-base ("Files changed") delta for the PR, which already excludes unrelated base advancement. Prefer it as the primary source, and feed it through `git patch-id --stable` for rename- and format-insensitive identity:

```bash
gh pr diff <number> --repo <owner>/<repo> --patch \
  | git patch-id --stable
```

`git patch-id` reads a diff on stdin and needs no repo or checkout, so this works on the no-checkout fallback path too. Use the first field as:

```text
patch-id:<hash>
```

`git patch-id --stable` is designed to recognize equivalent patch content across rebases. It ignores commit identity and many diff formatting details, which is exactly what this skip check needs.

Because the primary source is `gh pr diff`, the diff fingerprint does not require the base/head shallow fetch; it can be computed before any checkout.

If `patch-id` is unavailable or fails, fall back to a normalized PR patch hash from the same delta:

```bash
gh pr diff <number> --repo <owner>/<repo> --patch \
  | sed -E '/^(From |index |diff --git |similarity index |rename from |rename to )/d' \
  | shasum -a 256
```

Use the first field as:

```text
sha256:<hash>
```

Patch hashes are a fallback. They are usually good enough for same-diff detection, but they can be more sensitive than `patch-id` to rename or binary-file representation changes.

## Startup Context Fingerprint

The diff alone is not enough. A PR can keep the same patch while the stated issue, acceptance criteria, or review conversation changes.

The fingerprint must be byte-identical across runs that see the same context, so never assemble or serialize the payload by hand: model-side serialization varies run to run and a varying hash silently defeats the dedup. Compute it with exactly this command:

```bash
gh pr view <number> --repo <owner>/<repo> \
  --json title,body,baseRefName,headRefName,closingIssuesReferences,comments,reviews \
| jq -Sc '{
    title, body,
    base: .baseRefName, head: .headRefName,
    issues: [.closingIssuesReferences[]? | .number],
    comments: [.comments[]?
      | select(.body | test("^🦎(🍃|⚖️|🔎|⚔️)") | not)
      | {a: .author.login, b: .body}],
    reviews: [.reviews[]?
      | select(.body | test("^🦎(🍃|⚖️|🔎|⚔️)") | not)
      | {a: .author.login, s: .state, b: .body}]
  }' \
| shasum -a 256
```

Use the first field as:

```text
sha256:<hash>
```

Guard the fetch: if the `gh pr view` call fails, the pipeline still "succeeds" by hashing empty input to `e3b0c442...`, and because that hash is identical across all failures it could wrongly match a prior failed run and skip a review that was needed. Confirm the `gh` call exited zero and produced JSON before hashing; on failure use `context=unknown`, which never matches.

The recipe encodes deliberate design constraints; preserve them if it ever changes:

- No timestamps, IDs, or commit SHAs. Rebases, merge refreshes, and time passing must not move the fingerprint; editing the title, body, or a comment must.
- Reviews and comments from this skill are excluded by their lizard marker, not by author login, so the fingerprint is stable no matter which account runs the skill and this skill's own reviews never change it on later runs. This skill's reviews are parsed separately for deduplication metadata.
- Arrays stay in API (chronological) order; `-S` sorts object keys only. Do not sort or filter the arrays beyond the marker exclusion.

If the context fingerprint differs, continue with review even when the diff fingerprint matches.

## Skip Safety

Skip only when all of these are true:

- Previous review is from this skill.
- Previous hidden metadata has the same selected `profile`.
- Previous hidden metadata has a non-`unknown` `diff` equal to the current diff fingerprint.
- Previous hidden metadata has a non-`unknown` `context` equal to the current startup context fingerprint.
- The caller did not explicitly request a rerun.

If any input is missing, ambiguous, or `unknown`, continue with the review. A duplicate review is less bad than skipping a genuinely changed PR.

This check is best-effort, not a barrier. It reads previously posted reviews and then acts, so under parallel execution two concurrent runs on the same PR/head/profile can both read "not yet reviewed" and both post. That is accepted: the skill fails open by design (see SKILL.md Automation Behavior). Do not add locking to close this window, because a lock that is never released would strand a PR unreviewed, which is the worse failure.
