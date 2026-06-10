# GitHub Review Mechanics

Exact `gh` commands for fetching PR data and submitting the review. All commands accept `--repo <owner>/<repo>` (or the `GH_REPO` env var); `gh api` additionally accepts `--hostname` for GitHub Enterprise hosts.

## Fetch PR Metadata

```bash
gh pr view <number> --repo <owner>/<repo> --json \
  number,title,body,author,isDraft,state,url,\
baseRefName,headRefName,headRefOid,\
changedFiles,additions,deletions,files,\
reviewDecision,latestReviews,reviews,comments,\
closingIssuesReferences,statusCheckRollup
```

Useful fields:

- `headRefOid`: the current head SHA. This is the SHA to compare against prior reviews and to pin the submitted review to.
- `closingIssuesReferences`: GitHub issues linked via closing keywords.
- `reviews` / `comments`: review summaries and issue comments for profile selection and context.
- `statusCheckRollup`: CI check conclusions without running anything.

For CI in a friendlier shape (`bucket` is one of `pass`, `fail`, `pending`, `skipping`, `cancel`):

```bash
gh pr checks <number> --repo <owner>/<repo> --json name,state,bucket,link || true
```

`gh pr checks` exits non-zero when checks are failing or pending, so guard it with `|| true` in scripts.

## Fetch the Diff

```bash
gh pr diff <number> --repo <owner>/<repo>              # unified diff
gh pr diff <number> --repo <owner>/<repo> --name-only  # changed paths
gh pr diff <number> --repo <owner>/<repo> --patch      # patch format
```

Prefer the shallow local checkout from the Setup section for reading surrounding source files. As a fallback without a checkout, read a single file at the PR head:

```bash
gh api "repos/<owner>/<repo>/contents/<path>?ref=<headRefOid>" \
  -H "Accept: application/vnd.github.raw+json"
```

## List Existing Reviews and Inline Comments

Top-level review submissions (one object per submitted review):

```bash
gh api "repos/<owner>/<repo>/pulls/<number>/reviews" --paginate
```

Each review object includes `user.login`, `state`, `body`, `submitted_at`, and `commit_id`. `commit_id` is the head SHA the review was submitted against; this is how prior reviews are matched to a head SHA, since the SHA is not in the review body.

Inline review comments (per-line threads, separate endpoint from reviews):

```bash
gh api "repos/<owner>/<repo>/pulls/<number>/comments" --paginate
```

Non-review issue comments on the PR:

```bash
gh api "repos/<owner>/<repo>/issues/<number>/comments" --paginate
```

## Find Previous Reviews From This Skill

Filter reviews whose body starts with the lizard marker, and extract the marker and covered head SHA:

```bash
gh api "repos/<owner>/<repo>/pulls/<number>/reviews" --paginate \
  --jq '[.[] | select(.body | test("^🦎(🍃|⚖️|🔎|⚔️)"))
         | {marker: (.body | split(" ")[0]), state, commit_id, submitted_at}]'
```

Marker to profile: `🦎🍃` passive, `🦎⚖️` neutral, `🦎🔎` assertive, `🦎⚔️` aggressive. The leading lizard marks the review as coming from this skill.

Skip rule for automation: if this list contains an entry whose `marker` matches the selected profile and whose `commit_id` equals the PR's current `headRefOid`, this skill has already reviewed this head with this profile; skip unless explicitly rerun.

Persona selection uses this same list: the count of entries whose `marker` matches the selected profile is the review count in the persona index formula in SKILL.md's Review Persona section.

## Submit One Review With Inline Comments

Do not use `gh pr review` (top-level body only, no inline comments) or `gh pr comment` (creates an issue comment, not a review). Build a JSON payload and POST it as a single review:

```bash
cat > "$repo_dir/.ai-cache/review-payload.json" <<'EOF'
{
  "commit_id": "<headRefOid>",
  "event": "COMMENT",
  "body": "🦎⚔️ Iris: One loose thread made eye contact. 🤔\n\nWhy:\n- ⚠️ P1: ...",
  "comments": [
    {
      "path": "src/records/filter.ts",
      "line": 42,
      "side": "RIGHT",
      "body": "⚠️ P1 — Archived records are still excluded here.\n\nEvidence: ...\nImpact: ...\nDirection: ...\n\n```suggestion\nreturn records.filter((record) => record.active || record.archived)\n```"
    },
    {
      "path": "src/records/filter.test.ts",
      "start_line": 10,
      "start_side": "RIGHT",
      "line": 14,
      "side": "RIGHT",
      "body": "🔧 P2 — ..."
    }
  ]
}
EOF

gh api --method POST "repos/<owner>/<repo>/pulls/<number>/reviews" \
  --input "$repo_dir/.ai-cache/review-payload.json"
```

Payload rules:

- `event` is `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`. Omitting it creates a pending (unsubmitted) review; always set it.
- `commit_id` should be the `headRefOid` that was actually reviewed, so the review attaches to the right head even if the author pushes mid-review.
- `body` must start with the exact emoji marker as its first characters.
- `comments` may be an empty array or omitted when there are no inline findings.

Inline comment rules:

- `path` is the repo-relative file path as it appears in the diff.
- `line` is the file's line number on the chosen side, not a diff offset. `side` is `RIGHT` for added/modified lines, `LEFT` for removed lines.
- For a multi-line comment, set `start_line`/`start_side` for the first line of the range and `line`/`side` for the last; the whole range must be contiguous changed lines in one hunk.
- Every anchor must be a line that is part of the PR diff. Anchoring to an unchanged or out-of-diff line fails the whole POST with HTTP 422.
- `suggestion` blocks replace exactly the commented line or range, and only work on `RIGHT`-side anchors. Build and verify every suggestion with the protocol below.

## Suggestion Block Protocol

When the author clicks apply, GitHub replaces exactly lines `start_line..line` of the head file with the block content and commits the result. Anchors and block content must therefore be derived from the PR head and verified mechanically, never estimated from the unified diff; eyeballed line arithmetic from `@@` hunk headers is the main source of wrong anchors and broken applied commits.

These commands use the refs fetched in Setup (`origin/pr-<number>` for the head, `origin/base-<number>` for the base).

1. Derive the anchor from the file, not the diff. Find the target line's number in the head file:

   ```bash
   git grep -n 'records.filter((record) => record.active)' origin/pr-<number> -- src/records/filter.ts
   ```

   That line number is `line` with `"side": "RIGHT"`. If the pattern matches more than once, narrow it until the intended occurrence is unambiguous. Then confirm the anchor is a changed line: the `+<start>,<count>` in each hunk header of

   ```bash
   git diff -U0 origin/base-<number> origin/pr-<number> -- src/records/filter.ts
   ```

   lists the new-side changed ranges, and the anchor (and every line of a multi-line range) must fall inside one of them.

2. Build the block by copy-then-edit. Print the exact anchored range from the head file:

   ```bash
   git show origin/pr-<number>:src/records/filter.ts | sed -n '<start_line>,<line>p'
   ```

   Copy those lines into the `suggestion` block verbatim, then apply the minimal edit. Never retype code from memory: indentation (tabs versus spaces), quoting, and trailing characters must survive exactly.

3. Verify the splice before submitting. For every suggestion, check:

   - Every line the fix changes lies inside `start_line..line`.
   - Every line of the anchored range is accounted for in the block, either unchanged or deliberately edited; anything missing gets deleted on apply.
   - Splicing the block into the file in place of the range leaves it well formed (balanced brackets, commas, fences, indentation consistent with neighbors).

4. Downgrade when verification fails. If the fix needs a line outside the anchored range, widen the anchor to the contiguous changed range that covers it; if the needed lines are not contiguous changed lines, do not use a suggestion. Use a plain fenced code block with a prose direction instead. A described fix beats a misapplied one.

5. Guardrails:

   - `start_line` must be strictly less than `line`, both with `"side"`/`"start_side"` of `RIGHT`.
   - Suggestion ranges in the same file must not overlap. For directly adjacent ranges, prefer one merged multi-line suggestion over two back-to-back ones, since authors often batch-apply.
   - If the replacement itself contains triple backticks, fence the suggestion with four backticks.

If the POST fails with a 422, the most likely cause is one bad anchor. Identify the offending comment from the error message, move that finding into the top-level `body` with the same severity, and resubmit, rather than dropping the review or scattering loose comments.
