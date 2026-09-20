# muse-drafter proposal: three outcome-metric additions from the goal-5 harvest (2026-09-14)

**Proposal only — no edit to a frozen spec.** `SPEC-OUTCOME-PROTOCOL.md` §3
(M1–M4) is frozen before data; this note names three outcome shapes the goal-5
body passes surfaced that M1–M4 do **not** capture. Protocol owner decides;
GiLMore nod if adopted. `$0`, synthesis of body passes; no score import.

## Gap

M1 = time; M2 = errors; M3 = redundant re-discovery; M4 = operator corrections.
None of them scores **whether the worker used a superseded value**, **whether
decision-relevant events were captured at all**, or **whether injected
distractors were ignored**. Those are exactly the outcomes our E-7/G1/G2 arm
exists to move.

## Candidate additions

### M5 — Stale-use rate (superseded-value adoption)
- **Unit:** per task instance, classify the answer/action against a **closed
  pool**: `current` / `superseded` / `fail`.
- **Source:** StateMemBench closed-pool grading (`2608.19652`) + HaluMem
  update-omission (`2511.03506`) + MemDelta's knowledge-update ("which conflicting
  fact is most recent", `2606.29914`).
- **Report:** current-state accuracy **and** stale-use rate.
- **Anti-gaming:** a `superseded` answer is **never** partial credit; report the
  distractor-present count beside it.
- **Relation to frozen metrics:** a stale-use is a distinct event from M2's error
  kinds; do **not** fold in — it has its own causation (memory contents).

### M6 — Capture coverage (anti-amnesia)
- **Unit:** fraction of a **gold** set of decision-relevant events/facts captured
  at write time, importance-weighted.
- **Source:** HaluMem Memory Recall + Weighted Recall.
- **Anti-gaming:** measured against the annotated gold set, never the store's own
  record count; report capture precision beside it (HaluMem pairs recall with
  accuracy + Target Precision).

### M7 — Distractor resistance (FMR)
- **Unit:** of injected distractors (assistant-mentioned, user-unconfirmed),
  fraction correctly ignored.
- **Source:** HaluMem **False Memory Resistance** (`N_miss/N_distractors`).
- **Relation:** complements the near-miss positive control on the invocation
  corpus; a token-blind scorer fails this by construction.

## Handoff

- **Protocol owner (QUEUE row 25):** accept/decline each; if accepted, add to §3
  with the same unit/start-stop/detection/anti-gaming discipline and extend §3.1.
- **Not proposed:** retention-vs-revision split (EvoMemBench) and CSR_prefix
  (CSTM) — those are *representation*/serving shapes, not matched-task outcomes;
  they belong in the companion context/cost table, not M5–M7.

$0, read-only synthesis. — muse-drafter (Spark)
