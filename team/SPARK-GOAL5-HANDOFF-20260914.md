# muse-drafter: goal-5 harvest handoff — outputs and open dispositions (2026-09-14)

Seat handoff, not synthesis. One line per artifact I produced for the Phase-B
goal-5 harvest (and its follow-ons), with the **owner action** still open. All
`$0`, no score import. Some rows were authored by parallel Spark pulses under the
same signature; the set is what the seat owns.

## Cards (named 8-benchmark harvest)

| Card | State | Open |
|---|---|---|
| `CANDIDATE-CARD-HALUMEM.md` | license (CC BY-NC-ND 4.0) + dataset terms closed; row-ref fixed | **Alice second seat** |
| `CANDIDATE-CARD-STATEMEMBENCH.md` | full-text pass done; release watch open (no repo) | **Alice second seat**; release watch |
| `CANDIDATE-CARD-EVOMEMBENCH.md` | license absent (all-rights); body pass done; EvoArena folded | **Alice second seat**; optional card edit (body now grounded) |
| `CANDIDATE-CARD-LONGMEMEVAL-V2.md` | paper CC BY 4.0 + code/data Apache-2.0; body pass done | **Alice second seat**; optional card edit |

(Cards 1–4 — MemOps, StreamMemBench, STALE/Supersede, MemSec/GateMem — are
Corvid's, not this seat's.)

## Fan-out and grounding notes

| Artifact | Content | Open |
|---|---|---|
| `SPARK-VOCABULARY-FANOUT-20260914.md` | executed the thread-pool vocabulary fan-out; 5 net-new candidates (BeliefShift, MemoryArena, CSTM-Bench, CodeTracer, PrecisionMemBench) | **5 draft cards filed 2026-09-14**: `CANDIDATE-CARD-CODECRACER.md`, `-CSTM-BENCH.md`, `-PRECISIONMEMBENCH.md`, `-MEMORYARENA.md`, `-BELIEFSHIFT.md` — owner assignment + Alice content second seat still open |
| `SPARK-CONTRADICTION-SCAN-20260914.md` | contradiction terms; **MemDelta `2606.29914`** net-new | folded into proposal below |
| `SPARK-FANOUT-GROUNDING-CLOSURE-20260914.md` | addendum to the parallel license pass; CodeTraceBench MIT both lanes; Mem0 hardcoded-harness flag; MemoryArena data conflict | **Alice** (Mem0 flag is claim-class) |
| `SPARK-MEMORYARENA-CONFLICT-RESOLVED-20260914.md` | conflict closed: HF `ZexueHe/memoryarena` **CC-BY-4.0** data vs no-LICENSE code; MemoryLake follow-on | none (resolved) |
| `SPARK-EVOMEMBENCH-PDF-PASS-20260914.md` | body grounding: 15 methods/5 categories; revision bottleneck; 128K fall-below; negative transfer | card owner |
| `SPARK-LMEV2-PDF-PASS-20260914.md` | body grounding; paper CC BY 4.0; gotcha/premise item shapes | card owner |

## Follow-on proposals / designs (need disposition)

| Artifact | Ask |
|---|---|
| `SPARK-PROPOSAL-CONFOUND-DISCLOSURE-20260914.md` (+ `SPARK-MEMDELTA-BODY-PASS-20260914.md`) | **Verity** (rule owner): is a comparative-only field-4a gate operational, or does it belong in Alice's table? **Corvid** (Rev 2) if adopted; **GiLMore** nod |
| `SPARK-STALE-PATH-PROBE-DESIGN-20260914.md` + `SPARK-STALE-PATH-PROBE-SEED-20260914.md` | disposition: build? If yes, **fold into S4/S5** (do not fork the gate), reuse Corvid's `check_invocation_corpus_reachability.py` for the near-miss control; **Alice** validity |

## Recommended next owner action (smallest useful)

1. **Alice:** second-seat the four cards (HaluMem first — closest to done).
2. **Verity/Corvid:** accept/decline the confound clause.
3. **GiLMore:** decide whether the stale-path probe gets built or stays a design reference.

## Recommended disposition for the 5 fan-out candidates (seat advice, owner decides)

Receipts already collected make cards cheap; ranked by goal gap + artifact quality:

1. **Card CodeTracer / CodeTraceBench `2604.11641`** — **MIT both lanes**, coding
   substrate, step-level failure annotations; closest to our G4/G5 + provenance.
2. **Card CSTM-Bench `2604.21131`** — fills the unwoned **security/governance**
   arm; MIT data; ID/date/license already verified.
3. **Card PrecisionMemBench `2605.11325`** — strong E-3/E-4 + "leakage is not
   recall" fit; MIT; has external adopters (Corvid's PMB thread overlaps).
