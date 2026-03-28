# skills

A collection of reusable Claude Code skills, distributed via [skills.sh](https://skills.sh).

**Website:** [skills.paulie.app](https://skills.paulie.app/)

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

### brainstorm

Brainstorm competing solutions to a problem using parallel agents. Each proposer independently designs an approach, then all proposers peer-review each other's work. Revised proposals are compared in a structured trade-off matrix.

**Workflow:** Frame → Propose → Peer Review → Revise → Compare → Handoff

### competing-hypotheses

Debug problems by investigating multiple hypotheses in parallel. Spawns investigator agents each pursuing a different theory, gathering evidence and counter-evidence, then compares findings to identify the most likely root cause.

**Workflow:** Hypothesize → Investigate → Compare → Fix (optional)

### sync-fork

Sync a forked repository with its upstream. Resets shared branches to upstream, re-merges local-only work, and cleans up branches already merged upstream. Auto-detects remotes or asks when ambiguous.

**Workflow:** Identify Remotes → Assess Divergence → Reset & Re-merge → Clean Up

### restack

Manage stacked branches without external tooling. Infers the dependency graph from git history, cascades rebases when trunk advances or a mid-stack branch changes, detects landed PRs, and cleans up. Lightweight alternative to Graphite — no account, no init, no metadata files.

**Workflow:** Infer Graph → Show Status → Restack / Sync → Clean Up

### image-to-svg

Convert raster images (photos, illustrations, AI-generated art) into high-quality SVG recreations. Decomposes the image into isolated features, builds each as a standalone SVG via parallel agents, then composites and iterates with programmatic render-compare loops.

**Workflow:** Analyze → Decompose → Build Features (parallel) → Align → Composite → Deliver

### dotfiles-mac

Create, update, or apply a macOS dotfiles repo using GNU Stow and plain git. Audits your system (Homebrew, shell, git, SSH, GPG, app configs, Claude/AI configs, macOS defaults), lets you pick what to track, and generates a stow-based repo with an idempotent setup script.

**Workflows:** Create new repo, Update/capture current state, Apply to a new machine

### ask-me-about

Extract and sharpen the user's mental model through targeted questioning. Interviews the user about an idea, concept, or design — probing gaps, challenging assumptions, and surfacing contradictions — then summarizes the shared understanding and asks what action to take.

**Workflow:** Interview → Summarize → Decide action (document, research, implement, hand off)

### improve-code-structure

Analyze and improve code structure across a repo or targeted scope. Spawns parallel analysts examining five lenses — function decomposition, file decomposition, complexity reduction, pattern deduplication, and test coverage — then implements approved changes sequentially.

**Workflow:** Analyze (parallel) → Synthesize → Approve → Implement (sequential)

## License

[MIT](LICENSE)
