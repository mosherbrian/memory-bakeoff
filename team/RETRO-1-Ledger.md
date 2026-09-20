# RETRO-1 — Ledger

## 1. STOP

**Stop treating file-based state as self-maintaining.**

SCOREBOARD-20260912 required me to reconcile four sources (ROLES.md, CAMPAIGN-1.md, DECISIONS.md, implementer-repo mirror) that had drifted from each other — silent drops, bare paths that resolve only under `implementer/repo/`, a window line that vanished between v2 and v3.  Nobody's job was to keep them consistent; everybody assumed they were.  The star topology means GiLMore transcribes worker output into canonical files, but there is no diff-audit step after transcription.  That is where drift enters.

Two-file sync (canonical `team/` vs implementer mirror) is a second instance of the same problem.  If the record is the memory — and for amnesiac workers it literally is — then a stale record is a stale agent.  Stop assuming convergence; assign a named owner for consistency checks after each file merge.


## 2. START

**Start a standing "intake" step before any worker writes.**

Right now a worker gets dispatched, produces output, and writes it to `team/`.  If the output overlaps or conflicts with something another worker already wrote (Alice/Assay capture-supersession overlap is the clearest case), deconfliction happens after the budget is spent.

Concrete change: before dispatching a bounded task, GiLMore pastes the one-line intent into a `DISPATCH-LOG.md` with a timestamp.  Workers check that log before writing.  Cost: one file read per dispatch.  Benefit: overlap is caught before execution, not after.


## 3. CONTINUE

**The probe-before-execute discipline.**

Alice's remember+admission probe and Assay's native-capture reproduction saved this project from building on a false premise — that native Perseus capture/admission could activate records.  Both came back negative.  Both were cheap (zero-generation, bounded).  Both became hard guardrails that now gate campaign-1.

That pattern — spend a small bounded task to falsify the assumption before spending a large unbounded one to build on it — is the single highest-value practice this team has.  Do not lose it.  Every campaign workstream should name the assumption it depends on and cite the probe that tested it, or flag that no probe exists.


## 4. LEFT OUT?

Honest answer: mostly, yes — I was left out.

The scoreboard was useful work, but it was one deliverable.  The synthesis role ("distills 300 pages into the sentence that matters") had material to work with — four completed probes, a campaign draft at v3, six success criteria, three workstreams, standing instrument rules — but was only invoked once.  The cross-reference for campaign-1 (tried/failed/open) is listed as my lane but has not been dispatched.

What blocked me: **work shape, not the star topology.**  The probes were correctly scoped as single-worker bounded tasks.  The campaign draft converged through Kiln+Cairn+Verity iteration.  There was no synthesis bottleneck because the pieces were small enough that GiLMore could aggregate them directly.  The star topology did not block me; the work simply did not need a dedicated synthesiser at the volume it ran.

If campaign-1 execution produces more concurrent findings (Cairn's trial cycles, triggering fire-rate data, stale-action detection, burden counts), synthesis becomes a real bottleneck and the seat earns its keep.  Until then, I was parked.


## 5. WILD

**Run the retro itself as a scored probe.**

This retro asks nine seats (including idle ones) to self-report on process.  GiLMore aggregates to a summary.  Brian reads it.  That is the standard retrospective pattern — and it has the same vulnerability as the native-capture probe: the output might not reflect reality.

Concrete proposal: after GiLMore posts RETRO-1-SUMMARY.md, assign one worker (Verity is the obvious choice given her audit seat) to score the retro against the file record.  For each claim any worker makes ("X blocked me", "Y worked well"), Verity checks whether the record supports it, contradicts it, or is silent.  Publish the score alongside the summary.

This is weird but testable.  It costs one bounded task.  It produces a calibration signal on self-report reliability — which matters because campaign-1 will rely on self-reported instrument readings (trigger fire-rate, burden counts) and we need to know how much to trust them.
