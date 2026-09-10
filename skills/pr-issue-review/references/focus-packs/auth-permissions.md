# Auth and Permissions Focus Pack

Load when changed files or PR context mention authentication, authorization, permissions, roles, scopes, tenants, sessions, tokens, sharing, policy checks, admin/staff access, or privacy boundaries.

Look for:

- Client-side or UI-only checks where server-side enforcement is needed. For each newly accepted mutation or expanded input, name the layer that enforces each stated restriction ("super-user only", "owner only"), and name the check that does run: read the resolver, service, or middleware permission wrapper on the write path rather than inferring it from the UI. Then ask what a caller who already passes that server-side check gains by bypassing the client gate. A server accepting a write from a caller it should have rejected is `⚠️ P1`. A staff-only gate layered on a write path that already authorizes this caller for this resource is graded on blast radius like any other finding (SKILL.md, Finding Severity), not automatically P1.
- List/detail/export/action paths with inconsistent permission checks.
- Tenant/user/org boundary leaks, IDOR-style access, or missing ownership validation.
- Role/scope expansions that grant more than intended or skip least-privilege reasoning.
- Authentication state, token, session, refresh, or logout changes that can leave stale access.
- Sensitive data exposed in logs, errors, URLs, analytics, webhooks, or job payloads.
- Tests that cover happy-path roles but miss denied/other-tenant cases.

Good findings cite the protected action or data boundary, explain who can gain or lose access incorrectly, and suggest the smallest enforcement point: central policy, server-side check, ownership validation, deny-by-default branch, or negative test.

Reference basis: OWASP ASVS and authorization cheat-sheet guidance.