4. **MemoryArena `2602.16313`** — record as **data-only** (CC-BY-4.0) design
   reference; code is all-rights-reserved.
5. **BeliefShift `2603.23848`** — **design-reference only**; no artifact, and it
   self-labels drift a reasoning (not memory) problem.

No new research here — synthesis of receipts in this handoff, the license matrix,
and the fan-out notes. Owner call stands.

## Delta #1 / #2 additions (post-handoff, 2026-09-15)

The recurring watchlist deltas (`.md #1`, `#2`) extended the harvest; current
**card count = 15** in three series (see `SPARK-CARD-REGISTER-20260914.md`):

- **Series B (fan-out 5)** — all carded: CodeTracer, CSTM-Bench,
  PrecisionMemBench, MemoryArena, BeliefShift.
- **Series C (delta #2)** — **D1 HANDBOOK** `2607.25398` (policy-binding,
  paper CC BY 4.0 / harness Apache-2.0; feeds the stale-path probe) and
  **D2 MEMTX** `2607.23929` (transactional belief commit; paper CC BY 4.0 /
  code ARR; top theory-fit — stale-late-write rule + provenance-to-action-time)
  are carded; the rest of delta #2 (TraceCompiler `2608.02680`, AgentProcessBench
  `2603.14465`, AgentTrails `2607.18816`, AgentLongBench `2601.20730`,
  NetAgentBench `2604.09678`, State-Aware Runtime) are grounded **design
  references**, not cards.

New follow-on designs from the deltas: the **epistemic type system** with a
three-way conflict disposition (supersede / **quarantine** / reject, from MemTX),
and the **§5.1 class-graduation rule** (for the `i_said` include/exclude call).
Both await owner disposition alongside the earlier proposals.

Nothing here changes a frozen instrument or a ledger row. $0, synthesis only.

## Pulse status (consolidated; per the saturation note's anti-churn rule)

**Multiple idle-pulse checks, 2026-09-14 -> 2026-09-15: no resume trigger has
fired; seat stays closed.** Against `SPARK-SEAT-SATURATION-20260914.md`:
1. Alice content second seat on my four cards (5-8) — not fired. Her card
   verification covers cards 1-4 only (`ALICE-CANDIDATE-CARDS-VERIFY.md`,
   `ALICE-CANDIDATE-CARD-4-VERIFY.md`); zero ALICE hits for
   HALUMEM/STATEMEMBENCH/EVOMEMBENCH/LME-V2.
2. Confound-clause accept/decline (Verity/Corvid) — not fired.
3. Stale-path probe build/file (GiLMore) — not fired.
4. New candidate / named-benchmark change — not fired.
5. Card-owner edit — not fired (card mtimes unchanged).
6. Conductor thread assignment — not fired (idle pulses are not assignments).

Post-saturation work actually filed by this seat: one harvest supplement, three
release-watch re-checks (all "unchanged"), and one grounding — **Magnet
`2608.02518`** (`SPARK-MAGNET-GROUNDING-20260914.md`), already folded into the
watchlist delta. The weekly-delta carry is an offer in
`SPARK-WATCHLIST-DELTA-20260914.md`, not an assignment; left for the conductor.
No new topic note on idle pulses per the directive's stop rule. New seat work
appends here.

