# Issue Fit Lens

Determine whether the PR has a discernible reason to exist and solves the stated issue.

Check:

- Why does this PR exist? Identify the problem, request, incident, cleanup goal, or follow-up that motivates the change.
- What problem the PR claims to solve from the title, body, branch name, comments, linked issues, and cached context
- Whether the diff plausibly implements the required behavior
- Whether acceptance criteria are missing, contradicted, or only partially handled
- Whether tests or changed docs align with the stated issue
- Whether this PR appears to be one part of a stack or multi-PR solution

For non-trivial PRs, roughly more than 5 changed lines, an empty or placeholder PR body is a signal to look harder for intent. If the title, branch name, linked issues, comments, or cached context still do not make the reason clear, treat this as a `⚠️ P1` issue-fit finding. Use `COMMENT`, not `APPROVE`, and recommend adding a short PR body with the intended behavior change, scope, and any follow-up or stack context.

If no stated issue, acceptance criteria, or discernible reason for the PR can be identified after checking PR metadata and discovered references, do not invent one. Use `COMMENT`, not `APPROVE`, and state that issue fit could not be verified because the review could not determine why the PR exists.

If the reason for the PR is clear but the diff does not appear to solve it, use `COMMENT`, not `APPROVE`, and explain the mismatch.

For stacked changes, judge whether this PR is a coherent step and state what appears to be deferred to companion PRs.
