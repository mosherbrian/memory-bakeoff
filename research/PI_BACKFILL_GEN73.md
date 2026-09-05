# Gen73: the fixture built to confirm the mirror broke half of it instead

Gen72 reported a mirror: Perseus retains superseded belief but cannot reach a
backfilled fact; Hindsight places the backfill correctly and loses the belief.
Gen73 built a fixture to test whether that was architecture or an artefact of one
correction and one backfill.

It is partly an artefact — **of my own harness**, not of the corpus.

## What the new fixture is

`backfill-v1`: 12 observations, 7 checkpoints, 13 cases, hash `784dfc56`. Four
independent late-arriving facts at three depths — 2 days, 9 days (twice) and 18
days behind their arrival — split across two fates, `historical_only` and
`later_corrected`. Two independent superseded beliefs, so belief retention is
measured more than once. Queries copy `longitudinal-v1`'s terse style, because a
full-sentence question is a different retrieval task and comparability requires
parity. `longitudinal-v1` is untouched.

## The defect

The Perseus adapter derives **both** temporal arguments from one call:

```python
instant = time_base.store_instant(case.event_time.isoformat())
arguments["as_of_unix_ms" if operation == "recall_hybrid_as_of" else "valid_at"] = instant
```

`store_instant` bisects **ingestion** times and returns a **store write
instant**. That is a transaction-time coordinate. So `valid_at` — the operation
that is supposed to ask *what was true on this date* — is being asked *what did
the store contain at the write instant nearest this date*.

Where event time and arrival nearly coincide the two are indistinguishable. A
backfill is precisely the case where they diverge, and then the resolved instant
lands **before the backfilled fact was written**:

| fixture | observation | arrival lag | `valid_at` resolves | actually written |
|---|---|---|---|---|
| backfill-v1 | B004 | 2 days | 1150 | 1300 |
| backfill-v1 | B006 | 9 days | 1150 | 1500 |
| backfill-v1 | B008 | 18 days | 999 | 1700 |
| backfill-v1 | B011 | 9 days | 1250 | 2000 |
| **longitudinal-v1** | **L011** | **9 days** | **1850** | **2000** |

The last row is the one that matters. `L011` is the single backfilled fact in the
**original** fixture — the one every late-arrival conclusion since Gen68 rests
on. It was unreachable by construction there too.

## What is retracted

**Perseus was never asked for a backfilled fact at its event time.** It was asked
what its store contained before that fact existed, and correctly returned
nothing. So these claims are withdrawn:

- Gen72: "Perseus makes backfilled event-time facts unreachable" — not
  established. The harness never posed the question.
- Gen71: `recall_hybrid_valid_at` classified `effective_time_capable` — not
  established. It was fed a transaction-time instant, so effective-time
  capability was never exercised.
- Gen68/70/72: Perseus's late-arrival failures — attributable to the adapter.

## What still stands

- **Perseus retains superseded belief**, 6 of 6 in Gen68 and unaffected here.
  Those are `as_of` cases, which are genuinely transaction-time questions and are
  mapped correctly. The other three engines' `belief_truth_confusion` is likewise
  untouched.
- **Hindsight's `query_timestamp` accepts a timestamp and leaks anyway**, 15 of
  15. That is Hindsight's own parameter on Hindsight's own path; no Perseus
  adapter is involved.
- **mem0 and agentmemory expose no temporal surface at all.** Unaffected.
- Gen70's future-leakage result for the three engines without a working temporal
  filter is unaffected. Perseus's "0 of 15 temporal leaks" now carries a caveat:
  an empty or pre-write snapshot cannot leak, so that figure is not evidence of a
  working filter.

So the mirror's **Hindsight arm survives** and its **Perseus arm does not**.

## What I did not do

I did not modify the frozen adapter. Its hash appears in every committed Round-2
result, and changing it would silently invalidate them. The correct repair is a
new adapter revision that passes `effective_time` to `valid_at`, run as its own
generation with its own provenance — not a quiet edit.

I also did not re-run the other three engines on `backfill-v1`. Until the
adapter question is settled the comparison would carry the same defect for
Perseus, and a three-engine table with one arm known-broken invites exactly the
misreading this generation exists to prevent.

## How it was found

A trial run scored Perseus 0 of 13 and I did not report it. Plain recall returned
three items per case, so retrieval plainly worked, which made "every temporal
operation returns nothing" a harness hypothesis rather than an engine one. The
adapter confirmed it in six lines.

## Artifacts

- `src/memory_bakeoff/backfill.py` - the fixture, hash `784dfc56`
- `scripts/run_gen73_backfill.py` - the multi-engine runner, ready once the adapter is fixed
- `scripts/run_gen73_valid_at_audit.py` - the defect audit, no engine required
- `results/backfill_gen73/valid_at_audit.json` - both fixtures, per observation
- `results/backfill_gen73/perseus.json` - the trial run that surfaced it
