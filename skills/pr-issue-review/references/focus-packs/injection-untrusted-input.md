# Injection and Untrusted Input Focus Pack

Load when changed code interpolates or concatenates request, user, or external data into SQL/NoSQL queries, shell commands, file paths, HTML, redirects/URLs, headers, log lines, deserializers, or eval-like sinks, in any repo. This pack covers *accidentally introduced* injectability; deliberately malicious diffs remain the safety lens's territory.

Look for:

- SQL/NoSQL built by string concatenation or template interpolation where any input segment can be influenced by a request, user record, or external system. Trace each changed sink back to its sources (taint trace: parameter → sink).
- Shell commands, subprocess arguments, or CLI invocations assembled from non-literal input without an argument-array API or escaping.
- File paths joined from user-influenced segments without normalization/containment checks (path traversal).
- HTML rendered from unescaped input: `dangerouslySetInnerHTML`, `innerHTML`, unescaped template output, markdown rendered as raw HTML.
- Fetch/request targets, redirect destinations, or webhook URLs influenced by user input (SSRF, open redirects), especially when the request runs with server-side credentials or network position.
- Response headers or emails assembled from unvalidated input (header injection).
- Deserialization of untrusted payloads with formats or options that permit code execution or type confusion.
- Untrusted data written into log lines without encoding, enabling log forging or log-pipeline injection.

Good findings name the source-to-sink path, state who can control the input, and suggest the smallest safe alternative already used in the repo: the parameterized query helper, the argument-array subprocess API, the sanitizer or escaping function nearby. Prefer pointing at the repo's existing safe pattern over generic advice.

Reference basis: OWASP Top 10 injection categories and the relevant OWASP cheat sheets.
