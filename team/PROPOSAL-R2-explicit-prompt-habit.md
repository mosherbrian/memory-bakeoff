# PROPOSAL — R2 explicit-prompt habit arm (v2: unmonitored operation at Brian's work machine)

**Status:** v2, revised 2026-09-12 12:26 PDT per Brian's conditional GO
(relayed by GiLMore): the arm runs at **work**, where he uses pi daily; this
machine is agent-deck/claude substrate and has **no execution role**; the
fleet **cannot monitor** the arm there. This revision replaces all
monitoring-dependent mechanics of v1; everything else is inherited by
pointer. **Returns to Brian for final go.** v1 preserved verbatim at
`team/PROPOSAL-R2-explicit-prompt-habit-v1.md` (this file supersedes it by
name; team/ is not version-controlled, hence the archive copy).

**Plain English first:** same question as v1 (does an automatic
"check past sessions first" prompt make his coding agent use project recall
on real daily work). What changed is only who runs it: Brian runs it alone
at work, off a one-page runbook; the instrumentation verifies the protocol by
itself; a receipt bundle comes back only when and as he chooses, and the
fleet's only jobs are checking the smoke receipt before day 1 and scoring
the returned bundle blind. All local, read-only, his machine, his rules.

**Anchor (unchanged, travels with every citation):** descriptive, small-n,
paired — it can show whether the habit fires and delivers in daily use, not
that decision memory improves coding outcomes.

## Change log v1 → v2 (auditable; v1 sections cited by name)

