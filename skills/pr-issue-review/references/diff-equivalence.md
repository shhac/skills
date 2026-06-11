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

It is okay to shallow-fetch the minimal base/head refs needed only for fingerprinting after the in-progress reaction is added. Do not do remote context discovery, lens loading, surrounding-source exploration, or full review reasoning before this check. The point is to avoid the slow work when the PR is only a rebase or merge refresh.

## Diff Fingerprint

Prefer Git's stable patch identity when a shallow checkout is available:

```bash
git diff --find-renames --binary origin/base-<number> origin/pr-<number> \
  | git patch-id --stable
```

Use the first field of `git patch-id --stable` as:

```text
patch-id:<hash>
```

`git patch-id --stable` is designed to recognize equivalent patch content across rebases. It ignores commit identity and many diff formatting details, which is exactly what this skip check needs.

If the shallow checkout is not available yet, or `patch-id` fails, use a normalized PR patch hash from `gh pr diff --patch`:

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

Build a startup context fingerprint from lightweight metadata available before full review:

- PR title
- PR body
- base branch name
- head branch name
- issue comments and review summaries visible in startup metadata, excluding reviews/comments from this skill
- closing issue references if already fetched in startup metadata

Normalize by using stable JSON key order when possible. Hash the normalized payload with SHA-256 and store it as:

```text
sha256:<hash>
```

Keep previous reviews from this skill out of the context fingerprint. They are parsed separately for deduplication metadata; including them in the context hash would make this skill's own review change the fingerprint on every later run.

If the context fingerprint differs, continue with review even when the diff fingerprint matches.

## Skip Safety

Skip only when all of these are true:

- Previous review is from this skill.
- Previous hidden metadata has the same selected `profile`.
- Previous hidden metadata has a non-`unknown` `diff` equal to the current diff fingerprint.
- Previous hidden metadata has a non-`unknown` `context` equal to the current startup context fingerprint.
- The caller did not explicitly request a rerun.

If any input is missing, ambiguous, or `unknown`, continue with the review. A duplicate review is less bad than skipping a genuinely changed PR.
