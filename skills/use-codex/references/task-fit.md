# Scope a Codex handoff

Codex draws on the signed-in ChatGPT account or OpenAI API billing. Each run takes time and uses quota or credits, so delegate when it can do substantial independent work or add a second perspective.

| Task | Give Codex |
| --- | --- |
| Repo exploration | The entry point or symptom, the paths already checked, and the question to answer with file and line references. |
| Implementation | The chosen approach, relevant project instructions, files or interfaces in scope, acceptance criteria, and the checks to run. |
| Mechanical edits | The transformation, exceptions, and a way to detect missed or unintended changes. |
| Review | The diff or commit range, the intended behavior, and known areas of risk. Ask for reproducible findings with file and line references. |
| Stuck bug | The reproduction, observed and expected behavior, prior attempts, and how to verify a fix. |

Resolve design decisions with the user when they affect what counts as success. If multiple turns share substantial context, resume by session ID. Verify the result against the repo before using it.
