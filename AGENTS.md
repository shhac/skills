# Skills Repo

A collection of reusable Claude Code skills distributed via [skills.sh](https://skills.sh).

## Repo Structure

```
skills/
  <skill-name>/
    SKILL.md          # Skill definition with YAML frontmatter
scripts/
  <skill-name>/       # Optional per-skill maintenance scripts
    README.md         # Run instructions for the scripts
README.md             # Public-facing docs — lists all skills
LICENSE               # MIT
```

## Per-skill maintenance scripts

Some skills have helper scripts (validators, cleaners, generators) under `scripts/<skill-name>/`. They are **not** part of the shipped skill — they exist to help maintainers keep the skill's files consistent. No git hooks are configured; run them manually.

**When making changes to a skill, check `scripts/<skill-name>/README.md` (if it exists) for additional steps that should be done before committing** — typically running a validate script after editing, or a clean script after a bulk import.

## Skills.sh Conventions

- Each skill lives in `skills/<name>/SKILL.md`
- SKILL.md must have YAML frontmatter with `name` and `description`
- The `description` field is the trigger — Claude uses it to decide when to activate the skill
- Install via `npx skills add shhac/skills`

## Maintaining This Repo

- **README must stay in sync with skills.** When adding, removing, or renaming a skill, update the Skills section in `README.md` to match.
- Each skill should be self-contained and independently useful — users may install any combination.
- Skills should not reference or depend on each other, but can share ideas/patterns.

## Skill Design Guidelines

- Write skills as instructions for Claude, not documentation for humans
- Use YAML frontmatter `description` as the primary trigger — make it specific enough to avoid false activations
- Prefer the Teams pattern (`TeamCreate`/`SendMessage`/`TaskCreate`) for workflows with long-lived agents that benefit from retained context
- Prefer the Subagents pattern (`Task` tool) for short-lived, fire-and-forget work
- Don't hardcode project-specific tooling — detect dynamically (e.g., test runner, linter)
- Don't hardcode scratch directory paths — discover from `.gitignore` or fall back to `.ai-cache/`
