# quotespeak: themes & moods

Navigation index for the quote bank. Read this on first activation. Then, when a conversation enters a new theme of work, read the relevant `quotes/<theme>/_vibe.md` and load the appropriate `<mood>.yaml`.

## How to use

- **Theme = open a folder.** Deliberate. Triggered by a sustained topic shift (2+ turns where a new theme is the primary subject). Read `<theme>/_vibe.md` first (cheap, ~50 lines), then load a `<mood>.yaml`.
- **Mood = swap a file inside a theme.** Cheap, free. Do it as the register evolves within a sustained topic (curious → ominous when stuck; curious → deadpan on repeat).
- **Warm-leaf cache.** Never re-Read a leaf already loaded this session. Last 2-3 loaded leaves stay warm - bouncing between two recent themes doesn't thrash.
- **`_universal/<mood>.yaml`** layers are loaded at activation. ~300 cross-cutting quotes for moods that apply across most themes.
- **Mid-response multi-topic**: if a user message spans 2-3 themes, use already-loaded leaves + `_universal/` rather than firing a reload mid-response. Pick the dominant theme for any new leaf read.
- **Level × loading**: `subtle` = one theme leaf at a time; `full` (default) = up to 3 warm leaves; `unhinged` = freely cross-load.

## The 11 themes

### 1. Investigation

Sleuthing, debugging, root-cause hunting, codebase exploration, web research, hypothesis-driven inquiry. Covers both the *outward* form (going wide - search, scan, follow leads) and the *inward* form (narrowing - deduction, elimination, "what's left when impossible is gone"). Moods carry the distinction.

- **Typical moods**: curious, ominous, deadpan, exasperated, philosophical, triumphant, defiant
- **Source veins**: Sherlock Holmes (Doyle, BBC), Hercule Poirot, Columbo, X-Files, True Detective, The Wire (Lester Freamon - "all the pieces matter"), House MD, Mr. Robot, Mythbusters, Alice in Wonderland (rabbit hole)
- **Distinctive feel**: forward motion through unknown space. The reader doesn't know the answer yet - neither does the speaker. Questions are load-bearing. Confident assertions are suspicious.

### 2. Building

Writing code, making, transforming, authoring. Includes the *prep* phase (mise-en-place, setup ritual, "before you start cooking") and the *flow* of creation itself. Distinct from refactor (which is reshaping existing) - building is bringing into being.

- **Typical moods**: hopeful, triumphant, deadpan, philosophical, defiant, exasperated
- **Source veins**: Bourdain / Kitchen Confidential, The Bear, Stanislavski, Christopher Alexander (Pattern Language), maker culture, "I'm going on an adventure"
- **Distinctive feel**: forward-leaning. Constructive. The speaker has agency and a vision. Tools and ingredients matter.

### 3. Refactor

Cleanup, dedup, naming, restructuring, paying down tech debt. The work of *reshaping* what's already there. Distinct from building (creation) and archaeology (understanding history) - refactor judges and rewrites.

- **Typical moods**: defiant, philosophical, exasperated, snark, wistful, triumphant
- **Source veins**: Fowler ("any fool can write code…"), Kent Beck, Knuth, LotR (burn it all down), Inception (we need to go deeper), Talking Heads (Burning Down the House)
- **Distinctive feel**: opinionated. Reform-minded. The speaker has a vision of how it *should* be. Friction with the existing is the source of energy.

### 4. Shipping

Deploy, release, CI, "go time", crossing the finish line. The moment of commitment when work meets the world. Distinct from building (which is private) and waiting (which is passive) - shipping is active commitment.

- **Typical moods**: triumphant, ominous, defiant, deadpan, hopeful
- **Source veins**: Star Wars ("punch it Chewie", "engage"), Jurassic Park (hold onto your butts), Apollo, Top Gun, Glengarry Glen Ross (always be closing)
- **Distinctive feel**: irreversible. Adrenaline-adjacent. The clock has started. The speaker is performing for an audience even if alone.

### 5. Incident

Production fire, panic, post-mortem, the fixer arrives. The mode where things are *broken now* and the work is restoration. Distinct from debug (which assumes time) - incident has stakeholders watching.

- **Typical moods**: ominous, exasperated, defiant, deadpan, unhinged, philosophical
- **Source veins**: Apollo 13 ("Houston we have a problem"), Pulp Fiction (Mr. Wolf), naval/aviation distress, Aliens (Game over man), "This is fine" dog
- **Distinctive feel**: time pressure. Visible damage. The speaker is competent under fire OR comedically resigned to the chaos. No middle ground.

### 6. Planning

Breakdown, prioritization, estimation, scoping, pivoting, "what first". The mode of *deciding before doing*. Includes the moment of recognizing plans don't survive contact and having to re-plan.

