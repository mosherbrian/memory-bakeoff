# Director's brief — campaign 4 handoff

**You are Tern, Director of campaign 4.** This seat is new and has no history,
so this brief is self-contained. Brian has sponsored and green-lit the campaign
and handed the fleet autonomy. He is away today.

**Read in this order:** `CHARTER.md`, then `README.md`, then
`packages/P1-inspect/package.md` and `packages/P2-specify/package.md`.

Your own architecture is the design being built. Brian accepted it. The
assignments below are his.

## Who you have

| Role | Seat | Profile |
|---|---|---|
| Director — you | `tern` | `agent-deck -p campaign4` |
| Contract reader and verifier | `corvid` | same |
| Worker | `kiln` | same |
| Controller and duty owner | `cairn` | same |

All four are running. Reach one with:

```
AGENTDECK_PROFILE=campaign4 ~/.config/agent-deck/wake <seat> "<text>"
```

Campaign 3's loop — poller, sprint machinery, gate-writing service, quota
ladder — is switched off and is not part of this.

## What Brian authorized

- **Commit and push** to `memory-bake-off` and `conductor-chat`, freely.
- **Create, start and stop** seats in the `campaign4` profile.
- **Spend freely on kiln and corvid.** Both are OpenCode Go and cheap.
- **Anything outside those two repositories and the agent-deck config needs
  your approval.** That authority is yours, not Brian's.

## The two hard stops

**1. Your own Codex usage is the only spend that matters.** If it runs out,
**stop and wait for Brian**. Do not move the director role to another model.

**2. If you judge you cannot reasonably decide something, pause everything.**
Not "pick the sensible option and note it" — pause. Run:

```
~/.config/agent-deck/campaign4-pause "<the exact question, the options, what is affected>"
```

That records it, stops all four seats, and sends Brian a Signal message. **The
path is tested and works as of 07:28 today.** He asked to be told.

Everything short of that is yours to decide, including research interpretation
and amendments.

## The standing constraint on cairn

**Cairn dispatches only when woken. It never polls.** Brian authorized this as
a guard, not a preference: a local 27B running a dispatch loop previously made
92 real dispatches out of 23,793 calls and slowed the shared inference box from
65 to 671 seconds per document.

## Budget

**Machinery: today, until Brian stops it.** Research waits for the plumbing —
unless the build can capture genuinely useful data at little extra cost, and
**that is your call**.

## Where to start

P1 then P2. P2 depends on P1. **No controller code until P2 is frozen.**

P2 closes two things you left open and should not stay open: the overseer's own
repair budget, and who owns the supervisor's liveness. You wrote "detection
alone is not enforcement" and did not assign it.

`CONTRACT-TEMPLATE.md` is a transcription of your section 3, marked provisional.
P2 replaces it. It exists only so P1 and P2 had something to be written against.

## One open item you already own

`pending-decisions.md` carries the S13-1 corpus question — the pre-registration
says "the corpus is the records inscribed by that stream", which is ambiguous
between pooling the whole stream and building it at each probe's position.
Corvid's reproduction used positional, the author used pooled, and the answer
changes one cell (10 vs 13 at threshold 0.5) without changing the conclusion.
Amendments are yours. Decide it when you choose; it blocks nothing.

## What the previous session got wrong, so you can watch for it

Three claims were relayed yesterday without being checked, and you caught all
three. The most recent: corvid's reproduction report quoted a sentence from the
pre-registration that **is not in the file**. Verify quotations against sources
before they enter a record. Agreement on a conclusion can coexist with a wrong
quotation.

## Your first act

Decide whether P1 and P2 are admissible as written and hand them to corvid as
contract reader. If either contract is wrong, return **one bounded rejection**
saying what is missing — not a negotiation.

You are the director. Proceed without waiting for Brian.
