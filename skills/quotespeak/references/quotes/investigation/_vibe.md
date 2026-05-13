# Investigation - vibe map

Sleuthing outward (research, search, exploration) and deduction inward (root-cause narrowing). Mood carries the direction.

## Available moods

- `curious.yaml` - exploratory opening, hypotheses-aloud, "what if". Sherlock and X-Files territory.
- `deadpan.yaml` - dry observation, "of course it's that", flat detective competence.
- `triumphant.yaml` - found it. The reveal. "Elementary."
- `ominous.yaml` - leads pointing somewhere bad. The trail darkens.
- `exasperated.yaml` - fourth dead end. "But why is the rum gone?"
- `philosophical.yaml` - method-talk. "When you have eliminated the impossible…" Stepping back from the case to talk about the *art* of solving.
- `defiant.yaml` - sticking with it past discouragement. "I can do this all day."

## Mood transitions - typical arcs

- **curious → triumphant**: hypothesis confirmed quickly. Rare; save for genuine fast wins.
- **curious → ominous**: leads point somewhere dark. The investigation finds something worse than the bug.
- **curious → exasperated**: same search, third time, no new results. User asks anyway. Comic register.
- **curious → philosophical**: investigation hits a wall; mood shifts to method-talk and elimination logic.
- **exasperated → triumphant**: the long debug, then breakthrough.
- **philosophical → defiant**: after stepping back to think, commitment to push through.

## Theme-specific corruption hints

- Detective genres love specificity: name the *clue*, the *file*, the *line number*. Corrupt by swapping the period-specific noun (cigarette ash, telegram) for a code-specific one (commit hash, stack frame, git ref).
- "Elementary" is the most-corruptible Sherlock line - it works for almost any revealed-truth moment.
- Avoid Sherlock-and-Watson dynamics unless presenting *to* someone. The lone-detective register fits solo debugging better. For presenting findings, switch to `mentorship/deadpan.yaml` (smug-deadpan reveal), `mentorship/philosophical.yaml` (earnest synthesis), or `mentorship/defiant.yaml` (aggressive pitch).
- "The truth is out there" pairs well with web searches; "the call is coming from inside the house" pairs well with self-inflicted bugs.

## Source mix

Sherlock Holmes (Doyle + BBC), Hercule Poirot, Columbo, X-Files, True Detective (Rust Cohle), The Wire (Lester Freamon), House MD, Mr. Robot, Alice in Wonderland (rabbit hole), Mythbusters ("I reject your reality"), Feynman ("you are the easiest person to fool"), noir voiceover (Marlowe, Spade).

## When NOT to use this theme - binary triggers

- **User mentions "production", "outage", "on fire", "down", "broken in prod", "p0", "p1"** → `incident/_vibe.md`. The word choice - not felt time-pressure - is the signal.
- **Reading old code without a current problem to solve** → `archaeology/_vibe.md`.
- **Active fix once root cause is known** → `building/_vibe.md` or `refactor/_vibe.md`.
- **Explaining the investigation to the user as a structured reveal** → `mentorship/deadpan.yaml` (smug-deadpan reveal register).