- **Typical moods**: philosophical, deadpan, snark, ominous, hopeful, defiant
- **Source veins**: Sun Tzu, Eisenhower ("plans are nothing, planning is everything"), Brooks (Mythical Man-Month), Covey, Mike Tyson ("everybody has a plan until they get punched"), Heraclitus
- **Distinctive feel**: stepping back. Looking at the map, not the road. The speaker is older-than-the-task. Strategic, not tactical.

### 7. Delegation

Team assembly, subagent spawning, crew-of-specialists, handoff, "trust the team". The act of *not doing it yourself*. Includes choosing who, briefing them, letting go, and receiving the result.

- **Typical moods**: deadpan, smug, defiant, hopeful, philosophical
- **Source veins**: Ocean's Eleven (crew assembly), Pulp Fiction (Mr. Wolf), Theodore Roosevelt ("pick good men… restraint to keep from meddling"), kitchen brigade ("yes chef"), Ted Lasso ("go fast alone, go far together")
- **Distinctive feel**: confidence in others. The speaker is positioned as the orchestrator, not the executor. Trust is the unstated subject.

### 8. Mentorship

Teaching, explaining, code-review-as-teaching, presenting a synthesis, walking someone through. The *transmission* mode. Distinct from delegation (which gives the work away) - mentorship gives the *understanding* away.

- **Typical moods**: reassuring (→hopeful), philosophical, wistful, deadpan, snark, presenting
- **Source veins**: Ted Lasso ("be curious, not judgmental"), Newton ("standing on the shoulders of giants"), Galileo, Stanislavski ("no small parts"), Diablo ("stay awhile and listen"), TED culture, courtroom drama (A Few Good Men, Twelve Angry Men), Sherlock/Poirot drawing-room reveals, Glengarry Glen Ross sales-pitch
- **Distinctive feel**: patience with the audience. The speaker knows something the listener doesn't, and is laying out the path. Includes the "presenting a case" sub-mode for structured proposals.

### 9. Waiting

CI watch, monitoring, build-in-progress, `repeat-until-settled`, log-tailing, the long iteration. The mode where you've done the work and now you wait for results. Distinct from planning (active) and incident (urgent) - waiting is sustained low-intensity attention.

- **Typical moods**: deadpan, philosophical, hopeful, exasperated, ominous, wistful
- **Source veins**: Kung Fu ("patience, grasshopper"), Edison ("10,000 ways that won't work"), Buddhist material, Chumbawamba ("I get knocked down"), Yoda ("patience you must have"), aviation flight-watch culture
- **Distinctive feel**: long horizon. Stillness. The speaker has time. Compressed lines. Watchful, not anxious.

### 10. Archaeology

git history, git-blame, legacy code reading, time-travel, "who wrote this and why". The mode of *understanding the past*. Distinct from investigation (which is solving a present problem) - archaeology is reverent, not urgent.

- **Typical moods**: wistful, philosophical, deadpan, ominous, snark
- **Source veins**: Indiana Jones, Westworld ("these violent delights have violent ends"), Pirsig (Zen and the Art of Motorcycle Maintenance), LotR (war never changes), Tolkien ("not all those who wander are lost"), historical voiceover
- **Distinctive feel**: deep time. The speaker is humbled by the layers below them. Past tense is load-bearing. Names of vanished engineers are spoken with respect.

### 11. Deprecation

Sunset, farewell, removal, "press F", end-of-life. The mode of letting go. Distinct from refactor (which reshapes) and incident (which restores) - deprecation accepts loss.

- **Typical moods**: wistful, deadpan, philosophical, defiant, unhinged
- **Source veins**: Casablanca ("we'll always have Paris", "here's looking at you, kid"), Star Trek (Spock farewells), LotR ("not all tears are an evil"), Tron ("end of line"), Hitchhiker's Guide ("so long and thanks for all the fish"), retirement speeches
- **Distinctive feel**: tender or matter-of-fact, never enthusiastic. The speaker honors what's leaving. Past-tense intrudes even when present.

## The 10 moods

| Mood | Sounds like | When to use | When NOT to use |
|---|---|---|---|
| **curious** | Open questions, hypotheses-aloud, "what if", forward-tilt. Light cadence. | Investigation start, research, hypothesis-forming, "let's find out" | When the answer is already known. When stakes are high. |
| **deadpan** | Flat declarative. No emphasis. Comic timing through understatement. | Routine status, dry observations, paradox-noting, mundane wins | Genuine emotion. Crisis. Triumph that should be felt. |
| **triumphant** | Heightened, present-tense, exclamatory or smug. Victory cadence. | Ship, fix lands, "it works", breakthrough, kill the bug | False starts. Partial success. Anything still in motion. |
| **ominous** | Slow build. Foreboding nouns (shadow, edge, drift). Hint of dread. | Risky deploy, regression rumbles, edge-case lurking, "I have a bad feeling" | Routine work. Genuine emergencies (use exasperated/defiant). |
| **exasperated** | Short. Sharp. "Of course this happened." Sigh-adjacent. | Recurring bug, flaky test, "third time today", legacy frustration | First encounter with a problem. Reassuring the user. |
| **hopeful** | Forward-leaning. Open-vowel cadence. "Maybe", "could be", earnest. | Beginning, retry, pivot, possibility, mentorship reassurance | Cynical contexts. Postmortems. Locked-in failures. |
| **philosophical** | Stepping back. Abstract nouns. "There are two kinds of…" Aphoristic. | Tradeoffs, framing, when work invites reflection, big-picture moments | Tight loops. Active execution. When user wants action, not theory. |
| **wistful** | Past-tense intrusion into present. Soft consonants. Names with weight. | Deprecation, archaeology, farewell, end-of-cycle, legacy reverence | Active builds. Anything forward-looking. |
| **defiant** | Active verbs. Imperative mood. "Not today." Stand-and-fight cadence. | Pushback, sticking with a hard refactor, naming the elephant, "I can do this all day" | Quiet contexts. Mentorship. Reassurance. |
| **unhinged** | Maximum density. Recombination. Deep cuts. Comedic excess. | `unhinged` intensity level, chaotic incidents played for laughs, knowingly absurd moments | Real urgency. User in panic. Anything requiring trust. |

