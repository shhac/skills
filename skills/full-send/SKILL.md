---
name: full-send
description: Complete an explicitly assigned task autonomously through parallel agents, peer-reviewed decisions, and automatic retries of temporary blockers. Use only when the user explicitly invokes Full Send.
disable-model-invocation: true
---

# Full Send

Carry the user's assigned work through implementation, verification, and delivery. Stay in this mode for that task until it is complete or the user stops or redirects it. Keep the main agent focused on gathering context, making decisions, and orchestrating workers; delegate substantive investigation, implementation, and verification throughout.

## Select the harness guide

Identify the current harness from session instructions and available tools, rather than guessing from the model family. Read only the matching guide, resolving paths from this skill's directory:

- Codex: [references/codex.md](references/codex.md).
- Claude Code: [references/claude-code.md](references/claude-code.md).
- Other or unknown harness: use the shared workflow and the concurrency limit explicitly supplied by the session. Report unavailable delegation or review capabilities and continue with the tools you have.

## Start and decide

Establish the requested outcome, constraints, existing work, and what will demonstrate completion. If a needed decision is unclear at the outset and you cannot confidently recommend an option, **ask the user immediately**, before investing in dependent work. Continue independent work while waiting; do not treat silence as an answer.

For decisions within the user's authorized scope:

- With a confident recommendation, choose it and proceed.
- With less certainty, consult the plan auditor described in the harness guide, or another independent agent if that auditor is unavailable. Give the agent the options, evidence, and trade-offs; agree on a choice and proceed.
- If no consensus emerges, investigate the smallest missing fact that could change the decision. If uncertainty remains, make the best supported choice and proceed. Ask the user only when the missing answer is essential to their intended outcome or authorization.

Keep a brief decision record: the choice, why it was made, who reviewed it, and any uncertainty that matters. Include these decisions in the final summary.

If a goal facility is available and no goal is already mid-flight, you may create a goal for the assigned outcome. Preserve an existing goal; do not replace it, invent a token budget, or mark it complete while required work remains.

## Plan and delegate

Break the outcome into bounded tasks with explicit dependencies. When making a plan, obtain the cross-agent read-only audit specified in the harness guide before committing to dependent implementation. Give the auditor the user's request, relevant repository instructions, constraints, current evidence, and proposed plan. Ask for omissions, invalid assumptions, sequencing problems, and a recommended resolution. Evaluate its findings and revise the plan; retain the auditor's context for later uncertain decisions when possible.

Dispatch independent tasks in parallel, capped at **10 concurrent subagents unless the user specifies otherwise**, and always respect lower session limits. Apply this cap across the whole delegation tree, including nested agents, reviewers, and team teammates; the coordinator does not count. Keep useful workers active as dependencies clear; reuse agents with relevant context. Do not manufacture tasks to fill slots when work is inherently sequential.

Each delegation must include:

- The requested result and enough context to work independently.
- Owned files or work areas, dependencies, and permitted actions.
- Completion evidence and the format of the returned findings.
- An instruction to report blockers and decisions promptly, and to leave unrelated user changes intact.

Give concurrent editors disjoint ownership or isolated worktrees. Route shared-file changes through one owner. Delegate integration and verification too when practical; do only work yourself that requires the main agent's context or tools, resolves coordination, or is cheaper than handing it off. Check worker outputs against the request and evidence before accepting them.

## Wait out temporary blockers

For an interruption expected to clear without a user decision, arrange a short recheck, normally in 2–5 minutes or at the service's stated retry time. Continue unblocked work meanwhile. On recheck, inspect the actual blocker and resume automatically when it clears.

Use an available timer, wakeup, or continuation facility that can resume this task. If none exists, keep the session alive with interruptible waits, using short polling intervals and progress updates. A detached shell sleep does not itself resume an agent; never claim a future retry is scheduled unless a real continuation was registered.

Recheck observation or status before repeating a mutation whose outcome is unknown. Retry transient failures; investigate repeated identical failures instead of indefinitely polling them. Stop waiting when the user cancels, an explicit budget expires, or evidence shows that progress requires a user answer or an external change with no useful retry path. Report the blocker and what would resume the work.

## Finish

Continue until the requested outcome and its appropriate checks are complete. Full Send grants autonomy within the assigned task; it does not expand the task, bypass permission controls, or supply authorization that the user has not given. Complete independently authorized work before surfacing any required approval.

End with a concise, self-contained summary of:

- What was completed, with links to the results.
- What verification passed, failed, or could not run.
- Decisions made autonomously, their reasons, and material auditor findings.
- Anything still blocked or pending, including an actual scheduled recheck if one exists.
