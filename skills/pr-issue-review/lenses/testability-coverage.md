# Testability And Coverage Lens

Check whether the PR is easy to test and whether the tests support confidence in the stated issue.

Check:

- Missing tests for the behavior the PR claims to fix or add
- Missing edge-case, failure-path, permission, migration, or integration coverage
- Tests that assert implementation details instead of user-visible or contract-level behavior
- Brittle fixtures, excessive mocking, timing assumptions, or order dependencies
- Code that is hard to test because logic is coupled to IO, global state, framework glue, or hidden side effects

When suggesting tests, name the behavior or scenario to cover rather than prescribing a large test rewrite.
