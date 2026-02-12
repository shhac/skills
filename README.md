# skills

A collection of reusable Claude Code skills, distributed via [skills.sh](https://skills.sh).

## Installation

```bash
npx skills add shhac/skills
```

## Skills

### team-solve

Investigate and solve problems using a team of specialist agents. Decomposes a problem into parallel investigation tracks, synthesizes findings, then implements solutions serially (or in parallel when safe).

**Workflow:** Investigate → Discuss → Implement → Validate

### orchestrate-subagents

Activate orchestrator mode for complex multi-task work using sub-agents. Delegates aggressively, coordinates via gitignored scratch files, and keeps the main context window clean.

**Workflow:** Analyze → Spawn → Coordinate → Collect

### multi-review

Review code changes from multiple specialist perspectives in parallel. Spawns five reviewer agents — security, performance, correctness, test coverage, and edge/ripple — then synthesizes into a unified review.

**Reviewers:** Security, Performance, Correctness, Test Coverage, Edge & Ripple

### competing-hypotheses

Debug problems by investigating multiple hypotheses in parallel. Spawns investigator agents each pursuing a different theory, gathering evidence and counter-evidence, then compares findings to identify the most likely root cause.

**Workflow:** Hypothesize → Investigate → Compare → Fix (optional)

### dotfiles-mac

Create, update, or apply a macOS dotfiles repo using GNU Stow and plain git. Audits your system (Homebrew, shell, git, SSH, GPG, app configs, Claude/AI configs, macOS defaults), lets you pick what to track, and generates a stow-based repo with an idempotent setup script.

**Workflows:** Create new repo, Update/capture current state, Apply to a new machine

## License

[MIT](LICENSE)
