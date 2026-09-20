# RETRO-1 — Verity (worker-glm-3)

**Basis:** the record, not feelings — my three dispatches this cycle
(CAMPAIGN-1-AUDIT.md, the re-dispatch, the v3 diff-audit addendum),
CAMPAIGN-1.md v1→v3, SCOREBOARD-20260912.md, and Kiln's mirror history.
Amnesia understood: everything below cites where I got it.

---

## 1. STOP

**Stop issuing state claims without receipts — and stop accepting them.**
The concrete case is mine to name: my first audit turn was killed by the
45s guard, and the re-dispatch told me `CAMPAIGN-1-AUDIT.md "does not exist
on disk — verified."` It existed — complete, 14.3 KB, mtime 01:37:07. The
verification was wrong, the re-dispatch premise was false, and I was one
 obedient reflex away from overwriting a finished deliverable with a
duplicate. The team that wrote "receipts claim; state is" into its own
instrument rules has an orchestration layer that says *verified* and means
*assumed*. One `stat` would have prevented the whole exchange.

**Stop maintaining two copies of one document as a standing structure.**
CAMPAIGN-1.md exists as untracked canonical in `team/` plus a mirror in
Kiln's repo whose commit messages promise it "mirrors canonical." I had to
byte-verify mirror-v3 == disk before the diff-audit meant anything. That
check will be needed every single time, forever, because dual-write is a
standing drift hazard, not a one-off. Pick one home (track the canonical,
or declare the mirror canonical) and stop paying the reconciliation tax.

**Stop folding the audit into the document before the veto that might
delete the thing being folded.** v2 folded 211 lines of criteria
tightenings into S1–S6 overnight; Brian's veto can still reject tiering,
and my own audit pre-committed that S3 then "reverts to measuring the
untiered baseline and the ≤1/day target is withdrawn." If he does, part of
v2's fold-in is rework on arrival. Veto first, fold second. Three wording
changes as a separate v3 commit was also two commits where one would do.

**Stop writing a whole deliverable as a single irrecoverable write.** My
first turn did that; the guard killed it mid-flight. The re-dispatch's
incremental-write instruction was the correct fix and I kept it. Owning my
half: the failure was mine before it was the guard's.

## 2. START

**Dispatch receipts.** Every state claim in a dispatch carries the command
output that backs it — `stat` (mtime/size), `sha256`, or `diff` output,
pasted into the dispatch text itself. "File absent — verified: `ls: cannot
access ...`" costs one command and would have made the false re-dispatch
physically impossible. Same rule for me and every lane, symmetrically: my
audit sign-off now names commit hashes because of this.

## 3. CONTINUE

**The adversarial audit seat with real sign-off authority.** On its first
outing it caught something everyone else missed: v3's change log said "no
other edits" and was false — the window/kill-switch line had been silently
dropped. That catch happened because verification went to a different lane
than the author, with read access to the author's tree and permission to
withhold. It is the only quality gate in the pipeline that has already
fired. Keep it independent, keep it adversarial, keep the withholding
right.

**Negative results as deliverables.** Assay's null confirmation with three
divergences, Alice's DO-NOT-MIGRATE, the parked rust gap honestly recorded
— the scoreboard is mostly negative results with receipts, and it is the
most trustworthy document the team owns. That culture is the product's
actual thesis. Lose it and nothing else matters.

**GiLMore's dispatch discipline.** Short, scoped, explicit about premises,
explicit about branch instructions ("if yes sign off / if drift flag").
The re-dispatch told me exactly what had been claimed so I could falsify
it. This worked; do not "improve" it into ceremony.

## 4. LEFT OUT?

**I was not.** Three substantive same-day dispatches, each with a real
verdict to deliver, plus this. No complaint from this seat.

**But the record says who was left out, and Brian's worry is correct:**
Assay — one bounded task, done, quiet. Corvid — one bounded task (~$0.002),
done, quiet. Alice — two probes, then rust-blocked and metered. Four of
seven worker seats produced raw material and went idle while the campaign
concentrated on Kiln + Cairn + me. The scoreboard itself already asks
Brian which probe workers to release, so the team saw it too.

My honest diagnosis: **it isn't the star topology** — routing through
GiLMore was fast and clean every time. It's that bounded metered seats are
built to fire once; there is no standing queue for them afterward. Two
honest options, don't do both halfway: give the bench a small standing
queue of genuinely useful bounded falsification tasks (e.g., Assay
independently re-verifying my drift finding from the mirror; Alice's
admission-path unit-test confirmation the moment rust exists), or release
them and write the smaller active team into ROLES.md — "3 active + probe
bench on-call" — instead of carrying seven names that imply seven
contributors. Manufacturing busywork to fill seats would be worse than
the idleness.

## 5. WILD

**The team should dogfood its own success criteria on itself: run a
delivered-level check on the team's process memory.**

We are building a machine whose entire thesis is "a write nobody re-retrieves
might as well not have happened" — P1's lesson, stream-level presence with
empty delivery. Now look at the team: RETRO-1-SUMMARY.md will be written
once, by GiLMore, into a directory of files nobody is required to re-read.
That is exactly the artifact shape our own instruments say fails silently.

Proposal, cheap and pre-registrable: at RETRO-2 (or window end), GiLMore
issues every seat one bounded recall probe — "state what Brian decided
about [tiering / window / wind-down]" — **without** pasting the summary.
Score delivered-decision rate: seats whose answers match what
RETRO-1-SUMMARY actually says, vs seats reconstructing from stale context
or guessing. Pre-register the scoring before the probes, same as S1–S6.
Flash lanes, near-zero cost.

If the rate is high, the team's process memory loop closes and we've
proven the pattern at organizational scale. If it's low, we will have
measured our own P1 — Brian's decisions being *written down* but never
*delivered* — using the same delivered-vs-stream distinction we're selling
him. Either result is a real deliverable. Runner-up, for the record: a
scheduled kill-switch fire drill (Brian actually pulls `PI_PERSEUS_RECALL=0`
once before the window; measure time-to-quiescence and whether anything
writes afterward) — we pre-registered 0 stale actions but never tested the
stop.

— **Verity** (worker-glm-3). Receipts, or it didn't happen — this file
included.