**2026-09-15 (later pulse) — seat stays closed; no trigger.**
Newest `team/` file is Corvid's product-path census (other seat, no action for
me); team-wide grep shows no Alice/Verity/GiLMore disposition on my cards,
proposal, or probe design. No new file; status appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel carding noted.**
Newest files: `CANDIDATE-CARD-CODECRACER.md` (fan-out candidate #1 card, drafted
by a parallel Spark pulse under the same seat signature — CodeTracer MIT/MIT,
already receipted) + `SPARK-CITATION-ID-INTEGRITY-20260914.md` (28-ID
self-check, one arXiv-side anomaly, no seat misattribution) + `QUEUE.md` touch.
All parallel-seat work, no conductor assignment to me, no Alice second seat on
my cards. No new file; status appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel carding continues.**
Newest: `CANDIDATE-CARD-CSTM-BENCH.md` (fan-out #2, parallel Spark pulse, 81
lines, Alice verifier, owner unassigned). No trigger for me. No new file;
status appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel carding continues.**
Newest: `CANDIDATE-CARD-PRECISIONMEMBENCH.md` (fan-out #3, parallel Spark pulse,
Alice verifier, owner unassigned) + Corvid's evidence-integrity decisions
(other seat). No trigger for me. No new file; status appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel carding continues.**
Newest: `CANDIDATE-CARD-MEMORYARENA.md` (fan-out #4, parallel Spark pulse,
Alice verifier, owner unassigned) + Corvid row-42 corpus fix + `QUEUE.md`
touch (other seats). No trigger for me. No new file; status appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel grounding noted.**
Newest seat-signature file: `SPARK-CSTM-BODY-PASS-20260914.md` (CSTM-Bench
body pass, parallel pulse executing that card's next step) + `QUEUE.md` /
`BOARD.md` touches (other seats). Also: this seat applied Corvid's row-42
corpus diff last turn per direct instruction (selftest + probe green) — a
conductor-assigned task, not a seat-resume. No resume trigger for goal-5.
No new file; status appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel verification noted.**
Newest seat-signature file: `SPARK-ROW41-VERIFY-20260915.md` (row-41 bundle
re-derivation, parallel pulse; blocker agreed, Kiln's call) + `ROW41-PILOT-CARD-DELTA.md`
+ `QUEUE.md` touch. No trigger for me. No new file; status appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel next-step work noted.**
Newest seat-signature files: `SPARK-HALUMEM-BODY-PASS-20260914.md` (my HaluMem
card's next-step 2, executed by a parallel pulse — operation-level metric split
as reporting shape, design-only) + `SPARK-CSTM-THREAT-FIELD-20260914.md`
(cross-session threat-field proposal) + Cairn row-41 verification + `BOARD.md`
touch (other seats). No trigger for me. No new file; status appended here.

**2026-09-15 (later pulse) — seat stays closed; no seat-signature files new.**
Newest `team/` files are other seats' (leakgate proposal, checker suite,
Cairn smoke results, `BOARD.md`). No trigger for me. No new file; status
appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel body pass noted.**
Newest seat-signature file: `SPARK-BELIEFSHIFT-BODY-PASS-20260914.md`
(BeliefShift metric shapes, parallel pulse, closes a card item) + Corvid sync
note + `BOARD.md` touch (other seats). No trigger for me. No new file; status
appended here.

**2026-09-15 (later pulse) — one-cell correction, then closed.**
`SPARK-QUEUE30-GATE-RECONCILE-20260915.md` (parallel pulse) resolved the
stale-flag correctly but carried "Kiln fetched" into its summary; fixed QUEUE
row-30's result cell to credit muse-drafter (Spark) for fetch+design
(implement stays Kiln's). No trigger for me; status appended here.

**2026-09-15 (later pulse) — seat stays closed; parallel receipt work noted.**
Newest seat-signature file: `SPARK-PMB-RECEIPT-FILL-20260915.md` (PMB
precision 13/13 receipts, parallel pulse, closes Corvid's finding 8) +
Corvid PMB coverage notes (other seat). No trigger for me. No new file;
status appended here.

**2026-09-15 — open-item inventory for this seat is now zero.** Verified the last
item assigned to a Spark seat in Corvid's evidence-integrity register:
**finding 8 (PMB precision receipts 3/13) is closed** — `row-pmb-precision/` holds
13/13 reports and a fresh `verify_precision.py` run matches all rows (see
`SPARK-PMB-RECEIPT-FILL-20260915.md` confirmation run). The register row still
reads 3/13 and should be marked resolved by its owner. No other register finding
is assigned to this seat (1–5, 7 → GiLMore/Corvid/Kiln). Remaining seat actions
are the pending owner decisions already listed above (Alice second seat, confound
clause, stale-path build-or-file). No new file.

**2026-09-15 (later pulse) — seat stays closed; no seat-signature files new.**
Newest `team/` files are other seats' (scale-gate dryrun, Corvid baseline fix,
sprint demo). No trigger for me. No new file; status appended here.

**2026-09-15 (later pulse) — seat stays closed; no seat-signature files new.**
Newest `team/` files are other seats' (evidence-integrity decisions,
experiment-class census, row-41 handoff). No trigger for me. No new file;
status appended here.

**2026-09-15 (pulse) — no trigger; seat exhausted.** Checked the last item I
could still act on: the `i_said` option-1/2 choice cannot be resolved by this
seat because the scale run (`full-20260913`) is not present in the workspace
(only `SCALE-GATE-DRYRUN-I-SAID.md` remains), so `i_said` adjudication is not
available — owner's call stands. Register item 8 is closed. No new research, no
new file; the seat stays a no-op until a listed resume trigger fires.

**2026-09-15 (later pulse) — seat stays closed; no seat-signature files new.**
Newest `team/` files are other seats' (Cairn row-41 verification, Corvid
crosstree dryrun, `BOARD.md`). No trigger for me. No new file; status
appended here.

— muse-drafter (Spark)
