# Conventions

Shared definitions used across all phases of this skill. SKILL.md links here instead of repeating these definitions in each phase, so any update lands in one place.

## Terminology

Use these terms consistently across SKILL.md and all reference files. They are load-bearing — don't introduce synonyms.

- **lead** — the orchestrator running the skill. Spawns subagents, synthesizes, implements, and talks to the user. There is exactly one.
- **subagent** — the umbrella term for any spawned worker. Each plays one of three roles depending on phase:
  - **analyst** — Phase 1 worker running one lens over the scope, emitting findings.
  - **scanner** — Phase 3b worker doing the single broad dead-code sweep.
  - **auditor** — Phase 3c worker verifying one dead-code finding and returning a verdict.
- **finding** — a single issue a subagent reports, in the Finding Record schema. The atomic unit of analysis.
- **recommendation** — a synthesized, user-facing plan item the lead produces from one or more findings. Findings are internal; recommendations are what the user approves.
- **lens** — one analysis perspective from lenses.md. One analyst runs one lens.

## Subagent conventions

When a phase says "spawn a subagent", the lead:

1. Spawns it via whatever mechanism the harness provides (Agent/Task tool in Claude Code, subagent API in the Claude Agent SDK, equivalent constructs elsewhere).
2. Treats it as **fire-and-forget** — the lead reads the report and discards. The lead does not hold an ongoing dialogue with analysts or auditors.
3. Includes these standard fields in the prompt:
   - **Role** — which lens or task this subagent is for.
   - **Scope** — which files, directories, or findings to consider.
   - **Output format** — the exact Finding Record schema below.
   - **Bias** — how to weigh false positives vs false negatives. Phase 1 analysts and Phase 3b broad scanners both bias toward high-confidence claims; missed findings can be caught on a later run, false claims waste downstream cycles.
   - **Dependency notes** — instruction to flag interactions with sibling subagents' findings.
4. Runs subagents in parallel when the work is independent (Phase 1 analysts, Phase 3c auditors).

## Finding Record schema

Every subagent reports findings in this exact format:

```
## {Lens or category} Analysis

### Findings (prioritized)
1. **[impact: high/medium/low]** **{file:line}** — {what's wrong and why it matters}
   - Suggestion: {concrete recommendation}
   - Improves: {testability, readability, reuse, maintainability, safety, simplicity}
   - Risk: {blast radius of the change — what it touches, what could break, and the assumption being made about why the existing code is shaped this way. Omit for small local changes; required for any restructuring that spans files or removes a layer/abstraction.}
   - Verdict: {confirmed-dead | not-dead | uncertain}    # Phase 3c auditors only
   - Dependencies: {other findings this interacts with, if any}

### Summary
{1–2 sentences}
```

The `Verdict` line is included only by Phase 3c deep auditors. Phase 1 analysts and Phase 3b broad scanners omit it. The `Risk` line is included by any finding that proposes a restructuring spanning multiple files or the removal of a layer or abstraction (structural-simplification and abstraction-fit findings most often); small local changes omit it.

## Verification loop

Whenever an instruction says "run verification" or "verify the change":

1. Detect the project's verification tooling — see [verification.md](verification.md) for a per-toolchain catalog and a fallback for unfamiliar toolchains.
2. Run **everything available**: tests, typecheck, lint. There is no time pressure that justifies skipping any.
3. If any check fails:
   - Revert the single change that triggered the failure. Do not amend or fix on top — revert, then re-evaluate.
   - Record: which change was reverted, which check failed, the failure message.
   - Continue to the next pending change unless the calling phase says otherwise.
4. If no verification tooling can be detected at all, do not treat that as "passed". Surface the absence to the user — autonomous structural changes against a project with no verification path require explicit acknowledgement that there is no safety net, and the user may want to halt.
