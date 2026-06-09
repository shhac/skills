# Conventions Lens

Check whether the PR follows established repo conventions.

Infer conventions from nearby files, existing tests, docs, project configuration, and patterns in the changed area.

Check:

- File placement, module organization, imports, and export style
- Naming style, formatting conventions, framework idioms, and preferred helper APIs
- Error handling, logging, observability, accessibility, security, and data-access patterns the repo already uses
- Whether the PR introduces a one-off approach where the repo has an established path

Do not invent conventions from general preference. Tie findings to examples from the local codebase whenever possible.
