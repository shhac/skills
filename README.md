# skills

A collection of reusable Claude Code skills, distributed via [skills.sh](https://skills.sh).

**Website:** [skills.paulie.app](https://skills.paulie.app/)

## Installation

```bash
npx skills add shhac/skills
```

## Skills

### firestop

Rapid operational alert triage and incident coordination from a Slack channel, alert, incident, Linear issue, or GitHub reference. Keeps incident communication in the relevant thread, posts an opening update before investigating and keeps posting as it goes rather than going quiet until it has an answer, gives every update a concrete next action and owner, re-checks human context before major conclusions, and preserves human control of incident state.

**Workflow:** Orient → Post opening update → Triage (people + signal + change + impact + precedent) → Recommend / act → Human handoff

### pr-issue-review

Review a GitHub pull request against its stated issue using the `passive`, `neutral`, `assertive`, or `aggressive` profile. Statically reads the PR diff, metadata, comments, and discovered Linear/Slack/Notion/GitHub context; caches fetched context under the temporary checkout's untracked `.ai-cache/`; then loads the chosen profile, a reviewer persona (voice only, caller-selectable), review lenses, and any matching focus packs before leaving an emoji-marked GitHub review with severity-tagged findings, a concise top-level rationale, targeted inline comments, and suggestion blocks for quick wins. Designed for automated review loops: never runs code, usually approves or comments, and only blocks malicious-looking changes.

**Workflow:** Fetch PR shallowly → Discover context → Cache context → Choose review profile + persona → Load lenses/focus packs → Approve or comment with inline suggestions

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

### create-profile-atlas

Create or extend generated profile/portrait emoji atlases for Slack-style custom emoji. Generates chroma-keyed pixel/profile/person/mascot emoji sets, splits them into transparent PNGs, validates 48px readability, packages manifests/previews/zips, and can optionally upload custom emoji to Slack.

**Workflow:** Collect references → Generate atlas → Inspect → Split & clean → Validate → Package / Upload

### dotfiles-mac

Create, update, or apply a macOS dotfiles repo using GNU Stow and plain git. Audits your system (Homebrew, shell, git, SSH, GPG, app configs, Claude/AI configs, macOS defaults), lets you pick what to track, and generates a stow-based repo with an idempotent setup script.

**Workflows:** Create new repo, Update/capture current state, Apply to a new machine

### ask-me-about

Extract and sharpen the user's mental model through targeted questioning. Interviews the user about an idea, concept, or design — probing gaps, challenging assumptions, and surfacing contradictions — then summarizes the shared understanding and asks what action to take.

**Workflow:** Interview → Summarize → Decide action (document, research, implement, hand off)

### improve-code-structure

Analyze and improve code structure across a repo or targeted scope. Spawns parallel analysts — one per lens (function decomposition, file decomposition, complexity reduction, pattern deduplication, test coverage, structural simplification, abstraction fit; extensible) — then implements approved changes sequentially with full verification (tests + typecheck + lint) between each. After refactoring, sweeps for dead/unreachable/orphaned code introduced as side effects, audits each finding deeply against false-positive traps, and removes anything confirmed dead while verification stays green. Harness-portable (Claude Code, Agent SDK, API).

**Workflow:** Analyze (parallel) → Synthesize → Approve → Implement (sequential) → Dead-code sweep + per-finding audit → Validate

### seam-audit

Diagnostic pass over a codebase's module *boundaries*, not the code inside them. Defines a "seam" as the import-direction edge between two interfaces; enumerates every module's incoming and outgoing seams; produces a layered ASCII topology diagram; classifies each module as narrow, hub-by-design, or accidental hub. Outputs a flagged-for-review list plus a sanity-check "not actioned" list. Diagnostic only — emits no code changes, hands off to a refactor skill if action is wanted. Sibling to `improve-code-structure`: that one fixes problems inside modules, this one identifies whether the boundaries are in the right places.

**Workflow:** Define module granularity → Enumerate seams → Diagram → Classify + flag accidental hubs / cycles / layer violations

### repeat-until-settled

Run another skill in a loop until its output settles — meaning no further substantive changes or recommendations. Domain-agnostic: works on code in a git repo, prose in a manuscript directory, image files, configs, anything. Detects cycles (oscillation between two or more states) and resolves them forward — never backwards: either Stay (current state is a fixed point) or Forward-escape (instruct the inner skill toward the better alternate). Detects stalls (recommendations that won't land), pauses with an orchestration-layer-aware diagnosis, and switches to a deeper-stall pause that drops "retry" once it's clear retry isn't working. Optionally chains to a follow-up skill on settle. No iteration cap by default; explicit `max=N` opt-in.

**Example:** `repeat-until-settled improve-code-structure then release`

**Workflow:** Parse args → Pick state recipe → Iterate (capture pre → invoke inner → capture post → classify) → Settle / Cycle-resolve (stay or forward-escape) / Stall-pause → Exit-reason dispatch → Convergence summary → Follow-up

### quotespeak

Speak using pop culture quotes, movie lines, song lyrics, and memes, verbatim or playfully corrupted to fit. The defining rule: quotes *substitute* for plain prose, never decorate it ("You shall not pass!" replaces "auth was rejected", not added on top). Tagged catalog of 1,000+ quotes organized into 11 themes of work (investigation, building, refactor, shipping, incident, planning, delegation, mentorship, waiting, archaeology, deprecation) and 10 moods (curious, deadpan, triumphant, ominous, exasperated, hopeful, philosophical, wistful, defiant, unhinged), with a `_universal/` cross-cutting layer. Progressive-disclosure loading: only the active theme/mood files load into context, not the whole bank. Placeholder-corruption strategy for iconic lines whose canonical form is workplace-NSFW or copyright-sensitive. Intensity levels: `subtle`, `full` (default), `unhinged`. Auto-clarity carve-outs are unconditional: code, commits, CLI commands, security warnings, and irreversible-action confirmations stay plain.

**Example:** `/quotespeak unhinged`

**Levels:** subtle (~1 per response) → full (laced through) → unhinged (every sentence is a reference)

### lucid

Shape every chat response so a human scanning a terminal gets all the information without waffle and without it buried in prose. Concision comes from a per-sentence test rather than a word budget: every sentence must add a fact, an instruction, a number, or a decision the reader did not already have. Every rule derives from five facts about how terminal output is actually read (the first line decides whether the rest gets read, the reader is hunting one specific fact, structure costs vertical space, scrollback is expensive, paths are the payload). Constrains what must be present and what must be cut, and deliberately does not prescribe layout, since uniform structure is its own tell. A "what is not waffle" section protects real uncertainty, destructive-action detail, requested explanations, and admissions of skipped work from the trimming pass.

**Example:** `/lucid`

**Scope:** chat responses only, on by default, until "stop lucid" or "normal mode"

**Surfaces:** Claude Code TUI and Desktop, Codex TUI and Desktop. Written for the narrowest of them.

### lucid-doc

Sibling to `lucid`, pointed at written deliverables: PR descriptions, READMEs, reports, RFCs, issues, status updates. The reader was not in the conversation, needs to decide or act, and skims before reading, so load-bearing context gets inlined instead of linked, headings make claims instead of naming categories, and no section restates what the diff or the code already says. Includes the "could this paragraph appear unchanged in another project's document" test. Reproduction steps, risks, and legal or security precision are exempt from trimming.

**Example:** `/lucid-doc` on a PR description draft

**Scope:** invoked on a target document, never automatic

### use-codex

Delegate scoped work to the OpenAI Codex CLI (`codex exec`) on a separate token budget. Covers when delegation pays off (repo Q&A, well-specified implementation, mechanical edits, adversarial review, stuck bugs) and when it doesn't, plus verified invocation mechanics: final-message-only capture (`-o`), session-ID capture via `--json`, non-interactive resume by thread ID, sandbox ladder, and effort-scaled timeouts. Progressive disclosure — the decision heuristic loads first; flag references only load if delegating.

**Workflow:** Decide (delegate vs keep) → Invoke (read-only or workspace-write) → Verify output as a peer's work → Resume session for follow-ups

### use-claude

Sibling to `use-codex`, pointing the other way: delegate scoped work to Claude Code's headless mode (`claude -p`) from a non-Claude agent, on a separate token budget. Covers when Claude's quality-per-task premium pays off (hard multi-file implementation, long-horizon debugging, test authoring, cross-family review) and when it doesn't, plus verified mechanics: single-JSON result capture (`--output-format json`), session resume by ID, the permission ladder for headless runs, and the variadic-flag gotcha. Opens with a self-exclusion line ("If you are Claude, you do not need this skill") — progressive disclosure keeps flag references out of context unless delegating.

**Workflow:** Decide (delegate vs keep) → Invoke (read-only tools or acceptEdits) → Verify output as a peer's work → Resume session for follow-ups

## Deprecated

Kept for reference under `deprecated/`, prefixed `dep-`. Not distributed by skills.sh and not installed by `npx skills add`.

### dep-multi-review

Review code changes from multiple specialist perspectives in parallel. Spawns five reviewer agents — security, performance, correctness, test coverage, and edge/ripple — then synthesizes into a unified review.

**Reviewers:** Security, Performance, Correctness, Test Coverage, Edge & Ripple

### dep-orchestrate-subagents

Activate orchestrator mode for complex multi-task work using sub-agents. Delegates aggressively, coordinates via gitignored scratch files, and keeps the main context window clean.

**Workflow:** Analyze → Spawn → Coordinate → Collect

### dep-team-solve

Investigate and solve problems using a team of specialist agents. Decomposes a problem into parallel investigation tracks, synthesizes findings, then implements solutions serially (or in parallel when safe).

**Workflow:** Investigate → Discuss → Implement → Validate

## License

[MIT](LICENSE)
