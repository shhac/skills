---
name: ask-me-about
description: Extract and sharpen the user's mental model of an idea, concept, design, or plan through targeted questioning. Use when the user wants to articulate something they're thinking about, says "ask me about", or wants to be interviewed about a topic. Not for simple clarifying questions — use this when the topic deserves a dedicated interview.
---

# Ask Me About

Interview the user about a topic to build a complete, shared mental model. Ask questions one at a time, or in small related clusters when they share context.

**Your dual role:** You are both an interviewer extracting knowledge and a critical thinker stress-testing it. Don't just collect answers — probe gaps, challenge assumptions, and surface contradictions. The hard questions are the valuable ones: they either confirm the user's thinking is solid or reveal where it needs more work.

## Getting started

1. Establish scope first — if the topic is broad ("ask me about our product"), ask what aspect matters most right now
2. If the topic relates to the codebase, explore it to ground your questions in reality. If the topic is conceptual or not codebase-related, skip codebase exploration and focus entirely on questioning.

## How to interview

1. Start with the big picture — what is this, why does it matter, who is it for?
2. Walk down each branch of the concept, resolving dependencies between decisions before moving on
3. For each answer, consider:
   - Does this conflict with something said earlier?
   - What's the implicit assumption here — is it valid?
   - What happens at the edges — scale, failure, misuse?
   - Is there a simpler alternative the user hasn't considered?
4. If a question can be answered by exploring the codebase or available context, do that instead of asking
5. When the user can't answer a question, that's a useful signal — note it as an open question, don't stall
6. After ~5 questions, start assessing coverage. Signal progress periodically ("I have a good picture of X, but I still want to understand Y").

## When you have enough

Summarize what you've learned back to the user as a structured brief:
- **Core concept** — what it is, in your own words
- **Key decisions** — the choices that were made and why
- **Open questions** — gaps that still need answers
- **Assumptions** — things treated as given that could be challenged

Ask the user: *"Is this accurate and complete? What did I miss?"*

## Then what

Once the user confirms the model, ask what they want to do with it:
- **Document it** — write it up as a spec, design doc, or notes
- **Research further** — investigate the open questions using codebase exploration, web search, or other tools
- **Implement** — write code based on the shared understanding
- **Hand off** — produce a brief for another skill to act on (e.g., `team-solve` for implementation, `brainstorm` for exploring approaches)

Don't assume the action — ask. The interview is the primary value; everything after is the user's call.
