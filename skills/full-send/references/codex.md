# Full Send in Codex

## Concurrency

**Aim for 10 concurrent subagents when doing this work, unless the user specifies otherwise.** The effective target is the smaller of that cap (or the user's replacement cap) and the active session's advertised or configured subagent capacity. If the harness reports total slots including the coordinator, subtract one: four total slots means aim for **3 concurrent subagents**. Count descendants and other running agents against shared capacity. Keep slots occupied with useful independent work, subject to dependencies.

There is no documented universal numeric hard maximum. In local Codex, `agents.max_concurrent_threads_per_session` limits open spawned threads, excluding the coordinator; `agents.max_threads` is its legacy alias. The backend chooses the default when unset. API defaults also differ: Responses multi-agent defaults to 3 concurrent subagents, while Agents API defaults to 6. These defaults do not override the active session's limits. Do not change harness configuration merely to increase concurrency.

Use the exposed spawn, message, follow-up, wait, and lifecycle tools. Reuse agents with relevant context and release completed threads when supported; an idle open thread may still occupy local Codex capacity. Keep orchestration and user communication in the main agent.

Sources, checked 2026-10-09: [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference), [Responses multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent), [Agents API multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent).

## Read-only plan audit: Claude Code, Opus Medium

When making a plan, if Claude Code is available through an authenticated CLI or an equivalent delegation tool, have **Opus at medium effort** audit the plan read-only. Ask for findings and recommended decisions, not implementation. If unavailable, use an independent native agent and record the fallback; do not stop otherwise unblocked work to install or configure another harness.

For the CLI, put the self-contained audit request, relevant instructions, evidence, and plan in a file in a discovered gitignored scratch directory (fall back to `.ai-cache/`) or an available temporary directory. Set `audit_input_file` to that file. Run from the task's workspace:

```sh
CLAUDE_CODE_EFFORT_LEVEL=medium claude -p \
  --model opus --effort medium \
  --permission-mode plan \
  --tools="Read,Glob,Grep" \
  --strict-mcp-config --mcp-config='{"mcpServers":{}}' \
  --safe-mode --output-format json \
  < "$audit_input_file"
```

The explicit environment value prevents an inherited effort setting from overriding medium. Restricting built-in tools and excluding MCP servers keeps the reviewer from editing or calling external mutation tools; safe mode disables customizations, so include relevant repository guidance in the input. Read the returned findings, verify material claims, and incorporate justified changes. Preserve the returned session ID if useful for later decision consultations; maintain these read-only restrictions on follow-ups. Check installed CLI support before invoking. If Opus or medium effort is unsupported, report the fallback rather than silently changing the requested reviewer.

Sources: [Claude CLI reference](https://code.claude.com/docs/en/cli-reference), [effort configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level).
