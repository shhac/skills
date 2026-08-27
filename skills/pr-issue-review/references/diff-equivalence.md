# Diff Equivalence

Use this reference to decide whether a PR still represents work this skill has already reviewed, across three independent channels: the code, the stated intent, and the human conversation.

## Hidden Review Metadata

Every top-level review body from this skill must end with one hidden metadata comment:

```html
<!-- pr-issue-review:v2 profile=<profile> head=<headRefOid> diff=<diff-fingerprint> intent=<intent-fingerprint> convo=<convo-fingerprint> -->
```

Rules:

- Keep it as the final line of the top-level review body.
- Use the selected profile name, not the emoji marker, in `profile`.
- Use the exact `headRefOid` that the review was pinned to in `head`.
- Use `<channel>=unknown` for any fingerprint whose inputs could not be fetched or were truncated. `unknown` never matches, so it always falls open into a review.
- Do not put findings, severity, or private context inside the hidden comment.

A `v1` stamp (`diff=` and `context=`, no `intent=`/`convo=`) is read as `intent=unknown convo=unknown`. It can therefore never authorize a skip. This costs one extra review per open PR at rollout and is self-healing; do not add translation logic between the formats.

## Why Three Fingerprints

A single fingerprint cannot express two things this skill needs.

**Per-channel noise policy.** Bot comments that rewrite themselves in place (deploy tables, coverage bots, CI summaries) move a whole-conversation hash on every redeploy and buy a full re-review that has nothing to review. A body edit does not. Separate projections let each channel filter its own noise.

**Per-channel consequence.** New code needs a full pass. A changed claim needs a full pass against the new criteria. An author replying to a finding needs neither: it needs that finding re-judged. One hash cannot say which happened.

The guiding principle for what belongs in a fingerprint: **a fingerprint is a wake-up trigger, not a context inventory.** Bot comments are still read during a review. They just do not cause one.

| channel | source | moves when |
| --- | --- | --- |
| `diff` | the PR patch | code changed |
| `intent` | title, body, base ref, closing issues | the stated claim changed |
| `convo` | human comments, review bodies, thread replies, thread resolution | a person said something |

## Startup Check

Run this before lens loading, remote context discovery, surrounding-source exploration, or any review reasoning. All three fingerprints are computed from `gh` metadata and need no checkout, so the whole check runs before any fetch.

1. Fetch previous reviews from this skill on this PR and parse their hidden metadata.
2. Add the in-progress reaction optimistically.
3. Compute all three current fingerprints.
4. Compare against the most recent previous review from this skill **at the same profile**.
5. Decide with the table below.

There is no separate head-SHA short circuit. An unchanged head SHA is simply the case where `diff` matches; whether that skips depends on the other two channels. Skipping on the SHA alone is what makes a reply to a finding invisible.

| `diff` | `intent` | `convo` | action |
| --- | --- | --- | --- |
| same | same | same | **skip.** Remove the reaction and stop without posting. |
| changed | — | — | **full review.** New code. |
| — | changed | — | **full review.** The claim moved, so every prior finding needs re-judging against the new criteria. |
| same | same | changed | **targeted re-review.** See SKILL.md, Targeted Re-Review. |
| any `unknown` | | | **full review.** Never skip on an unmatched channel. |

## Diff Fingerprint

Fingerprint the PR's own delta, not a tree-to-tree diff of the two fetched tips. The shallow checkout fetches base and head as independent `--depth=1` tips with no shared history, so `git diff origin/base-<number> origin/pr-<number>` is a full tree diff: when the base branch advances past the PR's fork point it absorbs unrelated base changes, and the fingerprint then changes on every base movement even when the PR's effective diff is identical. That defeats the rebase/merge-refresh dedup this channel exists for.

`gh pr diff` returns GitHub's merge-base ("Files changed") delta for the PR, which already excludes unrelated base advancement. Prefer it as the primary source, and feed it through `git patch-id --stable` for rename- and format-insensitive identity:

```bash
gh pr diff <number> --repo <owner>/<repo> --patch \
  | git patch-id --stable
```

`git patch-id` reads a diff on stdin and needs no repo or checkout, so this works on the no-checkout fallback path too. Use the first field as:

```text
patch-id:<hash>
```

`git patch-id --stable` is designed to recognize equivalent patch content across rebases. It ignores commit identity and many diff formatting details, which is exactly what this check needs.

If `patch-id` is unavailable or fails, fall back to a normalized PR patch hash from the same delta:

```bash
gh pr diff <number> --repo <owner>/<repo> --patch \
  | sed -E '/^(From |index |diff --git |similarity index |rename from |rename to )/d' \
  | shasum -a 256
```

Use the first field as `sha256:<hash>`. Patch hashes are a fallback: usually good enough, but more sensitive than `patch-id` to rename or binary-file representation changes.

## Intent Fingerprint

What the PR claims to do. A quiet channel with no bot traffic, so it needs no filtering.

```bash
gh pr view <number> --repo <owner>/<repo> \
  --json title,body,baseRefName,closingIssuesReferences \
| jq -Sc '{
    title, body,
    base: .baseRefName,
    issues: [.closingIssuesReferences[]? | .number]
  }' \
| shasum -a 256
```

