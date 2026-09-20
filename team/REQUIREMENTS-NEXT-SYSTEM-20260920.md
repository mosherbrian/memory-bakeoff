# What the next system has to do — capabilities, not files

Brian, 2026-09-20: *"I was thinking more conceptually, as in requirements for a
new system. Ex: a director role, fleet memory in files not context, a research
pipeline, a good web UI, a sprint status board that shows the state of the
fleet for observability, and so on."*

Written as requirements. Each one says what it must do, and what we learned
that makes it a requirement rather than a preference. Some of these we already
have and should not lose; some we have badly; some we have never had.

---

## A. The work

### A1. A director that holds the research question
Someone must be able to answer, on demand: what do we know, what would change
it, what is next, and why is the current work serving that. Not a row-picker —
a synthesis that cites evidence and can say "no new evidence" or "this backlog
would not move the open questions."

*Why:* without it the fleet optimises for closing rows. We added this late
(Tern) and the first thing it produced was the first fleet output Brian said he
could actually read.

### A2. A research pipeline with provenance
Question → experiment → evidence → answer, where every answer can name the
frozen inputs it rests on: dataset hash, prompt version, parser version, seeds,
the exact tool build.

*Why:* today a question sweep ran against a label file that was being rewritten
underneath it. Without pinned inputs the result described a set that no longer
existed. Provenance is not bookkeeping; it is the difference between a result
and a number.

### A3. Work admission: every item declares how it will be judged
An item may enter only with an artifact path **and** a runnable check, or an
explicit "a human will read this." Anything else can only be closed on trust.

*Why:* the whole loop is only as good as the weakest row. This is the rule that
makes every other mechanism possible.

### A4. The gate is written from the request, never from the answer
Whoever writes the check must not see the implementation. Whoever verifies must
not be whoever produced.

*Why:* this is the single most valuable thing we built. Four gates in a row
were rejected for four different real defects, including one that passed its
own 53 test fixtures while mismatching the real data shape. A self-certified
gate would have passed all four.

---

## B. Truth and state

### B1. Every consequential transition is computed, never claimed
Done, verified, claimed, blocked — each derived from a file, an exit code, or
an append-only record. No agent writes its own state. Prose is commentary.

*Why:* this is the founding lesson and it still bites. Three separate tools
counted an unwritten row as finished today because the word "closed" appeared
in a sentence about a different row.

### B2. Nothing important is inferred from a proxy
If a fact matters to a decision, one component owns it and writes it down.
Never inferred from a name, a port, a word in free text, or who arrived first.

*Why:* every one of today's six failures was a proxy standing in for a fact
nobody had declared — the conductor identified by its name prefix, the
escalation target by whoever grabbed a port, a rejected gate by whether it
passed its own self-test, a verification claim by the fact that someone
claimed.

### B3. Intended state is representable
"Off on purpose" must be distinguishable from "broken." "Held pending" must be
distinguishable from "stalled."

*Why:* a seat was stopped deliberately, another seat read that as a fault and
restarted it, and the corpus run lost its GPU again. Nothing in the system
could express the intent.

### B4. Corrections are append-only
A wrong record is retracted by adding a line, never by editing. The reader
honours the last word.

*Why:* the ledger is evidence about the agents. A file an agent can rewrite is
not evidence about that agent. When we had a genuinely wrong entry today, the
append-only discipline still gave us a way to fix it.

---

## C. Memory

### C1. Durable facts live in files, not in context
Anything that must survive a restart, a compaction or a session death is on
disk, addressable, and readable by any seat without being handed to it.

*Why:* this is already one of the system's real strengths and it should be
carried forward unchanged. The research corpus, the answer page and the
evidence cards outlived every session that produced them.

### C2. Memory is searchable by machine and by human
A seat must be able to find the prior result without a human remembering it
exists. An index over the corpus, not a folder of files.

*Why:* today I rebuilt a jargon detector with a model when a better mechanical
one had been in the repo since the 17th. Nobody looked, because looking was
not cheap.

---

## D. Being watched

### D1. A status board computed from evidence, not authored
One page showing what is being worked, what is blocked and why, what closed and
on what proof. Every number on it derived; none of it typed by a seat.

*Why:* we have this and it is good. It also spent the day reporting "4/4
finished" for a sprint with three finished rows, because one predicate read
prose. The idea is right; the discipline has to be total.

### D2. Supervision covers "switched off", not only "failed"
A component that is quietly not running must be as visible as one that crashed.

*Why:* an agent stopped the gate timer to avoid a race, never restarted it, and
nothing noticed. A stopped timer is not a failed unit, so no alarm exists for
it.

### D3. The human is never the detector
Every condition that needs a person must arrive by a path that fires without
anyone asking a question.

*Why:* four of today's six defects were found because Brian asked something.
That is the failure, independent of the bugs themselves.

### D4. Escalation does not depend on who is listening
Append-only, delivered on read, surviving a dead session, a restart or nobody
being at the keyboard. A fast path may exist; it may not be the only path.

*Why:* for 23 hours escalations went to whichever session had grabbed a port
first — a window nobody was reading.

### D5. A web view that works from a phone
The board and the lanes, readable on the device Brian actually has, showing
role and state plainly.

*Why:* already true and worth keeping. It also showed the conductor as an idle
worker for four days because it inferred role from a name.

---

## E. Language

### E1. Human-facing output passes a mechanical plain-language gate
Not a model's opinion of its own writing — a deterministic check for our words,
our ids, and numbers with no referent.

*Why:* asked whether its own text is clear, a model says yes. The mechanical
checker ranked our seats the way Brian does; the classifier ranked them
backwards.

---

## F. Money and stopping

### F1. Spend is bounded by a ceiling derived from what remains
Not a remembered constant. A guard that is correct only on the day it was
written will keep enforcing after it stops being true.

*Why:* a batch cap written for a metered seat blocked free work on a different
seat weeks later, and paged a human to ask permission for something free.

### F2. A stop switch the human holds, and nothing can route around
### F3. An idle system costs nothing
No polling loop that spends to discover nothing changed.

*Why:* measured — 58% of one iteration's spend was asking whether anything had
changed, and a 27B conductor spent 98% of its actions reading files to form an
opinion the poller had already computed.

---

## G. What is NOT required

Stated explicitly, because each cost us real time:

- **A conductor that routes work.** The driver dispatches. Measured: 92 of the
  conductor's 23,793 actions were dispatches.
- **Seats waking seats.** It makes every seat a participant in every other
  seat's failure modes.
- **Many seats.** The work is sequential: one producer, one independent
  verifier, a gate writer who sees only the request.
- **A window dance.** Scheduling that exists to chase a promotional price is
  scheduling that breaks when the promotion ends — which is today.

---

## The one-line test

**Can it tell you it is stuck without being asked?** Everything above is in
service of that. A system that produces correct work but needs a human to
notice when it has stopped is the system we have, and it is the one thing that
has not improved in three iterations.
