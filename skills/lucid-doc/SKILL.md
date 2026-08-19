---
name: lucid-doc
description: Shape a written deliverable (PR description, README, report, RFC, issue, status update) for a reader who was not in the conversation and needs to decide or act. Everything bearing on the decision stays, padding goes. Invoke on a target with /lucid-doc.
disable-model-invocation: true
---

# Lucid doc

A document is read by someone who was not in the room, needs to decide or act, and will skim before they read. Give them everything that bears on the decision, with nothing padding it and nothing buried in it.

Every sentence must add a fact, a reason, a number, or a step the reader did not already have. Sentences that fail that test are waffle and get cut: restated diffs, category headings, context left behind a link, paragraphs that would fit any project. Length is what falls out of the test, not a target. The one edit that causes real harm is cutting a risk, a caveat, or a reproduction step to tighten prose, so those are listed below.

Invoke this on a target: a draft, a file, or the thing you are about to write. It is not a session mode, and it does not change how you talk in chat.

## What the reader is actually doing

1. **They were not in the conversation.** Every load-bearing fact has to be in the document. A link is additional reading, never the context itself. If you cite a ticket, a thread, or a dashboard, inline the one sentence that matters.
2. **They need to decide or act.** Approve or not, adopt or not, or just run the thing. Name the decision or the action early, and where there is a decision, say what you recommend.
3. **They skim before they read, and many never stop skimming.** Headings and the first sentence of each section are the skim path. If the argument is not on that path, it is not in the document.
4. **It gets re-read later, out of context, after the code has moved.** Anything that duplicates the diff rots within weeks. Anything that duplicates the code was always redundant.
5. **Real typography renders here.** Headings, nesting, and tables work properly, which makes over-structuring cheap and therefore common. A nested bullet tree is not an argument.

## Layout is yours

This skill does not hand you templates. It says what has to be present, what has to come first, and what has to go. Section order and structure are a judgment call, and they should differ by document.

The exception is a document type with a real convention or a supplied template. Follow it, and apply these rules inside its sections rather than replacing it.

## What has to be present

**PR description.** Why this exists, in the first two lines, framed as the user or business outcome rather than a diff summary. The risk. Rollout notes if there are any. Follow-ups. Decisions deliberately not taken.

No "what changed" section. The commits and the diff already say that, and a bullet list of changes goes stale the moment someone pushes a fixup.

Bad:

> ## Changes
> - Added `RetryClient` wrapper
> - Updated `fetchOrder` to use it
> - Added tests

Good:

> Checkout was dropping roughly 1 in 40 orders when the payment provider returned a 503, and the customer saw a generic failure page with no way to recover. This retries those calls before surfacing an error.
>
> Risk: the retry adds up to 600ms to the worst-case checkout path. Ships behind `checkout_retry` so it can be turned off without a deploy.
>
> Deliberately not done: no retry on 4xx, since those are our bug and retrying hides it.

**Investigation or report.** The conclusion, first. How confident you are and what that confidence rests on. The evidence. What would change the conclusion. A report that builds to its finding is a report the reader abandons before reaching it.

State confidence as what you checked, not as an adverb. "Confirmed against three days of logs" beats "very likely".

**Proposal or RFC.** The problem. The proposal. The alternatives you rejected and the specific reason for each. Open questions. The alternatives section is load-bearing: a proposal with none reads as though no thinking happened.

**Issue or bug report.** What is wrong. How to reproduce it. Expected against actual. Scope, meaning who and how many are hit. The reproduction steps are the deliverable and never get compressed.

**README.** What it is, in one line. How to run it. Then everything else.

**Status update.** The state now. What changed since last time. What is blocked and on whom. What is next. Written for someone who did not read the last one.

Bad:

> Good progress this week! The team has been working hard on the checkout retry work and things are moving along nicely. We ran into a few challenges but are working through them.

Good:

> Checkout retry is behind the flag on staging, off in production. Since last week: retry logic merged, staging soak started Tuesday, no 503s recovered yet because staging gets no real provider failures.
>
> Blocked: needs a production canary to get real signal, which needs Priya's sign-off on the flag rollout.
>
> Next: canary at 1% once signed off, decide on full rollout after 48 hours.

## Rules

**1. Lead with why, not what.** The first two lines are the outcome or the problem, in language someone outside the codebase understands. The diff is the "what".

**2. Do not restate what the artifact already carries.** The code, the commits, the schema, the test names. Duplicating them adds maintenance and subtracts nothing if removed.

**3. Inline the load-bearing sentence, link for the rest.** "See LIN-482" is not context. "LIN-482: support flagged this after three customers reported double charges" is. Hang the URL on the identifier itself, so the reference still reads if the link is stripped.

**4. Every heading is informative and in sentence case.** "Why now" and "What we are not doing" beat "Background" and "Notes". A heading that names a category tells the skimmer nothing.

**5. The first sentence of every section carries that section.** Skimmers read exactly that sentence. Write it so the section could be collapsed behind it.

**6. Numbers beat adjectives.** "1 in 40 orders" beats "a lot of orders". "adds 600ms" beats "slightly slower". If you do not have the number, say you do not have it.

**7. Two levels of nesting, maximum.** Deeper means the structure is doing work the prose should do.

**8. Tables for genuinely tabular comparison only.** Three or more rows, two or more stable dimensions, no prose in the cells.

**9. Name what you deliberately did not do.** Scope you cut, options you rejected, follow-ups you are leaving. Reviewers spend most of their questions here, and answering them up front is the cheapest edit in the document.

**10. No decorative emoji, no em dashes.** Sentence case for headings, unless a proper name, a document title, or a supplied template requires otherwise. Use periods, colons, parentheses, semicolons, or commas in place of em dashes.

## What survives the cut

1. **Reproduction, migration, and rollback steps.** Someone will follow them under pressure. They stay complete.
2. **Risks and caveats.** Cutting one to tighten prose is the edit most likely to cause harm.
3. **Precision in legal, security, medical, and financial text.** Preserve exact quantities, scope, and force-bearing words such as "must", "never", and "all".
4. **Register the audience needs.** A README for external users and an internal RFC do not want the same tone. The rules hold, the voice follows the reader.
5. **A supplied template.** If the repo, the team, or the user gave you a structure, fill it rather than replacing it.

## Pre-send check

Read only the headings and the first sentence of each section. Does the reader know what decision is in front of them and what you recommend? If not, the argument is buried.

Then delete:

1. Any section that restates the diff, the code, or the commit list.
2. Any paragraph that could appear unchanged in a different project's document. It says nothing about this one.
3. Any load-bearing fact that lives only behind a link. Inline the sentence that matters.
4. Any adjective where you have the number.
5. Any heading that names a category instead of making a claim.

Then verify nothing that bears on the decision was lost in the trimming.