Use the first field as `sha256:<hash>`. If the `gh` call fails or emits no JSON, use `intent=unknown`.

The head branch name is deliberately excluded: renaming a branch does not change what the PR claims to do.

## Conversation Fingerprint

What people have said. This is the noisy channel and the one that carries replies to findings.

`reviewThreads` is not a `gh pr view` field, and resolution state exists only in GraphQL, so this channel uses one GraphQL query. It also returns an author typename, which is the only reliable bot/human split available: `gh pr view --json comments` reports `is_bot` as null for bot and human alike.

```bash
gh api graphql -f owner=<owner> -f repo=<repo> -F number=<number> -f query='
query($owner:String!,$repo:String!,$number:Int!){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$number){
      comments(first:100){
        pageInfo{hasNextPage}
        nodes{ author{login __typename} body }
      }
      reviews(first:100){
        pageInfo{hasNextPage}
        nodes{ author{login __typename} state body }
      }
      reviewThreads(first:100){
        pageInfo{hasNextPage}
        nodes{
          isResolved
          comments(first:100){
            pageInfo{hasNextPage}
            nodes{ author{login __typename} body }
          }
        }
      }
    }
  }
}'
```

Project it with exactly this filter, then hash the result:

```jq
def mine_top: test("^🦎(🍃|⚖️|🔎|⚔️)");
def mine_inline: test("pr-issue-review:inline");
def human: .author.__typename == "User";
.data.repository.pullRequest
| if (.comments.pageInfo.hasNextPage
      or .reviews.pageInfo.hasNextPage
      or .reviewThreads.pageInfo.hasNextPage
      or ([.reviewThreads.nodes[].comments.pageInfo.hasNextPage] | any))
  then "OVERFLOW"
  else {
    comments: [.comments.nodes[]
      | select(human) | select(.body | mine_top | not)
      | {a: .author.login, b: .body}],
    reviews: [.reviews.nodes[]
      | select(human) | select(.body | mine_top | not)
      | {a: .author.login, s: .state, b: .body}],
    threads: [.reviewThreads.nodes[]
      | {r: .isResolved,
         c: [.comments.nodes[]
             | select(human) | select(.body | mine_inline | not)
             | {a: .author.login, b: .body}]}
      | select((.c | length) > 0 or .r)]
  }
  end
```

Pipe through `jq -Sc -f` and then `shasum -a 256`; use the first field as `sha256:<hash>`. If the projection emits `"OVERFLOW"`, or the `gh` call fails, use `convo=unknown`.

### Exclusion is per comment, not per thread

Dropping whole threads that this skill started destroys the exact signal this channel exists for. The canonical shape of a useful trigger is this skill's finding at position 0 and the author's rebuttal at position 1; filtering by thread origin discards it.

But filtering per comment alone reintroduces a loop: posting a new inline comment adds a thread to the array, which moves the hash, which triggers a review, which posts a comment. Hence the `select((.c | length) > 0 or .r)` guard. A thread is included when it has at least one surviving human comment **or** it is resolved.

| thread state | included | why |
| --- | --- | --- |
| ours, no reply, unresolved | no | no self-trigger when this skill posts |
| ours + a human reply | yes, reply only | the signal this channel exists for |
| ours, resolved with no reply | yes, flag only, no bodies | "I have handled this" |
| a bot's, no human reply | no | bot traffic is context, not a trigger |
| a bot's + a human reply | yes, reply only | |

Two constraints hold this together, and breaking either restores the loop:

- Every inline comment from this skill ends with `<!-- pr-issue-review:inline -->` (SKILL.md, Inline Comment Marker). The account running this skill reports as a `User`, so the typename filter does not exclude it.
- This skill never resolves a review thread. Resolution is an input here, so resolving its own thread would self-trigger.

Inline comments posted before the marker existed are indistinguishable from a human's and will keep this channel moving once each. That resolves itself after the next review on each affected PR.

### Design constraints

Preserve these if the recipes change:

- No timestamps, IDs, or commit SHAs anywhere. Rebases, merge refreshes, and time passing must not move a fingerprint; editing a body or posting a reply must.
- This skill's own output is excluded by marker, never by author login, so the fingerprints are stable no matter which account runs the skill.
- Arrays stay in API (chronological) order. `-S` sorts object keys only. Do not sort or filter arrays beyond the documented exclusions.
- Truncation must never be silent. A frozen hash loses a trigger, which is the failure this file exists to prevent, so any `hasNextPage` becomes `unknown` and buys a review rather than losing one.

## Skip Safety

Skip only when all of these are true:

- The previous review is from this skill.
- Its hidden metadata has the same selected `profile`.
- All three of `diff`, `intent`, and `convo` are non-`unknown` and equal to the current fingerprints.
- The caller did not explicitly request a rerun.

If any input is missing, ambiguous, or `unknown`, review. A duplicate review is less bad than skipping a genuinely changed PR.

This check is best-effort, not a barrier. It reads previously posted reviews and then acts, so under parallel execution two concurrent runs on the same PR/profile can both read "not yet reviewed" and both post. That is accepted: the skill fails open by design (see SKILL.md Automation Behavior). Do not add locking to close this window, because a lock that is never released would strand a PR unreviewed, which is the worse failure.