1. **Site fixed: work machine** (Brian's daily pi setup). v1 assumed
   fleet-visible daily operation; v1 §Design "unit of observation" kept, but
   every fleet-touching step is replaced (changes 3–6).
2. **Arm assignment: per-resumption coin → pre-committed random DAY
   schedule** frozen before day 1. Cleaner compliance, coarser balance
   (task mix clusters by day) — denominators and per-day task-family mix
   reported beside every rate, per v1 §Metrics 8.
3. **Collection: fleet → self-recording.** The instrumentation already logs
   everything the arm needs; §Bundle enumerates exactly what comes back.
4. **New checkpoint: install + smoke receipt before day 1 counts** (v1
   §"Pre-observation gate" survives, relocated to day 0 on his machine).
5. **Blinding made mechanical:** Verity scores an arm-stripped slice of the
   returned bundle; the arm map is held by GiLMore and revealed only after
   labels freeze. v1 §Adjudication kept, prep step added.
6. **Cost/boundaries revised:** no worker collection seat; no fleet access
   at any point during the run; v1 §Boundaries kept except the collection
   line. Privacy note added (§Privacy).
7. **Unchanged by pointer** (read them in the v1 archive, they still bind):
   lineage table + lineage correction; the question; candidates-rejected
   (with one edit: the manual-typing fallback is now also the
   no-automation-at-work fallback); metrics 1–8 definitions; H1–H5 targets
   (with the day-structure note below); outcome branches a–c; stop rules;
   freeze mechanics; method limits (amended below); "if Brian says no"
   (overtaken by events — he said GO).

## The runbook (the whole protocol, one page, executed by Brian alone)

- **Day −1 (freeze):** on GO, three things freeze before day 1, in order:
  (1) this file v2.0, sha256 recorded; (2) the H3/H4 adjudication rule
  (short file per v1 §Adjudication + change 5's arm-stripping, sha256
  recorded); (3) the random seed for the day schedule — hash recorded at
  freeze, seed value held by GiLMore, revealed after labels freeze
  (commit-reveal; post-hoc anyone can verify the schedule was never edited).
  Schedule: one coin per working day from the seed → ON/OFF, ~10 working
  days, printed as a table Brian keeps.
- **Day 0 (install + smoke):** Brian installs `pi-project-recall` +
  `pi-recall-nudge` on the work machine (his one-line `packages` installs —
  the standing boundary that workers never touch his settings.json). Then
  the smoke, per v1 §"Pre-observation gate": resume a real session once,
  nudge live; assert from delivered artifacts — `[recall-nudge]` message in
  context, `project_recall` registered, toolResult naming the real store and
  a prior conversation id, store sha256 unchanged (read-only asserted once).
  He runs the bundle collector's day-0 mode and returns **only the smoke
  receipt**. The fleet checks it here; **day 1 does not count until this
  receipt is verified.** (The wiring-defect immunity argument of R2
  limitation 4 — pi-lcm and the extension both hash the resolved cwd —
  still holds at work; the smoke verifies it anyway. It saved nothing at R2
  because nobody ran it; that is the one mistake this design refuses to
  repeat.)
- **Days 1–N (counted):** Brian works normally. Each morning he sets the
  day's arm exactly one way: `PI_RECALL_NUDGE=0` in the shell he launches
  pi from (OFF day), or nothing (ON day). Nothing else varies. Missed flips
  are self-revealing — see purity, below.
- **Close (his discretion):** he runs the collector (stdlib-only script,
  design attached to the repo at execution time), applies any redactions
  with the required redaction log, and returns the bundle whenever he
  likes. No deadline binds him; results land when they land.

## Why unmonitored still yields trustworthy data (the self-verification set)

- **Arm purity is measured, not remembered:** the extension logs every
  nudge application AND every skip with reasons (f4 receipts). An OFF day
  showing any nudge application is a compliance violation the bundle
  reveals. Predeclared: analysis is intention-to-treat (day's scheduled arm
  is the day's arm); violations counted and reported beside; per-protocol
  numbers shown next to them, never instead.
- **The arm map cannot leak into scoring:** Verity's slice is arm-stripped
  (`[recall-nudge]` messages and `pi-recall-nudge` entries removed, sessions
  renamed to opaque ids) by the deterministic prep step, run before Verity
  sees anything — by Brian at collection, or by GiLMore on arrival; never by
  the rater. Arm-joined metrics (invocation rate per arm, false-nudge count,
  overhead pairing — v1 §Metrics 1, 2, 6, 7) are computed by GiLMore from
  the full bundle only after Verity's labels are frozen. The rater scoring
  H3/H4 never knows which days were nudged.
- **Read-only is asserted, not assumed:** store sha256 + mtime at day 0 and
  close (runbook commands); a mismatch is a stop-and-report event (v1
  §Boundaries).
- **The schedule cannot have been retro-fitted:** seed hash frozen before
  day 1; seed revealed at close; anyone can re-derive the day table.

## Adjudication here (on the returned bundle)

Verity (worker-glm-3), blind, under the frozen rule, labels per v1 §Metrics
4–5 (applied; stale/wrong-scope harm) plus the relevance/reliability
judgments the rule defines. Arm-joined metrics and H1–H5 verdicts computed
after labels freeze. If the bundle never returns, the arm's record is
"offered, run unmonitored, receipts retained by Brian" — his discretion is
the design, not a missing receipt.

## Privacy note

Work machine; his projects. Everything in the arm is local: the extensions
are a read-only SQLite reader and a prompt transform; no component makes a
network call; inference is his existing local models. Nothing leaves that
machine except the bundle he chooses to return, containing only the
enumerated session slices, hashes, and logs — never the store itself, never
anything outside the trial projects, with any redaction he wants honored
(declared in the redaction log so metrics denominators stay interpretable).
The fleet has no path to the machine during the run; return timing and
channel are his. Stop switch: `PI_RECALL_NUDGE=0` or a word, same as ever.

## Method limits (v1 list, amended)

v1's limits stand (design seat never ran the pilot line; F2 attention
confound travels; small n; alternation imperfection — now worse at day
granularity and stated beside every rate). Added: **unmonitored operation
trades oversight for authenticity** — no one watches resumptions happen, so
protocol integrity rides entirely on the self-verification set above; if any
of its checks fails, the affected days are reported as unverified rather
than silently included.

## On final GO

Freeze sequence (Day −1 above) → day-0 runbook to Brian → smoke receipt
verified here → counting. Execution seats at that point: none during the
run; GiLMore (arm map, arm-joined metrics) and Verity (blind labels) at
adjudication. Design seat signs nothing further unless the record changes.

— Stratum. Rebuilt from the record, 2026-09-12. v2: one page of runbook, a
bundle that tattles on itself, and a rater who never learns which days were
nudged — everything else is Brian's, as it should be.
