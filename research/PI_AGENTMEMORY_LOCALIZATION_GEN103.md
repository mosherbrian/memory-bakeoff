# Gen103 — AgentMemory Supersession Mechanism Localization

**AgentMemory only. No broad interference rerun.** Two-record probes on the
kestrel pair, semantic content unchanged, both v2 and v3 orders as controls.

## The rule, read from the pinned source

`src/functions/remember.ts`, agentmemory 0.9.29:

- on each write, existing candidates are scanned; the **first** with Jaccard
  **> 0.7** is superseded **by the incoming record**;
- the superseded row gets `isLatest = false`, **stays in KV**, and is **removed
  from both search indexes** — the code's own comment: *"recall returning an
  outdated fact as if current is worse than returning nothing"*;
- supersession **never crosses an explicit project boundary**.

A separate maintenance pass, `src/functions/auto-forget.ts`, retires the record
with the **older `createdAt`** at threshold **0.9**. That is not the write path,
and the distinction matters: the two rules differ in both threshold and direction.

## What the probe measured, stage by stage

Decisive internal state recorded at every stage — stored rows with their
retirement metadata, and search visibility — rather than inferred from outcomes.

| order | after write 1 | after write 2 | search hits |
|---|---|---|---|
| **v2** (current first) | `C2-CUR` live | `C2-CUR` **retired**, `C2-SUP` live | 1 — `C2-SUP` |
| **v3** (superseded first) | `C2-SUP` live | `C2-SUP` **retired**, `C2-CUR` live | 1 — `C2-CUR` |
| **v3 + foreign** | `C2-SUP` live | `C2-SUP` retired, `C2-CUR` live | 1 — `C2-CUR` |

The search hit's `obsId` **exactly equals the live row's `id`** in every case.

## The localisation

**Write-time mutation.** Not lifecycle drift, not retrieval filtering. The
incoming write retires the near-duplicate at the moment of the write; the row
survives in KV and leaves the index; search then returns exactly the live record.

**The behaviour is correct, and the v3 repair works.** With the superseded record
written first, the current record is the survivor and the only search hit. The
Gen100 direction was right — the rule retires the older record — and the Gen101
repair does exactly what it was designed to do.

**The project guard behaves correctly.** Adding the foreign record — the one
fixture record the two-record probe omits, and the one rule the source names —
changes nothing: it appears in neither the agent-scoped rows nor the search, and
supersession is unaffected. That was the one targeted test the source justified,
and it rules the foreign record out.

## A correction against my own Gen102 run

Gen102 reported AgentMemory still losing the current record in kestrel **under
v3**. This probe, on the same pair in the same order, shows the opposite: the
current record survives and is the only hit.

**The Gen102 AgentMemory result is therefore a harness artefact, not product
behaviour.** The product does the right thing on the corrected fixture.

What is *not* established is where the Gen102 path goes wrong. The foreign record
is ruled out. The remaining candidates are in the run path itself — most likely
the provenance mapping, which rebuilds a native-id table after each write while
rows are being retired underneath it. **I am naming that as the next thing to
find, not guessing it.** Round 3 has already had one result inverted by a
mapping defect (Gen97's hindsight probe), and the discipline is to locate this one
before reporting a cause.

## A probe defect caught and fixed

The first run used a fixed run id, so the agent identity was reused and a second
invocation listed **both runs' rows** — four where there should be two. The
conclusion was unchanged, but a localisation claim must not rest on a store shared
with an earlier probe. The run id is now unique per invocation and the table above
is from a clean run.

## What this does not say

It does not revisit any other engine, and no broad interference run was repeated.
It does not say AgentMemory handles supersession well in general — it says the
write-time rule is what the source describes, that it fires where the source says
it fires, and that on the corrected chronology it keeps the right record.
