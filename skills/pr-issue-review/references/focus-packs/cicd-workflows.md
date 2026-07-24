# CI/CD Workflows Focus Pack

Load when changed files include CI pipeline configuration (`.github/workflows/`, other pipeline YAML), deploy scripts, release automation, or action/runner configuration.

Look for:

- Untrusted interpolation into `run:` steps: expressions like `${{ github.event.issue.title }}`, branch names, PR titles/bodies, or commit messages expanded directly into shell (workflow command injection). Prefer passing untrusted values through `env:` and quoting.
- `pull_request_target`, `workflow_run`, or checkout-of-fork patterns that run privileged workflows against untrusted code, and secrets exposed to runs triggerable from forks.
- Third-party actions referenced by mutable tags instead of pinned SHAs, and new actions with broad repository or secret access.
- `GITHUB_TOKEN`/credential permissions broader than the workflow needs, or new secrets granted to jobs that do not use them.
- Merge-gating checks silently weakened: required jobs removed, made skippable, `continue-on-error` added, failure conditions loosened, or a gate rewired so it no longer runs for the paths it guards.
- Deploy/waiter semantics: retry loops that cannot distinguish a terminal failure from slowness (burning the full timeout before reporting a hard failure), missing fail-fast on rollback or failed-task states, and steps whose failure leaves a deploy half-applied.
- Redundant machinery: a new gate or job duplicating a signal the pipeline already receives elsewhere — ask whether it should exist, and what it costs every run (runners, wall-clock, a new shared prerequisite for unrelated jobs).
- Scheduled workflows assuming a timezone (`cron` is UTC), or event triggers that quietly stop matching after a rename.

Good findings name the trigger context and privilege level involved, state what an attacker or a failure could do differently after this change, and suggest the smallest safer direction: pin the action, narrow permissions, move untrusted input to env, split privileged from unprivileged workflows, or fail fast on terminal states.

Reference basis: GitHub Actions security hardening guidance and general CI/CD supply-chain practice.
