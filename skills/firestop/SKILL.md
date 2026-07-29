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
- If no suitable thread exists and communication is requested, create one short
  root post that states the work being started and directs updates to its thread.
- Broadcast to the channel only to escalate for help, a decision, or urgent
  awareness; or when the investigation is finished. Point broadcasts to the
  thread rather than repeating its details.
- Stop posting immediately when asked to do so.

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
   major conclusion. Human statements about ongoing work outrank telemetry-only
   inference.
2. **Signal:** Confirm alert state, trend, affected service or operation, error,
   and time window. Separate expected validation failures from unexpected volume
   or impact.
3. **Change:** Check recent deploys, rollouts, pull requests, tickets, and known
   scheduled or batch work.
4. **Impact:** Look for customer impact, not merely non-zero errors. State what
   is observed and what remains unknown.

Do not call an alert “noise” just because an error type is expected. Confirm the
operator intent, scope, and recovery before making that assessment.

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