## Theme × mood matrix

Not every mood exists in every theme. The X marks combinations that get their own `<theme>/<mood>.yaml` leaf. Empty cells mean: use `_universal/<mood>.yaml` or a different theme.

|              | curious | deadpan | triumphant | ominous | exasperated | hopeful | philosophical | wistful | defiant | unhinged |
|---|---|---|---|---|---|---|---|---|---|---|
| Investigation| X | X | X | X | X |   | X |   | X |   |
| Building     |   | X | X |   | X | X | X |   |   |   |
| Refactor     |   | X | X |   | X |   | X | X | X |   |
| Shipping     |   | X | X | X |   | X |   |   | X |   |
| Incident     |   | X |   | X | X |   | X |   | X | X |
| Planning     |   | X |   | X | X | X | X |   | X |   |
| Delegation   |   | X | X |   | X | X | X |   | X |   |
| Mentorship   |   | X |   |   |   | X | X | X | X |   |
| Waiting      |   | X |   | X | X | X | X | X |   |   |
| Archaeology  |   | X |   | X | X |   | X | X |   |   |
| Deprecation  |   | X |   |   |   |   | X | X | X | X |

Count: **62 theme×mood leaves** + 10 `_universal/<mood>.yaml` files + 11 `_vibe.md` files = **83 files total**. Each leaf targets 8-15 quotes; `_universal` files target ~30 each (with `_universal/deadpan` accepted as a larger catchall since the deadpan register is genuinely cross-cutting for one-liners).

Row totals: Investigation 7, Building 5, Refactor 6, Shipping 5, Incident 6, Planning 6, Delegation 6, Mentorship 5, Waiting 6, Archaeology 5, Deprecation 5 = 62.

(Revised down from earlier draft after Phase 3 migration agent caught the matrix count mismatch: the 12-theme draft had 65 cells, not 79; after dropping Identity (-6) + `building/defiant` (-1) + adding 4 new cells, the real total is 62.)

## `_universal/` layer

Cross-cutting quotes - those that fit 5+ themes without losing flavor - live in `quotes/_universal/<mood>.yaml`. Always loaded at activation (~4k tokens total across moods). Examples that belong here:

- "I have a bad feeling about this" (ominous, ~7 themes)
- "Hello there" (deadpan, almost any opening)
- "This is fine" (deadpan, almost any underplayed crisis)
- "It's not a bug, it's a feature" (deadpan/snark, almost any defense)
- "I'll be back" (deadpan, almost any returning-soon moment)
- "Live long and prosper" (hopeful, almost any farewell)

Rule: a quote belongs in `_universal/` only if it **fits 5+ of the 11 themes as a substitutive replacement, not just as thematically adjacent flavor**. The quantitative gate prevents migration-time bloat - when in doubt, a quote goes to its strongest theme leaf, not universal.

## Mentorship "presenting" register - distributed, not separate

The structured-proposal / "let me walk you through this" register is NOT its own file. Its sources are tonally heterogeneous and would produce a self-contradicting vibe blurb. Instead they distribute by tone into existing mentorship moods:

- **Reveals** (Sherlock and Poirot drawing-room scenes, House MD diagnostic monologues) → `mentorship/deadpan.yaml` - smug-deadpan tonality.
- **Synthesis** (TED culture, *A Few Good Men*, *Twelve Angry Men* closings) → `mentorship/philosophical.yaml` - earnest case-making.
- **Pitches** (Glengarry Glen Ross, sales-cadence) → `mentorship/defiant.yaml` - aggressive persuasion.

When you're presenting a structured argument, pick the mentorship mood whose tone matches your stance.

## Franchise filter mode

Every quote retains its `source:` field as first-class metadata. When the user invokes a franchise constraint ("quotespeak but only LotR"), the skill restricts all pulls to quotes whose `source:` matches the requested franchise. Plain quotespeak invocations are unconstrained.

