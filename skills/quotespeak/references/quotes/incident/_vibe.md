# Incident - vibe map

Production fire, panic, the fixer arrives. Things broken *now* with stakeholders watching. Time pressure is load-bearing.

## Available moods

- `deadpan.yaml` - "This is fine." Underplayed crisis. The IT Crowd register.
- `ominous.yaml` - escalating, "Houston we have a problem", things-getting-worse cadence.
- `exasperated.yaml` - third outage this week, "why is everything on fire".
- `philosophical.yaml` - postmortem reflection. "Reality is often disappointing."
- `defiant.yaml` - fixer-arrives. Mr. Wolf calm. "I solve problems."
- `unhinged.yaml` - chaotic incidents played for laughs. "Now panic and freak out."

## Mood transitions - typical arcs

- **ominous → defiant**: situation worsens, Mr. Wolf arrives mentally. "Calm down. Let's think." Speaker takes command of the chaos.
- **exasperated → unhinged**: third outage today, the system is on fire and so are we. Played for dark comedy. "Now panic and freak out."
- **ominous → philosophical**: post-recovery debrief. "Reality is often disappointing." Step-back from the moment to assess.
- **deadpan → exasperated**: started routine, escalated. "This is fine" → "Why is everything on fire?"
- **defiant → deadpan**: fixer has it under control. The drama drops. Operational tone returns.

## Theme-specific corruption hints

- Mr. Wolf register is **quiet competence**, not chest-thumping. Don't corrupt his lines triumphantly - his power is in being matter-of-fact while everyone else panics.
- "This is fine" is over-used in real ops culture - when corrupting, lean on adjacency ("This is, technically, fine") rather than the literal phrase.
- Apollo / NASA voice is *procedural calm under pressure*. Corrupt by swapping aerospace nouns (telemetry, attitude, fuel) for ops nouns (latency, CPU, replicas).

## Source mix

Apollo 13, Pulp Fiction (Mr. Wolf), Aliens (Hudson), naval/aviation distress procedures, The IT Crowd, KC Green ("this is fine"), Naked Gun, war-room scenes generally.

## When NOT to use this theme - binary triggers

- **Activate this theme only when user mentions**: "production", "outage", "on fire", "down", "broken in prod", "p0", "p1", "war room", "page", "alert", "rolled back", "hotfix". Otherwise default to `investigation/_vibe.md` even if the speaker feels urgency.
- **Postmortem write-up days later (cool retrospective)** → `archaeology/_vibe.md` or `mentorship/philosophical.yaml`.
- **Pre-incident risk assessment** → `planning/_vibe.md`.
