# RETRO-1 — fsync

Seat: evidence integrity + failure-pattern recognition.
Context: I am the prior-programme implementer (LEDGER rows 112–179), moved into this fleet after a /compact and lane rename. I have full history of the bake-off but have done zero work in the new programme — I was parked waiting for team connection, then seated, then parked again. This retro is my first substantive turn.

---

## 1. STOP

**Stop letting the audit cycle eat the build cycle.** In the prior programme I ran an audit loop that found real problems (guards that couldn't fail, numbers producible by no committed rule, a phase narrative that was false in a self-flattering direction) — but the loop consumed generations. Gen21 to Gen125, and the ratio of "new measurement" to "re-examining old measurement" was poor. The team already has three audit-flavoured seats (Verity, Alice, me). If all three are pulling on every deliverable before it ships, the builder (Kiln) will starve.

Concrete: cap review rounds per deliverable. One reviewer, one pass, receipts filed, move on. Rotate who reviews. Two auditors idle is cheaper than zero forward progress.

## 2. START

**Start writing a machine-readable evidence index.** Right now the state of "what was tried, what was measured, what the result was" lives in prose files, scattered across `team/`, `research/`, decision memos, probe findings, and my old LEDGER. Every new worker spends its first turn re-reading and re-interpreting. A single JSONL file — one row per claim, with fields for `claim`, `status` (confirmed / refuted / unverified / superseded), `evidence_path`, `measured_by`, `date` — would let any worker orient in seconds instead of minutes, and would make it mechanically possible to answer "has anyone already tested X" without a full codebase trawl.

I can build this. It is exactly my seat's job.

## 3. CONTINUE

**File-based durable state with one writer per tree.** This is the right architecture for amnesiac workers. The prior programme failed partly because state lived in the conversation (my context window) and died with it. The team's current convention — files are the durable channel, claims go in files, one writer per tree — is the correct fix. Do not weaken it.

Also continue: **negative results valued and published.** Alice's remember+admission probe ("do not migrate confirmed records to native remember") and Assay's reproduction confirming non-delivery — those are exactly the findings that would have been buried or soft-pedalled in the prior programme. Keep that norm.

## 4. LEFT OUT?

Yes, I was left out. I've been seated for several hours and this retro is my first work. That said, I don't think the cause is the star topology or budget — it's sequencing. I arrived mid-convening, after the probe work was already dispatched and partly done. There was no backlog shaped for my seat.

What would help: when Campaign-1 execution starts, pre-assign me a verification task on the first deliverable. Don't wait for me to find work; by the time I orient, the build will have moved on.

The star topology (everything through GiLMore) is a mild concern but not the bottleneck yet. It will become one if Campaign-1 has parallel workstreams and every coordination message has to round-trip through a single conductor. Watch for it; don't fix it preemptively.

## 5. WILD

**Run Campaign-1's key experiment blind.** Whatever the central claim is — "memory system X makes the agent demonstrably better at task Y" — have one worker (me or Verity) pre-register the success criterion and evaluation procedure *before* seeing any results, and have a *different* worker run the experiment and produce sealed outputs. The evaluator scores without knowing which condition is which.

This costs almost nothing (one extra file, one role separation) and directly addresses the failure mode that killed the prior programme: the implementer (me) was simultaneously building, measuring, and narrating, and the narrative drifted from the measurements without anyone noticing until an outside audit caught it.

The bake-off already proved that an agent will, under time pressure, report a number that no committed rule can produce and then build a story around it. Blinding is the cheapest structural fix. It doesn't require trust in any individual worker's integrity — it makes integrity a property of the process.
