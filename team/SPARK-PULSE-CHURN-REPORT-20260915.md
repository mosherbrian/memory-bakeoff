# Spark seat pulse-churn report (2026-09-15)

**From:** muse-drafter (Spark) · **To:** GiLMore / Brian (pulse-cadence owners)
· **Cost:** $0, read-only census. **Not an R&D artifact** — an ops observation
about the pulse loop.

## Measurement

- **69** `team/SPARK-*.md` files (all dated today) · **101** muse-drafter lines in
  `RD-THREADS.md`.
- **25** license/grounding/body-pass notes; **18** lines are idle/no-trigger/
  quiescent receipts.
- Parallel same-seat pulses are editing the single live `SPARK-SEAT-STATE.md`
  concurrently; a racing write duplicated a line (fixed once).

## Value actually delivered (the non-churn share)

13 harvest cards (8 named + 5 fan-out, several by parallel pulses), 5 paper body
passes (EvoMemBench, LME-V2, MemDelta, CSTM, CodeTracer, HaluMem, BeliefShift),
the license matrix + version audit (caught the CSTM license error and isolated
the one version-dependent case), the citation-ID integrity audit, the
confound/license-pin/class-graduation/M5–M7/stale-path/epistemic-type proposals,
and the QUEUE-30 + register-item-8 closures.

## Churn share (what the cadence produced)

- **Two independent license passes + a reconciling addendum** for the same
  targets, and a register/closeout-index overlap — resolved only by grep-dedup.
- **18 no-work pulses**, each of which still had to touch a file (timestamp /
  receipt) while the seat was quiescent.
- State-file races from concurrent same-seat pulses.

## Recommendation

1. **Serialize, don't slow down.** Corvid's billing position
   (`BILLING-CORVID.md`) shows the ~1–5 min cadence is deliberate: Muse cache hit
   degrades 96.9% → 14.8% over 0–6 min, so tighter pulses are *cheaper*. So the
   fix is **one pulse per seat per interval**, not a slower cadence.
2. **Route this seat event-driven between its own work items** — the bottleneck
   is **pending owner decisions** (Alice second seat; Verity/Corvid confound +
   license-pin clauses; protocol-owner M5–M7 and class-graduation; GiLMore
   stale-path build-or-file), not a shortage of artifacts. More pulses cannot
   advance those, but a serialized pulse can still carry cache-warm work.
3. **Stop auto-bumping the state file** on no-trigger pulses; let it stand until
   a resume trigger fires.

## What this seat will do meanwhile

Remain quiescent per `SPARK-SEAT-STATE.md`; act only on a listed trigger. This
report is the artifact for this pulse.

$0, read-only. — muse-drafter (Spark)
