# skills

A collection of reusable Claude Code skills, distributed via [skills.sh](https://skills.sh).

## Installation

```bash
npx skills add shhac/skills
```

## Skills

### team-solve

Investigate and solve problems using a team of specialist agents. Decomposes a problem into parallel investigation tracks, synthesizes findings, then implements solutions serially (or in parallel when safe).

**Workflow:**
1. **Investigate** — parallel teammates each own a problem/theme
2. **Discuss** — review findings, revise scope if needed
3. **Implement** — investigators solve their own problems
4. **Validate** — fresh teammate verifies everything

### orchestrate-subagents

Activate orchestrator mode for complex multi-task work using sub-agents. Delegates aggressively, coordinates via `.ai-cache/` files, and keeps the main context window clean.

**Workflow:**
1. **Analyze** — break work into delegatable units
2. **Spawn** — launch sub-agents with clear prompts
3. **Coordinate** — inter-agent communication via gitignored scratch directory
4. **Collect** — receive summaries, verify commits, report to user

### multi-review

Review code changes from multiple specialist perspectives in parallel. Spawns five reviewer agents — security, performance, correctness, test coverage, and edge/ripple — then synthesizes into a unified review.

**Reviewers:**
- **Security** — injection, auth, data exposure, OWASP top 10
- **Performance** — N+1 queries, allocations, missing indexes, hot paths
- **Correctness** — logic errors, race conditions, unhandled states
- **Test Coverage** — untested paths, missing edge cases, test quality
- **Edge & Ripple** — "what happens to..." (docs, adjacent features, API consumers) and "what happens if..." (bad data, interrupted flows, concurrent access)

### competing-hypotheses

Debug problems by investigating multiple hypotheses in parallel. Spawns investigator agents each pursuing a different theory, gathering evidence and counter-evidence, then compares findings to identify the most likely root cause.

**Workflow:**
1. **Hypothesize** — generate 2-5 plausible theories
2. **Investigate** — parallel agents race to find evidence
3. **Compare** — rank hypotheses by evidence strength
4. **Fix** — winning investigator implements the fix (optional)

## License

[MIT](LICENSE)
