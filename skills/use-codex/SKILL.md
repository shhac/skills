---
name: use-codex
description: 'Delegate a coding task to the OpenAI Codex CLI: codebase Q&A, well-specified implementation, mechanical edits at scale, adversarial second opinions, or bugs stuck after 2+ attempts. Spends ChatGPT quota instead of Claude tokens. Use on "use codex", "ask codex", "codex exec", "second opinion", or to offload token-heavy scoped work.'
---

# Use Codex

**If you are already Codex, proceed with your normal workflow.** Use this skill from another agent to delegate scoped work to the non-interactive Codex CLI (`codex exec`) using ChatGPT quota or OpenAI API billing.

## Should this go to Codex?

Delegate when the task is **scoped and the answer/diff is all that matters**:

- Repo exploration & Q&A ("where is X handled?", "trace this flow")
- Implementation where the architecture is already decided and unknowns reduced
- Mechanical edits at scale (renames, migration sweeps)
- Second-opinion / adversarial review of a plan or diff
- A bug stuck after 2+ failed attempts (different model, different angle)

Keep the user conversation, unresolved design decisions, and questions you can answer from existing context in the current session. For a handoff that needs more context, see [task fit](references/task-fit.md).

## Run Codex

Default to **GPT-6.1 Sol with high reasoning**. Supply the repo path as `repo_dir` and a self-contained task as `prompt`. Include the relevant files, expected output, and how to verify it.

```bash
run_dir=$(mktemp -d) &&
  codex exec -m gpt-6.1-sol -c 'model_reasoning_effort="high"' \
    --sandbox read-only -C "$repo_dir" \
    -o "$run_dir/final.txt" "$prompt" \
    </dev/null > /dev/null 2>"$run_dir/progress.log" &&
  cat "$run_dir/final.txt"
```

- Use `read-only` for questions and reviews. Select `workspace-write` when delegated edits are in scope and account for any existing changes in the working tree.
- For a long run, use the shell tool's background execution when available. Check the exit status before reading the result. Inspect `progress.log` if the run stalls or fails.
- Add `--skip-git-repo-check` when intentionally running outside a Git repository.

See the [invocation reference](references/invocation.md) for JSONL events, session resume and fork, structured output, and troubleshooting.

## After it returns

Verify claims against the code. Review the diff and run relevant checks for any edits. Tell the user which work Codex contributed.
