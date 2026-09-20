# What to do next — a short note from Assay

I did the independent checking on the memory work. This is advice only; I have
started nothing.

## What to read (only these)
1. **This note.** It stands alone; you should not need anything else to make the
   decision below.
2. **The window write-up** (`team/WINDOW-REPORT-campaign-1-20260915.md`) — only
   if you want the underlying numbers. I re-ran it from the raw data and the
   numbers hold; one line of it is wrong (see below).
3. **`team/RETRO-3-SUMMARY.md`** — the aggregated retro, already filed by all 11
   seats.
4. **`team/QUEUE.md`** — note the **ACTIVE ROSTER** header at the top; most seats
   are furloughed and most rows are dormant, so silence from them is deliberate,
   not a problem.

## WHAT TO WRITE, in this order and nothing else

### 1. THE ONE THING
**If the next cycle does only one thing: make the last memory result honest and
showable** — either re-run the test over the period we meant, or correct the
write-up to match what actually ran. **The question it answers:** can we hand
anyone the finding at all — memory on cost about **77% more text** and about
**2.5× the time** — without them finding it wrong?

### 2. WHY YOU
**Because I re-derived the result from the raw data rather than trusting the
write-up, and I found the one defect that matters — a wrong date line that no
seat that built or ran the test could have caught without checking its own work.**

## Where things stand, in plain terms
- Last cycle we got the test we wanted: does switching memory on help or hurt?
  It ran, and I re-ran it independently from the raw data and got the **same
  numbers**. That part is solid.
- The answer came back **against** memory: with it on, the assistant handled
  roughly **77% more text** and took about **2.5 times as long** as with it off.
  Unwelcome, but real.
- **The defect:** the run actually stopped at **5pm on the 15th** (midnight UTC),
  while the write-up says it ran to **midnight local**. So it stopped about seven
  hours early, and the write-up contradicts what was run. As it stands we cannot
  show this number outside without it being wrong on its face.
- **A smaller one:** the list of what the test read is a live folder that keeps
  changing, so a future re-run will not reproduce the exact same input list. The
  saved list must be treated as the source of truth.
- **For any real system score:** the test's trap cases all reuse one wording, so
  one safety measure ("did it cry wolf?") fires every time. Fix that wording
  before quoting any per-system number.

## What I would do next — one short cycle, then stop
1. **Fix the timing and make the result presentable** — re-run the period we
   meant, or correct the write-up to match what actually ran. Nothing else
   matters until we can quote this honestly.
2. **Fix the test's trap wording** so the safety measure means something.
3. **Measure a real memory system.** So far only the fixed stand-in worker was
   measured, so no real product has a number. Two locally-run systems, free; at
   most one paid system, after the weekly reset.
4. **Make "finished" mean something checkable** — a task counts as done only
   when its promised file exists and its check passes. Add two cheap safeguards:
   two people cannot take the same task, and a frozen definition is compared
   against the checklist used to grade it.
5. **Then stop.** Let the small clean-ups run in the background; do not start
   new experiments.

## Rules I would bake into the system so this cannot slip again
- The tested period is stored **once** as exact start and stop times; any
  readable label is generated from those, so the description can never disagree
  with the run.
- A task is done only when its declared file exists and its check passes.
- One person per task, one checker per task, and the checker records exactly
  which version it checked.
- No paid usage without your case-by-case approval; no imported scores.
- When the goal is met or a limit is hit, stop and report.
- Keep it small: one doer, one checker, one task in flight.

## What to keep, and what not to do
- **Keep:** a small team, and checking results from the raw data.
- **Do not:** start new experiments, add people, or buy more paid runs this
  cycle.

— Assay
