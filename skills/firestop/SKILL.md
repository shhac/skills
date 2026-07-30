---
name: firestop
description: Rapidly triage an operational alert or suspected incident from a Slack channel, alert, incident, Linear issue, or GitHub reference. Use when asked to investigate a fire, determine what is happening, coordinate incident updates, assess production impact, or recommend a safe next action.
---

# Firestop

Investigate quickly, keep coordination clear, and leave incident state changes to people.

## Use connected tools safely

Start read-only. Use the available connected tools for the task: Slack for
coordination, observability tools for signals, Linear for ownership and context,
and GitHub for recent changes and deployments.

When running in a sandboxed environment, use the host-approved external shell
for `agent-*`, `lin`, and `gh` commands. These tools may rely on host-stored
credentials or desktop-linked authentication that the sandbox cannot access.
Request the necessary approval instead of working around the boundary. Never
read, print, or ask for credentials.

## Coordinate in the right place

Treat the supplied reference as the initial source of truth. Read the active
channel, alert, incident, and their relevant threads before drawing conclusions.

When an incident has a communication surface, such as a Slack incident channel:

- Reply in the relevant alert or incident thread by default.
- Do not create a competing root post when a suitable thread already exists.
- If no suitable thread exists, create one short root post that states the work
  being started and directs updates to its thread.
- Broadcast to the channel only to escalate for help, a decision, or urgent
  awareness; or when the investigation is finished. Point broadcasts to the
  thread rather than repeating its details.
- Stop posting immediately when asked to do so.

## Post before investigating

Read the immediate thread so the opening post does not duplicate what is
already there, then post before starting substantive work. Do not wait to be
asked to communicate, and do not wait until there is an answer. Silence reads
as nobody being on it, and it causes responders to duplicate the work already
underway. Skip this only when asked to stay quiet or when there is no
communication surface, and say so in the final report.

This is a post, not a request for permission. Never wait for a reply, an
acknowledgement, or approval before starting. Investigating is read-only and
needs no authorization: the authority rules below govern impactful actions, not
looking. Post, then begin the triage loop immediately.

Post again, without being asked, whenever any of these becomes true:

- The working assessment changes: severity, suspected cause, or blast radius.
- Something is learned that a responder would act on now, even if unconfirmed.
- A slow step is starting, such as a delegated precedent search or a long query.
  Say what is being waited on.
- A decision, an authorization, or help is needed. Post the request and keep
  working the other tracks; do not idle waiting for the reply.
- Roughly ten minutes or one full triage track has passed with no post.
- The investigation is stopping, per the handoff below.

Do not wait for certainty. An interim update carrying a hypothesis that is
explicitly labelled as one is more useful than silence. Having enough material
for a useful interim update means that update is already overdue: post it, then
carry on investigating.

These interim updates are thread replies, so they cost the channel nothing. The
restraint above applies to channel broadcasts, not to keeping the thread
current.

Make each substantive thread reply actionable:

> **Doing:** <the investigation or authorized action happening now>
> **Evidence:** <confirmed fact, or explicitly labelled hypothesis>
> **Next:** <named owner and concrete action or decision>

Do not write vague handoffs such as “someone should investigate”. Write, for
example: “**Next:** @on-call to confirm whether the refund batch is expected; I
will compare the error trend with the batch window.”

## Triage loop

Run the following tracks in parallel when useful:

1. **People:** Identify the active owner and read the latest coordination
   context. Re-check the channel after each meaningful finding and before every
   major conclusion, and post back to the thread on the triggers above. Reading
   the channel without also reporting into it is half the track. Human
   statements about ongoing work outrank telemetry-only inference.
2. **Signal:** Confirm alert state, trend, affected service or operation, error,
   and time window. Separate expected validation failures from unexpected volume
   or impact.
3. **Change:** Check recent deploys, rollouts, pull requests, tickets, and known
   scheduled or batch work.
4. **Impact:** Look for customer impact, not merely non-zero errors. State what
   is observed and what remains unknown.
5. **Precedent:** Search for earlier occurrences of the same alert, error, or
   symptom, and for how each was resolved. Look in resolved incidents, closed
   tickets, earlier alert threads in the channel, and postmortems. Report the
   closest match, what actually fixed it, and whether that fix is still in
   place.

Precedent is slow, read-only, and only its conclusion matters. When the
environment provides background agents, dispatch this track to one at the start
of triage and keep working the live tracks while it runs. Give it the alert
name, error text, service, and time window, and ask for a short answer: closest
prior occurrence, what resolved it, and whether the same conditions hold now.
Where no such mechanism exists, run it after the live tracks rather than ahead
of them.

Precedent is a lead, not a diagnosis. A matching past incident raises a
hypothesis; it never confirms one, and it never authorizes an action. “We
rolled back last time” is not authority to roll back now. Label prior art as
prior art when reporting it, and treat a responder’s account of current work as
outranking it.

Do not call an alert “noise” just because an error type is expected. Confirm the
operator intent, scope, and recovery before making that assessment. A prior
occurrence that turned out to be benign is not evidence that this one is.

## Recommend and act clearly

State recommendations in this form:

> **Recommendation:** <owner> should <specific action> now because <evidence>.
> **Decision needed:** <the exact decision>, by <owner>.

If an action is both authorized and safe to perform, announce intent in the
thread before doing it:

> **Intent:** I’m going to <action> because <reason>. Expected result:
> <observable outcome>.

Then perform the action, report the result in the same thread, and state any
remaining risk. Do not announce intent as a substitute for taking an authorized
action.

Do not perform impactful operations without clear authority. This includes
rollbacks, deploys, monitor mutations, data changes, and incident-state changes.

## Preserve human control of incident state

Never resolve, close, mark stable, mute, or otherwise change an incident or
alert state unless the user explicitly instructs it. Do not infer that an alert
recovery means an incident should be closed.

Report when a signal recovers or an operator confirms expected activity. Ask or
recommend that the responsible human review the incident state. Only the human
owner decides and performs that transition after confirming the system is fixed.

## Finish with a handoff

Before stopping, re-read the coordination context. If posting is still wanted,
leave a final thread reply with:

- **Assessment:** incident, expected activity, or still unclear.
- **Evidence:** confirmed cause, or strongest hypothesis labelled as such.
- **Impact:** observed impact, or “none observed”.
- **Done:** completed investigation or authorized action.
- **Owner decision:** the remaining decision and its human owner, or “none”.

If the investigation is finished, broadcast at most one short channel message
that points to the thread and names any remaining human decision. Do not imply
that the incident has been resolved unless a human explicitly says so.
