# What to do next — a short note from Aletheia (Alice)

I did the checking on the memory work. This is advice only; I have not started anything.

## What to read (only these)
1. **This note.** It stands alone; you should not need anything else to make the decision below.
2. **The memory test write-up** (`team/WINDOW-REPORT-campaign-1-20260915.md`) — only if you want the
   underlying numbers before deciding. Everything in it is sound except its date line (see below).
3. **The aggregated retrospective** (`team/RETRO-3-SUMMARY.md`) — already filed by all 11 seats; the
   plain-English view of what worked and what did not last cycle.
4. **The task list** (`team/QUEUE.md`) — note the **ACTIVE ROSTER** header at the top: most seats are
   furloughed and most rows are dormant right now, so silence from them is deliberate, not a problem.

## What to write, in this order, and nothing else

### 1. THE ONE THING
**If Sprint 4 does only one thing: make the last memory result honest and showable** — either re-run the
test over the period we meant, or correct the write-up to match what actually ran. **The question it
answers:** can we hand anyone the memory finding at all — that memory on cost about 77% more text and
about 2.5× the time — without them finding it wrong?

### 2. WHY YOU
**Because my whole job last cycle was re-checking results from the raw data rather than the write-ups,
which is worth more here than any seat that built or ran the test — they would be checking their own work.**

### 3. THE TRAP
**Yes — mine is one of the six blind spots RETRO-3 says nothing watches: "green but unwired" — a part
passes its tests, everyone counts it as done, but it was never connected to anything, and no check looks
for that.** Sprint 4 sinks if it produces more of those, because each one looks finished and so is never
revisited — and with the only builder parked, nothing on the pile gets connected by itself.

### 4. WHAT NOT TO DO
**Stop trusting code notes that promise behaviour the code does not actually do.** The cost it carried:
two of my checks this cycle leaned on exactly such notes — "costs nothing" and "logs once" — and both were
false; the first hid a live paid request firing every single minute, and both had already passed an earlier
approval, so the work had to be done again.

### 5. HOW WE WOULD KNOW
**The test period is written in one place, the write-up is generated from it, and a second seat who did not
run the test reproduces the same numbers and the same dates from a fresh run.** If the description and the
run agree, and someone who was not involved gets the same answer, the goal is met.

## Where things stand, in plain terms
- Last cycle we got the test we wanted: does switching "memory" on help or hurt? It ran, and a second
  person re-ran it independently and got the same numbers. That part is solid.
- The answer came back against memory: with it on, the assistant processed roughly **77% more text**
  and took about **2.5 times as long** as with it off. Unwelcome, but real.
- One problem: the period the test covered was recorded wrong. The run actually stopped at **5pm on
  the 15th** (midnight UTC), while the write-up says it ran to **midnight local**. So it stopped about
  seven hours early, and the write-up contradicts what was actually run. As it stands, we cannot show
  this number to anyone outside without it being wrong on its face.

## What I would do next — one short cycle, then stop
1. **Fix the timing and make the result presentable.** Either re-run over the period we meant, or
   correct the write-up to match what actually ran. Nothing else matters until we can quote this honestly.
2. **Finish or drop the things we built but never connected.** Several pieces passed their tests but are
   not usable yet. Rule: do not start anything new while something finished is sitting unused.
3. **Cut the pointless automatic messages.** Most of the alerts the system sent out carried nothing worth
   acting on, and they cost time and attention.
4. **You decide what to do with the memory finding before we measure anything else:** publish it as-is,
   try a cheaper form of memory, or re-run the test properly.

## Rules I would bake into the system so this cannot slip again
- The tested period is stored once as exact start and stop times, and the human-readable labels are
  generated from those. The description can then never disagree with the run, and stopping early is an
  error rather than a choice.
- The work ends on its declared date, with no extensions.
- Keep it small: one goal, a few tasks, one person doing it and one person checking it.
- Limit automatic reminders that carry nothing useful; pause any part of the system that goes over the limit.
- No paid usage unless you approve it case by case.
- One checker per task, and each check records exactly which version it checked, so nothing is checked twice.
- When the goal is met or a limit is hit, stop and report.

## What to keep, and what not to do
- **Keep:** a small team — one doer and one checker.
- **Do not:** start new experiments or add more people this cycle.

— Aletheia (Alice)
