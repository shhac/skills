# Skills Repo

A collection of reusable Claude Code skills distributed via [skills.sh](https://skills.sh).

## Repo Structure

```
skills/
  <skill-name>/
    SKILL.md          # Skill definition with YAML frontmatter
README.md             # Public-facing docs — lists all skills
LICENSE               # MIT
```

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
