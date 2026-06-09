# Safety Lens

Look for malicious-looking or intentionally dangerous changes.

Check:

- Secret exfiltration, credential leakage, hidden network calls, or suspicious telemetry
- Destructive data changes, dangerous migrations, or surprising filesystem/process access
- Suspicious install hooks, generated binaries, minified payloads, obfuscated code, or dependency swaps
- Authentication, authorization, permission, or tenant-boundary regressions
- Logging or error handling that exposes sensitive user, business, or infrastructure data

This is the only lens that can justify `REQUEST_CHANGES`, and only when the evidence suggests malicious or intentionally dangerous behavior.
