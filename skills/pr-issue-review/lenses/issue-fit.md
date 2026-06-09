# Issue Fit Lens

Determine whether the PR solves the stated issue.

Check:

- What problem the PR claims to solve from the title, body, branch name, comments, linked issues, and cached context
- Whether the diff plausibly implements the required behavior
- Whether acceptance criteria are missing, contradicted, or only partially handled
- Whether tests or changed docs align with the stated issue
- Whether this PR appears to be one part of a stack or multi-PR solution

If no stated issue or acceptance criteria can be identified after checking PR metadata and discovered references, do not invent one. Use `COMMENT` and state that issue fit could not be verified.

For stacked changes, judge whether this PR is a coherent step and state what appears to be deferred to companion PRs.
