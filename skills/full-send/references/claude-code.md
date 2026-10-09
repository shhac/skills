# Full Send in Claude Code

## Concurrency

**Aim for 10 concurrent subagents when doing this work, unless the user specifies otherwise.** The effective target is the smaller of that cap (or the user's replacement cap) and the session's enforced capacity. Keep useful independent tasks filling available slots, subject to dependencies; do not create filler tasks.

Claude Code defaults to 20 running Agent-tool subagents per session. `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` can set any positive whole number, so there is no universal hard maximum. This concurrency setting is separate from nesting depth and total agents spawned over the session. Account for existing running subagents and forks before spawning more. When the cap is reached, wait for capacity rather than repeatedly retrying the spawn or using resume to evade it. Do not change harness settings just to increase concurrency.

Use `Agent` (or `Task` on older installations) for bounded work. Prefer `TeamCreate`, `TaskCreate`, and `SendMessage` when a long-lived team needs retained context and coordination and those tools are available. Team teammates have separate harness limits, but still count toward Full Send's user-selected cap (10 by default). Coordinate task ownership and completion from the main conversation.

Sources, checked 2026-10-09: [Concurrent subagent limit](https://code.claude.com/docs/en/sub-agents#concurrent-subagent-limit), [agent teams](https://code.claude.com/docs/en/agent-teams).

## Read-only plan audit: Codex, Sol High

When making a plan, if Codex is available through an authenticated CLI or an equivalent delegation tool, have **GPT-6 Sol at high reasoning effort** audit it read-only. Use `gpt-6-sol` with `high`; do not silently substitute GPT-6.1 Sol or another family member. Ask for findings and recommended decisions, not implementation. If unavailable, use an independent native agent and record the fallback; do not stop otherwise unblocked work to install or configure another harness.

For the CLI, put the self-contained audit request, relevant instructions, evidence, and plan in a file in a discovered gitignored scratch directory (fall back to `.ai-cache/`) or an available temporary directory. Set `audit_input_file` to that file and `audit_output_file` to a destination for the findings. Run from the task's workspace:

```sh
codex exec --model gpt-6-sol \
  -c 'model_reasoning_effort="high"' \
  --sandbox read-only --json \
  -o "$audit_output_file" \
  - < "$audit_input_file"
```

Explicitly instruct the reviewer to return findings only, with no implementation or external mutations. The filesystem sandbox does not restrict external MCP mutations: ensure the audit's exposed connectors are read-only or disabled before launching, using the installed harness's supported configuration. Check installed CLI and model support. If the requested reviewer cannot run read-only, use the native read-only fallback and report why.

Read the findings file and verify material claims before revising the plan. Preserve the `thread_id` from the JSON events if useful for later decision consultations; maintain the read-only sandbox and tool restrictions on any resumed audit.

Sources: [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [model catalog](https://learn.chatgpt.com/docs/models).
