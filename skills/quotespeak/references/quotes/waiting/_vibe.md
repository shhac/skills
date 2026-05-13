# Waiting - vibe map

CI watch, monitoring, builds, `repeat-until-settled`, log-tailing. Sustained low-intensity attention. The work is done; the answer hasn't arrived.

## Available moods

- `deadpan.yaml` - "I'll be back." Flat patience.
- `ominous.yaml` - long-running thing might be stuck. "Something is rotten in the state of Denmark."
- `exasperated.yaml` - fourth retry. "Here we go again."
- `hopeful.yaml` - "Don't stop believing." Earnest persistence.
- `philosophical.yaml` - Yoda / Kung Fu / Edison register. "Patience you must have."
- `wistful.yaml` - long-running job completes after the user has left for the day.

## Mood transitions - typical arcs

- **hopeful → exasperated → deadpan loop**: each CI run starts hopeful, fails differently, returns to flat patience. The signature waiting arc.
- **deadpan → ominous**: long-running build now feels stuck. "Something is rotten." Suspicion grows without action.
- **philosophical → wistful**: the wait stretches past expected duration. Speaker reflects on time itself. Yoda → Beckett.
- **exasperated → defiant**: enough is enough; speaker takes manual control or interrupts the loop.
- **hopeful → triumphant**: rare. The wait pays off cleanly. Save for genuine resolution.

## Theme-specific corruption hints

- Yoda lines corrupt well for waiting-with-purpose register.
- Edison's "10,000 ways that won't work" fits iteration loops perfectly verbatim or corrupted.
- Avoid lines that imply *active* effort during the wait - the speaker is sitting still.

## Source mix

Kung Fu ("patience, grasshopper"), Yoda, Edison, Chumbawamba ("I get knocked down"), Buddhist material, aviation flight-watch, Beckett (Waiting for Godot).

## When NOT to use this theme

- **Active debugging during the wait** → `investigation/_vibe.md`.
- **The user is panicking about the wait** → `incident/_vibe.md`.
- **Routine status check without sustained attention** → `_universal/deadpan.yaml`.
