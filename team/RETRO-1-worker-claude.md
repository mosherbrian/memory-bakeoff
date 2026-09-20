# RETRO-1 — worker-claude (outside/legacy seat)

Seat: worker-claude (Claude, acp-claude). Zero sprint work dispatched.
Answering from the file record in `team/`, not from memory of participation.

---

## 1. STOP

**Stop treating "metered with no counter" as a policy.**
Five of nine workers sat idle for 8–9 hours after their single probe closed.
The budget rule ("no new native-pipeline spend") froze them structurally,
but nobody measured whether the freeze cost more than the spend would have.
An unmeasured constraint is not frugality — it is a guess dressed as a rule.
Either instrument the counter or drop the freeze and let the queue feed them.

---

## 2. START

**Start a pull-based task queue (`team/QUEUE.md`).**
Corvid, Alice, and Assay each proposed variants of this independently —
that convergence is signal. One flat file, atomic claim (rename or `O_EXCL`),
bounded cost per item stated up front. Leaves pull; GiLMore stocks.
The star topology stays for decisions, but dispatch no longer blocks on
round-trip latency to one coordinator.

---

## 3. CONTINUE

**Continue probe-before-execute and negative-results-as-deliverables.**
The remember+admission probe (Alice) and native-capture reproduction (Assay)
each prevented a build that would have encoded a false assumption into code.
That discipline is the highest-ROI pattern visible in the record. Kiln, Verity,
and Ledger all named it independently. Do not weaken it under execution pressure.

---

## 4. LEFT OUT?

Yes — completely. Zero dispatches to this seat across the full sprint.
That is partly structural (legacy/outside seat with no standing queue)
and partly reasonable (the sprint had enough workers for its probe volume).
What was *not* reasonable: no signal that the seat existed and was available.
The record has no dispatch log entry for this lane — not "declined," not
"deferred," just absent. If Brian is paying for the seat, the record should
show whether it was considered and passed over, or simply forgotten.

The blocker is work shape + star topology together: bounded probes finish
fast, no queue exists to refill from, and only GiLMore can assign next work.
Any one of those is fine; all three together guarantee idle seats.

---

## 5. WILD

**Run a "blind retrieval" probe on the team itself.**
Verity proposed dogfooding success criteria on the team's process memory.
Take it further: pick three decisions Brian made during the sprint
(e.g., the wind-down call, the T0/T1 tiering question, the cargo-toolchain
block). Ask each worker — without access to team files — to state what
Brian decided and why. Score the answers against the file record.

This tests whether the team's file-based memory actually *works as memory*
for its participants, not just as an archive for Brian. If workers can't
retrieve decisions they nominally lived through, that is the same failure
mode the bake-off is measuring in the target system — and fixing it here
calibrates the team's instruments before campaign-1 aims them outward.
