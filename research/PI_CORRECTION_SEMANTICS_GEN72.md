# Gen72: the Perseus/Hindsight split is storage semantics, not retrieval noise

Gen68 left an anomaly. Perseus was the only engine that could say what was
*believed* at a past moment, and the only one that failed on history that
*arrived* late. The other three were exactly the opposite. This generation
explains it. No engine was run.

## Three shapes of revision, deliberately different

The fixture contains three, and they interrogate different parts of a storage
model:

- **a correction with a backdated effective time.** `L005` corrects `L001` on
  20 January about a measurement valid on the 10th. Event time is *later* than
  effective time, so a store that files by arrival puts it in the wrong place.
- **an invalidation chain with aligned times.** `L012` invalidated by `L013`,
  replaced by `L014`. Nothing backdated; the only question is whether the
  superseded version survives.
- **late-arriving history.** `L011` describes 5 February but is ingested tenth,
  after facts about the 10th, and is marked historical-only — it was never
  current.

Each failure is attributed to a mechanism rather than folded into a score.

## The result: an exact mirror

| engine | belief confusions | late arrival | reading |
|---|---|---|---|
| **perseus** | **0** | **6 of 6 absent** | keeps belief history; a fact arriving out of order is not addressable at its own event time |
| **hindsight** | 6 | **6 of 6 clean** | files by event time, so backfill lands correctly; the superseded version is not addressable |
| mem0 | 6 | 3 misfiled | neither |
| agentmemory | 6 | 3 misfiled | neither |

Perseus and Hindsight are opposites on both axes at once. That is the answer to
the question: **this is storage semantics.**

The strongest single piece of evidence is the *kind* of Perseus failure. Its
late-arriving fact is not misfiled — it is **absent**, 6 times out of 6. mem0 and
agentmemory return the wrong version (`misplaced`); Perseus returns nothing at
all. A retrieval-ranking difference produces wrong ordering; it does not make a
stored fact unreachable. Perseus appears to place observations on a knowledge
timeline, and something ingested tenth but dated fifth has nowhere to live on it.

Hindsight is the mirror: it places the backfilled fact correctly every time, and
answers every past-belief question with the version that superseded it. It keeps
an event clock and does not retain belief state.

**No engine on this fixture keeps both clocks.** That is asserted in a test.

## What the correction cluster adds

Every engine except Perseus shows `belief_truth_confusion` in *both* the
backdated-correction cluster and the aligned-time invalidation cluster. So their
inability to recover a superseded belief is not about backdating — it is that the
prior version is not addressable at all once revised.

Perseus shows `correction_not_applied` 6 times instead: it retains both versions
and sometimes serves the pre-correction value where the correction should apply.
That is a different fault with a different fix — a resolution-order problem, not
a data-loss problem.

`agentmemory` shows the one instance of `overwrote_prior_truth`, where neither
version came back.

## What this does not establish

One fixture, one correction, one invalidation chain, one backfilled fact, three
repetitions. This names a pattern and gives it a mechanism; it does not prove a
storage design. Confirming it would need either engine documentation or a fixture
with several independent backfills at different depths.

The mechanisms must not be averaged into a "temporal accuracy" score — that is
enforced in the contract and in a test, because averaging is precisely what would
have hidden the mirror.

## Artifacts

- `results/correction_semantics_gen72/semantics.json` - per-case mechanisms, per-cluster tallies, per-engine reading
- `src/memory_bakeoff/correction_semantics.py` - the mechanism attribution and the two discriminators
- `scripts/run_gen72_semantics.py` - reads committed Gen68 records only
