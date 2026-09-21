# Campaign 4

**Read `CHARTER.md` first.** It records what Brian authorized, to whom, and
where it stops.

## How this works

A **work package** is the unit. It carries a contract, runs through a bounded
lifecycle, and ends in a terminal state. Finishing one does **not** authorize
starting another — that is the whole point of the design.

```
packages/<id>/package.md     the contract
packages/<id>/...            everything that package produced
pending-decisions.md         work that stopped because nobody could decide it
CONTRACT-TEMPLATE.md         provisional; P2 replaces it
```

## Roles

**tern** directs and decides · **corvid** reads contracts and verifies ·
**kiln** works · **cairn** controls and holds duty · **Brian** sponsors.

Worker and verifier never coincide. Whoever repairs a contract cannot certify
that repair.

Seats live in their own profile: `agent-deck -p campaign4 list`.

## The two rules that matter most

1. **Cairn dispatches only when woken. It never polls.**
2. **If Tern cannot reasonably decide something, everything pauses**, the
   question goes in `pending-decisions.md`, and Brian is notified. Nobody
   guesses.

## Where it starts

`P1-inspect` then `P2-specify`. P2 depends on P1. No controller code is written
until P2 is frozen.

## What is NOT here

Campaign 3's loop — poller, sprint machinery, gate-writing service, quota
ladder — is switched off and is not part of this. The research track (the cairn
memory pilot) waits for the plumbing unless Tern judges the build can capture
useful data cheaply along the way.
