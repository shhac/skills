# User-Visible Text Lens

Use this lens when the PR changes UI copy, user-facing errors, notifications, emails, logs exposed to users, generated documents, locale/message files, or code paths that choose text shown outside the system.

Look for:

- New user-visible strings that bypass the repo's message, localization, or copy-review conventions
- Locale/message files containing placeholder copy, untranslated text, or inconsistent entries across supported languages
- Error or fallback paths that prefer raw strings over translated or structured messages
- Dynamic strings that cannot be localized or pluralized because counts and placeholders are not structured
- Copy added to one surface but not the related user-facing surfaces that should stay consistent
- Nearby repo guidance such as local agent instructions, style guides, localization docs, or message-file conventions

Good findings cite the local rule or neighboring pattern, explain the user-visible impact, and point to the smallest direction: add real translations, return structured error codes/counts, use the repo's message layer, or move display text to the appropriate boundary.
