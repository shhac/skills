# Iteration state capture

The loop needs to:

1. Detect when an iteration changed anything (compare `pre` to `post`).
2. Detect when a state recurs (compare `post` to earlier iterations' states for cycle detection).
3. Capture per-iteration data for the convergence summary.

The recipe for capturing a "state" depends on the project type. The orchestrator picks a recipe at Setup based on what it sees in the working directory. If no recipe fits cleanly, it asks the user — silent miscapture is worse than a brief pause.

## Recipe: git project

Marker: `.git/` directory present.

State capture:

```
HEAD_SHA       = git rev-parse HEAD
STATUS_HASH    = sha256(git status --porcelain=v1 -z)
DIFF_HASH      = sha256(git diff HEAD)
UNTRACKED_HASH = sha256(concatenated content of files matching `git ls-files --others --exclude-standard`, sorted by path)

state = (HEAD_SHA, STATUS_HASH, DIFF_HASH, UNTRACKED_HASH)
```

Two states are equal iff all four components are equal. The combination is robust to: the inner skill committing (HEAD_SHA changes), staging without committing (STATUS_HASH changes), uncommitted edits (DIFF_HASH changes), and creating new files (UNTRACKED_HASH changes — easy to miss with naive `git diff` alone).

Per-iteration data for the convergence summary:

- `git diff --stat <pre.HEAD_SHA>..<post.HEAD_SHA>` for committed work
- `git diff --stat HEAD` for uncommitted work at end of iteration
- List of new untracked files, if any

## Recipe: plain filesystem (no git)

Marker: no `.git/` directory; project is a plain directory tree (e.g. a manuscript, an artwork project, configs without version control).

State capture:

```
state = sha256(concatenated (path, content-hash) pairs for every file in scope, sorted by path)
```

The orchestrator picks "in scope" at Setup. Default: all files under the working directory excluding common dependency/build/cache directories (`node_modules/`, `target/`, `build/`, `dist/`, `.cache/`, `__pycache__/`, `.next/`, `.venv/`). Always exclude IDE state (`.vscode/`, `.idea/`) and OS metadata (`.DS_Store`, `Thumbs.db`). The user can override scope at invocation time.

Per-iteration data for the convergence summary:

- Count of files changed, added, deleted relative to the prior iteration
- For text-heavy projects (novels, docs): word-count delta on changed files

## Recipe: ambiguous or mixed

When the project doesn't fit either recipe cleanly — a subset of files matters, the project mixes versioned and unversioned content, or you're operating on a single artifact (one document, one image) within a larger directory — ask the user at Setup. Suggested questions:

- "What set of files should I treat as the state that this loop is iterating on?"
- "How should I detect whether an iteration changed anything?"

Do not invent a state-capture mechanism without confirmation when the project shape is ambiguous. False equality (capturing too little) silently breaks settle and cycle detection. False inequality (capturing too much — log files, timestamps, build outputs) makes every iteration look like progress and the loop never settles.

## Anti-recipe — never capture

These change spuriously and must NOT be part of the state hash:

- File modification timestamps (use content hashes only)
- Generated/build artifacts that change every build
- Log files
- Lockfiles regenerated on every install
- IDE state (`.vscode/`, `.idea/`, etc.)
- OS metadata (`.DS_Store`, `Thumbs.db`)

When unsure whether something is volatile, exclude it and ask the user.
