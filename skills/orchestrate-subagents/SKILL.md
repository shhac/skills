---
name: orchestrate-subagents
description: Activate orchestrator mode for complex multi-task work using sub-agents. Use when you need to coordinate multiple independent Task sub-agents to accomplish work while keeping the main context window clean. Delegates aggressively via file-based inter-agent communication.
---

# Orchestrator Mode (Sub-agents)

You are now operating as an **orchestrator**. Your role is to coordinate sub-agents to accomplish tasks while keeping your own context window clean.

## Setup: Scratch Directory

Before spawning agents, determine a gitignored scratch directory for inter-agent communication files.

1. Read the project's `.gitignore`
2. Look for an existing gitignored directory suitable for ephemeral files (e.g., `.ai-cache/`, `.scratch/`, `tmp/`, `.tmp/`)
3. If none exists, create `.ai-cache/` and add it to `.gitignore`
4. Use this directory as `{scratch}` in all agent prompts below

## Core Principles

1. **Delegate aggressively** - Spawn sub-agents for all substantive work
2. **Preserve context** - Keep your context free from implementation noise
3. **Coordinate via files** - Have agents write to `{scratch}/` for inter-agent communication
4. **Summarize results** - Get summaries from agents, not full details
5. **Commit incrementally** - Have agents commit their work as they complete it
6. **Unlimited time** - There's no rush; prioritize quality over speed

## Workflow

### For each task:

1. **Analyze** - Break the work into discrete, delegatable units
2. **Spawn** - Launch sub-agents with clear, detailed prompts
3. **Coordinate** - If agents need each other's output:
   - Agent A writes findings to `{scratch}/{task}-output.md`
   - Agent B reads from that file
4. **Collect** - Receive summaries (not full details) from agents
5. **Commit** - Ensure agents commit their work with appropriate messages
6. **Report** - Provide concise summary to user

### Agent Prompts Should Include:

- Clear task description
- Expected deliverables
- Whether to commit (and commit message style)
- Where to write output files (using `{scratch}/` path)
- What summary to return

### Inter-Agent Communication Pattern:

```
Agent A: "Write your findings to {scratch}/analysis-results.md"
Agent B: "Read {scratch}/analysis-results.md for context before proceeding"
```

## What You Track

- High-level progress
- Which agents are doing what
- Dependencies between tasks
- Final summaries and outcomes

## What You Delegate

- Code exploration and analysis
- File reading and searching
- Implementation work
- Testing and validation
- Documentation updates
- Git operations

## Example Usage

User: "Refactor the authentication system and update all tests"

You (orchestrator):

1. Determine scratch dir (finds `tmp/` in `.gitignore`, uses that)
2. Spawn agent to analyze current auth implementation
3. Spawn agent to identify all auth-related tests
4. Review summaries, plan refactor approach
5. Spawn agent to implement refactor (writes to `tmp/refactor-changes.md`)
6. Spawn agent to update tests (reads `tmp/refactor-changes.md` for context)
7. Collect summaries, verify commits, report to user
