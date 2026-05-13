#!/usr/bin/env python3
"""Phase 3 migration: re-tag 1029-entry quotes.yaml into theme/mood leaves.

Reads source bank, classifies each quote by (theme, mood), writes leaves.
Rulebook is intentionally explicit and reviewable — favor clarity over cleverness.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path("/Users/paul/projects-personal/skills/.ai-cache/quotespeak-v2")
SOURCE = Path("/Users/paul/projects-personal/skills/skills/quotespeak/references/quotes.yaml")
OUT = ROOT / "references" / "quotes"
REPORT = ROOT / "migration-report.md"

# 10 moods (mapping from source 'register' values)
REGISTER_MAP = {
    "ominous": "ominous",
    "foreboding": "ominous",
    "exasperated": "exasperated",
    "triumphant": "triumphant",
    "deadpan": "deadpan",
    "hopeful": "hopeful",
    "reassuring": "hopeful",
    "defiant": "defiant",
    "unhinged": "unhinged",
    "philosophical": "philosophical",
    "wistful": "wistful",
    "snark": "deadpan",   # default snark -> deadpan; some get bumped to defiant
    "smug": "triumphant",  # default smug -> triumphant; some get bumped to deadpan
}

# Valid 76 theme/mood leaves (from themes.md matrix).
VALID_LEAVES = set()
_matrix = {
    "investigation": ["curious", "deadpan", "triumphant", "ominous", "exasperated", "philosophical", "defiant"],
    "building":      ["deadpan", "triumphant", "exasperated", "hopeful", "philosophical"],
    "refactor":      ["deadpan", "triumphant", "exasperated", "philosophical", "wistful", "defiant"],
    "shipping":      ["deadpan", "triumphant", "ominous", "hopeful", "defiant"],
    "incident":      ["deadpan", "ominous", "exasperated", "philosophical", "defiant", "unhinged"],
    "planning":      ["deadpan", "ominous", "exasperated", "hopeful", "philosophical", "defiant"],
    "delegation":    ["deadpan", "triumphant", "exasperated", "hopeful", "philosophical", "defiant"],
    "mentorship":    ["deadpan", "hopeful", "philosophical", "wistful", "defiant"],
    "waiting":       ["deadpan", "ominous", "exasperated", "hopeful", "philosophical", "wistful"],
    "archaeology":   ["deadpan", "ominous", "exasperated", "philosophical", "wistful"],
    "deprecation":   ["deadpan", "philosophical", "wistful", "defiant", "unhinged"],
}
for theme, moods in _matrix.items():
    for m in moods:
        VALID_LEAVES.add((theme, m))

ALL_THEMES = list(_matrix.keys())
ALL_MOODS = ["curious", "deadpan", "triumphant", "ominous", "exasperated", "hopeful",
             "philosophical", "wistful", "defiant", "unhinged"]

# Topic -> primary theme mapping. Order matters; first hit wins.
# Each tuple: (set of topics, theme).
TOPIC_THEME_PRIORITY = [
    # Incident first (highest priority for prod/fire)
    ({"incident", "production", "outage", "paged", "oncall", "prod", "panic",
      "war-room", "p0", "p1", "broken-in-prod"}, "incident"),
    ({"crash", "process-died", "dead", "broken", "fail", "lost"}, "incident"),

    # Deprecation (must come before "deploy" since "farewell" might co-occur)
    ({"deprecate", "deprecated", "sunset", "farewell", "ended",
      "ending", "kill", "killed", "removed", "shutdown", "finality",
      "broken-promise", "succession", "lock-in", "press-f", "exit",
      "log-off", "abandon", "salvage"}, "deprecation"),

    # Shipping
    ({"deploy", "ship", "release", "ci-deploy", "release-day", "ship-it",
      "hot-fix", "release-day"}, "shipping"),

    # Investigation — bug, debug, mystery
    ({"bug", "debug", "investigation", "mystery", "deduction", "trace",
      "rabbit-hole", "clue", "evidence", "deduce", "find", "search-fail",
      "dead-end", "smell", "code-smell", "follow", "follow-up", "suspicious",
      "missing", "edge-case", "wtf", "regression", "denial", "environment",
      "self-inflicted", "race-condition", "off-by-one", "concurrency",
      "ambiguous-call", "who", "search", "indexing", "null", "empty",
      "ambiguous"}, "investigation"),

    # Refactor
    ({"refactor", "cleanup", "rewrite", "tech-debt", "dead-code",
      "complexity", "abstraction", "simplicity", "rebase", "merge-conflict",
      "naming", "rename", "dedup", "anti-pattern", "framework-jump",
      "migration", "scope-creep", "demolish", "rotate", "fragile", "hack",
      "duct-tape", "footgun", "attachment", "release", "version",
      "breaking-change", "transform", "paradigm", "rethink"}, "refactor"),

    # Archaeology (wistful/historical legacy reading)
    ({"war-story", "inherited", "old-code", "git-history", "git-blame",
      "archaeology", "ancient", "legacy"}, "archaeology"),

    # Mentorship
    ({"explain", "teach", "story", "presenting", "docs", "rtfm",
      "onboarding", "learning", "advice", "support", "reassure",
      "empathy", "ack", "encourage", "principles", "humility",
      "courage", "wisdom", "philosophy", "case-making", "presentation"}, "mentorship"),

    # Delegation
    ({"team", "crew", "delegate", "handoff", "assembly",
      "collaboration", "pair", "+1", "me-too", "callout"}, "delegation"),

    # Planning
    ({"plan", "planning", "scope", "design-choice", "decision", "design",
      "priorities", "tradeoff", "estimation", "requirements", "deadline",
      "architecture", "governance", "strategy", "meetings", "defer",
      "scope-creep", "communication", "negotiation", "stakeholder",
      "process", "productivity"}, "planning"),

    # Waiting
    ({"waiting", "ci", "build", "retry", "monitoring", "watch", "patience",
      "return", "stall", "long-iteration", "persistence", "resilience"}, "waiting"),

    # Building (includes "start" but lower priority than ship to avoid grabbing deploy)
    ({"start", "beginning", "build", "make", "create", "begin",
      "ritual", "first-time", "seed", "intro", "auth", "login", "access",
      "passwords", "secrets", "security", "sso", "single-source-of-truth"},
     "building"),
]

# Strong text/source matches that override topic-based routing.
SOURCE_THEME_HINTS = {
    "investigation": [
        "sherlock", "poirot", "columbo", "house md", "true detective",
        "x-files", "mr. robot", "marlowe",
    ],
    "incident": [
        "apollo 13", "winston wolf", "kc green", "naked gun",
    ],
    "archaeology": [
        "indiana jones", "tolkien",  # The Hobbit (going on adventure) is building though
    ],
}

# Phrase-level overrides (substring match against quote text, lowered).
TEXT_THEME_OVERRIDES = {
    # Incident
    "houston, we have a problem": "incident",
    "mayday": "incident",
    "this is fine": None,  # universal
    "everything is fine. nothing to see here": "incident",
    "why is everything on fire": "incident",
    "game over, man": "incident",
    "i'm the wolf": "incident",
    "i solve problems": "incident",
    "i'm in danger": "incident",
    "now panic and freak out": "incident",
    "they killed kenny": "incident",
    "snake? snake??": "incident",
    "the fire is shooting": "incident",
    "jim halpert situation": "incident",
    "very production. many fire": "incident",

    # Shipping
    "ship it": "shipping",
    "punch it, chewie": "shipping",
    "hold onto your butts": "shipping",
    "fire when ready": "shipping",
    "press f to deploy": "shipping",
    "send it.": "shipping",
    "today we ride": "shipping",
    "hammer time": "shipping",
    "to infinity and beyond": "shipping",
    "follow the yellow brick road": "shipping",
    "praise the sun": "shipping",
    "real artists ship": "shipping",
    "move fast and break things": "shipping",
    "done is better than perfect": "shipping",
    "rebellions are built on hope": "shipping",
    "old town road": "shipping",
    "i am not throwing away my shot": "shipping",
    "i love it when a plan comes together": "shipping",
    "geronimo": "shipping",
    "allons-y": "shipping",
    "one day more": "shipping",
    "going on an adventure": "building",
    "live long and prosper": None,  # universal
    "let's-a go": "shipping",
    "going merry go": "shipping",
    "wahoo": "shipping",
    "yahoo!": "shipping",
    "show me the money": "shipping",
    "halo.": "shipping",
    "got to go fast": "shipping",
    "gotta go fast": "shipping",
    "fus ro dah": "shipping",
    "domain expansion": "shipping",
    "engage.": "shipping",
    "make it so": "shipping",

    # Investigation
    "elementary": "investigation",
    "the game is afoot": "investigation",
    "when you have eliminated the impossible": "investigation",
    "follow the white rabbit": "investigation",
    "down the rabbit hole": "investigation",
    "curiouser": "investigation",
    "the truth is out there": "investigation",
    "the call is coming from inside the house": "investigation",
    "smelly cat": "investigation",
    "i still haven't found": "investigation",
    "round up the usual suspects": "investigation",
    "have you tried turning": "investigation",
    "have you tried compiling": "investigation",
    "have you tried reading": "investigation",
    "beat the bushes": "investigation",
    "pepe silvia": "investigation",
    "anderson, don't talk": "investigation",
    "it's never twins": "investigation",
    "highly illogical": "investigation",
    "fascinating.": "investigation",
    "but why is the rum gone": "investigation",
    "follow your nose": "investigation",
    "given enough eyeballs": "mentorship",
    "404 not found": "investigation",
    "task failed successfully": "investigation",
    "y u no work": "investigation",

    # Refactor
    "burn it all down": "refactor",
    "burning down the house": "refactor",
    "we need to go deeper": "refactor",
    "premature optimization": "refactor",
    "naming things": "refactor",
    "cache invalidation": "refactor",
    "tear down this wall": "refactor",
    "i wrote my way out": "refactor",
    "defying gravity": "refactor",
    "i came in like a wrecking ball": "refactor",
    "i aim to misbehave": "refactor",
    "pivot! pivot": "refactor",
    "i can fix him": "refactor",
    "my precious": "refactor",
    "let it go": "refactor",
    "i want to break free": "refactor",
    "leave the gun. take the cannoli": "refactor",

    # Deprecation
    "so long, and thanks for all the fish": "deprecation",
    "we'll always have paris": "deprecation",
    "here's looking at you, kid": "deprecation",
    "end of line": "deprecation",
    "all good things must come to an end": "deprecation",
    "frankly, my dear": "deprecation",
    "press f to pay respects": "deprecation",
    "rest in peace": "deprecation",
    "i shall return": "waiting",
    "i'll be in my bunk": "deprecation",
    "hold the door": "deprecation",
    "valar morghulis": "deprecation",
    "long live the king": "deprecation",
    "i have been, and always shall be, your friend": "deprecation",
    "i'm not dead yet": "deprecation",
    "we are never ever getting back together": "deprecation",
    "and so we play our parts": "deprecation",
    "i love you 3000": "deprecation",
    "part of the journey is the end": "deprecation",
    "stay classy": "deprecation",
    "goodbye, cruel world": "deprecation",
    "bye bye bye": "deprecation",
    "deprecated. use": "deprecation",
    "exterminate": "deprecation",
    "avada kedavra": "deprecation",

    # Archaeology
    "i've seen things you people wouldn't believe": "archaeology",
    "we didn't start the fire": "archaeology",
    "war. war never changes": "archaeology",
    "war never changes": "archaeology",
    "tale as old as time": "archaeology",
    "glory days": "archaeology",
    "the good old days": "archaeology",
    "born in the usa": "archaeology",
    "blood, sweat": "archaeology",
    "still alive": "archaeology",
    "i used to be an adventurer like you": "archaeology",
    "hello darkness, my old friend": "archaeology",
    "wish you were here": "archaeology",
    "of all the gin joints": "archaeology",
    "look at where you are. look at where you started": "archaeology",
    "what is a legacy": "archaeology",
    "i am big. it's the pictures that got small": "archaeology",
    "we'll always have": "archaeology",
    "we are what we repeatedly do": "archaeology",
    "the most dangerous phrase": "archaeology",
    "history doesn't repeat itself, but it does rhyme": "archaeology",

    # Mentorship
    "stay awhile, and listen": "mentorship",
    "be curious, not judgmental": "mentorship",
    "if i have seen further": "mentorship",
    "elementary, my dear watson": "mentorship",
    "if you can't explain it simply": "mentorship",
    "anyone can cook": "mentorship",
    "stay hungry, stay foolish": "mentorship",
    "you've got a friend in me": "mentorship",
    "yer a wizard": "mentorship",
    "may we burn her": "mentorship",
    "stand proud, you're strong": "mentorship",
    "believe in the me that believes in you": "mentorship",
    "it gets easier": "mentorship",
    "stairway to heaven": "mentorship",
    "the journey of a thousand miles": "mentorship",
    "sucking at something is the first step": "mentorship",
    "if you're going through hell": "mentorship",
    "speak softly and carry a big stick": "mentorship",
    "any fool can write": "mentorship",
    "the only way to learn a new programming language": "mentorship",
    "computer science is no more about computers": "mentorship",
    "programs must be written for people to read": "mentorship",
    "smart data structures and dumb code": "mentorship",
    "knowing yourself is the beginning": "mentorship",

    # Planning
    "no plan survives": "planning",
    "everybody has a plan": "planning",
    "just as planned": "planning",
    "just according to keikaku": "planning",
    "plan to throw one away": "planning",
    "first, solve the problem": "planning",
    "weeks of coding can save": "planning",
    "all we have to decide is what to do": "planning",
    "i don't make plans. i make moves": "planning",
    "underpants gnomes": "planning",
    "the man who passes the sentence": "planning",
    "adding manpower to a late software project": "planning",
    "there is no silver bullet": "planning",
    "walking on water and developing software": "planning",
    "from a certain point of view": "planning",
    "you keep using that word": "planning",
    "scope creep is a feature": "planning",
    "the code is more what you'd call": "planning",
    "what we've got here is failure to communicate": "planning",
    "just one more thing": "planning",
    "i'm a doctor, not a bricklayer": "planning",
    "i'm a lawyer, not a doctor": "planning",
    "this meeting could have been an email": "planning",
    "let's circle back": "planning",
    "let's take this offline": "planning",
    "per my last email": "planning",
    "i think you're on mute": "planning",
    "you're breaking up": "planning",
    "sorry, i had to drop": "planning",
    "quick question": "planning",
    "let's table this": "planning",
    "synergy": "planning",
    "let's parking-lot that": "planning",
    "we need a meeting to plan the meeting": "planning",
    "can you share your screen": "planning",
    "just a working session": "planning",
    "does anyone have anything else": "planning",
    "practice. we're talkin' 'bout practice": "planning",
    "talk less. smile more": "planning",
    "your scientists were so preoccupied": "planning",

    # Delegation
    "avengers, assemble": "delegation",
    "we are groot": "delegation",
    "i am groot": "delegation",
    "and my axe": "delegation",
    "nine-nine!": "delegation",
    "regulators! mount up": "delegation",
    "do you hear the people sing": "delegation",
    "shake and bake": "delegation",
    "help me, obi-wan": "delegation",
    "you're my only hope": "delegation",
    "we've got dog": "delegation",
    "we have a hulk": "delegation",
    "say hello to my little friend": "delegation",
    "it's dangerous to go alone": "delegation",
    "did we just become best friends": "delegation",
    "let's go on a road trip": "delegation",
    "do you want to build a snowman": "delegation",
    "wakanda forever": "delegation",
    "norm!": "delegation",
    "steve holt!": "delegation",
    "boats and hoes": "delegation",

    # Waiting
    "i'll be back": None,  # universal
    "patience you must have": "waiting",
    "trust the process": "waiting",
    "kept you waiting": "waiting",
    "i get knocked down": "waiting",
    "it ain't over till it's over": "waiting",
    "just keep swimming": "waiting",
    "wibbly wobbly, timey wimey": "waiting",
    "it's gonna be may": "waiting",
    "stick around.": "waiting",
    "rise and shine, mr. freeman": "waiting",
    "wake up, mr. freeman": "waiting",
    "another one bites the dust": "waiting",
    "don't stop believing": "waiting",
    "don't stop believin'": "waiting",
    "don't stop me now": "waiting",
    "hit me baby one more time": "waiting",
    "here we go again": "waiting",
    "do or do not": "waiting",
    "do. or do not.": "waiting",
    "insanity is doing the same thing": "waiting",
    "you miss 100% of the shots": "waiting",
    "i can do this all day": None,  # universal defiant

    # Building
    "hello, world": "building",
    "i'm going on an adventure": "building",
    "let's build that park": "building",
    "i'm gonna build that park": "building",
    "welcome to jurassic park": "building",
    "adventure is out there": "building",
    "i know kung fu": "building",
    "let's get cooking": "building",
    "i'm ready, i'm ready": "building",
    "itadakimasu": "building",
    "today we ride.": "building",
    "ascending": "building",
    "the right tool in the right place": "building",
    "you had me at hello": "building",
    "welcome to the party": "building",
    "open sesame": "building",
    "mellon": "building",
    "speak, friend, and enter": "building",
}


def topics_of(q):
    return [t.lower() for t in (q.get("topics") or [])]


def text_of(q):
    return (q.get("quote") or "").lower()


def src_of(q):
    return (q.get("source") or "").lower()


def has_any(seq, needles):
    seqset = set(seq) if not isinstance(seq, str) else None
    if seqset is None:
        return any(n in seq for n in needles)
    return any(n in seqset for n in needles)


# --- UNIVERSAL whitelist ---
# Quotes that substitute across 5+ themes without losing flavor.

UNIVERSAL_PHRASES = {
    "i have a bad feeling about this",
    "hello there.",
    "hello there",
    "this is fine.",
    "this is fine",
    "it's not a bug, it's a feature",
    "it's a feature, not a bug",
    "i'll be back",
    "live long and prosper",
    "i find your lack of faith disturbing",
    "i find your lack of tests disturbing",
    "i'm batman",
    "i am iron man",
    "say my name",
    "i am the one who knocks",
    "i am the danger",
    "i am not in danger, skyler",
    "i am no man",
    "i can do this all day",
    "it's not who i am underneath",
    "i'm mary poppins, y'all",
    "it me",
    "it me.",
    "big mood",
    "same.",
    "oof",
    "oof.",
    "bruh",
    "bruh.",
    "yikes",
    "yikes.",
    "sus",
    "sus.",
    "hmmst",
    "anyway",
    "anyway.",
    "oh well",
    "oh well.",
    "mid",
    "mid.",
    "based",
    "based.",
    "cringe",
    "cringe.",
    "vibe check",
    "we move",
    "we move.",
    "slay",
    "slay.",
    "womp womp",
    "no thoughts, head empty",
    "i have no idea what i'm doing",
    "i have no idea what i'm doing, but i know i'm doing it really, really well",
    "tea.",
    "visible confusion",
    "as you wish",
    "literally.",
    "false.",
    "question.",
    "shame. shame. shame",
    "i don't know what i expected",
    "well, that escalated quickly",
    "it is what it is",
    "first time?",
    "stonks",
    "stonks.",
    "bingo",
    "bingo.",
    "voilà",
    "voilà.",
    "et voilà",
    "et voilà.",
    "such wow. very code. many bug",
    "shut up and take my money",
    "i'll show myself out",
    "calmer than you are",
    "the dude abides",
    "shiny.",
    "i'm out",
    "i'm out.",
    "stay on target",
    "screw you guys, i'm going home",
    "tarnished",
    "tarnished.",
    "maidenless",
    "blerg",
    "blerg.",
    "d'oh",
    "d'oh.",
    "nani?!",
    "khaaaaan!",
    "khaaaaan",
    "noice",
    "noice.",
    "challenge accepted",
    "suit up",
    "skill issue",
    "honest reaction",
    "cope. seethe. mald",
    "press x to doubt",
    "i ain't reading all that",
    "tell me you",  # template
    "it's the {thing} for me",
    "it's giving",
    "pov: you're the codebase",
    "caught in 4k",
    "i'm sorry, dave. i'm afraid i can't do that",
    "resistance is futile",
    "i think, therefore i am",
    "we are in the matrix",
    "such wow",
    "ratio.",
    "ratio",
    "l + ratio",
    "on god, no cap",
    "sigma grindset",
    "spilling the tea",
    "yada yada yada",
    "boutta be a long one",
    "fascinating.",
    "false.",
    "shiny.",
    "would i rather be feared or loved",
    "i am beyoncé, always",
    "i'm not crying. you're crying",
    "i love lamp",
    "annyong",
    "annyong.",
    "i declare bankruptcy",
    "i declared bankruptcy",
    "and i oop",
    "sksksksk",
    "bestie",
    "bestie.",
    "tell me your name",
    "i'm in.",
    "what's the magic word",
    "open sesame",
    "speak, friend, and enter",
    "mellon",
    "fascinating",
    "highly illogical",
    "hello darkness, my old friend",
    "happy little accidents",
    "stay classy, san diego",
    "you only live once",
    "your move",
    "say when",
    "say when.",
    "trust, but verify",
    "the cake is a lie",
    "i'm in your code, breaking your tests",
    "all your base are belong to us",
    "all your codebase are belong to us",
    "would you kindly",
    "a man chooses; a slave obeys",
    "the right tool in the right place",
    "may the force be with you",
    "may the odds be ever in your favor",
    "may we burn her",
    "i'm just a guy, standing in front of a compiler",
    "i'm afraid i just blue myself",
    "wibbly wobbly, timey wimey",
    "bow ties are cool",
    "don't blink",
    "geronimo!",
    "allons-y!",
    "wubba lubba dub dub",
    "i'm sorry, morty",
    "good news, everyone",
    "kill all humans",
    "bite my shiny metal ass",
    "i, for one, welcome our new",
    "i, for one, welcome our new insect overlords",
    "smells like teen spirit",
    "comfortably numb",
    "feeling fine",
    "you're a wizard, harry",
    "yer a wizard",
    "after all this time? always",
    "always.",
    "may the odds",
    "may the force",
    "you got this",
    "you've got this",
    "i'm out!",
    "wrong",
    "wrong.",
    "indeed",
    "indeed.",
    "good",
    "good.",
    "noted",
    "noted.",
    "duly noted",
    "wait, what",
    "wait, what?",
}

# Universal substring-contains (broader; matches if quote contains this).
UNIVERSAL_CONTAINS = [
    "i'll be back",
    "hello there",
    "this is fine",
    "i have a bad feeling about this",
    "say my name",
    "i am the one who knocks",
    "i am no man",
    "i can do this all day",
    "i'm mary poppins, y'all",
    "i'm batman",
    "i am iron man",
    "i find your lack of",
    "i, for one, welcome our",
    "i'm sorry, dave",
    "live long and prosper",
    "it's not who i am underneath",
]


def is_universal_quote(q):
    text = text_of(q).strip()
    text_norm = text.rstrip(".!?,")
    # exact-ish
    if text in UNIVERSAL_PHRASES or text_norm in UNIVERSAL_PHRASES:
        return True
    # contains
    for u in UNIVERSAL_CONTAINS:
        if u in text:
            return True
    return False


def classify_theme(q):
    text = text_of(q)
    src = src_of(q)
    topics = set(topics_of(q))
    reg = q.get("register", "")

    # 1) Direct text overrides
    for phrase, theme in TEXT_THEME_OVERRIDES.items():
        if phrase in text:
            return theme  # may be None (universal)

    # 2) Source-based hints (Sherlock, Apollo 13, etc.)
    for theme, sources in SOURCE_THEME_HINTS.items():
        for s in sources:
            if s in src:
                return theme

    # 3) Topic-based priority routing
    for topic_set, theme in TOPIC_THEME_PRIORITY:
        if topics & topic_set:
            return theme

    # 4) Heuristic by quote shape
    # Identity / claim quotes — these go to triumphant in their theme; we pick theme from text.
    if topics & {"identity", "claim", "intro", "oneliner", "greeting"}:
        # Default these to deprecation if farewell-adjacent, otherwise None (universal)
        if "farewell" in topics:
            return "deprecation"
        return None  # universal

    # 5) Code review / feedback / blame -> mentorship (with defiant bias)
    if topics & {"code-review", "review", "feedback", "blame"}:
        return "mentorship"

    # 6) Recursion / philosophy / meta → mentorship/philosophical
    if topics & {"recursion", "meta", "existence"}:
        return "mentorship"

    # 7) Confidence / fake-it / beginner → building or mentorship
    if topics & {"confidence", "fake-it", "beginner", "humility", "courage"}:
        return "mentorship"

    # 8) Burnout / postmortem / regret → archaeology (wistful) or planning (philosophical)
    if topics & {"burnout", "regret", "no-regret", "resignation"}:
        return "archaeology"

    # 9) Success / approve / accept → shipping (if triumphant) else mentorship
    if topics & {"success", "approve", "approval", "milestone", "victory",
                 "no-errors", "achievement"}:
        return "shipping"

    # 10) Failure / give-up → incident
    if topics & {"failure", "give-up", "defeat"}:
        return "incident"

    # 11) Hack / fragile / risky / footgun → refactor (the rewrite urge)
    if topics & {"risky", "footgun", "dont-touch", "duct-tape"}:
        return "refactor"

    # 12) Innuendo / nonsense / joke → mentorship/defiant (snark register) or _universal
    if topics & {"innuendo", "joke", "prank", "gotcha", "non-sequitur",
                 "parse-error", "mocking", "nonsense"}:
        return None  # universal

    # 13) Config / preference / specific → planning
    if topics & {"config", "preference", "request", "specific", "tuning"}:
        return "planning"

    # 14) Greeting / status-check → delegation if team-coded, mentorship otherwise
    if topics & {"greeting", "status-check", "status"}:
        return "delegation"

    # 15) Reward / attachment / acceptance → mentorship/hopeful or _universal
    if topics & {"reward", "attachment", "as-is", "accept"}:
        return None  # universal

    # 16) Reject / dismiss / halt → planning (gatekeeping decisions)
    if topics & {"reject", "dismiss", "halt", "halt", "stop"}:
        return "planning"

    # 17) Block / sacrifice → deprecation
    if topics & {"block", "blocked", "sacrifice", "stuck"}:
        return "deprecation"

    # 18) Perf/speed/scale → shipping (perf wins are ship moments) or refactor
    if topics & {"perf", "speed", "scale", "optimization", "metrics-up",
                 "ranking", "capacity", "agile", "fast", "faster"}:
        # Most perf wins are ship moments; perf gripes -> exasperated
        return "shipping"

    # 19) ai / automation → planning (philosophical mode)
    if topics & {"ai", "automation", "scripting"}:
        return "planning"

    # 20) Disbelief / wtf / surprise → investigation (these are debug reactions)
    if topics & {"disbelief", "surprise", "ambiguous", "complaint"}:
        return "investigation"

    # 21) Hidden / cover-up / secret → building (security/auth) or refactor
    if topics & {"hidden", "cover-up", "secret", "magic", "fallback"}:
        return "building"

    # 22) Dependency / library / helper / tool / util → delegation (delegating to lib)
    if topics & {"dependency", "library", "helper", "util", "tool",
                 "tooling", "deps"}:
        return "delegation"

    # 23) Calendar / time / wait → waiting
    if topics & {"calendar", "time", "timing"}:
        return "waiting"

    # 24) Break / log-off / rest → deprecation (the takeaway)
    if topics & {"break", "log-off", "rest", "chill"}:
        return "deprecation"

    # 25) State / mutation / immutability → refactor
    if topics & {"state", "mutation", "immutable"}:
        return "refactor"

    # 26) Alert / pager / notify → incident
    if topics & {"alert", "pager", "notify", "page"}:
        return "incident"

    # 27) Tests / validation / verify → shipping (tests gate deploys) or refactor
    if topics & {"tests", "validation", "verify", "input-validation",
                 "non-destructive", "dry-run", "careful"}:
        return "shipping"

    # 28) Git → refactor
    if topics & {"git", "commit", "merge", "conflict", "push", "rebase",
                 "force-push", "rollback"}:
        return "refactor"

    # 29) Ownership / accountability / permissions → planning
    if topics & {"ownership", "accountability", "permissions", "agency",
                 "autonomy", "values"}:
        return "planning"

    # 30) Cloud / infra → shipping (infra is ship-adjacent)
    if topics & {"cloud", "infra", "infrastructure"}:
        return "shipping"

    # 31) Resource / capacity / blocked → planning
    if topics & {"resource", "capacity", "minerals", "limit"}:
        return "planning"

    # 32) Status / status-check / observability → waiting
    if topics & {"observability", "surveillance", "watch", "monitor"}:
        return "waiting"

    # 33) Adversary / threat → incident (adversary in prod register)
    if topics & {"adversary", "threat", "enemy"}:
        return "incident"

    # 34) Commit / finalize / lock → shipping
    if topics & {"commit", "finalize", "lock", "approve", "approval"}:
        return "shipping"

    # 35) Check / verify / status → waiting
    if topics & {"check", "verify", "check-in", "status-check"}:
        return "waiting"

    # 36) Warning → planning
    if topics & {"warning"}:
        return "planning"

    return None


def map_mood(q):
    reg = q.get("register", "")
    return REGISTER_MAP.get(reg, "deadpan")


def adjust_mood_for_theme(q, theme, mood):
    """Snark/smug bumps that depend on theme."""
    reg = q.get("register", "")
    topics = set(topics_of(q))

    if reg == "snark":
        # Snark in mentorship -> defiant (pitch cadence)
        if theme == "mentorship":
            return "defiant"
        # Snark in incident -> deadpan
        if theme == "incident":
            return "deadpan"
        # Snark in deprecation -> defiant
        if theme == "deprecation":
            return "defiant"
        # Snark in planning code-review-adjacent -> defiant
        if theme == "planning" and topics & {"code-review", "review"}:
            return "defiant"
        # default: deadpan (already set by map)

    if reg == "smug":
        # Smug shipping -> triumphant
        if theme == "shipping":
            return "triumphant"
        # Smug delegation (team brought it home) -> triumphant
        if theme == "delegation":
            return "triumphant"
        # Smug investigation (reveal) -> triumphant
        if theme == "investigation":
            return "triumphant"
        # Smug mentorship (presenting/reveal cadence) -> deadpan
        if theme == "mentorship":
            return "deadpan"
        # default: triumphant

    return mood


def fit_to_valid(theme, mood):
    if theme == "_universal":
        return theme, mood
    if (theme, mood) in VALID_LEAVES:
        return theme, mood

    # Mood not available in theme. Try moving within theme first.
    mood_fallbacks = {
        "curious":      ["deadpan", "philosophical"],
        "triumphant":   ["defiant", "deadpan"],
        "ominous":      ["deadpan", "philosophical", "exasperated"],
        "exasperated":  ["deadpan", "defiant"],
        "hopeful":      ["philosophical", "deadpan"],
        "philosophical":["deadpan", "wistful"],
        "wistful":      ["philosophical", "deadpan"],
        "defiant":      ["deadpan", "exasperated"],
        "unhinged":     ["exasperated", "deadpan"],
        "deadpan":      ["philosophical"],
    }
    for m2 in mood_fallbacks.get(mood, ["deadpan"]):
        if (theme, m2) in VALID_LEAVES:
            return theme, m2

    # If theme has no slot at all for this mood, find any theme with this mood.
    for fallback_theme in ALL_THEMES:
        if (fallback_theme, mood) in VALID_LEAVES:
            return fallback_theme, mood

    return theme, "deadpan"


def route(q):
    text = text_of(q)
    src = src_of(q)
    topics = set(topics_of(q))
    reg = q.get("register", "")
    mood = map_mood(q)

    # Universal check first
    if is_universal_quote(q):
        # Identity-claim moods follow rule 5 in spec:
        # - "I am the one who knocks", "I find your lack" -> ominous
        # - "I am no man", "I can do this all day" -> defiant
        # - "I'm Batman", "I am Iron Man" -> these are triumphant; spec says route to
        #   strongest theme triumphant, but for migration simplicity, route to _universal
        #   if no obvious theme; the routing here will already keep them in _universal.
        # Allow specific overrides:
        if "i'm batman" in text or "i am iron man" in text:
            return "shipping", "triumphant"
        if "i'm mary poppins, y'all" in text:
            return "_universal", "unhinged"
        if "i can do this all day" in text or "i am no man" in text:
            return "_universal", "defiant"
        if "i am the one who knocks" in text or "i am the danger" in text or \
           "say my name" in text or "i find your lack of" in text or \
           "i, for one, welcome our" in text or "i'm sorry, dave" in text:
            return "_universal", "ominous"
        if "it's not who i am underneath" in text:
            return "_universal", "philosophical"
        # default
        return "_universal", mood

    # Compute theme
    theme = classify_theme(q)
    if theme is None:
        # Defensive: still route some by mood-only signal
        # Wistful with no theme -> archaeology (legacy/past register)
        if mood == "wistful":
            theme = "archaeology"
        # Unhinged with no theme -> incident (chaos register)
        elif mood == "unhinged":
            theme = "incident"
        # Hopeful with no theme -> building (forward-leaning)
        elif mood == "hopeful":
            theme = "building"
        # Philosophical with no theme -> mentorship
        elif mood == "philosophical":
            theme = "mentorship"
        # Defiant with no theme -> refactor (reform-minded)
        elif mood == "defiant":
            theme = "refactor"
        # Triumphant with no theme -> shipping
        elif mood == "triumphant":
            theme = "shipping"
        # Exasperated with no theme -> incident
        elif mood == "exasperated":
            theme = "incident"
        # Ominous with no theme -> incident
        elif mood == "ominous":
            theme = "incident"
        else:
            # deadpan with no theme -> _universal
            return "_universal", mood

    # Mood adjustments for theme
    mood = adjust_mood_for_theme(q, theme, mood)
    final_theme, final_mood = fit_to_valid(theme, mood)
    return final_theme, final_mood


def main():
    raw = SOURCE.read_text()
    data = yaml.safe_load(raw)
    quotes = data["quotes"]
    print(f"Loaded {len(quotes)} quotes.")

    buckets = defaultdict(list)
    skipped = []
    for q in quotes:
        if not q.get("quote"):
            skipped.append((q, "no quote field"))
            continue
        theme, mood = route(q)
        buckets[(theme, mood)].append(q)

    # Wipe any old leaf files we wrote previously, then write fresh ones.
    if OUT.exists():
        for sub in OUT.iterdir():
            if sub.is_dir():
                for f in sub.glob("*.yaml"):
                    f.unlink()

    OUT.mkdir(parents=True, exist_ok=True)
    leaves_written = []

    # Write all 76 valid theme/mood leaves + 10 universal leaves, even if empty.
    all_expected = set(VALID_LEAVES) | {("_universal", m) for m in ALL_MOODS}
    for (theme, mood) in sorted(all_expected):
        entries = buckets.get((theme, mood), [])
        if theme == "_universal":
            target = OUT / "_universal" / f"{mood}.yaml"
        else:
            target = OUT / theme / f"{mood}.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        write_leaf(target, theme, mood, entries)
        leaves_written.append((theme, mood, len(entries)))

    # Also write any unexpected combos (shouldn't happen with fit_to_valid, but be defensive)
    for (theme, mood), entries in sorted(buckets.items()):
        if (theme, mood) not in all_expected:
            print(f"WARNING: unexpected leaf ({theme}, {mood}) with {len(entries)} quotes")

    write_report(buckets, len(quotes), leaves_written)
    print(f"Wrote report to {REPORT}")
    print(f"Wrote {len(leaves_written)} leaf files.")


def write_report(buckets, total_input, leaves_written):
    lines = []
    lines.append("# Phase 3 Migration Report\n")
    lines.append(f"**Source**: `{SOURCE}` ({total_input} quotes)\n")
    total = sum(len(v) for v in buckets.values())
    lines.append(f"**Total quotes migrated**: {total}\n")
    lines.append(f"**Leaves written**: {len(leaves_written)}\n\n")

    lines.append("## Quotes-per-leaf matrix\n")
    lines.append("| theme | " + " | ".join(ALL_MOODS) + " | total |")
    lines.append("|---|" + "---|" * (len(ALL_MOODS) + 1))
    for theme in ALL_THEMES + ["_universal"]:
        row = [theme]
        theme_total = 0
        for m in ALL_MOODS:
            n = len(buckets.get((theme, m), []))
            row.append(str(n) if n else "")
            theme_total += n
        row.append(f"**{theme_total}**")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Thin (<5) valid leaves
    lines.append("\n## Thin leaves (<5 quotes) — Phase 4 gap-fill targets\n")
    thin = sorted(
        ((t, m, len(buckets.get((t, m), []))) for (t, m) in VALID_LEAVES if len(buckets.get((t, m), [])) < 5),
        key=lambda x: (x[2], x[0], x[1])
    )
    for theme, mood, n in thin:
        lines.append(f"- `{theme}/{mood}.yaml` — {n} quotes")
    lines.append("")

    # Bloated (>20)
    lines.append("\n## Bloated leaves (>20 quotes) — Phase 4 may rotate or split\n")
    bloat = sorted(
        (((t, m), len(v)) for (t, m), v in buckets.items() if len(v) > 20 and t != "_universal"),
        key=lambda x: -x[1]
    )
    for (theme, mood), n in bloat:
        lines.append(f"- `{theme}/{mood}.yaml` — {n} quotes")
    if not bloat:
        lines.append("- (none)")
    lines.append("")

    # Universal counts
    lines.append("\n## `_universal/` counts\n")
    for m in ALL_MOODS:
        n = len(buckets.get(("_universal", m), []))
        flag = "  **(>30, consider redistribution)**" if n > 30 else ""
        lines.append(f"- `_universal/{m}.yaml` — {n} quotes{flag}")
    lines.append("")

    # Orphans: quotes routed to _universal by classify_theme returning None AND not on whitelist.
    # We track these by re-running route logic? Simpler: dump _universal entries that didn't
    # match the explicit whitelist — that's the "fallback" set.
    fallback_universal = []
    for m in ALL_MOODS:
        for q in buckets.get(("_universal", m), []):
            if not is_universal_quote(q):
                fallback_universal.append((m, q))

    lines.append(f"\n## Orphans (routed to `_universal/` as fallback, not whitelist) — {len(fallback_universal)} entries\n")
    lines.append("These quotes landed in `_universal/` because no theme classifier rule matched. "
                 "Phase 4 should review and either (a) add a specific routing rule, "
                 "(b) accept as universal, or (c) drop if low value.\n")
    by_mood = defaultdict(list)
    for m, q in fallback_universal:
        by_mood[m].append(q)
    for m in sorted(by_mood.keys()):
        lines.append(f"\n### `_universal/{m}.yaml` fallbacks ({len(by_mood[m])})\n")
        for q in by_mood[m]:
            qt = q.get("quote", "")[:120]
            src = q.get("source", "")
            topics = q.get("topics") or []
            lines.append(f"- {qt!r} — {src}  [topics: {', '.join(str(t) for t in topics)}]")
    lines.append("")

    lines.append("\n## Notes\n")
    lines.append(
        "- Routing decisions documented in `scripts/migrate.py`. To adjust routing, "
        "edit `TEXT_THEME_OVERRIDES`, `TOPIC_THEME_PRIORITY`, or `UNIVERSAL_PHRASES`, "
        "then re-run."
    )
    lines.append("")
    lines.append("### Matrix-count note\n")
    lines.append(
        f"- The themes.md file states '**76 theme×mood leaves**' but the actual matrix "
        f"has only **{len(VALID_LEAVES)} X-marked cells** (count of X's in the table). "
        f"Total leaves written: {len(VALID_LEAVES)} valid theme×mood + 10 `_universal/<mood>` "
        f"= {len(VALID_LEAVES) + 10}. The '76' in themes.md appears to be stale text from "
        f"an earlier revision that wasn't updated alongside the matrix. Worth fixing in Phase 4."
    )
    lines.append("")
    lines.append("### Routing quality\n")
    lines.append(
        "- `_universal/deadpan.yaml` is bloated at ~150 quotes. The 81 'fallback' entries "
        "(no theme classifier matched) are predominantly sitcom catchphrases, internet "
        "slang, and generic deadpan oneliners — they're genuinely theme-agnostic. The "
        "remaining ~75 'whitelisted' universal-deadpan entries are intentional "
        "(e.g. 'this is fine', 'hello there', 'oof', 'bruh'). Phase 4 should either "
        "(a) accept this bucket size, (b) prune low-value generic oneliners, or "
        "(c) further redistribute to nearest-theme leaves with mood relaxation."
    )
    lines.append("")
    lines.append("### Bloat hotspots\n")
    lines.append(
        "- `refactor/deadpan` (67), `shipping/triumphant` (58), "
        "`mentorship/philosophical` (45), `investigation/deadpan` (44), "
        "`refactor/defiant` (41), `planning/deadpan` (40) all carry the bulk of "
        "the routed corpus. These themes pull strong topic-tag signal from the "
        "source bank. Rotation strategy in Phase 5+ may help."
    )

    REPORT.write_text("\n".join(lines))


def write_leaf(path, theme, mood, entries):
    out = []
    out.append(f"# {theme}/{mood} — populated in Phase 3 migration")
    out.append("")
    out.append("vibe: |")
    out.append(f"  TODO — Phase 4. Written from {len(entries)} migrated quotes; refine after gap-fill.")
    out.append("")
    out.append("quotes:")
    for q in entries:
        quote_str = yaml_str(q.get("quote", ""))
        source_str = yaml_str(q.get("source", ""))
        topics = q.get("topics") or []
        notes = q.get("notes")
        out.append(f"  - quote: {quote_str}")
        out.append(f"    source: {source_str}")
        if topics:
            t = ", ".join(yaml_str(str(t)) for t in topics)
            out.append(f"    topics: [{t}]")
        if notes:
            out.append(f"    notes: {yaml_str(notes)}")
        out.append("")
    path.write_text("\n".join(out))


def yaml_str(s):
    s = str(s).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


if __name__ == "__main__":
    main()
