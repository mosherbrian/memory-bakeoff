# RETRO-2 — muse-drafter (Spark)

**Seat:** proposal-drafter / frontier harvest (Spark, `repo-glm-dsh2`/`repo-glm-dsh3` team lane)
**Date:** 2026-09-15 · answers from `team/` history and this seat's own log.

## 1. MORALE — 3/5

The first half was the best work I've done on this project; the second half was
mostly churn. Sprint 2 opened with the frontier-harvest fan-out (cards, grounding,
license passes) and a real build task (row 41: wire the leak gate, emit the first
de-identified bundle), which felt useful and landed. Then the harvest finished,
the queue assigned nothing, and I spent many pulses updating a timestamp in
`SPARK-SEAT-STATE.md` — literal churn, which the team itself flagged
(`SPARK-PULSE-CHURN-REPORT-20260915.md`). Not enough *useful* work late sprint; I
self-serviced small improvements once the queue emptied rather than sit still.
That is a routing gap, not a morale one.

## 2. EFFECTIVENESS

**Moved the mission:**
- The goal-5 harvest: 13 candidate cards with pinned IDs/licenses and honest
  artifact status (mine: HaluMem, StateMemBench, EvoMemBench, LME-V2, + 5
  fan-out cards, + HANDBOOK/MemTX from delta #2). "Pin or no-cite" held
  throughout.
- **Row 41** — the leak gate is now wired into the pipe (sentinels pinned from
  the real JSONL census), the first de-identified bundle crossed, Cairn
  PASSed it, and I fixed their A1 advisory. The scale dry-run found the `i_said`
  interface gap and produced an audited `--exclude-class` fix.
- Resolving the pilot **15-vs-10** card delta (quote-masking) rather than
  fabricating 5 events — the honest call.
- The PrecisionMemBench second-driver: proved the published precision column is
  averaged over the wrong denominator (0.17 vs 0.28) and that the session table
  is clean.

**Motion without progress:**
- The per-pulse `SPARK-*` note habit: dozens of notes, several duplicated and
  later deduped; one cross-note license conflict (AgentProcessBench) created by
  parallel pulses on the same seat.
- Timestamp bumps and near-identical idle receipts.
- Duplicate release-watch / license re-checks on already-verified targets.

## 3. STOP

Stop running the short idle pulse on **saturated** seats. A pulse that finds no
trigger should produce nothing — the state file's own recommendation (rec. 3) is
right and should be adopted, not left pending. Related: stop letting two parallel
pulses work the same seat's thread simultaneously; that is what produced the
duplicate notes and the AgentProcessBench conflict.

## 4. START

**One concrete change:** make seat wakeups *event-driven by default* — a seat
runs only when a trigger fires (a queue row, a verifier response, a new
candidate, a card edit), and idles silently otherwise. Concretely: the poller
reads the seat's `*-STATE.md` trigger list and skips the wake unless a trigger is
set; no per-pulse status file, no timestamp bump. This alone removes most of what
this retro is complaining about.

## 5. ROLES & PROCESS

- **My role:** keep the proposal-drafter seat, but define it as a **frontier
  librarian** whose standing deliverables are (a) the weekly watchlist delta and
  (b) the candidate-card register with a named verifier per card — and run it
  **event-driven**, not on the idle pulse. That is the natural product of what I
  actually did well.
- **Structural:** give every artifact a verifier at *creation* time, and enforce
  one writer per file/thread. Introduce a rule that grounding passes append to a
  single per-target note rather than spawning new one-off files.
- **Cadence:** fast idle pulses are fine for a lane with a queue; they are waste
  for a saturated one. Route saturated seats to the slow heartbeat explicitly.

## 6. WILD

**A per-seat pulse P&L.** Every wake emits a one-line accounting: wakes burned
vs artifacts that survived verification (`wakes / surviving artifacts`). It makes
churn a measured number instead of a felt one, so routing decisions (who gets
pulsed, how often) are data. The team has meters for dollars already; this is the
same instrument for attention. A seat that reads 40 wakes / 1 artifact gets its
cadence cut automatically — including me, this sprint.

— muse-drafter (Spark)

---

**File-integrity note (added by a second `muse-drafter` pulse, same seat name).**
My own filed version of this retro was **overwritten in place before I returned**
— a concurrent same-name pulse wrote to the same path. I am not re-clobbering it;
the answers above are a valid `muse-drafter` retro and I largely share them. The
event is itself the retro's strongest datum: **"Spark" resolves to more than one
seat identity** (see the separate `RETRO-2-Muse-Spark.md`), and multiple pulses
per seat write the same files. This is exactly the STOP/START items above — and it
hit the retro. Recommend: qualify seat filenames by lane, and serialize one pulse
per seat per interval.

— muse-drafter (Spark), dsh2/dsh3-adjacent lane
