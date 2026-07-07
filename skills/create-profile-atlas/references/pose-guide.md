# Pose Guide

Use these as reusable pose specs. Keep shortcodes subject-neutral by replacing `<prefix>` with the requested prefix, for example `pixel-paul-heart-eyes`.

## Core First-Run Set

Recommended 21-pose order:

1. `<prefix>`: neutral/base portrait.
2. `<prefix>-sus`: skeptical side-eye; sideways pupils and raised brow must be clear.
3. `<prefix>-angry`: red-faced, furrowed brows, large red anger mark like `anger symbol`; mark must be oversized.
4. `<prefix>-crown`: large gold crown; jewels readable at 48px.
5. `<prefix>-hacker`: sunglasses plus laptop/code glow; screen/code should be large, not tiny.
6. `<prefix>-unwell`: sickly green/yellow face, droopy eyes, ill expression.
7. `<prefix>-deadpan`: flat unimpressed eyes and straight mouth.
8. `<prefix>-shocked`: wide eyes and open mouth; blue/cyan upper face like screaming-face emoji.
9. `<prefix>-facepalm`: one large hand covering forehead/face; hand should dominate.
10. `<prefix>-laughing`: joyful open-mouth laugh; closed happy eyes optional.
11. `<prefix>-thinking`: large hand on chin, raised brow.
12. `<prefix>-thumbs-up`: large thumb close to face.
13. `<prefix>-deep-regret`: pained regret, downcast/closed eyes, heavy shadow.
14. `<prefix>-raised-hand`: large raised hand beside face.
15. `<prefix>-sweat-smile`: nervous smile with one very large blue sweat bead.
16. `<prefix>-thumbs-down`: large thumb down close to face.
17. `<prefix>-overwhelmed`: spiral/stressed eyes and stress marks.
18. `<prefix>-fingers-crossed`: crossed fingers large and close to face.
19. `<prefix>-is-feeling-emotion`: teary tender expression, big sparkling tears.
20. `<prefix>-sob`: huge streaming tears and open crying mouth; tears must be very large.
21. `<prefix>-mind-blown`: top-of-head explosion/starburst; explosion must be large.

## Common Extension Poses

- `<prefix>-heart-eyes`: huge red/pink heart-shaped eyes and happy smile.
- `<prefix>-pray`: large praying hands directly in front of face/chest, humble pleading expression; hands should dominate.
- `<prefix>-salute`: one large hand saluting at forehead, confident respectful expression; hand must be oversized.
- `<prefix>-party`: party hat plus oversized confetti streamers around head, joyful open-mouth smile; confetti must be readable.
- `<prefix>-clown`: clown makeup, red nose, cheek circles, optional small clown hat; preserve identity cues.
- `<prefix>-dead`: skull face with subject hair; include skeleton neck/upper chest if the user wants it to read strongly as dead/skeleton.
- `<prefix>-shaking-fist`: large fist toward viewer or beside face with motion/emphasis marks.
- `<prefix>-sleepy`: closed eyes, sleepy mouth or drool, large blue `Zzz`; remove trapped green between hair and Zs during cleanup.

## Classic Slack Reaction Poses

- `<prefix>-wizard`: wizard hat with stars/moon, visible subject cues, oversized glowing wand and sparkles; magical prop must read at 48px.
- `<prefix>-ninja`: black face mask/headband, visible eyes or sunglasses, large throwing star or similar prop near the face; silhouette must read as ninja.
- `<prefix>-melting`: face melting downward like melting-face emoji, droopy liquid shapes, slipping glasses optional; melt shape must be oversized.
- `<prefix>-grimace`: awkward clenched-teeth grimace, tense brows, optional large sweat bead; teeth should be a big readable rectangle.
- `<prefix>-popcorn`: large popcorn tub close to face, watching-drama expression, oversized kernels; tub and popcorn should dominate.
- `<prefix>-rubber-duck`: large bright yellow rubber duck in foreground, held or hugged; duck must dominate and read as a debugging buddy.
- `<prefix>-100`: huge red `100` symbol with underline or emphasis marks plus approving subject expression; exact numerals must dominate.
- `<prefix>-this`: subject pointing emphatically at a large sign, speech bubble, or placard with exact word `THIS`; text must dominate.

## Prompt Requirements

- Ask for generated pixel art or the target style, not manual/vector overlays.
- Require flat solid `#00ff00` chroma-key background with no shadows, gradients, texture, floor plane, or lighting variation.
- Require green gutters between cells.
- Require no text labels, no numbers, no watermark, no borders, no grid lines.
- Require close face/bust crops and consistent scale.
- Require big readable details for every expression-specific prop or symbol.
- For text-heavy poses like `<prefix>-100` and `<prefix>-this`, state the exact allowed text and forbid all other text.

## Replacement Guidance

Regenerate a single cell when:

- A prop is too small at 48px.
- The subject identity drifts.
- A pose reads ambiguously.
- The background has trapped green in a place where normal border flood-fill cannot reach.

Keep the replacement on the same flat key color and compose it into the target slot during post-processing.
